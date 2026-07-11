"""Quality-focused regression matrix for Core and optional AI boundaries."""

from copy import deepcopy
import json
import unittest

from skill.ai import (
    AIProvider,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ResumeAIEnhancer,
)
from skill.improvement.schemas import ResumeImprovementResult


class ControlledProvider(AIProvider):
    def __init__(self, response: str | Exception | None = None, health: object = True):
        self.response = response if response is not None else json.dumps({"contract_version":"resume-improvement.v1","summary":"Safe output","rewritten_content":"Use supplied facts.","improvement_points":[],"keyword_suggestions":[],"factual_warnings":[]})
        self.health = health
        self.calls = 0

    def health_check(self) -> bool:
        if isinstance(self.health, Exception):
            raise self.health
        return bool(self.health)

    def generate(self, prompt: str, context: dict) -> str:
        del prompt, context
        self.calls += 1
        if isinstance(self.response, Exception):
            raise self.response
        return self.response or ""


class AIQualityRegressionTests(unittest.TestCase):
    def setUp(self):
        self.core_result = ResumeImprovementResult(
            issues=["Missing outcome metrics."],
            suggestions=["Add measurable outcomes where truthful."],
            improved_sections={"experience": ["Add measurable outcomes."]},
        )

    def test_successful_enhancement_does_not_mutate_rule_based_result(self):
        original = deepcopy(self.core_result)

        result = ResumeAIEnhancer(ControlledProvider()).enhance(self.core_result)

        self.assertTrue(result.success)
        self.assertEqual(self.core_result, original)

    def test_provider_failure_matrix_returns_structured_results_without_exception_details(self):
        scenarios = (
            "",
            ProviderTimeoutError(),
            ProviderUnavailableError(),
            ProviderResponseError(),
            RuntimeError("internal provider detail"),
        )
        for response in scenarios:
            with self.subTest(response=type(response).__name__):
                result = ResumeAIEnhancer(ControlledProvider(response)).enhance(self.core_result)
                self.assertFalse(result.success)
                self.assertNotIn("internal", result.error or "")

    def test_unhealthy_provider_matrix_does_not_generate(self):
        for health in (False, RuntimeError("health detail")):
            with self.subTest(health=type(health).__name__):
                provider = ControlledProvider(health=health)
                result = ResumeAIEnhancer(provider).enhance(self.core_result)
                self.assertFalse(result.success)
                self.assertEqual(result.error, "AI provider unavailable")
                self.assertEqual(provider.calls, 0)


if __name__ == "__main__":
    unittest.main()
