import unittest

from skill import CareerAnalysisReport, SkillResponse
from skill.agent import AgentRuntime
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class AgentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = AgentRuntime()
        self.profile = ResumeProfile(
            summary="Backend engineer focused on Python APIs.",
            skills=["Python", "FastAPI", "SQL"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built Python APIs with FastAPI."],
                )
            ],
        )

    def test_invoke_analyze_resume_returns_successful_skill_response(self):
        response = self.runtime.invoke(
            "analyze_resume",
            {"resume": "Backend engineer with Python and SQL experience."},
        )

        self.assertIsInstance(response, SkillResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.capability, "analyze_resume")
        self.assertIsNone(response.error)

    def test_invoke_match_job_uses_structured_resume_profile(self):
        response = self.runtime.invoke(
            "match_job",
            {
                "resume": self.profile,
                "job_description": "Backend role requiring Python, FastAPI, SQL, and Docker.",
            },
        )

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "match_job")
        self.assertIsInstance(response.result, JobMatchResult)
        self.assertIn("Python", response.result.matched_skills)
        self.assertNotIn("Docker", response.result.missing_skills)
        self.assertTrue(
            any(
                "Docker" in gap and "not evidenced" in gap
                for gap in response.result.gaps
            )
        )

    def test_invoke_career_analysis_returns_complete_report(self):
        response = self.runtime.invoke(
            "career_analysis",
            {
                "resume": self.profile,
                "job_description": "Backend role requiring Python and SQL.",
            },
        )

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "career_analysis")
        self.assertIsInstance(response.result, CareerAnalysisReport)
        self.assertTrue(response.result.success)

    def test_invoke_unknown_tool_returns_structured_failure(self):
        response = self.runtime.invoke("unknown_tool", {})

        self.assertIsInstance(response, SkillResponse)
        self.assertFalse(response.success)
        self.assertEqual(response.capability, "unknown_tool")
        self.assertIsNone(response.result)
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.code, "UNKNOWN_TOOL")
        self.assertIn("unknown tool", response.error.message)


if __name__ == "__main__":
    unittest.main()
