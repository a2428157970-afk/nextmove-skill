"""Request schemas for the application boundary."""

from dataclasses import dataclass

from skill.schemas.resume import ResumeProfile


@dataclass(slots=True)
class CareerAnalysisRequest:
    """Input accepted by the career-analysis application workflow."""

    resume: ResumeProfile | str
    job_description: str | None = None

    def validate(self) -> None:
        """Validate input types and required string content."""
        if not isinstance(self.resume, (ResumeProfile, str)):
            raise ValueError("resume must be a ResumeProfile or str")
        if isinstance(self.resume, str) and not self.resume.strip():
            raise ValueError("resume must not be empty")
        if not isinstance(self.job_description, (str, type(None))):
            raise ValueError("job_description must be a str or None")

    def normalized_job_description(self) -> str:
        """Return the job description in the string form required downstream."""
        return "" if self.job_description is None else self.job_description


__all__ = ["CareerAnalysisRequest"]
