"""Release acceptance checks for the offline AI enhancement demonstration."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import runpy
import unittest


class AIReleaseAcceptanceTests(unittest.TestCase):
    def test_offline_ai_enhancement_demo_emits_serializable_results(self):
        output = io.StringIO()
        example_path = Path(__file__).parents[1] / "examples" / "ai_enhancement_demo.py"

        with redirect_stdout(output):
            runpy.run_path(str(example_path), run_name="__main__")

        payload = json.loads(output.getvalue())
        self.assertIn("rule_based_resume_improvement", payload)
        self.assertTrue(payload["optional_ai_enhancement"]["success"])
        self.assertTrue(payload["application_runtime_result"]["success"])
        self.assertFalse(payload["disabled_ai_result"]["success"])
        self.assertEqual(
            payload["disabled_ai_result"]["error"], "AI provider unavailable"
        )


if __name__ == "__main__":
    unittest.main()
