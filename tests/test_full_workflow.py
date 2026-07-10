import json
import unittest

from examples.full_career_analysis import run_full_career_analysis
from skill import NextMoveSkill
from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.career import CareerAdviceResult
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.matching import JobMatchResult


class FullCareerWorkflowTests(unittest.TestCase):
    def test_full_career_analysis_runs_all_capabilities_and_returns_json_report(self):
        resume_text = """
            Jane Doe

            Summary
            Backend engineer focused on Python APIs and internal tooling.

            Experience
            Backend Engineer
            Built Python APIs with FastAPI and SQL.

            Skills
            Python, FastAPI, SQL, Testing
        """
        job_description = "Backend role requiring Python, FastAPI, SQL, Docker, and API testing."
        skill = NextMoveSkill()

        analysis = skill.run("analyze_resume", {"resume": resume_text})
        improvement = skill.run("improve_resume", {"resume": resume_text})
        job_match = skill.run(
            "match_job",
            {"resume": resume_text, "job_description": job_description},
        )
        career_advice = skill.run(
            "career_advice",
            {"resume": resume_text, "analysis": analysis.result},
        )

        responses = {
            "analysis": analysis,
            "improvement": improvement,
            "job_match": job_match,
            "career_advice": career_advice,
        }

        expected_capabilities = {
            "analysis": ("analyze_resume", ResumeAnalysisResult),
            "improvement": ("improve_resume", ResumeImprovementResult),
            "job_match": ("match_job", JobMatchResult),
            "career_advice": ("career_advice", CareerAdviceResult),
        }

        for report_key, (capability, result_type) in expected_capabilities.items():
            response = responses[report_key]
            self.assertTrue(response.success)
            self.assertEqual(response.capability, capability)
            self.assertIsInstance(response.result, result_type)

        report = run_full_career_analysis(resume_text, job_description)
        for report_key in expected_capabilities:
            self.assertIsInstance(report[report_key]["result"], dict)
        self.assertIsInstance(json.dumps(report), str)


if __name__ == "__main__":
    unittest.main()
