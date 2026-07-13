"""Deterministic evidence-based transition risk calibration."""

from skill.career.transition import (
    TransitionCapabilityGap,
    TransitionRiskAssessment,
    TransitionRiskLevel,
    TransitionType,
)
from skill.matching.schemas import EvidenceItem, RequirementStatus


class TransitionRiskAssessor:
    def assess(
        self,
        transition_type: TransitionType,
        direct_evidence: tuple[EvidenceItem, ...],
        transferable_evidence: tuple[EvidenceItem, ...],
        gaps: tuple[TransitionCapabilityGap, ...],
    ) -> TransitionRiskAssessment:
        if transition_type == TransitionType.UNKNOWN:
            return TransitionRiskAssessment(
                TransitionRiskLevel.UNKNOWN,
                ("Transition information is insufficient for calibrated risk.",),
                tuple(gap.capability for gap in gaps),
            )

        core_gaps = tuple(
            gap.capability
            for gap in gaps
            if gap.core and gap.evidence_status != RequirementStatus.MATCHED
        )
        if not direct_evidence and not transferable_evidence and len(core_gaps) >= 2:
            return TransitionRiskAssessment(
                TransitionRiskLevel.HIGH,
                ("No bridge evidence is available and multiple core capabilities need direct validation.",),
                core_gaps,
            )
        if (
            transition_type == TransitionType.CROSS_DOMAIN
            and len(direct_evidence) < 2
            and len(core_gaps) >= 2
        ):
            return TransitionRiskAssessment(
                TransitionRiskLevel.HIGH,
                ("Cross-domain evidence is limited and major target capabilities need direct validation.",),
                core_gaps,
            )
        if (
            transition_type in {TransitionType.SAME_ROLE, TransitionType.SAME_DOMAIN}
            and len(direct_evidence) >= 2
            and not core_gaps
        ):
            return TransitionRiskAssessment(
                TransitionRiskLevel.LOW,
                ("Direct target-domain evidence is strong and no major capability gap is identified.",),
                (),
            )

        factors = []
        if transferable_evidence and len(transferable_evidence) >= len(direct_evidence):
            factors.append("Current support relies mainly on transferable evidence.")
        if core_gaps:
            factors.append("Some core target capabilities need direct validation.")
        if not factors:
            factors.append("The transition has evidence areas that need further validation.")
        return TransitionRiskAssessment(
            TransitionRiskLevel.MEDIUM,
            tuple(factors),
            core_gaps,
        )
