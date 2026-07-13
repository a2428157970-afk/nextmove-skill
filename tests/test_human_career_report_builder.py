import unittest

from skill.career.stages import (
    CareerStage,
    CareerStageAssessment,
    StageConfidence,
    StageSignals,
)
from skill.career.transition import (
    CareerTransitionAssessment,
    TransitionAction,
    TransitionCapabilityGap,
    TransitionConfidence,
    TransitionGapKind,
    TransitionRiskAssessment,
    TransitionRiskLevel,
    TransitionType,
)
from skill.matching.explanations import (
    ExplanationItem,
    MatchExplanationResult,
)
from skill.matching.schemas import (
    EvidenceConfidence,
    EvidenceItem,
    JobMatchResult,
    RequirementEvidence,
    RequirementStatus,
)
from skill.matching.taxonomy import CareerDomain
from skill.reporting.builder import HumanCareerReportBuilder
from skill.reporting.schemas import JobFitLevel, ReportConfidenceLevel
from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment


def evidence(text: str, source: str = "experience") -> EvidenceItem:
    return EvidenceItem(text=text, source=source)


def requirement(
    name: str,
    status: RequirementStatus,
    *items: EvidenceItem,
) -> RequirementEvidence:
    return RequirementEvidence(
        requirement=name,
        kind="skill",
        status=status,
        evidence=tuple(items),
        confidence=(
            EvidenceConfidence.LOW
            if status == RequirementStatus.UNKNOWN
            else EvidenceConfidence.MEDIUM
        ),
    )


def sample_inputs():
    recruitment = evidence("Owned recruitment delivery.")
    coordination = evidence("Coordinated customer requirements.")
    unsafe = evidence("This work will guarantee an offer.")
    requirements = (
        requirement("Recruitment", RequirementStatus.MATCHED, recruitment),
        requirement("Stakeholder Coordination", RequirementStatus.PARTIAL, coordination),
        requirement("Product Planning", RequirementStatus.UNKNOWN),
    )
    explanation = MatchExplanationResult(
        requirements=requirements,
        strengths=(
            ExplanationItem(
                category="requirement_coverage",
                summary="Evidence supports Recruitment.",
                related_requirements=("Recruitment",),
                evidence=(recruitment,),
                confidence=EvidenceConfidence.HIGH,
            ),
            ExplanationItem(
                category="transferable_capability",
                summary="Transferable evidence supports Stakeholder Coordination.",
                related_requirements=("Stakeholder Coordination",),
                evidence=(coordination,),
                confidence=EvidenceConfidence.MEDIUM,
            ),
            ExplanationItem(
                category="requirement_coverage",
                summary="Unsupported leadership claim.",
                related_requirements=("Leadership",),
                evidence=(),
                confidence=EvidenceConfidence.LOW,
            ),
            ExplanationItem(
                category="requirement_coverage",
                summary="Unsafe claim.",
                related_requirements=("Offer Conversion",),
                evidence=(unsafe,),
                confidence=EvidenceConfidence.HIGH,
            ),
        ),
        gaps=(
            ExplanationItem(
                category="insufficient_evidence",
                summary="Product Planning is not evidenced in the resume.",
                related_requirements=("Product Planning",),
                confidence=EvidenceConfidence.LOW,
            ),
        ),
        risks=(
            ExplanationItem(
                category="partial_coverage",
                summary="Coordination ownership needs verification.",
                related_requirements=("Stakeholder Coordination",),
                evidence=(coordination,),
                confidence=EvidenceConfidence.MEDIUM,
            ),
        ),
    )
    transition = CareerTransitionAssessment(
        current_domain=CareerDomain.SALES,
        target_domain=CareerDomain.PRODUCT,
        transition_type=TransitionType.CROSS_DOMAIN,
        transferable_skills=("Stakeholder Coordination",),
        direct_evidence=(recruitment,),
        transferable_evidence=(coordination,),
        missing_capabilities=(
            TransitionCapabilityGap(
                capability="Product Planning",
                kind=TransitionGapKind.DIRECT_CAPABILITY,
                evidence_status=RequirementStatus.UNKNOWN,
                reason="Direct evidence is not available.",
                core=True,
            ),
            TransitionCapabilityGap(
                capability="PRD",
                kind=TransitionGapKind.DEVELOPMENT_AREA,
                evidence_status=RequirementStatus.UNKNOWN,
                reason="A reviewable work sample is needed.",
                core=False,
            ),
        ),
        transition_risk=TransitionRiskAssessment(
            level=TransitionRiskLevel.HIGH,
            factors=("Sparse direct product evidence.",),
            evidence_gaps=("Product Planning", "PRD"),
        ),
        recommended_actions=(
            TransitionAction(
                related_gap="PRD",
                objective="Create a reviewable PRD.",
                steps=("Select a fictional problem.", "Draft and review the PRD."),
                expected_evidence="A reviewable PRD work sample.",
                priority=2,
            ),
            TransitionAction(
                related_gap="Product Planning",
                objective="Create direct planning evidence.",
                steps=("Define a user problem.", "Validate a proposed plan."),
                expected_evidence="A product planning case study.",
                priority=1,
            ),
        ),
        confidence=TransitionConfidence.MEDIUM,
    )
    return (
        ResumeAnalysisResult(
            strengths=("Resume includes work experience.",),
            skill_assessment=SkillAssessment(strengths=("Recruitment",)),
            career_level="mid",
        ),
        JobMatchResult(match_score=70),
        CareerStageAssessment(
            stage=CareerStage.EXPERIENCED,
            signals=StageSignals(
                experience=("seven years",),
                responsibility=("owned delivery",),
                impact=(),
            ),
            confidence=StageConfidence.HIGH,
        ),
        explanation,
        transition,
    )


