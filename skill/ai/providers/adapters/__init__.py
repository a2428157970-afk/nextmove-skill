"""Provider adapter contracts and test-only implementations."""

from skill.ai.providers.adapters.base import BaseProviderAdapter
from skill.ai.providers.adapters.mock import MockProviderAdapter

__all__ = ["BaseProviderAdapter", "MockProviderAdapter"]
