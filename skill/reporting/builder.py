"""Aggregate existing career intelligence into an internal human report."""

from __future__ import annotations

from collections.abc import Iterable

from skill.career.stages import CareerStageAssessment
from skill.career.transition import (
    CareerTransitionAssessment,
    TransitionGapKind,
)
from skill.matching.explanations import MatchExplanationResult
from skill.matching.schemas import (
    JobMatchResult,
    RequirementStatus,
)
from skill.reporting.language import HumanReportLanguage
from skill.reporting.schemas import (
    ActionHorizon,
    ActionPlan,
    CapabilityGap,
    CareerStageNarrative,
    CurrentCareerProfile,
    HumanCareerReport,
    JobFitLevel,
    JobFitNarrative,
    ReportAction,
    ReportConfidence,
    ReportConfidenceLevel,
    ReportEvidence,
    ReportRisk,
    ReportStrength,
    TransitionPathNarrative,
)
from skill.schemas.analysis import ResumeAnalysisResult


_CONFIDENCE = {
    "high": ReportConfidenceLevel.HIGH,
    "medium": ReportConfidenceLevel.MEDIUM,
    "low": ReportConfidenceLevel.LOW,
}

_STATUS_RANK = {
    "missing": 0,
    "partial": 1,
    "unknown": 2,
    "development_area": 3,
}


