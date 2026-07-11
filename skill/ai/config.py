"""Provider configuration data without environment or credential management."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIProviderConfig:
    """Declarative configuration supplied by the application layer."""

    provider_name: str
    model_name: str
    metadata: dict[str, Any] = field(default_factory=dict)
