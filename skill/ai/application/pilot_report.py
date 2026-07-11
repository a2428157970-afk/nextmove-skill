"""Content-safe aggregate reporting for pilot runs."""
from dataclasses import asdict, dataclass
from skill.ai.application.pilot import AIPilotRun, AIPilotReviewRecord

@dataclass(frozen=True, slots=True)
class PilotReport:
    run: AIPilotRun
    reviews: tuple[AIPilotReviewRecord, ...]
    def to_dict(self) -> dict:
        return {"run": asdict(self.run), "review_summary": {"pending": sum(r.reviewer_status == "pending" for r in self.reviews), "approved": sum(r.reviewer_status == "approved" for r in self.reviews), "rejected": sum(r.reviewer_status == "rejected" for r in self.reviews)}, "validation_summary": {"validator_passed": sum(r.validator_passed for r in self.reviews), "validator_failed": sum(not r.validator_passed for r in self.reviews)}}
