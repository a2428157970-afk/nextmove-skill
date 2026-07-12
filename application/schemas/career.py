"""Career-analysis application response schemas."""

from dataclasses import dataclass

from application.schemas.execution import ExecutionMetadata
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
    metadata: ExecutionMetadata | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this response."""
        if self.success:
            response = {"success": True, "result": to_dict(self.result)}
        else:
            response = {
                "success": False,
                "error_code": self.error_code,
                "failed_step": self.failed_step,
                "message": self.message,
                "error": to_dict(self.error),
            }

        if self.metadata is not None:
            response["metadata"] = self.metadata.to_dict()

        return response


__all__ = ["ApplicationResponse", "CareerAnalysisReport"]
