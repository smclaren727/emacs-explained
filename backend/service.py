from typing import Dict, List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from backend.config import AppConfig
from backend.health import check_local_small_prereqs
from backend.prompts import ask_prompt_template, explain_region_prompt_template
from backend.providers.factory import get_chat_provider
from backend.telemetry import log_event


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


def _log_response(
    *,
    config: AppConfig,
    request_id: Optional[str],
    interaction: str,
    provider_name: str,
    model_name: str,
    skill_level: str,
    docs_count: int,
) -> None:
    log_event(
        {
            "event": "completion",
            "request_id": request_id,
            "interaction": interaction,
            "provider": provider_name,
            "model": model_name,
            "skill_level": skill_level,
            "retrieval_chunks": docs_count,
        },
        config,
    )


def ask_emacs(
    query: str,
    skill_level: str = "beginner",
    request_id: Optional[str] = None,
) -> Dict[str, object]:
    config = AppConfig.from_env()
    provider = _prepare_provider(config)

    docs = _retrieve_docs(query, config)
    context = _format_context(docs)
    prompt = ask_prompt_template().format(
        question=query,
        skill_level=skill_level,
        context=context,
    )

    answer = provider.generate(prompt)
    _log_response(
        config=config,
        request_id=request_id,
        interaction="ask",
        provider_name=provider.name,
        model_name=provider.model,
        skill_level=skill_level,
        docs_count=len(docs),
    )

    return {
        "answer": answer,
        "sources": _extract_sources(docs),
        "provider": provider.name,
        "model": provider.model,
        "request_id": request_id,
    }


def explain_region(
    code: str,
    language: str = "elisp",
    context: str = "",
    skill_level: str = "beginner",
    request_id: Optional[str] = None,
) -> Dict[str, object]:
    config = AppConfig.from_env()
    provider = _prepare_provider(config)

    retrieval_query = f"{language} {context} {code[:1200]}"
    docs = _retrieve_docs(retrieval_query, config)

    prompt = explain_region_prompt_template().format(
        skill_level=skill_level,
        language=language,
        extra_context=context or "(none)",
        docs_context=_format_context(docs),
        code=code,
    )

    answer = provider.generate(prompt)
    _log_response(
        config=config,
        request_id=request_id,
        interaction="explain_region",
        provider_name=provider.name,
        model_name=provider.model,
        skill_level=skill_level,
        docs_count=len(docs),
    )

    return {
        "answer": answer,
        "sources": _extract_sources(docs),
        "provider": provider.name,
        "model": provider.model,
        "request_id": request_id,
    }
