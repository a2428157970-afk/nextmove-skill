"""Non-sensitive observation metadata for an AI execution."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIExecutionMetadata:
    """Record execution facts without prompts, credentials, or user data."""

    request_id: str
    provider_name: str
    model_name: str
    latency: float
    status: str
