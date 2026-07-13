import unittest

from skill.career import CareerAdvisor
from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment
from skill.schemas.career import CareerAdviceResult
from skill.schemas.resume import ExperienceEntry, ProjectEntry, ResumeProfile


class CareerAdvisorTests(unittest.TestCase):
    def test_entry_stage_gets_portfolio_and_practice_advice(self):
        profile = ResumeProfile(
            projects=[ProjectEntry(name="Graduate project", description="Built a reporting dashboard.")]
        )

        result = CareerAdvisor().advise(profile)

        self.assertEqual(result.current_level, "junior")
        self.assertIn(
            "Build a focused portfolio project and seek supervised practical experience.",
            result.recommended_actions,
        )

    def test_developing_stage_gets_ownership_advice(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Operations Specialist",
                    start_date="2022-01",
                    end_date="2025-01",
                    highlights=["Owned an onboarding workflow across stakeholders."],
                )
            ]
        )

        result = CareerAdvisor().advise(profile)

        self.assertEqual(result.current_level, "mid")
        self.assertIn(
            "Document end-to-end ownership and expand responsibility for an adjacent scope.",
            result.recommended_actions,
        )

    def test_experienced_stage_gets_impact_and_cross_functional_advice(self):
        profile = ResumeProfile(
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

        result = CareerAdvisor().advise(profile)

        self.assertEqual(result.current_level, "senior")
        self.assertIn(
            "Frame complex cross-functional outcomes and mentorship evidence for senior opportunities.",
            result.recommended_actions,
        )

    def test_advanced_stage_gets_strategy_and_people_leadership_advice(self):
        profile = ResumeProfile(
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

        result = CareerAdvisor().advise(profile)

        self.assertEqual(result.current_level, "lead")
        self.assertIn(
            "Clarify strategic scope, people leadership, and organisation-level impact.",
            result.recommended_actions,
        )

    def test_career_changer_gets_bridge_advice_without_entry_downgrade(self):
        profile = ResumeProfile(
            summary="Transitioning from finance operations into business operations.",
            experience=[
                ExperienceEntry(
                    role="Finance Manager",
                    start_date="2015-01",
                    end_date="2024-01",
                    highlights=[
                        "Owned a cross-functional reporting process.",
                        "Reduced monthly close time by 25%.",
                    ],
                )
            ],
        )

        result = CareerAdvisor().advise(profile)

        self.assertEqual(result.current_level, "senior")
        self.assertIn(
            "Create a bridge example that connects transferable experience to the target domain.",
            result.recommended_actions,
        )

    def test_no_experience_resume_gets_general_development_advice(self):
        analysis = ResumeAnalysisResult(
            weaknesses=[
                "Resume is missing work experience.",
                "Resume is missing project experience.",
            ],
            skill_assessment=SkillAssessment(
                gaps=["Add a skills section with relevant tools and domains."]
            ),
            career_level="unknown",
        )

        result = CareerAdvisor().advise(ResumeProfile(), analysis)

        self.assertIsInstance(result, CareerAdviceResult)
        self.assertEqual(result.current_level, "unknown")
        self.assertIn("general career development", result.possible_paths)
        self.assertTrue(result.skill_gaps)
        self.assertIn("Build projects that demonstrate practical skills.", result.recommended_actions)

    def test_technical_background_gets_data_related_paths(self):
        profile = ResumeProfile(
            summary="Python data analyst focused on SQL reporting.",
            skills=["Python", "SQL", "Data Analysis"],
            experience=[
                ExperienceEntry(
                    role="Data Analyst",
                    highlights=["Built SQL dashboards and Python reports."],
                )
            ],
        )
        analysis = ResumeAnalysisResult(
            weaknesses=["Experience does not show quantified outcomes."],
            career_level="junior",
        )

        result = CareerAdvisor().advise(profile, analysis)

        self.assertEqual(result.current_level, "junior")
        self.assertIn("data analyst", result.possible_paths)
        self.assertIn("data engineer", result.possible_paths)
        self.assertIn("Add measurable achievements.", result.recommended_actions)

    def test_management_background_gets_management_paths(self):
        profile = ResumeProfile(
            summary="Engineering manager leading platform teams.",
            skills=["Leadership", "Planning", "Python"],
            experience=[
                ExperienceEntry(
                    role="Engineering Manager",
                    highlights=["Led a backend engineering team."],
                ),
                ExperienceEntry(
                    role="Tech Lead",
                    highlights=["Managed delivery for API projects."],
                ),
            ],
        )

        result = CareerAdvisor().advise(profile)

        self.assertEqual(result.current_level, "mid")
        self.assertIn("engineering manager", result.possible_paths)
        self.assertIn("team lead", result.possible_paths)
        self.assertIn("Strengthen leadership examples with team, scope, and business impact.", result.recommended_actions)


if __name__ == "__main__":
    unittest.main()
