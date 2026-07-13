import json
from pathlib import Path
import subprocess
import sys
import unittest

from benchmark.runner import run_benchmark


SCENARIOS = Path(__file__).parent / "benchmark" / "scenarios"


class CareerIntelligenceBenchmarkRunnerTests(unittest.TestCase):
    def test_report_contains_scenario_checks_violations_and_aggregate_metrics(self):
        report = run_benchmark(SCENARIOS)
        payload = report.to_dict()

        self.assertEqual(payload["summary"]["scenario_count"], 6)
        self.assertEqual(len(payload["scenario_results"]), 6)
        for result in payload["scenario_results"]:
            self.assertIn("passed_checks", result)
            self.assertIn("failed_checks", result)
            self.assertIn("safety_violations", result)
        self.assertEqual(
            list(payload["metrics"]),
            [
                "domain_accuracy",
                "career_stage_accuracy",
                "evidence_coverage",
                "explanation_completeness",
                "safety_pass_rate",
                "transition_type_accuracy",
                "transition_gap_grounding",
                "transition_risk_calibration",
                "transition_action_grounding",
                "transition_safety_pass_rate",
            ],
        )

    def test_json_runner_is_content_safe(self):
        completed = subprocess.run(
            [sys.executable, "-m", "benchmark.runner", "--format", "json"],
            cwd=Path(__file__).parents[1],
            check=False,
            capture_output=True,
            text=True,
        )

        report = json.loads(completed.stdout)
        serialized = completed.stdout.casefold()
        self.assertEqual(report["summary"]["scenario_count"], 6)
        self.assertEqual(
            completed.returncode,
            int(report["summary"]["failed_scenarios"] > 0),
        )
        for private_text in (
            "campus recruitment",
            "complex service migration",
            "product manager responsible",
            "onboarding document coordination",
            "looking for a motivated professional",
        ):
            self.assertNotIn(private_text, serialized)


if __name__ == "__main__":
    unittest.main()
