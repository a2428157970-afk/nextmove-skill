import unittest

from skill.reporting.language import HumanReportLanguage


class HumanCareerReportLanguageTests(unittest.TestCase):
    def test_sanitize_rewrites_forbidden_english_conclusions(self):
        policy = HumanReportLanguage()

        for unsafe in (
            "This will guarantee an offer.",
            "The transition is impossible.",
            "You are unsuitable for this role.",
            "You cannot transition.",
        ):
            with self.subTest(unsafe=unsafe):
                safe = policy.sanitize(unsafe)
                self.assertTrue(policy.is_safe(safe))
                self.assertIn("current evidence", safe.casefold())

    def test_sanitize_rewrites_forbidden_chinese_conclusions(self):
        policy = HumanReportLanguage()

        for unsafe in ("你一定成功", "你不适合这个岗位", "你无法转型", "保证拿 offer"):
            with self.subTest(unsafe=unsafe):
                safe = policy.sanitize(unsafe)
                self.assertTrue(policy.is_safe(safe))
                self.assertIn("当前证据", safe)

    def test_templates_use_evidence_and_validation_language(self):
        policy = HumanReportLanguage()

        self.assertIn("当前证据显示", policy.career_summary("human_resources", "developing"))
        self.assertIn("建议验证", policy.partial_gap("PRD"))
        self.assertIn("可以优先补充", policy.unknown_gap("Product Planning"))

    def test_safe_source_evidence_is_accepted_without_rewriting(self):
        policy = HumanReportLanguage()
        evidence = "Owned campus recruitment and attendance records."

        self.assertTrue(policy.is_safe(evidence))
        self.assertEqual(policy.sanitize(evidence), evidence)


if __name__ == "__main__":
    unittest.main()
