"""Tests for provider runtime operations without live provider traffic."""

import unittest

from skill.ai import (
    AIProvider,
    AIRequestContext,
    EnhancementService,
    ProviderRuntimePolicy,
    ProviderUnavailableError,
)


class CountingProvider(AIProvider):
    """Provider double that records generation calls."""

    def __init__(self, healthy: bool = True, failures_before_success: int = 0):
        self.healthy = healthy
        self.failures_before_success = failures_before_success
        self.generate_calls = 0

    def health_check(self) -> bool:
        return self.healthy

    def generate(self, prompt: str, context: dict) -> str:
        self.generate_calls += 1
        if self.generate_calls <= self.failures_before_success:
            raise ProviderUnavailableError()
        return f"{prompt}: enhanced"


class ProviderRuntimeOperationsTests(unittest.TestCase):
    def test_runtime_policy_uses_safe_default_values(self):
        policy = ProviderRuntimePolicy()

        self.assertTrue(policy.enabled)
        self.assertIsNone(policy.timeout)
        self.assertEqual(policy.max_retries, 0)
        self.assertTrue(policy.fallback_enabled)

    def test_runtime_policy_preserves_explicit_values(self):
        policy = ProviderRuntimePolicy(
            enabled=False,
            timeout=2.5,
            max_retries=1,
            fallback_enabled=False,
        )

        self.assertFalse(policy.enabled)
        self.assertEqual(policy.timeout, 2.5)
        self.assertEqual(policy.max_retries, 1)
        self.assertFalse(policy.fallback_enabled)

    def test_request_context_contains_only_request_metadata(self):
        request_context = AIRequestContext(
            provider_name="openai-compatible",
            model_name="test-model",
            capability="resume_improvement",
            request_id="request-123",
        )

        self.assertEqual(request_context.provider_name, "openai-compatible")
        self.assertEqual(request_context.model_name, "test-model")
        self.assertEqual(request_context.capability, "resume_improvement")
        self.assertEqual(request_context.request_id, "request-123")

    def test_provider_default_health_check_is_healthy(self):
        class ExistingProvider(AIProvider):
            def generate(self, prompt: str, context: dict) -> str:
                return prompt

        self.assertTrue(ExistingProvider().health_check())

    def test_disabled_policy_returns_structured_unavailable_without_generation(self):
        provider = CountingProvider()
        service = EnhancementService(
            provider=provider,
            runtime_policy=ProviderRuntimePolicy(enabled=False),
        )

        result = service.enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(provider.generate_calls, 0)

    def test_unhealthy_provider_returns_structured_unavailable_without_generation(self):
        provider = CountingProvider(healthy=False)
        service = EnhancementService(provider=provider)

        result = service.enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(provider.generate_calls, 0)

    def test_default_policy_makes_one_generation_attempt(self):
        provider = CountingProvider(failures_before_success=1)
        service = EnhancementService(provider=provider)

        result = service.enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(provider.generate_calls, 1)

    def test_policy_retries_generation_for_configured_additional_attempt(self):
        provider = CountingProvider(failures_before_success=1)
        service = EnhancementService(
            provider=provider,
            runtime_policy=ProviderRuntimePolicy(max_retries=1),
        )

        result = service.enhance("Improve", {})

        self.assertTrue(result.success)
        self.assertEqual(result.enhanced_content, "Improve: enhanced")
        self.assertEqual(provider.generate_calls, 2)

    def test_service_accepts_request_context_without_persisting_it(self):
        provider = CountingProvider()
        service = EnhancementService(provider=provider)
        request_context = AIRequestContext(
            provider_name="mock",
            model_name="mock-model",
            capability="resume_improvement",
            request_id="request-456",
        )

        result = service.enhance("Improve", {}, request_context)

        self.assertTrue(result.success)
        self.assertFalse(hasattr(service, "request_context"))


if __name__ == "__main__":
    unittest.main()
