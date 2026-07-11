"""Provider abstractions for optional AI enhancement."""

from skill.ai.providers.adapters import BaseProviderAdapter, MockProviderAdapter
from skill.ai.providers.base import AIProvider
from skill.ai.providers.factory import ProviderFactory
from skill.ai.providers.openai import HTTPTransport, OpenAICompatibleProvider
from skill.ai.providers.registry import ProviderRegistry

__all__ = [
    "AIProvider",
    "BaseProviderAdapter",
    "MockProviderAdapter",
    "HTTPTransport",
    "OpenAICompatibleProvider",
    "ProviderFactory",
    "ProviderRegistry",
]
