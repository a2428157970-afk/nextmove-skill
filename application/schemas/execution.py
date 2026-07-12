"""Execution lifecycle metadata owned by the application layer."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal


ExecutionStatus = Literal["started", "completed", "failed"]
_VALID_STATUSES = frozenset(("started", "completed", "failed"))


@dataclass(frozen=True, slots=True)
class ExecutionMetadata:
    """Immutable metadata describing one workflow execution lifecycle."""

    execution_id: str
    workflow_name: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: datetime | None = None
    failed_step: str | None = None

    def __post_init__(self) -> None:
        """Validate status, UTC timestamps, and lifecycle invariants."""
        if self.status not in _VALID_STATUSES:
            raise ValueError("status must be started, completed, or failed")

        self._validate_utc_datetime("started_at", self.started_at)
        if self.completed_at is not None:
            self._validate_utc_datetime("completed_at", self.completed_at)
            if self.completed_at < self.started_at:
                raise ValueError("completed_at cannot be before started_at")

        if self.status == "started":
            if self.completed_at is not None or self.failed_step is not None:
                raise ValueError("started executions cannot have completion metadata")
        elif self.status == "completed":
            if self.completed_at is None or self.failed_step is not None:
                raise ValueError("completed executions require completion only")
        elif self.completed_at is None or self.failed_step is None:
            raise ValueError("failed executions require completion and failed_step")

    @staticmethod
    def _validate_utc_datetime(name: str, value: datetime) -> None:
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError(f"{name} must be an aware UTC datetime")
        if value.utcoffset() != timedelta(0):
            raise ValueError(f"{name} must be an aware UTC datetime")

    def to_dict(self) -> dict[str, str | None]:
        """Return the fixed JSON-safe representation of this metadata."""
        return {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow_name,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at is not None else None
            ),
            "failed_step": self.failed_step,
        }


__all__ = ["ExecutionMetadata", "ExecutionStatus"]
