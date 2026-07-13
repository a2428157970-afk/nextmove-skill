import json
from dataclasses import fields, replace
from pathlib import Path
import unittest

from benchmark.evaluator import evaluate_scenario, observe_scenario
from benchmark.loader import load_scenarios
from skill.matching.schemas import JobMatchResult


SCENARIOS = Path(__file__).parent / "benchmark" / "scenarios"


class CareerIntelligenceBenchmarkDatasetTests(unittest.TestCase):
    def test_loads_five_scenarios_in_stable_order(self):
        scenarios = load_scenarios(SCENARIOS)

        self.assertEqual(
            [scenario.scenario_id for scenario in scenarios],
            [
                "hr-specialist",
                "backend-engineer",
                "sales-to-product-manager",
                "administrative-assistant-to-hr-assistant",
                "information-insufficient-resume",
            ],
        )

    def test_each_scenario_has_complete_structured_expectations(self):
        for scenario in load_scenarios(SCENARIOS):
            self.assertTrue(scenario.resume_fixture)
            self.assertTrue(scenario.target_role)
            self.assertTrue(scenario.target_jd)
            self.assertTrue(scenario.expected.domain)
            self.assertTrue(scenario.expected.career_stage)
            self.assertIsInstance(scenario.expected.strengths, tuple)
            self.assertIsInstance(scenario.expected.gaps, tuple)
            self.assertIsInstance(scenario.expected.risks, tuple)
            self.assertTrue(scenario.expected.forbidden_conclusions)

    def test_scenarios_are_fictional_and_exclude_personal_information(self):
        forbidden_keys = {
            "personal_information",
            "raw_text",
            "name",
            "email",
            "phone",
            "location",
            "links",
            "credential",
            "api_key",
        }
        for path in sorted(SCENARIOS.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            serialized = json.dumps(payload, ensure_ascii=False).casefold()
            self.assertFalse(forbidden_keys.intersection(payload["resume_fixture"]))
            self.assertNotIn("@", serialized)
            self.assertNotIn("http://", serialized)
            self.assertNotIn("https://", serialized)


class CareerIntelligenceObservationTests(unittest.TestCase):
    def test_observes_domain_stage_evidence_explanation_and_public_result(self):
        scenario = load_scenarios(SCENARIOS)[0]

        observation = observe_scenario(scenario)

        self.assertEqual(observation.resume_domain.domain.value, "human_resources")
        self.assertEqual(observation.target_domain.domain.value, "human_resources")
        self.assertEqual(observation.career_stage.stage.value, "developing")
        self.assertEqual(
            observation.explanation.requirements,
            observation.match_assessment.requirements,
        )
        self.assertIsInstance(observation.public_result, JobMatchResult)

    def test_public_result_contract_remains_exactly_six_fields(self):
        self.assertEqual(
            [item.name for item in fields(JobMatchResult)],
            [
                "match_score",
                "matched_skills",
                "missing_skills",
                "strengths",
                "gaps",
                "recommendations",
            ],
        )


class CareerIntelligenceQualityEvaluationTests(unittest.TestCase):
    def test_result_covers_domain_stage_evidence_explanation_and_safety(self):
        scenario = load_scenarios(SCENARIOS)[0]

        result = evaluate_scenario(scenario, observe_scenario(scenario))

        self.assertEqual(
            [metric.name for metric in result.metrics],
            [
                "domain_accuracy",
                "career_stage_accuracy",
                "requirement_coverage",
                "evidence_relevance",
                "evidence_grounding",
                "strength_correctness",
                "gap_correctness",
                "risk_correctness",
                "evidence_coverage",
                "explanation_completeness",
                "safety_pass_rate",
            ],
        )
        self.assertTrue(result.passed_checks)
        self.assertEqual(result.safety_violations, ())

    def test_unknown_to_missing_pollution_is_a_safety_violation(self):
        scenario = load_scenarios(SCENARIOS)[0]
        observation = observe_scenario(scenario)
        polluted = replace(
            observation,
            public_result=JobMatchResult(missing_skills=["行政事务"]),
        )

        result = evaluate_scenario(scenario, polluted)

        self.assertIn("unknown_not_missing", result.safety_violations)
        self.assertIn("safety.unknown_not_missing", result.failed_checks)
        safety = next(
            metric for metric in result.metrics if metric.name == "safety_pass_rate"
        )
        self.assertLess(safety.score, 100)

    def test_serialized_result_is_content_safe(self):
        scenario = load_scenarios(SCENARIOS)[0]

        payload = evaluate_scenario(
            scenario,
            observe_scenario(scenario),
        ).to_dict()
        serialized = json.dumps(payload, ensure_ascii=False).casefold()

        self.assertEqual(payload["scenario_id"], "hr-specialist")
        self.assertFalse(
            {
                "resume_fixture",
                "target_jd",
                "job_description",
                "professional_evidence",
                "explanation",
            }.intersection(payload)
        )
        self.assertNotIn("campus recruitment", serialized)
        self.assertNotIn("hr generalist role requiring", serialized)


if __name__ == "__main__":
    unittest.main()
