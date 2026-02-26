from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

from backend.config import AppConfig
from backend.service import ask_emacs, explain_region

app = FastAPI(title="Emacs Explained API", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    skill_level: str = Field(default="beginner")


class ExplainRegionRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = Field(default="elisp")
    context: str = Field(default="")
    skill_level: str = Field(default="beginner")


@app.get("/health")
def health() -> Dict[str, Any]:
    config = AppConfig.from_env()
    return {
        "status": "ok",
        "provider": config.model_provider,
        "chat_model": config.chat_model,
        "embedding_model": config.embedding_model,
    }


@app.get("/config")
def config() -> Dict[str, Any]:
    cfg = AppConfig.from_env()
    return {
        "model_provider": cfg.model_provider,
        "chat_model": cfg.chat_model,
        "embedding_model": cfg.embedding_model,
        "vector_db_dir": cfg.vector_db_dir,
        "retrieval_k": cfg.retrieval_k,
        "ollama_base_url": cfg.ollama_base_url,
        "local_small_base_url": cfg.local_small_base_url,
        "local_model_file": cfg.local_model_file,
        "enable_local_logs": cfg.enable_local_logs,
        "local_log_path": cfg.local_log_path,
        "has_openai_api_key": bool(cfg.openai_api_key),
        "openai_base_url": cfg.openai_base_url,
    }


@app.post("/ask")
def ask(payload: AskRequest) -> Dict[str, Any]:
    request_id = str(uuid4())
    result = ask_emacs(
        payload.question,
        skill_level=payload.skill_level,
        request_id=request_id,
    )
    return result


@app.post("/explain-region")
def explain(payload: ExplainRegionRequest) -> Dict[str, Any]:
    request_id = str(uuid4())
    result = explain_region(
        code=payload.code,
        language=payload.language,
        context=payload.context,
        skill_level=payload.skill_level,
        request_id=request_id,
    )
    return result
