import json
import unittest

from skill.matching.schemas import (
    DomainClassification,
    EvidenceConfidence,
    EvidenceItem,
    MatchConfidence,
)
from skill.matching.taxonomy import CareerDomain, JobFamily
from skill.matching.transfer import (
    TransferableCapability,
    TransferableSkillAssessment,
    TransferableSkillAssessor,
)
from skill.utils import to_dict


class TransferableSkillAssessorTests(unittest.TestCase):
    def setUp(self):
        self.assessor = TransferableSkillAssessor()

    @staticmethod
    def classification(domain, family):
        return DomainClassification(domain, family, MatchConfidence.HIGH, ())

    @staticmethod
    def evidence(*texts):
        return tuple(EvidenceItem(text=text, source="experience") for text in texts)

    def test_internal_model_has_requested_fields_and_is_content_safe(self):
        assessment = TransferableSkillAssessment(
            source_domain=CareerDomain.SALES,
            target_domain=CareerDomain.PRODUCT,
            direct_evidence=(EvidenceItem("Authored a PRD", "project"),),
            transferable_evidence=(
                EvidenceItem("Conducted customer research", "experience"),
            ),
            limitations=("Customer research does not prove product ownership.",),
            confidence=EvidenceConfidence.MEDIUM,
            capabilities=(
                TransferableCapability(
                    target_capability="用户理解",
                    evidence=(
                        EvidenceItem("Conducted customer research", "experience"),
                    ),
                    limitation="Customer research does not prove product ownership.",
                    confidence=EvidenceConfidence.MEDIUM,
                ),
            ),
        )

        payload = to_dict(assessment)

        self.assertEqual(
            list(payload),
            [
                "source_domain",
                "target_domain",
                "direct_evidence",
                "transferable_evidence",
                "limitations",
                "confidence",
                "capabilities",
            ],
        )
        self.assertNotIn("resume", payload)
        self.assertNotIn("job_description", payload)
        json.dumps(payload, ensure_ascii=False)

    def test_sales_to_product_maps_only_bounded_transferable_capabilities(self):
        result = self.assessor.assess(
            self.classification(CareerDomain.SALES, JobFamily.ACCOUNT_MANAGEMENT),
            self.classification(CareerDomain.PRODUCT, JobFamily.PRODUCT_MANAGER),
            self.evidence(
                "Led customer discovery and customer feedback synthesis.",
                "Coordinated requirement collection with client stakeholders.",
                "Owned customer management for regional accounts.",
            ),
        )

        targets = {capability.target_capability for capability in result.capabilities}
        self.assertEqual(targets, {"用户理解", "需求管理"})
        self.assertEqual(result.direct_evidence, ())
        self.assertTrue(result.transferable_evidence)
        self.assertEqual(result.confidence, EvidenceConfidence.HIGH)
        self.assertNotIn("产品规划", targets)
        self.assertFalse(
            any("customer management" in item.text.lower() for item in result.transferable_evidence)
        )

    def test_product_artifact_is_direct_even_on_a_sales_profile(self):
        result = self.assessor.assess(
            self.classification(CareerDomain.SALES, JobFamily.ACCOUNT_MANAGEMENT),
            self.classification(CareerDomain.PRODUCT, JobFamily.PRODUCT_MANAGER),
            self.evidence("Authored a PRD for a fictional product project."),
        )

        self.assertEqual(len(result.direct_evidence), 1)
        self.assertEqual(result.transferable_evidence, ())
        self.assertEqual(result.capabilities, ())

    def test_administration_to_hr_is_directional_and_does_not_infer_hr_expertise(self):
        result = self.assessor.assess(
            self.classification(CareerDomain.OPERATIONS, JobFamily.ADMINISTRATION),
            self.classification(CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST),
            self.evidence(
                "Coordinated onboarding documents and employee support requests.",
                "Maintained office process documentation.",
                "Managed office process workflows and coordination.",
            ),
        )

        targets = {capability.target_capability for capability in result.capabilities}
        self.assertIn("入职行政", targets)
        self.assertIn("员工档案", targets)
        self.assertIn("HR流程支持", targets)
        self.assertNotIn("招聘", targets)
        self.assertNotIn("薪酬", targets)
        self.assertNotIn("劳动关系", targets)

        reverse = self.assessor.assess(
            self.classification(CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST),
            self.classification(CareerDomain.OPERATIONS, JobFamily.ADMINISTRATION),
            self.evidence("Coordinated onboarding documents."),
        )
        self.assertEqual(reverse.transferable_evidence, ())
        self.assertEqual(reverse.capabilities, ())

    def test_empty_evidence_returns_empty_low_confidence_assessment(self):
        result = self.assessor.assess(
            self.classification(CareerDomain.SALES, JobFamily.ACCOUNT_MANAGEMENT),
            self.classification(CareerDomain.PRODUCT, JobFamily.PRODUCT_MANAGER),
            (),
        )

        self.assertEqual(result.direct_evidence, ())
        self.assertEqual(result.transferable_evidence, ())
        self.assertEqual(result.limitations, ())
        self.assertEqual(result.capabilities, ())
        self.assertEqual(result.confidence, EvidenceConfidence.LOW)


if __name__ == "__main__":
    unittest.main()
