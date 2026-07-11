"""Contract tests for the provider registry and prompt boundary."""

import unittest

from skill.ai import (
    AIProvider,
    AIProviderConfig,
    EnhancementService,
    PromptTemplate,
    ProviderRegistry,
)


class MockProvider(AIProvider):
    """Externally managed provider used for contract tests."""

    def generate(self, prompt: str, context: dict) -> str:
        return f"{prompt}: {context['core_result']}"


class MockPromptTemplate(PromptTemplate):
    """Template implementation without a production prompt."""

    def render(self, context: dict) -> str:
        return f"{self.name}: {context['focus']}"


class AIProviderContractTests(unittest.TestCase):
    def test_config_preserves_provider_model_and_metadata(self):
        config = AIProviderConfig(
            provider_name="mock",
            model_name="mock-model",
            metadata={"tier": "test"},
        )

        self.assertEqual(config.provider_name, "mock")
        self.assertEqual(config.model_name, "mock-model")
        self.assertEqual(config.metadata, {"tier": "test"})

    def test_registry_registers_gets_and_lists_external_provider(self):
        registry = ProviderRegistry()
        provider = MockProvider()

        registry.register_provider("mock", provider)

        self.assertIs(registry.get_provider("mock"), provider)
        self.assertEqual(registry.list_providers(), ["mock"])
        self.assertIsNone(registry.get_provider("unknown"))

    def test_prompt_template_renders_context(self):
        template = MockPromptTemplate(name="contract")

        rendered = template.render({"focus": "resume strengths"})

        self.assertEqual(rendered, "contract: resume strengths")

    def test_enhancement_service_resolves_provider_from_registry(self):
        registry = ProviderRegistry()
        registry.register_provider("mock", MockProvider())
        service = EnhancementService(registry=registry, provider_name="mock")

        result = service.enhance("Enhance", {"core_result": "analysis"})

        self.assertTrue(result.success)
        self.assertEqual(result.enhanced_content, "Enhance: analysis")
        self.assertIsNone(result.error)


if __name__ == "__main__":
    unittest.main()
