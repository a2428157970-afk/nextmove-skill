"""Provider-neutral resume improvement schema."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ResumeImprovementResult:
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    improved_sections: dict[str, list[str]] = field(default_factory=dict)
