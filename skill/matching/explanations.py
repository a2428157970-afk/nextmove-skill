"""Internal deterministic explanations derived from match evidence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from skill.matching.schemas import (
    EvidenceConfidence,
    EvidenceItem,
    MatchAssessment,
    MatchConfidence,
    RequirementEvidence,
    RequirementStatus,
)


@dataclass(frozen=True, slots=True)
class ExplanationItem:
    category: str
    summary: str
    related_requirements: tuple[str, ...] = ()
    evidence: tuple[EvidenceItem, ...] = ()
    confidence: EvidenceConfidence = EvidenceConfidence.LOW


@dataclass(frozen=True, slots=True)
class MatchExplanationResult:
    requirements: tuple[RequirementEvidence, ...]
    strengths: tuple[ExplanationItem, ...]
    gaps: tuple[ExplanationItem, ...]
    risks: tuple[ExplanationItem, ...]


class MatchExplanationBuilder:
    """Build internal strengths, gaps, and risks without changing match scores."""

    def build(
        self,
        requirements: Sequence[RequirementEvidence],
        assessment: MatchAssessment,
    ) -> MatchExplanationResult:
        ordered_requirements = tuple(requirements)
        strengths = self._strengths(ordered_requirements, assessment)
        gaps = self._gaps(ordered_requirements)
        risks = self._risks(ordered_requirements, assessment)
        return MatchExplanationResult(
            requirements=ordered_requirements,
            strengths=tuple(strengths),
            gaps=tuple(gaps),
            risks=tuple(risks),
        )

    @staticmethod
    def _strengths(
        requirements: tuple[RequirementEvidence, ...],
        assessment: MatchAssessment,
    ) -> list[ExplanationItem]:
        strengths: list[ExplanationItem] = []
        accepted_confidence = {
            EvidenceConfidence.HIGH,
            EvidenceConfidence.MEDIUM,
        }
        for requirement in requirements:
            if (
                requirement.status != RequirementStatus.MATCHED
                or requirement.confidence not in accepted_confidence
            ):
                continue
            scale_evidence = next(
                (
                    item.text
                    for item in requirement.evidence
                    if re.search(r"\d", item.text)
                ),
                None,
            )
            if scale_evidence is not None:
                category = "scope_or_impact"
                summary = (
                    f"Evidence supports {requirement.requirement} at demonstrated "
                    f"scale: {scale_evidence}."
                )
            else:
                category = "requirement_coverage"
                summary = f"Evidence supports {requirement.requirement}."
            strengths.append(
                ExplanationItem(
                    category=category,
                    summary=summary,
                    related_requirements=(requirement.requirement,),
                    evidence=requirement.evidence,
                    confidence=requirement.confidence,
                )
            )

        transferability = assessment.transferability
        if transferability is None:
            return strengths
        partial_requirements = {
            requirement.requirement
            for requirement in requirements
            if requirement.status == RequirementStatus.PARTIAL
        }
        for capability in transferability.capabilities:
            if (
                capability.target_capability not in partial_requirements
                or capability.confidence not in accepted_confidence
            ):
                continue
            strengths.append(
                ExplanationItem(
                    category="transferable_capability",
                    summary=(
                        "Transferable evidence supports "
                        f"{capability.target_capability}; limitation: "
                        f"{capability.limitation}"
                    ),
                    related_requirements=(capability.target_capability,),
                    evidence=capability.evidence,
                    confidence=capability.confidence,
                )
            )
        return strengths

    @staticmethod
    def _gaps(
        requirements: tuple[RequirementEvidence, ...],
    ) -> list[ExplanationItem]:
        gaps: list[ExplanationItem] = []
        for requirement in requirements:
            if requirement.status == RequirementStatus.MISSING:
                gaps.append(
                    ExplanationItem(
                        category="missing_capability",
                        summary=(
                            "Supplied evidence explicitly conflicts with requirement: "
                            f"{requirement.requirement}."
                        ),
                        related_requirements=(requirement.requirement,),
                        evidence=requirement.evidence,
                        confidence=requirement.confidence,
                    )
                )
            elif requirement.status == RequirementStatus.UNKNOWN:
                gaps.append(
                    ExplanationItem(
                        category="insufficient_evidence",
                        summary=(
                            f"{requirement.requirement} is not evidenced in the resume."
                        ),
                        related_requirements=(requirement.requirement,),
                        confidence=EvidenceConfidence.LOW,
                    )
                )
        return gaps

    def _risks(
        self,
        requirements: tuple[RequirementEvidence, ...],
        assessment: MatchAssessment,
    ) -> list[ExplanationItem]:
        transfer_capabilities = {
            capability.target_capability: capability
            for capability in (
                assessment.transferability.capabilities
                if assessment.transferability is not None
                else ()
            )
        }
        risks: list[ExplanationItem] = []
        for requirement in requirements:
            if requirement.status != RequirementStatus.PARTIAL:
                continue
            capability = transfer_capabilities.get(requirement.requirement)
            summary = (
                f"Evidence for {requirement.requirement} is incomplete and needs "
                "further verification."
            )
            if capability is not None:
                summary = (
                    f"Transferable evidence for {requirement.requirement} is partial: "
                    f"{capability.limitation} Further verification is needed."
                )
            risks.append(
                ExplanationItem(
                    category="partial_coverage",
                    summary=summary,
                    related_requirements=(requirement.requirement,),
                    evidence=requirement.evidence,
                    confidence=requirement.confidence,
                )
            )

        transition_requirements = tuple(
            requirement.requirement
            for requirement in requirements
            if requirement.status
            in {RequirementStatus.PARTIAL, RequirementStatus.UNKNOWN}
        )
        has_transferable_evidence = any(
            requirement.status
            in {RequirementStatus.MATCHED, RequirementStatus.PARTIAL}
            for requirement in requirements
        )
        is_domain_transition = (
            assessment.domain_score is not None
            and 0 < assessment.domain_score < 55
            and has_transferable_evidence
        )
        if is_domain_transition:
            risks.append(
                ExplanationItem(
                    category="domain_transition",
                    summary="Domain transition evidence needs further verification.",
                    related_requirements=transition_requirements,
                    confidence=self._assessment_confidence(assessment.confidence),
                )
            )

        has_partial = any(
            requirement.status == RequirementStatus.PARTIAL
            for requirement in requirements
        )
        unknown_requirements = tuple(
            requirement.requirement
            for requirement in requirements
            if requirement.status == RequirementStatus.UNKNOWN
        )
        if is_domain_transition and has_partial and unknown_requirements:
            risks.append(
                ExplanationItem(
                    category="career_transition",
                    summary=(
                        "Career transition evidence is incomplete; "
                        + ", ".join(unknown_requirements)
                        + " need further verification."
                    ),
                    related_requirements=transition_requirements,
                    confidence=EvidenceConfidence.LOW,
                )
            )
        return risks

    @staticmethod
    def _assessment_confidence(confidence: MatchConfidence) -> EvidenceConfidence:
        return {
            MatchConfidence.HIGH: EvidenceConfidence.HIGH,
            MatchConfidence.MEDIUM: EvidenceConfidence.MEDIUM,
            MatchConfidence.LOW: EvidenceConfidence.LOW,
        }[confidence]
