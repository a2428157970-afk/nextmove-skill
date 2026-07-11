"""Application-owned dependency assembly for the stable AI runtime."""

from skill.ai.application.policy import AIFeaturePolicy
from skill.ai.application.limits import AIApplicationLimits
from skill.ai.application.service import ApplicationEnhancementService
from skill.ai.configuration.settings import AIProviderSettings
from skill.ai.credentials.base import CredentialProvider
from skill.ai.enhancement.service import EnhancementService
from skill.ai.providers.factory import ProviderFactory
from skill.ai.runtime import AIRuntime


class ApplicationRuntimeAdapter:
    """Connect application infrastructure to the provider-neutral AI runtime."""

    def __init__(
        self,
        settings: AIProviderSettings,
        credential_provider: CredentialProvider,
        provider_factory: ProviderFactory,
        transport: object,
        feature_policy: AIFeaturePolicy | None = None,
        limits: AIApplicationLimits | None = None,
        live_request: bool = False,
    ):
        self.settings = settings
        self.credential_provider = credential_provider
        self.provider_factory = provider_factory
        self.transport = transport
        self.feature_policy = feature_policy or AIFeaturePolicy()
        self.limits = limits or AIApplicationLimits()
        self.live_request = live_request

    def build_runtime(self) -> AIRuntime:
        """Build the existing runtime without passing application transport."""
        return AIRuntime(
            settings=self.settings,
            credential_provider=self.credential_provider,
            provider_factory=self.provider_factory,
        )

    def build_enhancement_service(self) -> EnhancementService:
        """Build an enabled service or return its structured unavailable state."""
        if not self.feature_policy.enabled:
            return EnhancementService()
        if not self.feature_policy.enhancement_enabled:
            return EnhancementService()
        service = self.build_runtime().build_enhancement_service()
        return ApplicationEnhancementService(
            service,
            self.limits,
            live_request=self.live_request,
        )
