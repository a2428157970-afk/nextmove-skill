"""Thin service entry point for end-to-end career analysis."""

from typing import Any

from application.schemas import ApplicationResponse
from application.workflows import CareerAnalysisWorkflow
from skill import NextMoveSkill


class CareerAnalysisService:
    """Delegate career-analysis requests to the application workflow."""

    def __init__(
        self,
        skill: NextMoveSkill | None = None,
        workflow: CareerAnalysisWorkflow | None = None,
    ):
        self.workflow = workflow or CareerAnalysisWorkflow(skill or NextMoveSkill())

    def analyze(
        self, resume: Any, job_description: str | None = None
    ) -> ApplicationResponse:
        """Run career analysis through the configured workflow."""
        return self.workflow.run(resume, job_description)
