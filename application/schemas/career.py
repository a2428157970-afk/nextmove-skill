"""Career-analysis application response schemas."""

from dataclasses import dataclass

from skill.schemas import (
    CareerAdviceResult,
    JobMatchResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
    SkillError,
)
from skill.utils import to_dict


@dataclass(slots=True)
class CareerAnalysisReport:
    """Combined results from the four public career Skill capabilities."""

    resume_analysis: ResumeAnalysisResult
    improvement: ResumeImprovementResult
    job_match: JobMatchResult
    career_advice: CareerAdviceResult

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this report."""
        return to_dict(self)


@dataclass(slots=True)
class ApplicationResponse:
    """Application-layer outcome for an end-to-end career analysis."""

    success: bool
    result: CareerAnalysisReport | None = None
    error_code: str | None = None
    failed_step: str | None = None
    message: str | None = None
    error: SkillError | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this response."""
        if self.success:
            return {"success": True, "result": to_dict(self.result)}

        return {
            "success": False,
            "error_code": self.error_code,
            "failed_step": self.failed_step,
            "message": self.message,
            "error": to_dict(self.error),
        }


__all__ = ["ApplicationResponse", "CareerAnalysisReport"]
