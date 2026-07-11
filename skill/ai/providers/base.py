"""Provider interface without SDK, network, or configuration dependencies."""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Generate enhancement content from a prompt and structured context."""

    def health_check(self) -> bool:
        """Return whether the provider is available for a request.

        The default keeps existing provider implementations compatible.
        """
        return True

    @abstractmethod
    def generate(self, prompt: str, context: dict) -> str:
        """Return generated content for the supplied enhancement request."""
