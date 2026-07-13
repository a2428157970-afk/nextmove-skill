import json
import unittest
from dataclasses import FrozenInstanceError, fields

from skill.career.stages import CareerStage, CareerStageAssessment, StageConfidence, StageSignals
from skill.career.transition import (
    CareerTransitionAssessment,
    CareerTransitionAssessor,
    TargetRoleLevel,
    TargetRoleLevelAssessor,
    TransitionAction,
    TransitionCapabilityGap,
    TransitionConfidence,
    TransitionGapKind,
    TransitionRiskAssessment,
    TransitionRiskLevel,
    TransitionType,
)
from skill.matching.explanations import MatchExplanationResult
from skill.matching.schemas import (
    DomainClassification,
    EvidenceConfidence,
    EvidenceItem,
    MatchConfidence,
    RequirementEvidence,
    RequirementStatus,
)
from skill.matching.taxonomy import CareerDomain, JobFamily
from skill.matching.transfer import TransferableCapability, TransferableSkillAssessment
from skill.utils import to_dict


def classification(domain, family):
    return DomainClassification(domain, family, MatchConfidence.HIGH)


class CareerTransitionContractTests(unittest.TestCase):
    def test_contract_is_immutable_serializable_and_content_safe(self):
        gap = TransitionCapabilityGap(
            "Product Planning", TransitionGapKind.DIRECT_CAPABILITY,
            RequirementStatus.UNKNOWN, "Direct evidence is not available.", True,
        )
        assessment = CareerTransitionAssessment(
            CareerDomain.SALES, CareerDomain.PRODUCT, TransitionType.CROSS_DOMAIN,
            ("Customer Insight",), (), (), (gap,),
            TransitionRiskAssessment(TransitionRiskLevel.HIGH, ("major capability gaps",), ("Product Planning",)),
            (TransitionAction("Product Planning", "Build a product case", ("Draft a PRD",), "PRD and roadmap", 1),),
            TransitionConfidence.MEDIUM,
        )
        payload = to_dict(assessment)
        json.dumps(payload)
        self.assertEqual(payload["missing_capabilities"][0]["evidence_status"], "unknown")
        self.assertEqual(
            [item.name for item in fields(CareerTransitionAssessment)],
            ["current_domain", "target_domain", "transition_type", "transferable_skills", "direct_evidence", "transferable_evidence", "missing_capabilities", "transition_risk", "recommended_actions", "confidence"],
        )
        self.assertFalse({"resume", "resume_text", "job_description", "raw_text"} & set(payload))
        with self.assertRaises(FrozenInstanceError):
            assessment.confidence = TransitionConfidence.HIGH


class CareerTransitionTypeTests(unittest.TestCase):
    def setUp(self):
        self.assessor = CareerTransitionAssessor()
        self.hr = classification(CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST)

    def test_all_transition_types_and_directional_adjacency(self):
        admin = classification(CareerDomain.OPERATIONS, JobFamily.ADMINISTRATION)
        sales = classification(CareerDomain.SALES, JobFamily.ACCOUNT_MANAGEMENT)
        product = classification(CareerDomain.PRODUCT, JobFamily.PRODUCT_MANAGER)
        unknown = classification(CareerDomain.UNKNOWN, None)
        self.assertEqual(self.assessor.transition_type(self.hr, self.hr, TargetRoleLevel.PEER), TransitionType.SAME_ROLE)
        self.assertEqual(self.assessor.transition_type(self.hr, self.hr, TargetRoleLevel.MANAGEMENT), TransitionType.SAME_DOMAIN)
        self.assertEqual(self.assessor.transition_type(admin, self.hr, TargetRoleLevel.PEER), TransitionType.ADJACENT_ROLE)
        self.assertEqual(self.assessor.transition_type(self.hr, admin, TargetRoleLevel.PEER), TransitionType.CROSS_DOMAIN)
        self.assertEqual(self.assessor.transition_type(sales, product, TargetRoleLevel.PEER), TransitionType.CROSS_DOMAIN)
        self.assertEqual(self.assessor.transition_type(unknown, product, TargetRoleLevel.PEER), TransitionType.UNKNOWN)

    def test_role_level_is_transient_and_deterministic(self):
        assessor = TargetRoleLevelAssessor()
        self.assertEqual(assessor.classify("HR Specialist"), TargetRoleLevel.PEER)
        self.assertEqual(assessor.classify("HR Manager responsible for team management"), TargetRoleLevel.MANAGEMENT)
        self.assertEqual(assessor.classify("Product Manager"), TargetRoleLevel.PEER)
        self.assertEqual(assessor.classify("Product Manager with people leadership"), TargetRoleLevel.MANAGEMENT)
        self.assertEqual(assessor.classify("Product Manager managing five direct reports"), TargetRoleLevel.MANAGEMENT)
        self.assertEqual(assessor.classify("Product Manager reporting to Head of Product"), TargetRoleLevel.PEER)
        self.assertEqual(assessor.classify("Join our team"), TargetRoleLevel.UNKNOWN)
        self.assertFalse(hasattr(assessor, "text"))


