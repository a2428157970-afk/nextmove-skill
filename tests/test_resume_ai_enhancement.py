"""Workflow tests for resume improvement AI enhancement."""

import unittest

from skill.ai import AIProvider, ResumeAIEnhancer
from skill.improvement.schemas import ResumeImprovementResult


class CapturingProvider(AIProvider):
    """Provider double that records the enhancer request."""

    def __init__(self):
        self.prompt: str | None = None
        self.context: dict | None = None

    def generate(self, prompt: str, context: dict) -> str:
        self.prompt = prompt
        self.context = context
        return "Expanded improvement guidance"


class ResumeAIEnhancerTests(unittest.TestCase):
    def test_enhances_structured_resume_improvement_result(self):
        provider = CapturingProvider()
        improvement = ResumeImprovementResult(
            issues=["Resume is missing a summary."],
            suggestions=["Add a focused professional summary."],
            improved_sections={"summary": ["Add a focused summary."]},
        )

        result = ResumeAIEnhancer(provider).enhance(improvement)

        self.assertTrue(result.success)
        self.assertEqual(result.enhanced_content, "Expanded improvement guidance")
        self.assertIn("resume improvement", provider.prompt.lower())
        self.assertEqual(provider.context["issues"], improvement.issues)
        self.assertEqual(provider.context["suggestions"], improvement.suggestions)
        self.assertEqual(provider.context["improved_sections"], improvement.improved_sections)


if __name__ == "__main__":
    unittest.main()
