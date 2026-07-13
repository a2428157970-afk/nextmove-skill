import unittest

from skill.career.transition import (
    TransitionCapabilityGap,
    TransitionGapKind,
    TransitionRiskLevel,
    TransitionType,
)
from skill.career.transition_risk import TransitionRiskAssessor
from skill.matching.schemas import EvidenceItem, RequirementStatus


class TransitionRiskAssessorTests(unittest.TestCase):
    def setUp(self):
        self.assessor = TransitionRiskAssessor()
        self.direct = (EvidenceItem("recruitment delivery", "experience"), EvidenceItem("attendance operations", "skills"))
        self.transfer = (EvidenceItem("customer research", "experience"),)

    def gap(self, name="Product Planning", status=RequirementStatus.UNKNOWN, core=True):
        return TransitionCapabilityGap(name, TransitionGapKind.DIRECT_CAPABILITY, status, "Direct evidence is not available.", core)

    def test_unknown_requires_insufficient_transition_information(self):
        result = self.assessor.assess(TransitionType.UNKNOWN, (), (), ())
        self.assertEqual(result.level, TransitionRiskLevel.UNKNOWN)

    def test_low_for_strong_direct_same_domain_transition(self):
        result = self.assessor.assess(TransitionType.SAME_DOMAIN, self.direct, (), ())
        self.assertEqual(result.level, TransitionRiskLevel.LOW)

    def test_medium_for_transfer_dominant_or_development_transition(self):
        result = self.assessor.assess(TransitionType.ADJACENT_ROLE, (), self.transfer, (self.gap(core=False),))
        self.assertEqual(result.level, TransitionRiskLevel.MEDIUM)

    def test_high_for_cross_domain_with_multiple_core_gaps(self):
        result = self.assessor.assess(
            TransitionType.CROSS_DOMAIN, (), self.transfer,
            (self.gap(), self.gap("PRD"), self.gap("Product Delivery Ownership")),
        )
        self.assertEqual(result.level, TransitionRiskLevel.HIGH)

    def test_high_when_no_bridge_evidence_and_multiple_core_gaps(self):
        result = self.assessor.assess(
            TransitionType.ADJACENT_ROLE, (), (),
            (self.gap("Recruitment"), self.gap("Labor Relations")),
        )
        self.assertEqual(result.level, TransitionRiskLevel.HIGH)

    def test_language_describes_evidence_without_negative_judgment(self):
        result = self.assessor.assess(TransitionType.CROSS_DOMAIN, (), self.transfer, (self.gap(), self.gap("PRD")))
        rendered = " ".join((*result.factors, *result.evidence_gaps)).lower()
        for forbidden in ("unsuitable", "cannot transition", "not qualified", "不适合", "无法转型"):
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
