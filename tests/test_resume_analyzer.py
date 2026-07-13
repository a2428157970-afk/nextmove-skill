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

    def test_bare_experience_entries_remain_unknown_without_stage_signals(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(role="Engineer"),
                ExperienceEntry(role="Senior Engineer"),
                ExperienceEntry(role="Tech Lead"),
            ]
        )

        result = ResumeAnalyzer().analyze(profile)

        self.assertEqual(result.career_level, "unknown")

    def test_stage_mapping_preserves_legacy_career_level_values(self):
        graduate = ResumeProfile(
            projects=[ProjectEntry(name="Graduate project", description="Built a portfolio dashboard.")]
        )
        developing = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Specialist",
                    start_date="2022-01",
                    end_date="2025-01",
                    highlights=["Owned the reporting workflow."],
                )
            ]
        )
        experienced = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Senior Engineer",
                    start_date="2017-01",
                    end_date="2024-01",
                    highlights=[
                        "Led a complex migration across product teams.",
                        "Improved reliability by 35%.",
                    ],
                )
            ]
        )
        advanced = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Engineering Manager",
                    start_date="2016-01",
                    end_date="2024-01",
                    highlights=[
                        "Managed a team of 8 and owned platform strategy.",
                        "Reduced operating cost by 20%.",
                    ],
                )
            ]
        )

        analyzer = ResumeAnalyzer()

        self.assertEqual(analyzer.analyze(graduate).career_level, "junior")
        self.assertEqual(analyzer.analyze(developing).career_level, "mid")
        self.assertEqual(analyzer.analyze(experienced).career_level, "senior")
        self.assertEqual(analyzer.analyze(advanced).career_level, "lead")


if __name__ == "__main__":
    unittest.main()
