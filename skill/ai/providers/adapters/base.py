"""Shared boundary for future concrete AI provider adapters."""

from abc import ABC

from skill.ai.configuration.settings import AIProviderSettings
from skill.ai.providers.base import AIProvider


class BaseProviderAdapter(AIProvider, ABC):
    """An AIProvider with externally supplied, credential-free settings."""

    def __init__(self, settings: AIProviderSettings):
        self.settings = settings
