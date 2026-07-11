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

    def to_dict(self) -> dict:
        return asdict(self)
