"""Provider-neutral job matching schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from skill.matching.taxonomy import CareerDomain, JobFamily


class MatchConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(str, Enum):
    MATCHED = "matched"
    PARTIAL = "partial"
    MISSING = "missing"
    UNKNOWN = "unknown"


class EvidenceConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    text: str
    source: str


@dataclass(frozen=True, slots=True)
class RequirementEvidence:
    requirement: str
    kind: str
    status: RequirementStatus
    evidence: tuple[EvidenceItem, ...]
    confidence: EvidenceConfidence


@dataclass(frozen=True, slots=True)
class DomainClassification:
    domain: CareerDomain
    job_family: JobFamily | None
    confidence: MatchConfidence
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MatchAssessment:
    score: int
    confidence: MatchConfidence
    domain_score: int | None
    skill_score: int | None
    qualification_score: int | None
    strengths: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    matched_skills: tuple[str, ...] = ()
    missing_skills: tuple[str, ...] = ()
    requirements: tuple[RequirementEvidence, ...] = ()


@dataclass(slots=True)
class JobMatchResult:
    match_score: int = 0
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
