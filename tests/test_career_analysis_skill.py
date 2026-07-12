import json
import unittest
from pathlib import Path

from skill import NextMoveSkill, __version__
from skill.schemas.api import CareerAnalysisReport, SkillError, SkillResponse
from skill.utils import to_dict


RESUME = """
Jane Doe

Summary
Backend engineer focused on Python APIs.

Experience
Backend Engineer
Built internal APIs with Python and SQL.

Skills
Python, SQL, Testing
"""

JOB_DESCRIPTION = "Backend role requiring Python, SQL, Docker, and testing."


class RecordingSkill(NextMoveSkill):
    def __init__(self, failing_capability=None):
        super().__init__()
        self.calls = []
        self.failing_capability = failing_capability

    def run(self, capability, payload):
        self.calls.append(capability)
        if capability == self.failing_capability:
            return SkillResponse(
                success=False,
                capability=capability,
                error=SkillError(code="TEST_FAILURE", message="forced failure"),
            )
        return super().run(capability, payload)


class CareerAnalysisSkillTests(unittest.TestCase):
    def test_skill_metadata_describes_public_product_capability(self):
        metadata_path = Path(__file__).resolve().parents[1] / "skill.json"

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertEqual(metadata["version"], __version__)
        self.assertEqual(__version__, "0.8.0")
        self.assertIn("career_analysis", metadata["capabilities"])
        self.assertIn("input_schema", metadata)
        self.assertEqual(
            metadata["output_schema"]["properties"]["capability"]["const"],
            "career_analysis",
        )
        self.assertIn(
            "result",
            metadata["output_schema"]["properties"],
        )

    def test_career_analysis_uses_public_capabilities_in_fixed_order(self):
        skill = RecordingSkill()

        report = skill.career_analysis(RESUME, JOB_DESCRIPTION)

        self.assertIsInstance(report, CareerAnalysisReport)
        self.assertTrue(report.success)
        self.assertEqual(
            skill.calls,
            [
                "analyze_resume",
                "improve_resume",
                "match_job",
                "career_advice",
            ],
        )
        self.assertIsNone(report.failed_capability)
        self.assertIsNone(report.error)

    def test_career_analysis_report_is_json_serializable(self):
        response = NextMoveSkill().run(
            "career_analysis",
            {"resume": RESUME, "job_description": JOB_DESCRIPTION},
        )

        serialized = to_dict(response)
        json.dumps(serialized)

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "career_analysis")
        self.assertTrue(serialized["result"]["success"])
        self.assertIn("analysis", serialized["result"])
        self.assertIn("career_advice", serialized["result"])

    def test_career_analysis_stops_and_preserves_failure(self):
        skill = RecordingSkill(failing_capability="match_job")

        report = skill.career_analysis(RESUME, JOB_DESCRIPTION)

        self.assertFalse(report.success)
        self.assertEqual(
            skill.calls,
            ["analyze_resume", "improve_resume", "match_job"],
        )
        self.assertEqual(report.failed_capability, "match_job")
        self.assertEqual(report.error.code, "TEST_FAILURE")
        self.assertIsNotNone(report.analysis)
        self.assertIsNotNone(report.improvement)
        self.assertIsNone(report.job_match)
        self.assertIsNone(report.career_advice)

    def test_run_career_analysis_returns_invalid_input_for_missing_job(self):
        response = NextMoveSkill().run(
            "career_analysis",
            {"resume": RESUME},
        )

        self.assertFalse(response.success)
        self.assertEqual(response.error.code, "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
