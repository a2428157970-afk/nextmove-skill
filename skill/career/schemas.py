"""Provider-neutral career advice schema."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class CareerAdviceResult:
    current_level: str = "unknown"
    possible_paths: list[str] = field(default_factory=list)
    skill_gaps: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
