"""Registry of externally managed AI provider instances."""

from skill.ai.providers.base import AIProvider


class ProviderRegistry:
    """Store named provider instances without managing their lifecycle."""

    def __init__(self):
        self._providers: dict[str, AIProvider] = {}

    def register_provider(self, name: str, provider: AIProvider) -> None:
        """Register an externally created provider instance by name."""
        self._providers[name] = provider

    def get_provider(self, name: str) -> AIProvider | None:
        """Return a provider instance when it has been registered."""
        return self._providers.get(name)

    def list_providers(self) -> list[str]:
        """Return registered provider names in registration order."""
        return list(self._providers)
