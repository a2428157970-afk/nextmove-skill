import unittest

from skill.career import CareerAdvisor
from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment
from skill.schemas.career import CareerAdviceResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class CareerAdvisorTests(unittest.TestCase):
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
