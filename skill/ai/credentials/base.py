"""Credential boundary without storage, environment access, or lifecycle logic."""

from abc import ABC, abstractmethod


class CredentialProvider(ABC):
    """Supply an opaque credential value from an external application boundary."""

    @abstractmethod
    def get_credentials(self, provider_name: str) -> object | None:
        """Return external credentials for a provider, or None when unavailable."""
