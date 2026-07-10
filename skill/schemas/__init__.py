"""Core data schemas for NextMove Skill."""

from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment
from skill.schemas.api import SkillError, SkillResponse
from skill.schemas.career import CareerAdviceResult
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import (
    BasicInformation,
    CertificationEntry,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    ResumeProfile,
)

__all__ = [
    "BasicInformation",
    "CareerAdviceResult",
    "CertificationEntry",
    "EducationEntry",
    "ExperienceEntry",
    "JobMatchResult",
    "ProjectEntry",
    "ResumeAnalysisResult",
    "ResumeImprovementResult",
    "ResumeProfile",
    "SkillError",
    "SkillResponse",
    "SkillAssessment",
]
