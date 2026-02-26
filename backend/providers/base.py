from abc import ABC, abstractmethod
from typing import List, Optional


class ChatProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        pass


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass
