import re
import unittest
from pathlib import Path

from skill import NextMoveSkill
from skill.__main__ import build_parser


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = (
    "docs/quick-start.md",
    "docs/agent-prompt-template.md",
    "docs/output-guide.md",
    "docs/pilot-feedback-template.md",
    "docs/pilot-guidelines.md",
    "examples/data/sample_resume.txt",
    "examples/data/sample_job_description.txt",
    ".github/ISSUE_TEMPLATE/pilot_feedback.md",
)


class PilotKitAcceptanceTests(unittest.TestCase):
    def _read_required(self, relative_path: str) -> str:
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), f"missing Pilot Kit file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def test_required_pilot_files_exist(self):
        for relative_path in EXPECTED_FILES:
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())

    def test_fictional_sample_runs_complete_career_analysis(self):
        resume = self._read_required("examples/data/sample_resume.txt")
        job_description = self._read_required(
            "examples/data/sample_job_description.txt"
        )

        response = NextMoveSkill().run(
            "career_analysis",
            {"resume": resume, "job_description": job_description},
        )

        self.assertTrue(response.success)
        self.assertTrue(response.result.success)
        self.assertIsNotNone(response.result.analysis)
        self.assertIsNotNone(response.result.improvement)
        self.assertIsNotNone(response.result.job_match)
        self.assertIsNotNone(response.result.career_advice)
        self.assertTrue(response.result.analysis.strengths)
        self.assertTrue(response.result.improvement.suggestions)
        self.assertGreater(response.result.job_match.match_score, 0)
        self.assertTrue(response.result.career_advice.recommended_actions)

    def test_samples_are_labeled_fictional_and_contact_free(self):
        sample_text = "\n".join(
            self._read_required(path)
            for path in (
                "examples/data/sample_resume.txt",
                "examples/data/sample_job_description.txt",
            )
        )

        self.assertIn("fictional", sample_text.lower())
        self.assertIsNone(
            re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", sample_text)
        )
        self.assertNotRegex(sample_text.lower(), r"api[_ -]?key|bearer token")

    def test_agent_prompts_cover_scenarios_and_truthfulness(self):
        prompt_text = self._read_required("docs/agent-prompt-template.md")

        for heading in (
            "Complete Career Analysis",
            "Resume Improvement",
            "Job Matching",
            "Career Planning",
        ):
            self.assertIn(heading, prompt_text)
        for required_text in (
            "NextMove",
            "RESUME_TEXT",
            "JOB_DESCRIPTION",
            "Do not invent",
            "facts",
            "suggestions",
            "insufficient",
            "structured failure",
        ):
            self.assertIn(required_text, prompt_text)

        prompt_blocks = re.findall(r"```text\n(.*?)\n```", prompt_text, re.DOTALL)
        self.assertEqual(len(prompt_blocks), 4)
        for prompt in prompt_blocks:
            with self.subTest(prompt=prompt.splitlines()[0]):
                self.assertIn("If you cannot access NextMove", prompt)
                self.assertIn("do not simulate", prompt)
                self.assertIn("privacy-reviewed", prompt)

    def test_output_guide_explains_every_report_section(self):
        guide = self._read_required("docs/output-guide.md")

        for section in (
            "analysis",
            "improvement",
            "job_match",
            "career_advice",
            "Top strengths",
            "Top three improvements",
            "Visible skill gaps",
            "Next three actions",
            "structured failure",
        ):
            self.assertIn(section, guide)

    def test_feedback_channels_put_privacy_before_free_text(self):
        feedback_files = (
            ("docs/pilot-feedback-template.md", "## Observed errors"),
            (
                ".github/ISSUE_TEMPLATE/pilot_feedback.md",
                "## Anonymous reproduction details",
            ),
        )
        prohibited_terms = (
            "full resume",
            "job description",
            "real name",
            "phone",
            "email",
            "company confidential",
            "API key",
        )

        for path, free_text_marker in feedback_files:
            with self.subTest(path=path):
                content = self._read_required(path)
                self.assertLess(content.index("Privacy warning"), content.index(free_text_marker))
                for term in prohibited_terms:
                    self.assertIn(term, content)

    def test_deferred_cli_option_remains_unavailable(self):
        self.assertNotIn("--job-description-file", build_parser().format_help())


if __name__ == "__main__":
    unittest.main()
