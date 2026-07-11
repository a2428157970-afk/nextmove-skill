"""Non-sensitive metadata for correlating an AI enhancement request."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIRequestContext:
    """Describe a request without storing prompts, credentials, or user data."""

    provider_name: str
    model_name: str
    capability: str
    request_id: str
