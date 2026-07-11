"""Deterministic adapter used only to exercise the adapter contract."""

from skill.ai.providers.adapters.base import BaseProviderAdapter


class MockProviderAdapter(BaseProviderAdapter):
    """Return deterministic content without a network or SDK dependency."""

    def generate(self, prompt: str, context: dict) -> str:
        return f"{self.settings.provider_name}: {prompt}"
