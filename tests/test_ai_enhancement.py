"""Contract tests for the optional AI enhancement boundary."""

import unittest

from skill.ai import AIEnhancementResult, AIProvider, EnhancementService


class MockProvider(AIProvider):
    """Deterministic provider used to test the provider contract."""

    def generate(self, prompt: str, context: dict) -> str:
        return f"{prompt}: {context['core_result']}"


class FailingProvider(AIProvider):
    """Provider that represents an unavailable future integration."""

    def generate(self, prompt: str, context: dict) -> str:
        raise RuntimeError("provider connection failed")


class AIEnhancementTests(unittest.TestCase):
    def test_provider_subclass_can_generate_content(self):
        provider = MockProvider()

        content = provider.generate("Improve", {"core_result": "analysis"})

        self.assertEqual(content, "Improve: analysis")

    def test_service_returns_enhanced_content_from_injected_provider(self):
        service = EnhancementService(provider=MockProvider())

        result = service.enhance("Improve", {"core_result": "analysis"})

        self.assertIsInstance(result, AIEnhancementResult)
        self.assertTrue(result.success)
        self.assertEqual(result.enhanced_content, "Improve: analysis")
        self.assertIsNone(result.error)

    def test_service_returns_structured_failure_without_provider(self):
        service = EnhancementService(provider=None)

        result = service.enhance("Improve", {"core_result": "analysis"})

        self.assertFalse(result.success)
        self.assertIsNone(result.enhanced_content)
        self.assertEqual(result.error, "AI provider unavailable")

    def test_service_converts_provider_exception_to_structured_failure(self):
        service = EnhancementService(provider=FailingProvider())

        result = service.enhance("Improve", {"core_result": "analysis"})

        self.assertFalse(result.success)
        self.assertIsNone(result.enhanced_content)
        self.assertEqual(result.error, "AI provider unavailable")


if __name__ == "__main__":
    unittest.main()
