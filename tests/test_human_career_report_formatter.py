import json
import unittest

from skill.reporting.formatter import HumanCareerReportFormatter
from tests.test_human_career_report_schema import sample_report


class HumanCareerReportFormatterTests(unittest.TestCase):
    def test_json_formatter_returns_unicode_structured_payload(self):
        rendered = HumanCareerReportFormatter().to_json(sample_report())
        payload = json.loads(rendered)

        self.assertEqual(payload["career_summary"], "当前证据显示职业方向与目标岗位较一致。")
        self.assertEqual(payload["job_fit"]["match_score"], 82)
        self.assertNotIn("human_report", payload)

    def test_markdown_formatter_uses_fixed_five_section_order(self):
        rendered = HumanCareerReportFormatter().to_markdown(sample_report())
        headings = (
            "## 你的职业画像",
            "## 你的优势",
            "## 岗位匹配",
            "## 如果转型",
            "## 下一步行动",
        )

        positions = [rendered.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Owned recruitment delivery.", rendered)
        self.assertIn("### 立即行动", rendered)
        self.assertIn("### 短期提升", rendered)
        self.assertIn("### 长期发展", rendered)

    def test_markdown_formatter_keeps_empty_action_horizons_explicit(self):
        rendered = HumanCareerReportFormatter().to_markdown(sample_report())

        self.assertGreaterEqual(rendered.count("当前暂无基于证据的建议。"), 2)


if __name__ == "__main__":
    unittest.main()
