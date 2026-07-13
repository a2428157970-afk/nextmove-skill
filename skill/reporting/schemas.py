"""Internal, provider-neutral Human Career Report schemas."""

from dataclasses import dataclass
from enum import Enum

from skill.utils import to_dict as serialize


class ReportConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class JobFitLevel(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    EXPLORATORY = "exploratory"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ActionHorizon(str, Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


@dataclass(frozen=True, slots=True)
class ReportEvidence:
    text: str
    source: str
    confidence: ReportConfidenceLevel


@dataclass(frozen=True, slots=True)
class CurrentCareerProfile:
    current_domain: str
    core_capabilities: tuple[str, ...]
    profile_summary: str


@dataclass(frozen=True, slots=True)
class CareerStageNarrative:
    stage: str
    explanation: str
    evidence_signals: tuple[str, ...]
    confidence: ReportConfidenceLevel


@dataclass(frozen=True, slots=True)
class ReportStrength:
    capability: str
    explanation: str
    evidence: tuple[ReportEvidence, ...]


@dataclass(frozen=True, slots=True)
class CapabilityGap:
    capability: str
    status: str
    explanation: str
    evidence_needed: str


@dataclass(frozen=True, slots=True)
class JobFitNarrative:
    match_score: int
    level: JobFitLevel
    summary: str
    why_fit: tuple[str, ...]
    main_gaps: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TransitionPathNarrative:
    current_domain: str
    target_domain: str
    transition_type: str
    summary: str
    transferable_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReportAction:
    horizon: ActionHorizon
    priority: int
    related_gap: str
    objective: str
    steps: tuple[str, ...]
    expected_evidence: str


@dataclass(frozen=True, slots=True)
class ActionPlan:
    immediate: tuple[ReportAction, ...]
    short_term: tuple[ReportAction, ...]
    long_term: tuple[ReportAction, ...]


@dataclass(frozen=True, slots=True)
class ReportRisk:
    note: str
    basis: tuple[str, ...]
    verification: str


@dataclass(frozen=True, slots=True)
class ReportConfidence:
    level: ReportConfidenceLevel
    explanation: str
    missing_information: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HumanCareerReport:
    career_summary: str
    current_profile: CurrentCareerProfile
    career_stage: CareerStageNarrative
    strengths: tuple[ReportStrength, ...]
    job_fit: JobFitNarrative
    capability_gaps: tuple[CapabilityGap, ...]
    transition_path: TransitionPathNarrative
    action_plan: ActionPlan
    risks: tuple[ReportRisk, ...]
    confidence: ReportConfidence

    def to_dict(self) -> dict[str, object]:
        """Return a recursively JSON-serializable internal report payload."""

        return serialize(self)


__all__ = [
    "ActionHorizon",
    "ActionPlan",
    "CapabilityGap",
    "CareerStageNarrative",
    "CurrentCareerProfile",
    "HumanCareerReport",
    "JobFitLevel",
    "JobFitNarrative",
    "ReportAction",
    "ReportConfidence",
    "ReportConfidenceLevel",
    "ReportEvidence",
    "ReportRisk",
    "ReportStrength",
    "TransitionPathNarrative",
]
