import unittest

from skill import SkillResponse
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
        self.assertIn("Docker", response.result.missing_skills)

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
