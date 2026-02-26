import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    model_provider: str = "ollama"
    chat_model: str = "deepseek-r1"
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_db_dir: str = "emacs_db"
    retrieval_k: int = 4
    ollama_base_url: str = "http://localhost:11434"
    local_small_base_url: str = "http://127.0.0.1:8080/v1"
    local_model_file: str = "data/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            model_provider=os.getenv("MODEL_PROVIDER", "ollama").strip().lower(),
            chat_model=os.getenv("CHAT_MODEL", "deepseek-r1").strip(),
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2").strip(),
            vector_db_dir=os.getenv("VECTOR_DB_DIR", "emacs_db").strip(),
            retrieval_k=int(os.getenv("RETRIEVAL_K", "4")),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip(),
            local_small_base_url=os.getenv(
                "LOCAL_SMALL_BASE_URL", "http://127.0.0.1:8080/v1"
            ).strip(),
            local_model_file=os.getenv(
                "LOCAL_MODEL_FILE", "data/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            ).strip(),
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        )
