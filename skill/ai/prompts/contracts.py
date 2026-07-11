"""Abstract prompt-template contract without production prompt content."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class PromptTemplate(ABC):
    """A named template that renders structured caller-supplied context."""

    name: str

    @abstractmethod
    def render(self, context: dict) -> str:
        """Render the template from the supplied structured context."""
