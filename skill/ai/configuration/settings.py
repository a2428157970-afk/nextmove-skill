"""Provider settings without credential or environment handling."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIProviderSettings:
    """Application-supplied settings for a future provider adapter."""

    provider_name: str
    model_name: str
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
