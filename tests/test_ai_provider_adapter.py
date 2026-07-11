"""Contract tests for adapter readiness and provider error handling."""

import unittest

from skill.ai import (
    AIProvider,
    AIProviderSettings,
    EnhancementService,
    MockProviderAdapter,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class ErrorProvider(AIProvider):
    """Provider double that raises a supplied contract error."""

    def __init__(self, error: Exception):
        self.error = error

    def generate(self, prompt: str, context: dict) -> str:
        raise self.error


class AIProviderAdapterTests(unittest.TestCase):
    def test_mock_adapter_implements_provider_contract(self):
        settings = AIProviderSettings(
            provider_name="mock",
            model_name="mock-model",
            timeout=5.0,
        )
        adapter = MockProviderAdapter(settings)

        content = adapter.generate("Improve", {"core_result": "analysis"})

        self.assertIsInstance(adapter, AIProvider)
        self.assertEqual(content, "mock: Improve")

    def test_settings_preserve_timeout_and_metadata_without_credentials(self):
        settings = AIProviderSettings(
            provider_name="mock",
            model_name="mock-model",
            timeout=2.5,
            metadata={"region": "test"},
        )

        self.assertEqual(settings.provider_name, "mock")
        self.assertEqual(settings.model_name, "mock-model")
        self.assertEqual(settings.timeout, 2.5)
        self.assertEqual(settings.metadata, {"region": "test"})

    def test_service_converts_provider_contract_errors(self):
        cases = (
            (ProviderUnavailableError(), "AI provider unavailable"),
            (ProviderTimeoutError(), "AI provider timeout"),
            (ProviderResponseError(), "AI provider response error"),
        )

        for error, expected_message in cases:
            with self.subTest(error=type(error).__name__):
                result = EnhancementService(
                    provider=ErrorProvider(error)
                ).enhance("Improve", {"core_result": "analysis"})

                self.assertFalse(result.success)
                self.assertIsNone(result.enhanced_content)
                self.assertEqual(result.error, expected_message)


if __name__ == "__main__":
    unittest.main()
