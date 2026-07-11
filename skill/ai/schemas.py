"""Structured schemas for optional AI enhancement results."""

from dataclasses import dataclass


@dataclass(slots=True)
class AIEnhancementResult:
    """The outcome of an optional enhancement request."""

    success: bool
    enhanced_content: str | None = None
    error: str | None = None
