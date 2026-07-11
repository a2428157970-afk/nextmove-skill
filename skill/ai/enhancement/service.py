"""Provider-neutral orchestration for optional AI enhancements."""

from skill.ai.errors import (
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from skill.ai.context import AIRequestContext
from skill.ai.operations.policy import ProviderRuntimePolicy
from skill.ai.providers.base import AIProvider
from skill.ai.providers.registry import ProviderRegistry
from skill.ai.schemas import AIEnhancementResult


class EnhancementService:
    """Use an injected provider to enhance structured Skill Core output."""

    def __init__(
        self,
        provider: AIProvider | None = None,
        registry: ProviderRegistry | None = None,
        provider_name: str | None = None,
        runtime_policy: ProviderRuntimePolicy | None = None,
    ):
        self.runtime_policy = runtime_policy or ProviderRuntimePolicy()
        if provider is not None:
            self.provider = provider
        elif registry is not None and provider_name is not None:
            self.provider = registry.get_provider(provider_name)
        else:
            self.provider = None

    def enhance(
        self,
        prompt: str,
        context: dict,
        request_context: AIRequestContext | None = None,
    ) -> AIEnhancementResult:
        """Return enhanced content or a structured unavailable-provider result."""
        del request_context

        if self.provider is None or not self.runtime_policy.enabled:
            return AIEnhancementResult(
                success=False,
                error="AI provider unavailable",
            )

        try:
            if not self.provider.health_check():
                return AIEnhancementResult(
                    success=False,
                    error="AI provider unavailable",
                )
        except Exception:
            return AIEnhancementResult(
                success=False,
                error="AI provider unavailable",
            )

        error: str | None = None
        for _ in range(self.runtime_policy.max_retries + 1):
            try:
                enhanced_content = self.provider.generate(prompt, context)
            except ProviderUnavailableError:
                error = "AI provider unavailable"
            except ProviderTimeoutError:
                error = "AI provider timeout"
            except ProviderResponseError:
                error = "AI provider response error"
            except Exception:
                error = "AI provider unavailable"
            else:
                if not isinstance(enhanced_content, str) or not enhanced_content.strip():
                    error = "AI provider response error"
                    continue
                return AIEnhancementResult(
                    success=True,
                    enhanced_content=enhanced_content,
                )

        return AIEnhancementResult(success=False, error=error)
