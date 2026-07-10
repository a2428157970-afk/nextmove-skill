"""Provider-neutral resume analysis schema."""

from dataclasses import dataclass, field
from typing import Literal


CareerLevel = Literal["intern", "junior", "mid", "senior", "lead", "unknown"]


@dataclass(slots=True)
class SkillAssessment:
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass(slots=True)
class ResumeAnalysisResult:
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    skill_assessment: SkillAssessment = field(default_factory=SkillAssessment)
    career_level: CareerLevel = "unknown"