class CareerTransitionAggregationTests(unittest.TestCase):
    def test_empty_information_remains_unknown_without_invented_gaps_or_actions(self):
        result = CareerTransitionAssessor().assess(
            classification(CareerDomain.UNKNOWN, None),
            classification(CareerDomain.PRODUCT, JobFamily.PRODUCT_MANAGER),
            CareerStageAssessment(CareerStage.UNKNOWN, StageSignals(), StageConfidence.LOW),
            None, MatchExplanationResult((), (), (), ()), TargetRoleLevel.UNKNOWN,
        )
        self.assertEqual(result.transition_type, TransitionType.UNKNOWN)
        self.assertEqual(result.transition_risk.level, TransitionRiskLevel.UNKNOWN)
        self.assertEqual(result.confidence, TransitionConfidence.LOW)
        self.assertEqual(result.missing_capabilities, ())
        self.assertEqual(result.recommended_actions, ())

    def test_unknown_stays_unknown_and_partial_is_transferable_gap(self):
        customer = EvidenceItem("customer research", "professional_summary")
        transfer = TransferableSkillAssessment(
            CareerDomain.SALES, CareerDomain.PRODUCT, (), (customer,),
            ("does not prove product ownership",), EvidenceConfidence.MEDIUM,
            (TransferableCapability("User Understanding", (customer,), "does not prove product ownership", EvidenceConfidence.MEDIUM),),
        )
        requirements = (
            RequirementEvidence("User Understanding", "skill", RequirementStatus.PARTIAL, (customer,), EvidenceConfidence.MEDIUM),
            RequirementEvidence("Product Planning", "skill", RequirementStatus.UNKNOWN, (), EvidenceConfidence.LOW),
        )
        explanation = MatchExplanationResult(requirements, (), (), ())
        stage = CareerStageAssessment(CareerStage.EXPERIENCED, StageSignals(), StageConfidence.HIGH)
        result = CareerTransitionAssessor().assess(
            classification(CareerDomain.SALES, JobFamily.ACCOUNT_MANAGEMENT),
            classification(CareerDomain.PRODUCT, JobFamily.PRODUCT_MANAGER),
            stage, transfer, explanation, TargetRoleLevel.PEER,
        )
        gaps = {gap.capability: gap for gap in result.missing_capabilities}
        self.assertEqual(gaps["Product Planning"].evidence_status, RequirementStatus.UNKNOWN)
        self.assertEqual(gaps["User Understanding"].kind, TransitionGapKind.TRANSFERABLE_CAPABILITY)
        self.assertFalse(any(gap.evidence_status == RequirementStatus.MISSING for gap in gaps.values()))
        self.assertEqual(result.transferable_evidence, (customer,))

    def test_management_target_adds_grounded_development_area(self):
        direct = EvidenceItem("Led recruitment delivery", "experience")
        requirement = RequirementEvidence("Recruitment", "skill", RequirementStatus.MATCHED, (direct,), EvidenceConfidence.HIGH)
        result = CareerTransitionAssessor().assess(
            classification(CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST),
            classification(CareerDomain.HUMAN_RESOURCES, JobFamily.HR_GENERALIST),
            CareerStageAssessment(CareerStage.EXPERIENCED, StageSignals(), StageConfidence.HIGH),
            None, MatchExplanationResult((requirement,), (), (), ()), TargetRoleLevel.MANAGEMENT,
        )
        leadership = next(g for g in result.missing_capabilities if g.capability == "People Leadership")
        self.assertEqual(leadership.kind, TransitionGapKind.DEVELOPMENT_AREA)
        self.assertEqual(leadership.evidence_status, RequirementStatus.UNKNOWN)
        self.assertEqual(result.direct_evidence, (direct,))


if __name__ == "__main__":
    unittest.main()
