from pathlib import Path
import unittest

from benchmark.evaluator import evaluate_scenario, observe_scenario
from benchmark.loader import load_scenarios


SCENARIOS = Path(__file__).parent / "benchmark" / "scenarios"


class CareerIntelligenceScenarioTests(unittest.TestCase):
    def test_all_five_scenarios_execute_all_quality_dimensions(self):
        results = [
            evaluate_scenario(scenario, observe_scenario(scenario))
            for scenario in load_scenarios(SCENARIOS)
        ]

        self.assertEqual(len(results), 5)
        self.assertEqual(len({result.scenario_id for result in results}), 5)
        for result in results:
            names = {metric.name for metric in result.metrics}
            self.assertTrue(
                {
                    "domain_accuracy",
                    "career_stage_accuracy",
                    "evidence_coverage",
                    "explanation_completeness",
                    "safety_pass_rate",
                }.issubset(names)
            )

    def test_current_scenarios_preserve_hard_safety_invariants(self):
        for scenario in load_scenarios(SCENARIOS):
            result = evaluate_scenario(scenario, observe_scenario(scenario))
            self.assertEqual(result.safety_violations, (), result.scenario_id)
            safety = next(
                metric
                for metric in result.metrics
                if metric.name == "safety_pass_rate"
            )
            self.assertEqual(safety.score, 100, result.scenario_id)

    def test_expanded_taxonomy_scenarios_meet_semantic_expectations(self):
        results = {
            scenario.scenario_id: evaluate_scenario(
                scenario,
                observe_scenario(scenario),
            )
            for scenario in load_scenarios(SCENARIOS)
        }

        self.assertTrue(results["hr-specialist"].passed)
        self.assertTrue(results["backend-engineer"].passed)
        self.assertTrue(results["information-insufficient-resume"].passed)
        self.assertTrue(results["sales-to-product-manager"].passed)
        self.assertTrue(results["administrative-assistant-to-hr-assistant"].passed)


if __name__ == "__main__":
    unittest.main()
