"""Provider-neutral public Skill API response schemas."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SkillError:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SkillResponse:
    success: bool
    capability: str
    result: Any | None = None
    error: SkillError | None = None
