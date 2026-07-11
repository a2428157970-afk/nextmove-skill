"""OpenAI-compatible provider adapter with externally injected transport."""

from skill.ai.providers.openai.provider import OpenAICompatibleProvider
from skill.ai.providers.openai.transport import HTTPTransport

__all__ = ["HTTPTransport", "OpenAICompatibleProvider"]
