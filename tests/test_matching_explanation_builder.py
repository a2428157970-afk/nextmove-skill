import json
import unittest

from skill.matching.explanations import (
    ExplanationItem,
    MatchExplanationBuilder,
    MatchExplanationResult,
)
from skill.matching.schemas import (
    EvidenceConfidence,
    EvidenceItem,
    MatchAssessment,
    MatchConfidence,
    RequirementEvidence,
    RequirementStatus,
)
from skill.matching.taxonomy import CareerDomain
from skill.matching.transfer import (
    TransferableCapability,
    TransferableSkillAssessment,
)
from skill.utils import to_dict


class MatchExplanationBuilderTests(unittest.TestCase):
    @staticmethod
    def requirement(
        name,
        status,
        confidence=EvidenceConfidence.LOW,
        evidence=(),
        kind="responsibility",
    ):
        return RequirementEvidence(
            requirement=name,
            kind=kind,
            status=status,
            evidence=tuple(
                EvidenceItem(text=text, source=source)
                for text, source in evidence
            ),
            confidence=confidence,
        )

    @staticmethod
    def assessment(requirements, domain_score=100, transferability=None):
        return MatchAssessment(
            score=75,
            confidence=MatchConfidence.MEDIUM,
            domain_score=domain_score,
            skill_score=75,
            qualification_score=None,
            requirements=tuple(requirements),
            transferability=transferability,
        )

    def test_result_is_serializable_without_resume_or_job_description_fields(self):
        requirements = (
            self.requirement(
                "招聘",
                RequirementStatus.MATCHED,
                EvidenceConfidence.MEDIUM,
                (("校招全流程", "experience"),),
            ),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements),
        )
        payload = to_dict(result)

        self.assertIsInstance(result, MatchExplanationResult)
        self.assertIsInstance(result.strengths[0], ExplanationItem)
        self.assertEqual(
            list(payload),
            ["requirements", "strengths", "gaps", "risks"],
        )
        self.assertNotIn("resume", payload)
        self.assertNotIn("resume_text", payload)
        self.assertNotIn("job_description", payload)
        json.dumps(payload, ensure_ascii=False)

    def test_hr_requirements_build_strength_gap_and_verification_risk(self):
        requirements = (
            self.requirement(
                "招聘",
                RequirementStatus.MATCHED,
                EvidenceConfidence.HIGH,
                (
                    ("校招全流程", "experience"),
                    ("3个月完成1450人签约", "experience"),
                ),
            ),
            self.requirement(
                "考勤",
                RequirementStatus.MATCHED,
                EvidenceConfidence.MEDIUM,
                (("负责员工考勤", "experience"),),
            ),
            self.requirement("行政事务", RequirementStatus.UNKNOWN),
            self.requirement(
                "入离职流程",
                RequirementStatus.PARTIAL,
                EvidenceConfidence.LOW,
                (("员工关系协调", "experience"),),
            ),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements),
        )

        strength_text = " ".join(item.summary for item in result.strengths)
        gap_text = " ".join(item.summary for item in result.gaps)
        risk_text = " ".join(item.summary for item in result.risks)
        self.assertIn("招聘", strength_text)
        self.assertIn("1450", strength_text)
        self.assertIn("考勤", strength_text)
        self.assertIn("行政事务", gap_text)
        self.assertIn("not evidenced", gap_text)
        self.assertIn("入离职流程", risk_text)
        self.assertIn("further verification", risk_text)

    def test_sales_to_product_builds_transferable_strengths_and_transition_risks(self):
        requirements = (
            self.requirement(
                "客户洞察",
                RequirementStatus.MATCHED,
                EvidenceConfidence.MEDIUM,
                (("分析客户需求", "experience"),),
            ),
            self.requirement(
                "商业理解",
                RequirementStatus.MATCHED,
                EvidenceConfidence.MEDIUM,
                (("制定区域销售策略", "experience"),),
            ),
            self.requirement("产品规划", RequirementStatus.UNKNOWN),
            self.requirement(
                "产品交付",
                RequirementStatus.PARTIAL,
                EvidenceConfidence.LOW,
                (("跨部门协调客户方案", "experience"),),
            ),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements, domain_score=10),
        )

        strength_text = " ".join(item.summary for item in result.strengths)
        gap_text = " ".join(item.summary for item in result.gaps)
        risk_text = " ".join(item.summary for item in result.risks)
        self.assertIn("客户洞察", strength_text)
        self.assertIn("商业理解", strength_text)
        self.assertIn("产品规划", gap_text)
        self.assertIn("产品交付", risk_text)
        self.assertTrue(
            any(item.category == "domain_transition" for item in result.risks)
        )
        self.assertTrue(
            any(item.category == "career_transition" for item in result.risks)
        )
        self.assertNotIn("not suitable", risk_text.lower())
        self.assertNotIn("unable to perform", risk_text.lower())

    def test_unknown_is_insufficient_evidence_and_never_missing(self):
        requirements = (
            self.requirement("信息不足的要求", RequirementStatus.UNKNOWN),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements, domain_score=None),
        )

        self.assertEqual(result.strengths, ())
        self.assertEqual(len(result.gaps), 1)
        self.assertEqual(result.gaps[0].category, "insufficient_evidence")
        self.assertIn("not evidenced", result.gaps[0].summary)
        self.assertNotIn("missing", result.gaps[0].summary.lower())

    def test_no_resume_evidence_does_not_invent_domain_transition(self):
        requirements = (
            self.requirement("Python", RequirementStatus.UNKNOWN, kind="skill"),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements, domain_score=0),
        )

        self.assertEqual(result.risks, ())

    def test_explicit_missing_uses_missing_capability_gap(self):
        requirements = (
            self.requirement(
                "PMP certification",
                RequirementStatus.MISSING,
                EvidenceConfidence.HIGH,
                (("Not PMP certified", "certification"),),
                kind="qualification",
            ),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements),
        )

        self.assertEqual(result.gaps[0].category, "missing_capability")
        self.assertIn("explicitly conflicts", result.gaps[0].summary)
        self.assertEqual(result.gaps[0].evidence, requirements[0].evidence)

    def test_low_confidence_match_does_not_become_strength(self):
        requirements = (
            self.requirement(
                "Python",
                RequirementStatus.MATCHED,
                EvidenceConfidence.LOW,
                (("Python", "skill"),),
                kind="skill",
            ),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements),
        )

        self.assertEqual(result.strengths, ())

    def test_transferable_strength_is_limited_and_never_claims_direct_experience(self):
        evidence = (EvidenceItem("Led customer discovery", "experience"),)
        requirements = (
            self.requirement(
                "用户理解",
                RequirementStatus.PARTIAL,
                EvidenceConfidence.MEDIUM,
                (("Led customer discovery", "experience"),),
                kind="skill",
            ),
            self.requirement("产品规划", RequirementStatus.UNKNOWN, kind="skill"),
        )
        limitation = "Customer insight does not prove Product discovery ownership."
        transferability = TransferableSkillAssessment(
            source_domain=CareerDomain.SALES,
            target_domain=CareerDomain.PRODUCT,
            direct_evidence=(),
            transferable_evidence=evidence,
            limitations=(limitation,),
            confidence=EvidenceConfidence.MEDIUM,
            capabilities=(
                TransferableCapability(
                    target_capability="用户理解",
                    evidence=evidence,
                    limitation=limitation,
                    confidence=EvidenceConfidence.MEDIUM,
                ),
            ),
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(
                requirements,
                domain_score=10,
                transferability=transferability,
            ),
        )

        transferable = next(
            item
            for item in result.strengths
            if item.category == "transferable_capability"
        )
        self.assertIn("用户理解", transferable.summary)
        self.assertIn("transferable", transferable.summary.lower())
        self.assertIn("does not prove", transferable.summary.lower())
        risk_text = " ".join(item.summary for item in result.risks)
        self.assertIn("Product discovery ownership", risk_text)
        self.assertIn("产品规划", " ".join(item.summary for item in result.gaps))
        self.assertNotIn("direct product experience", transferable.summary.lower())

    def test_empty_transferability_does_not_create_strength(self):
        requirements = (
            self.requirement("用户理解", RequirementStatus.UNKNOWN, kind="skill"),
        )
        empty = TransferableSkillAssessment(
            source_domain=CareerDomain.SALES,
            target_domain=CareerDomain.PRODUCT,
            direct_evidence=(),
            transferable_evidence=(),
            limitations=(),
            confidence=EvidenceConfidence.LOW,
        )

        result = MatchExplanationBuilder().build(
            requirements,
            self.assessment(requirements, domain_score=10, transferability=empty),
        )

        self.assertEqual(result.strengths, ())


if __name__ == "__main__":
    unittest.main()
