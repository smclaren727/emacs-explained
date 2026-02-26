import json
from typing import Optional
from urllib import request

from backend.providers.base import ChatProvider


class LocalSmallChatProvider(ChatProvider):
    def __init__(self, model: str, base_url: str = "http://127.0.0.1:8080/v1") -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "local_small"

    @property
    def model(self) -> str:
        return self._model

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.2,
        }

        req = request.Request(
            url=f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(
                "local_small provider could not reach local inference server. "
                "Start an OpenAI-compatible local endpoint (for example llama.cpp server) "
                f"at {self._base_url}."
            ) from exc

        return data["choices"][0]["message"]["content"].strip()
