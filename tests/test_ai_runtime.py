"""Tests for application-layer AI runtime assembly."""

import unittest

from skill.ai import (
    AIProviderSettings,
    AIRuntime,
    CredentialProvider,
    MockProviderAdapter,
    ProviderFactory,
    ProviderRegistry,
)


class MockCredentialProvider(CredentialProvider):
    """External credential source returning an opaque test value."""

    def __init__(self, credentials: object | None):
        self.credentials = credentials

    def get_credentials(self, provider_name: str) -> object | None:
        return self.credentials


class MockProviderFactory(ProviderFactory):
    """Factory double that creates a deterministic adapter."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.received_credentials: object | None = None

    def create_provider(
        self,
        settings: AIProviderSettings,
        credentials: object,
    ) -> MockProviderAdapter:
        if self.should_fail:
            raise RuntimeError("adapter creation failed")
        self.received_credentials = credentials
        return MockProviderAdapter(settings)


class AIRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.settings = AIProviderSettings(
            provider_name="mock",
            model_name="mock-model",
        )

    def test_mock_credential_provider_returns_opaque_value(self):
        credentials = object()
        provider = MockCredentialProvider(credentials)

        self.assertIs(provider.get_credentials("mock"), credentials)

    def test_runtime_assembles_registers_and_invokes_provider(self):
        credentials = object()
        registry = ProviderRegistry()
        factory = MockProviderFactory()
        runtime = AIRuntime(
            settings=self.settings,
            credential_provider=MockCredentialProvider(credentials),
            provider_factory=factory,
            registry=registry,
        )

        service = runtime.build_enhancement_service()
        result = service.enhance("Improve", {"core_result": "analysis"})

        self.assertTrue(result.success)
        self.assertEqual(result.enhanced_content, "mock: Improve")
        self.assertIs(factory.received_credentials, credentials)
        self.assertIsNotNone(registry.get_provider("mock"))

    def test_runtime_returns_unavailable_service_when_credentials_are_missing(self):
        runtime = AIRuntime(
            settings=self.settings,
            credential_provider=MockCredentialProvider(None),
            provider_factory=MockProviderFactory(),
        )

        result = runtime.build_enhancement_service().enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")

    def test_runtime_returns_unavailable_service_when_factory_fails(self):
        runtime = AIRuntime(
            settings=self.settings,
            credential_provider=MockCredentialProvider(object()),
            provider_factory=MockProviderFactory(should_fail=True),
        )

        result = runtime.build_enhancement_service().enhance("Improve", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")


if __name__ == "__main__":
    unittest.main()
