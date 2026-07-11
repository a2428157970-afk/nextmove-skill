"""Stable provider failure contracts for the AI enhancement boundary."""


class ProviderUnavailableError(Exception):
    """Raised when a provider cannot be used for a request."""


class ProviderTimeoutError(Exception):
    """Raised when a provider request exceeds its external timeout."""


class ProviderResponseError(Exception):
    """Raised when a provider returns an unusable response."""
