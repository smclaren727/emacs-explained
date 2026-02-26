from typing import Dict, List

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from backend.config import AppConfig
from backend.health import check_local_small_prereqs
from backend.providers.factory import get_chat_provider

ASK_PROMPT_TEMPLATE = """
You are an Emacs learning assistant for non-technical users.

Rules:
- Start with a plain-language explanation first.
- Avoid jargon unless needed, and define it when used.
- Give practical steps the user can try in Emacs.
- If the question is advanced, still explain what problem the feature solves.
- If the answer is uncertain, say what is missing.

User skill level: {skill_level}

Context:
{context}

Question:
{question}

Helpful answer:
""".strip()

EXPLAIN_REGION_PROMPT_TEMPLATE = """
You are an Emacs Lisp explainer for non-technical users.

Rules:
- Explain what the code does in plain language first.
- Break down behavior line-by-line or block-by-block when helpful.
- Define any Emacs or Lisp jargon.
- Mention practical impact: what changes for the user.
- If relevant, include safe ways to test the code in Emacs.

User skill level: {skill_level}
Language: {language}
Extra context from user: {extra_context}

Reference docs:
{docs_context}

Code to explain:
{code}

Helpful explanation:
""".strip()


def _build_retriever(config: AppConfig):
    embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
    vectorstore = Chroma(
        persist_directory=config.vector_db_dir,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": config.retrieval_k})


def _retrieve_docs(query: str, config: AppConfig) -> List:
    retriever = _build_retriever(config)
    try:
        return retriever.invoke(query)
    except AttributeError:
        return retriever.get_relevant_documents(query)


def _format_context(docs: List) -> str:
    if not docs:
        return "No relevant context found in indexed resources."

    sections = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("resource_path") or doc.metadata.get("source", "unknown")
        sections.append(f"[Source {idx}: {source}]\\n{doc.page_content}")

    return "\\n\\n".join(sections)


def _extract_sources(docs: List) -> List[str]:
    sources: List[str] = []
    for doc in docs:
        source = doc.metadata.get("resource_path") or doc.metadata.get("source")
        if source and source not in sources:
            sources.append(source)
    return sources


def _prepare_provider(config: AppConfig):
    if config.model_provider == "local_small":
        check_local_small_prereqs(config)
    return get_chat_provider(config)


def ask_emacs(query: str, skill_level: str = "beginner") -> Dict[str, object]:
    config = AppConfig.from_env()
    provider = _prepare_provider(config)

    docs = _retrieve_docs(query, config)
    context = _format_context(docs)
    prompt = ASK_PROMPT_TEMPLATE.format(
        question=query,
        skill_level=skill_level,
        context=context,
    )

    answer = provider.generate(prompt)
    return {
        "answer": answer,
        "sources": _extract_sources(docs),
        "provider": provider.name,
        "model": provider.model,
    }


def explain_region(
    code: str,
    language: str = "elisp",
    context: str = "",
    skill_level: str = "beginner",
) -> Dict[str, object]:
    config = AppConfig.from_env()
    provider = _prepare_provider(config)

    retrieval_query = f"{language} {context} {code[:1200]}"
    docs = _retrieve_docs(retrieval_query, config)

    prompt = EXPLAIN_REGION_PROMPT_TEMPLATE.format(
        skill_level=skill_level,
        language=language,
        extra_context=context or "(none)",
        docs_context=_format_context(docs),
        code=code,
    )

    answer = provider.generate(prompt)
    return {
        "answer": answer,
        "sources": _extract_sources(docs),
        "provider": provider.name,
        "model": provider.model,
    }
