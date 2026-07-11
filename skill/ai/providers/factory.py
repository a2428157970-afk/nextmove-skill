"""Factory contract for creating future provider adapters."""

from abc import ABC, abstractmethod

from skill.ai.configuration.settings import AIProviderSettings
from skill.ai.providers.adapters.base import BaseProviderAdapter


class ProviderFactory(ABC):
    """Create an adapter from application-provided settings and credentials."""

    @abstractmethod
    def create_provider(
        self,
        settings: AIProviderSettings,
        credentials: object,
    ) -> BaseProviderAdapter:
        """Create a provider adapter without defining a concrete SDK client."""
