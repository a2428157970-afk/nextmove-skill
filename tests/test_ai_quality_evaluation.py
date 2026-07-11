"""Offline contract tests for the Epic-014 AI quality evaluator."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from tests.quality.evaluator import AIQualityCase, evaluate_case, load_cases


class AIQualityEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.case = AIQualityCase(
            case_id="quality-unit",
            improvement_result={
                "issues": ["Missing outcome metrics."],
                "suggestions": ["Add measurable outcomes where truthful."],
                "improved_sections": {"experience": ["Add measurable outcomes."]},
            },
            original_facts=("Built internal reporting tools.",),
            prohibited_content=("increased revenue by 50%",),
            expected_directions=("measurable outcomes",),
            keywords=("truthful",),
            min_output_length=20,
            max_output_length=300,
        )

    def test_accepts_safe_output_that_preserves_facts_and_direction(self):
        source = deepcopy(self.case.improvement_result)

        result = evaluate_case(
            self.case,
            "Keep 'Built internal reporting tools.' and add measurable outcomes where truthful.",
            source,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.score, 10)
        self.assertEqual(result.failures, [])
        self.assertEqual(source, self.case.improvement_result)
        self.assertEqual(json.loads(json.dumps(result.to_dict()))["case_id"], "quality-unit")

    def test_rejects_fabricated_or_sensitive_provider_output(self):
        result = evaluate_case(
            self.case,
            "Built internal reporting tools and increased revenue by 50%. "
            "Authorization: Bearer token",
            self.case.improvement_result,
        )

        self.assertFalse(result.success)
        self.assertIn("prohibited_content", result.failures)
        self.assertIn("sensitive_information", result.failures)

    def test_rejects_empty_output_and_provider_error_details(self):
        result = evaluate_case(
            self.case,
            "Traceback (most recent call last): ProviderTimeoutError",
            self.case.improvement_result,
        )

        self.assertFalse(result.success)
        self.assertIn("provider_internal_error", result.failures)

    def test_loads_synthetic_fixture_cases_stably(self):
        fixture_directory = Path(__file__).parent / "fixtures" / "ai_quality"

        cases = load_cases(fixture_directory)

        self.assertEqual(len(cases), 8)
        self.assertEqual(cases[0].case_id, "career-switcher")
        self.assertTrue(all(case.case_id for case in cases))


if __name__ == "__main__":
    unittest.main()