class HumanCareerReportBuilder:
    """Map completed assessments into a user-readable structured report."""

    def __init__(self, language: HumanReportLanguage | None = None) -> None:
        self.language = language or HumanReportLanguage()

    def build(
        self,
        resume_analysis: ResumeAnalysisResult,
        job_match: JobMatchResult,
        career_stage: CareerStageAssessment,
        match_explanation: MatchExplanationResult,
        career_transition: CareerTransitionAssessment,
    ) -> HumanCareerReport:
        """Aggregate existing results without invoking any intelligence engine."""

        strengths = self._strengths(match_explanation)
        gaps = self._gaps(match_explanation, career_transition)
        return HumanCareerReport(
            career_summary=self.language.career_summary(
                career_transition.current_domain.value,
                career_stage.stage.value,
            ),
            current_profile=CurrentCareerProfile(
                current_domain=career_transition.current_domain.value,
                core_capabilities=tuple(item.capability for item in strengths),
                profile_summary=self.language.profile_summary(
                    career_transition.current_domain.value
                ),
            ),
            career_stage=self._career_stage(career_stage),
            strengths=strengths,
            job_fit=self._job_fit(job_match, match_explanation, strengths, gaps),
            capability_gaps=gaps,
            transition_path=self._transition_path(career_transition),
            action_plan=self._action_plan(career_transition),
            risks=self._risks(match_explanation, career_transition),
            confidence=self._confidence(
                resume_analysis,
                career_stage,
                match_explanation,
                career_transition,
                strengths,
            ),
        )

    def _strengths(
        self,
        explanation: MatchExplanationResult,
    ) -> tuple[ReportStrength, ...]:
        strengths: list[ReportStrength] = []
        seen: set[str] = set()
        for item in explanation.strengths:
            if not item.related_requirements:
                continue
            safe_evidence = tuple(
                ReportEvidence(
                    text=evidence.text,
                    source=evidence.source,
                    confidence=self._map_confidence(item.confidence.value),
                )
                for evidence in item.evidence
                if self.language.is_safe(evidence.text)
            )
            if not safe_evidence:
                continue
            capability = item.related_requirements[0]
            key = capability.casefold()
            if key in seen:
                continue
            seen.add(key)
            strengths.append(
                ReportStrength(
                    capability=capability,
                    explanation=self.language.strength(
                        capability,
                        transferable=item.category == "transferable_capability",
                    ),
                    evidence=safe_evidence,
                )
            )
        return tuple(strengths)

    def _career_stage(
        self,
        assessment: CareerStageAssessment,
    ) -> CareerStageNarrative:
        signals = (
            *assessment.signals.experience,
            *assessment.signals.responsibility,
            *assessment.signals.impact,
        )
        return CareerStageNarrative(
            stage=assessment.stage.value,
            explanation=self.language.stage_explanation(assessment.stage.value),
            evidence_signals=tuple(signals),
            confidence=self._map_confidence(assessment.confidence.value),
        )

    def _job_fit(
        self,
        job_match: JobMatchResult,
        explanation: MatchExplanationResult,
        strengths: tuple[ReportStrength, ...],
        gaps: tuple[CapabilityGap, ...],
    ) -> JobFitNarrative:
        level = self._fit_level(job_match.match_score, bool(explanation.requirements))
        return JobFitNarrative(
            match_score=job_match.match_score,
            level=level,
            summary=self.language.fit_summary(job_match.match_score, level.value),
            why_fit=tuple(item.explanation for item in strengths),
            main_gaps=tuple(item.capability for item in gaps),
        )

    def _gaps(
        self,
        explanation: MatchExplanationResult,
        transition: CareerTransitionAssessment,
    ) -> tuple[CapabilityGap, ...]:
        action_evidence = {
            action.related_gap.casefold(): action.expected_evidence
            for action in transition.recommended_actions
        }
        ordered: list[CapabilityGap] = []
        positions: dict[str, int] = {}

        for requirement in explanation.requirements:
            if requirement.status == RequirementStatus.MATCHED:
                continue
            status = requirement.status.value
            self._add_gap(
                ordered,
                positions,
                CapabilityGap(
                    capability=requirement.requirement,
                    status=status,
                    explanation=self._gap_explanation(requirement.requirement, status),
                    evidence_needed=action_evidence.get(
                        requirement.requirement.casefold(),
                        self.language.verification(),
                    ),
                ),
            )

        for transition_gap in transition.missing_capabilities:
            status = self._transition_gap_status(
                transition_gap.kind,
                transition_gap.evidence_status,
            )
            self._add_gap(
                ordered,
                positions,
                CapabilityGap(
                    capability=transition_gap.capability,
                    status=status,
                    explanation=self._gap_explanation(transition_gap.capability, status),
                    evidence_needed=action_evidence.get(
                        transition_gap.capability.casefold(),
                        self.language.verification(),
                    ),
                ),
            )
        return tuple(ordered)

    def _add_gap(
        self,
        ordered: list[CapabilityGap],
        positions: dict[str, int],
        candidate: CapabilityGap,
    ) -> None:
        key = candidate.capability.casefold()
        if key not in positions:
            positions[key] = len(ordered)
            ordered.append(candidate)
            return
        position = positions[key]
        current = ordered[position]
        if _STATUS_RANK[candidate.status] < _STATUS_RANK[current.status]:
            ordered[position] = candidate
        elif candidate.evidence_needed != self.language.verification():
            ordered[position] = CapabilityGap(
                capability=current.capability,
                status=current.status,
                explanation=current.explanation,
                evidence_needed=candidate.evidence_needed,
            )

    def _gap_explanation(self, capability: str, status: str) -> str:
        return {
            "missing": self.language.missing_gap,
            "partial": self.language.partial_gap,
            "unknown": self.language.unknown_gap,
            "development_area": self.language.development_gap,
        }[status](capability)

    @staticmethod
    def _transition_gap_status(kind, evidence_status: RequirementStatus) -> str:
        if kind == TransitionGapKind.DEVELOPMENT_AREA:
            return "development_area"
        if kind == TransitionGapKind.TRANSFERABLE_CAPABILITY:
            return "partial"
        return evidence_status.value

    def _transition_path(
        self,
        transition: CareerTransitionAssessment,
    ) -> TransitionPathNarrative:
        current = transition.current_domain.value
        target = transition.target_domain.value
        transition_type = transition.transition_type.value
        return TransitionPathNarrative(
            current_domain=current,
            target_domain=target,
            transition_type=transition_type,
            summary=self.language.transition_summary(current, target, transition_type),
            transferable_capabilities=tuple(transition.transferable_skills),
            missing_capabilities=tuple(
                gap.capability for gap in transition.missing_capabilities
            ),
        )

    def _action_plan(
        self,
        transition: CareerTransitionAssessment,
    ) -> ActionPlan:
        buckets: dict[ActionHorizon, list[ReportAction]] = {
            ActionHorizon.IMMEDIATE: [],
            ActionHorizon.SHORT_TERM: [],
            ActionHorizon.LONG_TERM: [],
        }
        ordered = sorted(
            enumerate(transition.recommended_actions),
            key=lambda pair: (pair[1].priority, pair[0]),
        )
        for _, action in ordered:
            horizon = self._horizon(action.priority)
            buckets[horizon].append(
                ReportAction(
                    horizon=horizon,
                    priority=action.priority,
                    related_gap=action.related_gap,
                    objective=self.language.sanitize(action.objective),
                    steps=tuple(self.language.sanitize(step) for step in action.steps),
                    expected_evidence=self.language.sanitize(action.expected_evidence),
                )
            )
        return ActionPlan(
            immediate=tuple(buckets[ActionHorizon.IMMEDIATE]),
            short_term=tuple(buckets[ActionHorizon.SHORT_TERM]),
            long_term=tuple(buckets[ActionHorizon.LONG_TERM]),
        )

    def _risks(
        self,
        explanation: MatchExplanationResult,
        transition: CareerTransitionAssessment,
    ) -> tuple[ReportRisk, ...]:
        risks: list[ReportRisk] = []
        seen: set[str] = set()
        for item in explanation.risks:
            note = self.language.risk_note(item.summary)
            if note.casefold() in seen:
                continue
            seen.add(note.casefold())
            risks.append(
                ReportRisk(
                    note=note,
                    basis=tuple(item.related_requirements),
                    verification=self.language.verification(),
                )
            )
        for factor in transition.transition_risk.factors:
            note = self.language.risk_note(factor)
            if note.casefold() in seen:
                continue
            seen.add(note.casefold())
            risks.append(
                ReportRisk(
                    note=note,
                    basis=tuple(transition.transition_risk.evidence_gaps),
                    verification=self.language.verification(),
                )
            )
        return tuple(risks)

    def _confidence(
        self,
        analysis: ResumeAnalysisResult,
        stage: CareerStageAssessment,
        explanation: MatchExplanationResult,
        transition: CareerTransitionAssessment,
        strengths: tuple[ReportStrength, ...],
    ) -> ReportConfidence:
        levels = [
            self._map_confidence(stage.confidence.value),
            self._map_confidence(transition.confidence.value),
        ]
        levels.extend(
            self._map_confidence(requirement.confidence.value)
            for requirement in explanation.requirements
        )
        if not explanation.requirements:
            levels.append(ReportConfidenceLevel.LOW)
        level = self._confidence_level(levels)

        missing: list[str] = []
        if transition.current_domain.value in {"unknown", "other"}:
            missing.append("当前职业领域的具体经历")
        if stage.stage.value == "unknown":
            missing.append("职责、年限和成果信息")
        if not explanation.requirements:
            missing.append("目标岗位的具体要求")
        if not strengths:
            missing.append("可核验的优势证据")
        if not analysis.strengths and not analysis.skill_assessment.strengths:
            missing.append("简历中的职责、技能与成果")

        return ReportConfidence(
            level=level,
            explanation=self.language.confidence_explanation(level.value),
            missing_information=tuple(dict.fromkeys(missing)),
        )

    @staticmethod
    def _fit_level(score: int, has_requirements: bool) -> JobFitLevel:
        if not has_requirements:
            return JobFitLevel.INSUFFICIENT_EVIDENCE
        if score >= 80:
            return JobFitLevel.STRONG
        if score >= 60:
            return JobFitLevel.MODERATE
        return JobFitLevel.EXPLORATORY

    @staticmethod
    def _horizon(priority: int) -> ActionHorizon:
        if priority <= 1:
            return ActionHorizon.IMMEDIATE
        if priority == 2:
            return ActionHorizon.SHORT_TERM
        return ActionHorizon.LONG_TERM

    @staticmethod
    def _map_confidence(value: str) -> ReportConfidenceLevel:
        return _CONFIDENCE[value]

    @staticmethod
    def _confidence_level(
        levels: Iterable[ReportConfidenceLevel],
    ) -> ReportConfidenceLevel:
        ordered = tuple(levels)
        if ReportConfidenceLevel.LOW in ordered:
            return ReportConfidenceLevel.LOW
        if ReportConfidenceLevel.MEDIUM in ordered:
            return ReportConfidenceLevel.MEDIUM
        return ReportConfidenceLevel.HIGH


__all__ = ["HumanCareerReportBuilder"]
