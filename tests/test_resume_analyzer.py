import unittest

from skill.analysis import ResumeAnalyzer
from skill.schemas.resume import ExperienceEntry, ProjectEntry, ResumeProfile


class ResumeAnalyzerTests(unittest.TestCase):
    def test_empty_profile_reports_weaknesses(self):
        result = ResumeAnalyzer().analyze(ResumeProfile())

        self.assertTrue(result.weaknesses)
        self.assertEqual(result.career_level, "unknown")

    def test_complete_profile_reports_strengths(self):
        profile = ResumeProfile(
            summary="Backend engineer focused on Python services.",
            skills=["Python", "FastAPI", "SQL", "Docker", "Testing"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built APIs for internal career tools."],
                )
            ],
            projects=[
                ProjectEntry(
                    name="Career Intelligence Demo",
                    description="A resume analysis demo built with Python.",
                    technologies=["Python", "FastAPI"],
                )
            ],
        )

        result = ResumeAnalyzer().analyze(profile)

        self.assertTrue(result.strengths)

    def test_multiple_experiences_are_classified_as_senior(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(role="Engineer"),
                ExperienceEntry(role="Senior Engineer"),
                ExperienceEntry(role="Tech Lead"),
            ]
        )

        result = ResumeAnalyzer().analyze(profile)

        self.assertEqual(result.career_level, "senior")


if __name__ == "__main__":
    unittest.main()
