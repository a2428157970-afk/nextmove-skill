"""Run optional AI enhancement entirely offline with deterministic collaborators."""

from dataclasses import asdict
import json

from skill.ai import (
    AIFeaturePolicy,
    AIProviderSettings,
    ApplicationRuntimeAdapter,
    CredentialProvider,
    MockProviderAdapter,
    ProviderFactory,
    ResumeAIEnhancer,
)
from skill.improvement.schemas import ResumeImprovementResult


class DemoCredentialProvider(CredentialProvider):
    """Provide an opaque in-memory value without reading configuration."""

    def get_credentials(self, provider_name: str) -> object | None:
        del provider_name
        return "offline-demo-credential"


class DemoProviderFactory(ProviderFactory):
    """Build the deterministic provider used only by this offline example."""

    def create_provider(
        self,
        settings: AIProviderSettings,
        credentials: object,
    ) -> MockProviderAdapter:
        del credentials
        return MockProviderAdapter(settings)


def build_rule_based_improvement() -> ResumeImprovementResult:
    """Represent the existing deterministic improvement output."""
    return ResumeImprovementResult(
        issues=["Resume is missing a summary."],
        suggestions=["Add a focused professional summary."],
        improved_sections={"summary": ["Add a focused professional summary."]},
    )


def main() -> None:
    """Print JSON-only results without a network call or environment access."""
    settings = AIProviderSettings(provider_name="mock", model_name="offline-demo")
    improvement = build_rule_based_improvement()
    mock_provider = MockProviderAdapter(settings)

    ai_result = ResumeAIEnhancer(mock_provider).enhance(improvement)
    application_adapter = ApplicationRuntimeAdapter(
        settings=settings,
        credential_provider=DemoCredentialProvider(),
        provider_factory=DemoProviderFactory(),
        transport=object(),
    )
    application_result = application_adapter.build_enhancement_service().enhance(
        "Improve the structured resume guidance.", {"improvement": asdict(improvement)}
    )
    disabled_adapter = ApplicationRuntimeAdapter(
        settings=settings,
        credential_provider=DemoCredentialProvider(),
        provider_factory=DemoProviderFactory(),
        transport=object(),
        feature_policy=AIFeaturePolicy(enabled=False),
    )
    disabled_result = disabled_adapter.build_enhancement_service().enhance("prompt", {})

    print(
        json.dumps(
            {
                "rule_based_resume_improvement": asdict(improvement),
                "optional_ai_enhancement": asdict(ai_result),
                "application_runtime_result": asdict(application_result),
                "disabled_ai_result": asdict(disabled_result),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
