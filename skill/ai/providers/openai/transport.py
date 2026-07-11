"""Minimal injected HTTP transport protocol for OpenAI-compatible adapters."""

from typing import Protocol


class HTTPTransport(Protocol):
    """Execute an HTTP POST supplied by the external application layer."""

    def post(
        self,
        path: str,
        headers: dict[str, str],
        body: dict,
        timeout: float | None,
    ) -> dict:
        """Return a decoded JSON-compatible response object."""
