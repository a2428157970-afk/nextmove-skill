"""Tests for the application-owned AI runtime integration boundary."""

import unittest

from skill.ai import (
    AIApplicationLimits,
    AIFeaturePolicy,
    AIExecutionMetadata,
    AIProviderSettings,
    AIRuntime,
    ApplicationRuntimeAdapter,
    CredentialProvider,
    MockProviderAdapter,
    ProviderFactory,
)


class CountingCredentialProvider(CredentialProvider):
    def __init__(self, credentials: object):
        self.credentials = credentials
        self.calls = 0

    def get_credentials(self, provider_name: str) -> object | None:
        self.calls += 1
        return self.credentials


class CountingProviderFactory(ProviderFactory):
    def __init__(self):
        self.calls = 0
        self.received_credentials: object | None = None
        self.provider: CountingProviderAdapter | None = None

    def create_provider(
        self,
        settings: AIProviderSettings,
        credentials: object,
    ) -> MockProviderAdapter:
        self.calls += 1
        self.received_credentials = credentials
        self.provider = CountingProviderAdapter(settings)
        return self.provider


class CountingProviderAdapter(MockProviderAdapter):
    def __init__(self, settings: AIProviderSettings):
        super().__init__(settings)
        self.generate_calls = 0

    def generate(self, prompt: str, context: dict) -> str:
        self.generate_calls += 1
        return super().generate(prompt, context)


class RecordingTransport:
    def __init__(self):
        self.calls = 0

    def post(self, *args, **kwargs):
        self.calls += 1
        return {}


class AIApplicationRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.settings = AIProviderSettings(
            provider_name="mock",
            model_name="mock-model",
        )
        self.credentials = object()
        self.credential_provider = CountingCredentialProvider(self.credentials)
        self.provider_factory = CountingProviderFactory()
        self.transport = RecordingTransport()

    def test_feature_policy_defaults_to_enabled_enhancement(self):
        policy = AIFeaturePolicy()

        self.assertTrue(policy.enabled)
        self.assertTrue(policy.enhancement_enabled)

    def test_feature_policy_preserves_explicit_disabled_values(self):
        policy = AIFeaturePolicy(enabled=False, enhancement_enabled=False)

        self.assertFalse(policy.enabled)
        self.assertFalse(policy.enhancement_enabled)

    def test_execution_metadata_contains_only_approved_observation_fields(self):
        metadata = AIExecutionMetadata(
            request_id="request-123",
            provider_name="mock",
            model_name="mock-model",
            latency=12.5,
            status="success",
        )

        self.assertEqual(metadata.request_id, "request-123")
        self.assertEqual(metadata.provider_name, "mock")
        self.assertEqual(metadata.model_name, "mock-model")
        self.assertEqual(metadata.latency, 12.5)
        self.assertEqual(metadata.status, "success")
        self.assertEqual(
            set(metadata.__slots__),
            {"request_id", "provider_name", "model_name", "latency", "status"},
        )

    def test_adapter_builds_existing_runtime_with_application_dependencies(self):
        adapter = ApplicationRuntimeAdapter(
            self.settings,
            self.credential_provider,
            self.provider_factory,
            self.transport,
        )

        runtime = adapter.build_runtime()

        self.assertIsInstance(runtime, AIRuntime)
        self.assertIs(runtime.settings, self.settings)
        self.assertIs(runtime.credential_provider, self.credential_provider)
        self.assertIs(runtime.provider_factory, self.provider_factory)
        self.assertIs(adapter.transport, self.transport)

    def test_adapter_builds_enabled_service_with_credential_injection(self):
        adapter = ApplicationRuntimeAdapter(
            self.settings,
            self.credential_provider,
            self.provider_factory,
            self.transport,
        )

        result = adapter.build_enhancement_service().enhance("Improve", {})

        self.assertTrue(result.success)
        self.assertEqual(result.enhanced_content, "mock: Improve")
        self.assertEqual(self.credential_provider.calls, 1)
        self.assertEqual(self.provider_factory.calls, 1)
        self.assertIs(self.provider_factory.received_credentials, self.credentials)
        self.assertEqual(self.transport.calls, 0)

    def test_disabled_ai_returns_unavailable_without_accessing_dependencies(self):
        adapter = ApplicationRuntimeAdapter(
            self.settings,
            self.credential_provider,
            self.provider_factory,
            self.transport,
            feature_policy=AIFeaturePolicy(enabled=False),
        )

        result = adapter.build_enhancement_service().enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(self.credential_provider.calls, 0)
        self.assertEqual(self.provider_factory.calls, 0)
        self.assertEqual(self.transport.calls, 0)

    def test_disabled_enhancement_returns_unavailable_without_accessing_dependencies(self):
        adapter = ApplicationRuntimeAdapter(
            self.settings,
            self.credential_provider,
            self.provider_factory,
            self.transport,
            feature_policy=AIFeaturePolicy(enhancement_enabled=False),
        )

        result = adapter.build_enhancement_service().enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(self.credential_provider.calls, 0)
        self.assertEqual(self.provider_factory.calls, 0)
        self.assertEqual(self.transport.calls, 0)

    def test_adapter_applies_limits_before_provider_generation(self):
        adapter = ApplicationRuntimeAdapter(
            self.settings,
            self.credential_provider,
            self.provider_factory,
            self.transport,
            limits=AIApplicationLimits(
                max_prompt_characters=4,
                max_context_items=10,
            ),
        )

        result = adapter.build_enhancement_service().enhance("12345", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI application limit exceeded")
        self.assertEqual(self.provider_factory.provider.generate_calls, 0)

    def test_adapter_blocks_unapproved_live_request_before_provider_generation(self):
        adapter = ApplicationRuntimeAdapter(
            self.settings,
            self.credential_provider,
            self.provider_factory,
            self.transport,
            limits=AIApplicationLimits(allow_live_requests=False),
            live_request=True,
        )

        result = adapter.build_enhancement_service().enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(self.provider_factory.provider.generate_calls, 0)


if __name__ == "__main__":
    unittest.main()
