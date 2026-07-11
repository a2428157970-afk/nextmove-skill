"""Integration coverage for the offline AI quality runner."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


class AIQualityRunnerTests(unittest.TestCase):
    def test_runner_reports_all_synthetic_cases_as_json_without_outputs(self):
        script = Path(__file__).parents[1] / "scripts" / "run_ai_quality_evaluation.py"

        completed = subprocess.run(
            [sys.executable, str(script), "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["summary"]["total_cases"], 8)
        self.assertEqual(report["summary"]["passed_cases"], 8)
        self.assertEqual(report["summary"]["network_calls"], 0)
        self.assertNotIn("enhanced_content", completed.stdout)

    def test_runner_returns_one_when_a_quality_check_fails(self):
        script = Path(__file__).parents[1] / "scripts" / "run_ai_quality_evaluation.py"

        completed = subprocess.run(
            [sys.executable, str(script), "--format", "json", "--scenario", "fabricated"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 1)
        report = json.loads(completed.stdout)
        self.assertGreater(report["summary"]["failed_cases"], 0)


if __name__ == "__main__":
    unittest.main()
