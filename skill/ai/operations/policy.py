"""Pure runtime policy data for an optional AI provider request."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderRuntimePolicy:
    """Define provider request controls without credentials or network work."""

    enabled: bool = True
    timeout: float | None = None
    max_retries: int = 0
    fallback_enabled: bool = True
