import unittest

from skill.matching.scoring import MatchScorer
from skill.matching.schemas import (
    DomainClassification,
    MatchAssessment,
    MatchConfidence,
    RequirementStatus,
)
from skill.matching.taxonomy import CareerDomain, JobFamily
from skill.schemas.resume import EducationEntry, ExperienceEntry, ResumeProfile


class MatchingSchemaTests(unittest.TestCase):
    def test_internal_assessment_carries_confidence_and_components(self):
        assessment = MatchAssessment(
            score=87,
            confidence=MatchConfidence.HIGH,
            domain_score=100,
            skill_score=82,
            qualification_score=85,
            strengths=("domain aligned",),
            gaps=("certification not visible",),
        )

        self.assertEqual(assessment.score, 87)
        self.assertEqual(assessment.confidence, MatchConfidence.HIGH)
        self.assertEqual(assessment.domain_score, 100)


class MatchScorerTests(unittest.TestCase):
    def setUp(self):
        self.scorer = MatchScorer()

    @staticmethod
    def classification(domain, family=None, confidence=MatchConfidence.HIGH):
        return DomainClassification(domain, family, confidence, ())

    def test_domain_component_uses_frozen_compatibility_values(self):
        hr_recruitment = self.classification(
            CareerDomain.HUMAN_RESOURCES, JobFamily.RECRUITMENT
        )
        hr_generalist = self.classification(
            CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST
        )
        operations = self.classification(CareerDomain.OPERATIONS)
        supply_chain = self.classification(CareerDomain.SUPPLY_CHAIN)
        technology = self.classification(CareerDomain.TECHNOLOGY)
        unknown = self.classification(CareerDomain.UNKNOWN, confidence=MatchConfidence.LOW)

        self.assertEqual(self.scorer.domain_score(hr_recruitment, hr_recruitment, True), 100)
        self.assertEqual(self.scorer.domain_score(hr_recruitment, self.classification(CareerDomain.HUMAN_RESOURCES), True), 90)
        self.assertEqual(self.scorer.domain_score(hr_recruitment, hr_generalist, True), 75)
        self.assertEqual(self.scorer.domain_score(operations, supply_chain, True), 55)
        self.assertEqual(self.scorer.domain_score(unknown, operations, True, True), 30)
        self.assertEqual(self.scorer.domain_score(technology, hr_generalist, True), 10)
        self.assertEqual(self.scorer.domain_score(technology, hr_generalist, False), 0)

    def test_hr_skill_scoring_recognizes_required_and_default_requirements(self):
        profile = ResumeProfile(
            skills=["招聘", "考勤", "劳动关系"],
            experience=[ExperienceEntry(role="人事专员")],
        )
        job = "人事行政专员，要求招聘和考勤，负责薪酬与劳动关系。"
        hr = self.classification(CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST)

        result = self.scorer.assess(profile, job, hr, hr)

        self.assertIn("招聘", result.matched_skills)
        self.assertIn("考勤", result.matched_skills)
        self.assertIn("劳动关系", result.matched_skills)
        self.assertIn("薪酬", result.missing_skills)
        self.assertGreater(result.skill_score, 60)

    def test_domain_vocabulary_does_not_create_unmentioned_requirements(self):
        profile = ResumeProfile(skills=["招聘"])
        hr = self.classification(CareerDomain.HUMAN_RESOURCES)

        result = self.scorer.assess(profile, "招聘专员", hr, hr)

        self.assertEqual(result.matched_skills, ("招聘",))
        self.assertNotIn("薪酬", result.missing_skills)
        self.assertNotIn("Python", result.missing_skills)

    def test_qualification_score_is_conservative_and_ignores_negation(self):
        profile = ResumeProfile(
            education=[EducationEntry(degree="Bachelor")],
            experience=[ExperienceEntry(role="Accountant")],
            certifications=["CPA"],
            raw_text="3 years of accounting experience. English working proficiency.",
        )
        finance = self.classification(CareerDomain.FINANCE, JobFamily.ACCOUNTING)
        result = self.scorer.assess(
            profile,
            "Accountant requires 3 years experience, bachelor degree, CPA and English. No MBA required.",
            finance,
            finance,
        )

        self.assertEqual(result.qualification_score, 100)
        self.assertNotIn("MBA", result.missing_skills)

    def test_unavailable_components_redistribute_weights(self):
        profile = ResumeProfile(skills=["Python"], experience=[ExperienceEntry(role="Backend Engineer")])
        technology = self.classification(CareerDomain.TECHNOLOGY, JobFamily.BACKEND)

        result = self.scorer.assess(
            profile,
            "Backend Engineer requiring Python.",
            technology,
            technology,
        )

        self.assertEqual(result.domain_score, 100)
        self.assertEqual(result.skill_score, 100)
        self.assertIsNone(result.qualification_score)
        self.assertEqual(result.score, 100)

    def test_uninformative_job_returns_stable_low_confidence_zero(self):
        unknown = self.classification(CareerDomain.UNKNOWN, confidence=MatchConfidence.LOW)
        result = self.scorer.assess(
            ResumeProfile(skills=["Excel"]),
            "欢迎加入我们的团队。",
            unknown,
            unknown,
        )

        self.assertEqual(result.score, 0)
        self.assertEqual(result.confidence, MatchConfidence.LOW)
        self.assertEqual(result.matched_skills, ())
        self.assertEqual(result.missing_skills, ())
        self.assertTrue(any("insufficient" in gap.lower() for gap in result.gaps))

    def test_negated_skill_and_qualification_requirements_are_ignored(self):
        profile = ResumeProfile(experience=[ExperienceEntry(role="Backend Engineer")])
        technology = self.classification(CareerDomain.TECHNOLOGY, JobFamily.BACKEND)

        result = self.scorer.assess(
            profile,
            "Backend Engineer. Docker is not required. No CPA required. "
            "English not required. 无需 Kubernetes，不要求本科。",
            technology,
            technology,
        )

        self.assertNotIn("Docker", result.missing_skills)
        self.assertNotIn("Kubernetes", result.missing_skills)
        self.assertIsNone(result.qualification_score)
        self.assertFalse(any("cpa" in gap.lower() for gap in result.gaps))
        self.assertFalse(any("english" in gap.lower() for gap in result.gaps))
        self.assertFalse(any("bachelor" in gap.lower() for gap in result.gaps))

    def test_structured_languages_and_experience_dates_satisfy_qualifications(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Accountant",
                    start_date="2018-01",
                    end_date="2024-01",
                )
            ],
            languages=["English"],
        )
        finance = self.classification(CareerDomain.FINANCE, JobFamily.ACCOUNTING)

        result = self.scorer.assess(
            profile,
            "Accountant requiring 3 years experience and English.",
            finance,
            finance,
        )

        self.assertEqual(result.qualification_score, 100)
        self.assertFalse(any("years" in gap.lower() for gap in result.gaps))
        self.assertFalse(any("english" in gap.lower() for gap in result.gaps))

    def test_product_capabilities_map_direct_artifact_evidence(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Product Manager",
                    highlights=[
                        "Owned the PRD and feature design for account onboarding.",
                        "Prioritized the product roadmap using product metrics and A/B test results.",
                        "Coordinated product delivery and launch follow-up with engineering.",
                    ],
                )
            ]
        )
        product = self.classification(
            CareerDomain.PRODUCT,
            JobFamily.PRODUCT_MANAGER,
        )

        result = self.scorer.assess(
            profile,
            "Product Manager requiring user understanding, PRD, product roadmap, "
            "product metrics, and product delivery.",
            product,
            product,
        )

        statuses = {
            requirement.requirement: requirement.status
            for requirement in result.requirements
        }
        self.assertEqual(statuses["需求管理"], RequirementStatus.MATCHED)
        self.assertEqual(statuses["产品规划"], RequirementStatus.MATCHED)
        self.assertEqual(statuses["产品数据分析"], RequirementStatus.MATCHED)
        self.assertEqual(statuses["交付协作"], RequirementStatus.MATCHED)
        self.assertIn("需求管理", result.matched_skills)

    def test_sales_customer_evidence_is_not_direct_product_experience(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Account Manager",
                    highlights=[
                        "Conducted customer research, requirement collection, and customer feedback synthesis.",
                    ],
                )
            ]
        )
        sales = self.classification(
            CareerDomain.SALES,
            JobFamily.ACCOUNT_MANAGEMENT,
        )
        product = self.classification(
            CareerDomain.PRODUCT,
            JobFamily.PRODUCT_MANAGER,
        )

        result = self.scorer.assess(
            profile,
            "Product Manager requiring customer research, requirement collection, "
            "customer feedback, PRD, and product roadmap.",
            sales,
            product,
        )

        self.assertFalse(
            any(
                requirement.status == RequirementStatus.MATCHED
                for requirement in result.requirements
                if requirement.requirement in {"用户理解", "需求管理", "产品规划"}
            )
        )
        self.assertNotIn("用户理解", result.matched_skills)
        self.assertNotIn("需求管理", result.matched_skills)

    def test_sales_to_product_transfer_is_partial_and_direct_artifacts_stay_unknown(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Account Manager",
                    highlights=[
                        "Led customer discovery and requirement collection.",
                        "Used commercial analysis and stakeholder coordination for accounts.",
                    ],
                )
            ]
        )
        sales = self.classification(
            CareerDomain.SALES,
            JobFamily.ACCOUNT_MANAGEMENT,
        )
        product = self.classification(
            CareerDomain.PRODUCT,
            JobFamily.PRODUCT_MANAGER,
        )

        result = self.scorer.assess(
            profile,
            "Product Manager requiring customer insight, PRD, product roadmap, "
            "product metrics, and product delivery.",
            sales,
            product,
        )

        statuses = {
            requirement.requirement: requirement.status
            for requirement in result.requirements
        }
        self.assertEqual(statuses["用户理解"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["需求管理"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["产品数据分析"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["交付协作"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["产品规划"], RequirementStatus.UNKNOWN)
        self.assertFalse(
            {"用户理解", "需求管理", "产品数据分析", "交付协作"}
            & set(result.matched_skills)
        )
        self.assertIsNotNone(result.transferability)
        self.assertTrue(result.transferability.limitations)

    def test_administration_to_hr_maps_support_only_and_preserves_unknowns(self):
        profile = ResumeProfile(
            skills=["Attendance support"],
            experience=[
                ExperienceEntry(
                    role="Office Administrator",
                    highlights=[
                        "Coordinated onboarding documents, maintained process documentation, "
                        "and managed office process workflows.",
                    ],
                )
            ],
        )
        administration = self.classification(
            CareerDomain.OPERATIONS,
            JobFamily.ADMINISTRATION,
        )
        hr = self.classification(
            CareerDomain.HUMAN_RESOURCES,
            JobFamily.HR_GENERALIST,
        )

        result = self.scorer.assess(
            profile,
            "HR generalist assistant requiring attendance, onboarding administration, "
            "HR process support, recruitment coordination, employee file support, payroll, "
            "and labor relations.",
            administration,
            hr,
        )

        statuses = {
            requirement.requirement: requirement.status
            for requirement in result.requirements
        }
        self.assertEqual(statuses["考勤"], RequirementStatus.MATCHED)
        self.assertEqual(statuses["入职行政"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["员工档案"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["HR流程支持"], RequirementStatus.PARTIAL)
        self.assertEqual(statuses["招聘协调"], RequirementStatus.UNKNOWN)
        self.assertEqual(statuses["薪酬"], RequirementStatus.UNKNOWN)
        self.assertEqual(statuses["劳动关系"], RequirementStatus.UNKNOWN)
        self.assertTrue(
            any(
                "attendance" in item.text.lower()
                for item in result.transferability.direct_evidence
            )
        )


if __name__ == "__main__":
    unittest.main()
