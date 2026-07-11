"""Feature controls supplied by the application layer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIFeaturePolicy:
    """Control optional AI and enhancement availability."""

    enabled: bool = True
    enhancement_enabled: bool = True
