from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def analyze_resume(self, resume: Any) -> Any:
        """Analyze a resume without exposing provider-specific details."""

    @abstractmethod
    def analyze_job(self, job: Any) -> Any:
        """Analyze a job without exposing provider-specific details."""

    @abstractmethod
    def career_advice(self, career_profile: Any) -> Any:
        """Produce career advice through a provider-neutral contract."""
