import unittest

from skill import NextMoveSkill
from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.api import SkillError, SkillResponse
from skill.schemas.career import CareerAdviceResult
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class SkillApiTests(unittest.TestCase):
    def setUp(self):
        self.skill = NextMoveSkill()
        self.profile = ResumeProfile(
            summary="Backend engineer focused on Python APIs.",
            skills=["Python", "FastAPI", "SQL"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built 12 internal APIs with Python."],
                )
            ],
        )

    def test_run_analyze_resume_returns_success_response(self):
        response = self.skill.run("analyze_resume", {"resume": self.profile})

        self.assertIsInstance(response, SkillResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.capability, "analyze_resume")
        self.assertIsInstance(response.result, ResumeAnalysisResult)
        self.assertIsNone(response.error)

    def test_run_improve_resume_returns_success_response(self):
        response = self.skill.run("improve_resume", {"resume": self.profile})

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "improve_resume")
        self.assertIsInstance(response.result, ResumeImprovementResult)
        self.assertIsNone(response.error)

    def test_run_match_job_returns_success_response(self):
        response = self.skill.run(
            "match_job",
            {
                "resume": self.profile,
                "job_description": "Backend role requiring Python, FastAPI, SQL, and Docker.",
            },
        )

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "match_job")
        self.assertIsInstance(response.result, JobMatchResult)
        self.assertIn("Docker", response.result.missing_skills)
        self.assertIsNone(response.error)

    def test_run_career_advice_returns_success_response(self):
        response = self.skill.run("career_advice", {"resume": self.profile})

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "career_advice")
        self.assertIsInstance(response.result, CareerAdviceResult)
        self.assertIsNone(response.error)

    def test_run_unknown_capability_returns_error_response(self):
        response = self.skill.run("unknown", {"resume": self.profile})

        self.assertFalse(response.success)
        self.assertEqual(response.capability, "unknown")
        self.assertIsNone(response.result)
        self.assertIsInstance(response.error, SkillError)
        self.assertEqual(response.error.code, "UNKNOWN_CAPABILITY")

    def test_run_invalid_input_returns_error_response(self):
        response = self.skill.run("match_job", {"resume": self.profile})

        self.assertFalse(response.success)
        self.assertEqual(response.capability, "match_job")
        self.assertIsNone(response.result)
        self.assertIsInstance(response.error, SkillError)
        self.assertEqual(response.error.code, "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
