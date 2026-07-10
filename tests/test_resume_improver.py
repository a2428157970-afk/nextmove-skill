import unittest

from skill.improvement import ResumeImprover
from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class ResumeImproverTests(unittest.TestCase):
    def test_improver_generates_suggestions_from_analysis_weaknesses(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built internal APIs."],
                )
            ],
            skills=["Python", "SQL"],
        )
        analysis = ResumeAnalysisResult(
            weaknesses=[
                "Resume is missing a summary.",
                "Experience does not show quantified outcomes.",
                "Skills section is present but limited.",
            ],
            skill_assessment=SkillAssessment(
                gaps=["Expand the skills section with more relevant keywords."]
            ),
        )

        result = ResumeImprover().improve(profile, analysis)

        self.assertIsInstance(result, ResumeImprovementResult)
        self.assertIn("Resume is missing a summary.", result.issues)
        self.assertIn(
            "Add a concise summary that states your target role, core strengths, and career positioning.",
            result.suggestions,
        )
        self.assertIn(
            "Rewrite experience bullets to include measurable impact, such as revenue, efficiency, scale, or time saved.",
            result.suggestions,
        )
        self.assertIn(
            "Expand the skills section with relevant tools, domains, and role-specific keywords.",
            result.suggestions,
        )
        self.assertIn("summary", result.improved_sections)
        self.assertIn("experience", result.improved_sections)
        self.assertIn("skills", result.improved_sections)


if __name__ == "__main__":
    unittest.main()
