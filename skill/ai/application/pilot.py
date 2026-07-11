"""Content-safe records for opt-in real-provider quality pilots."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class AIPilotReviewRecord:
    """Review metadata only; never retain prompts, resumes, credentials, or output."""

    case_id: str
    contract_version: str
    provider_name: str
    model_name: str
    success: bool
    latency: float
    output_length: int
    validator_passed: bool
    reviewer_status: str = "pending"
    reviewer_notes: str = ""
    reviewer: str = ""
    reviewed_at: str | None = None
    quality_rating: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AIPilotRun:
    run_id: str
    started_at: str
    completed_at: str | None
    environment: str
    provider_name: str
    model_name: str
    case_count: int
    success_count: int
    failure_count: int
    validator_pass_count: int
    status: str

    def to_dict(self) -> dict:
        return asdict(self)
