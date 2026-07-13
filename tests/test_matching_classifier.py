import unittest

from skill.matching.classifier import DomainClassifier
from skill.matching.schemas import MatchConfidence
from skill.schemas.resume import ExperienceEntry, ResumeProfile
from skill.matching.taxonomy import (
    ADJACENT_DOMAINS,
    DOMAIN_FAMILIES,
    CareerDomain,
    JobFamily,
)


class CareerTaxonomyTests(unittest.TestCase):
    def test_v1_domain_values_are_frozen(self):
        self.assertEqual(
            {domain.value for domain in CareerDomain},
            {
                "human_resources",
                "technology",
                "finance",
                "sales",
                "marketing",
                "operations",
                "supply_chain",
                "manufacturing",
                "customer_service",
                "other",
                "unknown",
            },
        )

    def test_v1_job_families_are_small_and_domain_scoped(self):
        self.assertEqual(
            DOMAIN_FAMILIES[CareerDomain.HUMAN_RESOURCES],
            (
                JobFamily.HR_GENERALIST,
                JobFamily.RECRUITMENT,
                JobFamily.COMPENSATION_BENEFITS,
                JobFamily.EMPLOYEE_RELATIONS,
            ),
        )
        self.assertEqual(
            DOMAIN_FAMILIES[CareerDomain.TECHNOLOGY],
            (
                JobFamily.BACKEND,
                JobFamily.FRONTEND,
                JobFamily.DATA,
                JobFamily.DEVOPS,
            ),
        )
        self.assertEqual(DOMAIN_FAMILIES[CareerDomain.OTHER], ())
        self.assertEqual(DOMAIN_FAMILIES[CareerDomain.UNKNOWN], ())

    def test_adjacent_domains_are_symmetric(self):
        self.assertIn(
            (CareerDomain.OPERATIONS, CareerDomain.SUPPLY_CHAIN),
            ADJACENT_DOMAINS,
        )
        self.assertIn(
            (CareerDomain.SUPPLY_CHAIN, CareerDomain.OPERATIONS),
            ADJACENT_DOMAINS,
        )

    def test_other_and_unknown_are_distinct_states(self):
        self.assertNotEqual(CareerDomain.OTHER, CareerDomain.UNKNOWN)


class DomainClassifierTests(unittest.TestCase):
    def setUp(self):
        self.classifier = DomainClassifier()

    def test_classifies_chinese_hr_specialist_as_human_resources(self):
        result = self.classifier.classify_text(
            "人事行政专员，负责招聘、考勤、薪酬和劳动关系。"
        )

        self.assertEqual(result.domain, CareerDomain.HUMAN_RESOURCES)
        self.assertEqual(result.job_family, JobFamily.HR_GENERALIST)
        self.assertEqual(result.confidence, MatchConfidence.HIGH)
        self.assertIn("人事行政专员", result.evidence)

    def test_classifies_python_backend_engineer_as_technology(self):
        result = self.classifier.classify_text(
            "Python Backend Engineer building APIs with FastAPI and SQL."
        )

        self.assertEqual(result.domain, CareerDomain.TECHNOLOGY)
        self.assertEqual(result.job_family, JobFamily.BACKEND)

    def test_classifies_finance_and_operations_examples(self):
        finance = self.classifier.classify_text(
            "会计专员负责财务报表、月度结账与账目核对。"
        )
        operations = self.classifier.classify_text(
            "行政专员负责办公室管理、供应商协调与流程优化。"
        )

        self.assertEqual(finance.domain, CareerDomain.FINANCE)
        self.assertEqual(finance.job_family, JobFamily.ACCOUNTING)
        self.assertEqual(operations.domain, CareerDomain.OPERATIONS)
        self.assertEqual(operations.job_family, JobFamily.ADMINISTRATION)

    def test_distinguishes_unsupported_occupation_from_weak_text(self):
        unsupported = self.classifier.classify_text("中学教师负责课程设计与授课。")
        weak = self.classifier.classify_text("欢迎加入我们的团队。")
        empty = self.classifier.classify_text("")

        self.assertEqual(unsupported.domain, CareerDomain.OTHER)
        self.assertEqual(weak.domain, CareerDomain.UNKNOWN)
        self.assertEqual(empty.domain, CareerDomain.UNKNOWN)
        self.assertEqual(empty.confidence, MatchConfidence.LOW)

    def test_ambiguous_tied_domains_return_unknown(self):
        result = self.classifier.classify_text("招聘专员兼会计专员")

        self.assertEqual(result.domain, CareerDomain.UNKNOWN)
        self.assertEqual(result.confidence, MatchConfidence.LOW)

    def test_profile_uses_professional_evidence_and_deduplicates_aliases(self):
        profile = ResumeProfile(
            summary="Recruitment specialist",
            experience=[
                ExperienceEntry(
                    role="Recruitment specialist",
                    highlights=["Managed recruitment and interview coordination."],
                )
            ],
            skills=["Recruitment"],
        )

        result = self.classifier.classify_profile(profile)

        self.assertEqual(result.domain, CareerDomain.HUMAN_RESOURCES)
        self.assertEqual(len(result.evidence), len(set(result.evidence)))

    def test_selected_family_always_belongs_to_selected_domain(self):
        result = self.classifier.classify_text(
            "人事招聘招聘招聘 specialist accountant accountant"
        )

        self.assertEqual(result.domain, CareerDomain.HUMAN_RESOURCES)
        self.assertTrue(
            result.job_family is None
            or result.job_family in DOMAIN_FAMILIES[result.domain]
        )


if __name__ == "__main__":
    unittest.main()
