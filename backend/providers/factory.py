from backend.config import AppConfig
from backend.providers.base import ChatProvider
from backend.providers.local_small import LocalSmallChatProvider
from backend.providers.ollama_provider import OllamaChatProvider
from backend.providers.openai_provider import OpenAIChatProvider


def get_chat_provider(config: AppConfig) -> ChatProvider:
    if config.model_provider == "ollama":
        return OllamaChatProvider(model=config.chat_model, base_url=config.ollama_base_url)

    if config.model_provider == "openai":
        return OpenAIChatProvider(
            model=config.chat_model,
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
        )

    if config.model_provider == "local_small":
        return LocalSmallChatProvider(
            model=config.chat_model,
            base_url=config.local_small_base_url,
        )

    raise ValueError(
        "Unsupported MODEL_PROVIDER. "
        "Use one of: local_small, ollama, openai."
    )
