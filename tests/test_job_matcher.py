import unittest

from skill.matching import JobMatcher
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class JobMatcherTests(unittest.TestCase):
    def test_high_skill_match_returns_strong_score(self):
        profile = ResumeProfile(
            skills=["Python", "FastAPI", "SQL", "Docker"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built Python APIs with FastAPI and SQL."],
                )
            ],
        )
        job_description = "Backend Engineer role using Python, FastAPI, SQL, Docker, and APIs."

        result = JobMatcher().match(profile, job_description)

        self.assertIsInstance(result, JobMatchResult)
        self.assertGreaterEqual(result.match_score, 80)
        self.assertEqual(result.missing_skills, [])
        self.assertIn("Python", result.matched_skills)
        self.assertIn("FastAPI", result.matched_skills)
        self.assertTrue(result.strengths)
        self.assertTrue(result.recommendations)

    def test_skill_gaps_are_reported_from_job_keywords(self):
        profile = ResumeProfile(
            skills=["Python", "SQL"],
            experience=[
                ExperienceEntry(
                    role="Data Analyst",
                    highlights=["Analyzed product data with SQL."],
                )
            ],
        )
        job_description = "Data role requiring Python, SQL, Tableau, AWS, and Docker."

        result = JobMatcher().match(profile, job_description)

        self.assertLess(result.match_score, 80)
        self.assertIn("Python", result.matched_skills)
        self.assertIn("Tableau", result.missing_skills)
        self.assertIn("AWS", result.missing_skills)
        self.assertIn("Docker", result.missing_skills)
        self.assertTrue(result.gaps)

    def test_empty_resume_returns_zero_score_and_recommendations(self):
        job_description = "Backend Engineer role requiring Python, FastAPI, SQL, and Docker."

        result = JobMatcher().match(ResumeProfile(), job_description)

        self.assertEqual(result.match_score, 0)
        self.assertEqual(result.matched_skills, [])
        self.assertIn("Python", result.missing_skills)
        self.assertTrue(result.gaps)
        self.assertTrue(result.recommendations)


if __name__ == "__main__":
    unittest.main()