class HumanCareerReportBuilderTests(unittest.TestCase):
    def test_builder_keeps_only_safe_evidence_grounded_strengths(self):
        report = HumanCareerReportBuilder().build(*sample_inputs())

        self.assertEqual(
            [item.capability for item in report.strengths],
            ["Recruitment", "Stakeholder Coordination"],
        )
        self.assertTrue(all(item.evidence for item in report.strengths))
        self.assertIn("可迁移", report.strengths[1].explanation)

    def test_builder_copies_score_and_maps_fit_without_rescoring(self):
        report = HumanCareerReportBuilder().build(*sample_inputs())

        self.assertEqual(report.job_fit.match_score, 70)
        self.assertEqual(report.job_fit.level, JobFitLevel.MODERATE)
        self.assertEqual(
            report.job_fit.why_fit,
            tuple(item.explanation for item in report.strengths),
        )

    def test_builder_preserves_gap_meaning_and_action_linkage(self):
        report = HumanCareerReportBuilder().build(*sample_inputs())
        gaps = {item.capability: item for item in report.capability_gaps}

        self.assertEqual(gaps["Product Planning"].status, "unknown")
        self.assertIn("尚未看到", gaps["Product Planning"].explanation)
        self.assertEqual(gaps["PRD"].status, "development_area")
        self.assertEqual(
            gaps["Product Planning"].evidence_needed,
            "A product planning case study.",
        )
        actions = (*report.action_plan.immediate, *report.action_plan.short_term)
        self.assertEqual([item.related_gap for item in actions], ["Product Planning", "PRD"])

    def test_builder_preserves_transition_and_uses_conservative_confidence(self):
        report = HumanCareerReportBuilder().build(*sample_inputs())

        self.assertEqual(report.transition_path.current_domain, "sales")
        self.assertEqual(report.transition_path.target_domain, "product")
        self.assertEqual(report.transition_path.transition_type, "cross_domain")
        self.assertEqual(report.confidence.level, ReportConfidenceLevel.LOW)
        self.assertTrue(report.risks)
        self.assertTrue(all(item.verification for item in report.risks))

    def test_empty_requirements_force_insufficient_evidence_and_low_confidence(self):
        analysis, job_match, stage, explanation, transition = sample_inputs()
        explanation = MatchExplanationResult((), (), (), ())
        report = HumanCareerReportBuilder().build(
            analysis, job_match, stage, explanation, transition
        )

        self.assertEqual(report.job_fit.level, JobFitLevel.INSUFFICIENT_EVIDENCE)
        self.assertEqual(report.confidence.level, ReportConfidenceLevel.LOW)
        self.assertIn("目标岗位的具体要求", report.confidence.missing_information)


if __name__ == "__main__":
    unittest.main()
