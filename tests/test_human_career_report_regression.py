import unittest
from dataclasses import fields
from pathlib import Path

from application.schemas.career import (
    CareerAnalysisReport as ApplicationCareerAnalysisReport,
)
from skill.agent.tools import JOB_MATCH_OUTPUT_SCHEMA
from skill.matching.schemas import JobMatchResult
from skill.schemas.api import CareerAnalysisReport as SkillCareerAnalysisReport
from skill.utils import to_dict


ROOT = Path(__file__).resolve().parents[1]


class HumanCareerReportRegressionTests(unittest.TestCase):
    def test_public_result_fields_remain_exact(self):
        self.assertEqual(
            [field.name for field in fields(JobMatchResult)],
            [
                "match_score",
                "matched_skills",
                "missing_skills",
                "strengths",
                "gaps",
                "recommendations",
            ],
        )
        self.assertEqual(
            [field.name for field in fields(SkillCareerAnalysisReport)],
            [
                "success",
                "analysis",
                "improvement",
                "job_match",
                "career_advice",
                "failed_capability",
                "error",
            ],
        )
        self.assertEqual(
            [field.name for field in fields(ApplicationCareerAnalysisReport)],
            ["resume_analysis", "improvement", "job_match", "career_advice"],
        )

    def test_agent_job_match_contract_remains_exact(self):
        self.assertEqual(
            list(JOB_MATCH_OUTPUT_SCHEMA["properties"]),
            [
                "match_score",
                "matched_skills",
                "missing_skills",
                "strengths",
                "gaps",
                "recommendations",
            ],
        )

    def test_public_paths_do_not_import_reporting(self):
        protected = (
            ROOT / "skill" / "__init__.py",
            ROOT / "skill" / "interface.py",
            *sorted((ROOT / "skill" / "schemas").glob("*.py")),
            *sorted((ROOT / "skill" / "agent").glob("*.py")),
            *sorted((ROOT / "application").rglob("*.py")),
        )
        for path in protected:
            self.assertNotIn("skill.reporting", path.read_text(encoding="utf-8"))

    def test_existing_report_serialization_has_no_human_report_key(self):
        payload = to_dict(SkillCareerAnalysisReport(success=True))

        self.assertNotIn("human_report", payload)
        self.assertNotIn("reporting", payload)


if __name__ == "__main__":
    unittest.main()
