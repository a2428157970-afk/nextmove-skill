"""Application-ready assembly of the optional AI enhancement layer."""

from skill.ai.configuration.settings import AIProviderSettings
from skill.ai.credentials.base import CredentialProvider
from skill.ai.enhancement.service import EnhancementService
from skill.ai.providers.factory import ProviderFactory
from skill.ai.providers.registry import ProviderRegistry


class AIRuntime:
    """Compose external credentials, a factory, registry, and enhancement service."""

    def __init__(
        self,
        settings: AIProviderSettings,
        credential_provider: CredentialProvider,
        provider_factory: ProviderFactory,
        registry: ProviderRegistry | None = None,
    ):
        self.settings = settings
        self.credential_provider = credential_provider
        self.provider_factory = provider_factory
        self.registry = registry or ProviderRegistry()

    def build_enhancement_service(self) -> EnhancementService:
        """Assemble a service, falling back to its unavailable-provider state."""
        credentials = self.credential_provider.get_credentials(
            self.settings.provider_name
        )
        if credentials is None:
            return EnhancementService()

        try:
            provider = self.provider_factory.create_provider(
                self.settings,
                credentials,
            )
        except Exception:
            return EnhancementService()

        self.registry.register_provider(self.settings.provider_name, provider)
        return EnhancementService(
            registry=self.registry,
            provider_name=self.settings.provider_name,
        )
