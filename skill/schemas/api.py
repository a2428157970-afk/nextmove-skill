"""Provider-neutral public Skill API response schemas."""

from dataclasses import dataclass, field
from typing import Any

from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.career import CareerAdviceResult
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.matching import JobMatchResult


@dataclass(slots=True)
class SkillError:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SkillResponse:
    success: bool
    capability: str
    result: Any | None = None
    error: SkillError | None = None


@dataclass(slots=True)
class CareerAnalysisReport:
    success: bool
    analysis: ResumeAnalysisResult | None = None
    improvement: ResumeImprovementResult | None = None
    job_match: JobMatchResult | None = None
    career_advice: CareerAdviceResult | None = None
    failed_capability: str | None = None
    error: SkillError | None = None
