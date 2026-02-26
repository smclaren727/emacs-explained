from typing import Optional

from backend.providers.base import ChatProvider


class LocalSmallChatProvider(ChatProvider):
    def __init__(self, model: str) -> None:
        self._model = model

    @property
    def name(self) -> str:
        return "local_small"

    @property
    def model(self) -> str:
        return self._model

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        raise RuntimeError(
            "MODEL_PROVIDER=local_small is not implemented yet. "
            "Use MODEL_PROVIDER=ollama or MODEL_PROVIDER=openai for now."
        )
