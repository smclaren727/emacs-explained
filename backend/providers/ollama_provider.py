from typing import Optional

from langchain_community.llms import Ollama

from backend.providers.base import ChatProvider


class OllamaChatProvider(ChatProvider):
    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._base_url = base_url
        self._client = Ollama(model=model, base_url=base_url)

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model(self) -> str:
        return self._model

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        full_prompt = prompt
        if system:
            full_prompt = f"System:\n{system}\n\nUser:\n{prompt}"

        try:
            return self._client.invoke(full_prompt)
        except AttributeError:
            return self._client.predict(full_prompt)
