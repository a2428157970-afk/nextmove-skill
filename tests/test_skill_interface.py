import unittest

from skill import NextMoveSkill
from skill.schemas.career import CareerAdviceResult
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import ExperienceEntry, ProjectEntry, ResumeProfile


class NextMoveSkillInterfaceTests(unittest.TestCase):
    def test_analyze_resume_accepts_text_and_runs_parser_then_analyzer(self):
        text = """
Jane Doe
jane@example.com

Summary
Backend engineer focused on Python services.

Experience
Backend Engineer
Built 12 APIs for internal career tools.

Skills
Python, APIs, SQL, Docker, Testing

Projects
Career Intelligence Demo
Resume analysis demo built with Python.
"""

        result = NextMoveSkill().analyze_resume(text)

        self.assertIn("Resume includes a clear summary.", result.strengths)
        self.assertIn("Resume includes work experience.", result.strengths)
        self.assertIn("Resume includes project experience.", result.strengths)
        self.assertEqual(result.career_level, "junior")

    def test_analyze_resume_accepts_profile_and_runs_analyzer_directly(self):
        profile = ResumeProfile(
            summary="Backend engineer focused on Python services.",
            skills=["Python", "APIs", "SQL", "Docker", "Testing"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built APIs for internal career tools."],
                )
            ],
            projects=[
                ProjectEntry(
                    name="Career Intelligence Demo",
                    description="Resume analysis demo built with Python.",
                    technologies=["Python", "SQL"],
                )
            ],
        )

        result = NextMoveSkill().analyze_resume(profile)

        self.assertIn("Resume includes a clear summary.", result.strengths)
        self.assertIn("Resume includes work experience.", result.strengths)
        self.assertEqual(result.career_level, "junior")

    def test_improve_resume_accepts_profile_and_returns_improvement_result(self):
        skill = NextMoveSkill()
        profile = ResumeProfile(
            skills=["Python"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built APIs for internal tools."],
                )
            ],
        )

        result = skill.improve_resume(profile)

        self.assertIsInstance(result, ResumeImprovementResult)
        self.assertIn("Resume is missing a summary.", result.issues)
        self.assertIn("summary", result.improved_sections)
        self.assertIn("skills", result.improved_sections)

    def test_match_job_accepts_profile_and_job_description(self):
        skill = NextMoveSkill()
        profile = ResumeProfile(
            skills=["Python", "FastAPI", "SQL"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built Python APIs with FastAPI."],
                )
            ],
        )

        result = skill.match_job(
            profile,
            "Backend role requiring Python, FastAPI, SQL, and Docker.",
        )

        self.assertIsInstance(result, JobMatchResult)
        self.assertIn("Python", result.matched_skills)
        self.assertNotIn("Docker", result.missing_skills)
        self.assertTrue(
            any("Docker" in gap and "not evidenced" in gap for gap in result.gaps)
        )

    def test_career_advice_accepts_profile_and_returns_advice_result(self):
        skill = NextMoveSkill()
        profile = ResumeProfile(
            summary="Python data analyst focused on SQL reporting.",
            skills=["Python", "SQL", "Data Analysis"],
            experience=[ExperienceEntry(role="Data Analyst")],
        )

        result = skill.career_advice(profile)

        self.assertIsInstance(result, CareerAdviceResult)
        self.assertIn("data analyst", result.possible_paths)


if __name__ == "__main__":
    unittest.main()
