from typing import Dict, List

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from backend.config import AppConfig
from backend.health import check_local_small_prereqs
from backend.providers.factory import get_chat_provider

PROMPT_TEMPLATE = """
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


def _format_context(docs: List) -> str:
    if not docs:
        return "No relevant context found in indexed resources."

    sections = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("resource_path") or doc.metadata.get("source", "unknown")
        sections.append(f"[Source {idx}: {source}]\n{doc.page_content}")

    return "\n\n".join(sections)


def _extract_sources(docs: List) -> List[str]:
    sources: List[str] = []
    for doc in docs:
        source = doc.metadata.get("resource_path") or doc.metadata.get("source")
        if source and source not in sources:
            sources.append(source)
    return sources


def ask_emacs(query: str, skill_level: str = "beginner") -> Dict[str, object]:
    config = AppConfig.from_env()
    if config.model_provider == "local_small":
        check_local_small_prereqs(config)

    embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
    vectorstore = Chroma(
        persist_directory=config.vector_db_dir,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.retrieval_k})

    try:
        docs = retriever.invoke(query)
    except AttributeError:
        docs = retriever.get_relevant_documents(query)

    context = _format_context(docs)
    prompt = PROMPT_TEMPLATE.format(
        question=query,
        skill_level=skill_level,
        context=context,
    )

    provider = get_chat_provider(config)
    answer = provider.generate(prompt)

    return {
        "answer": answer,
        "sources": _extract_sources(docs),
        "provider": provider.name,
        "model": provider.model,
    }
