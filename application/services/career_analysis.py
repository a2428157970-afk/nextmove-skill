"""Thin service entry point for end-to-end career analysis."""

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from application.schemas import (
    ApplicationResponse,
    CareerAnalysisRequest,
    ExecutionMetadata,
)
from application.workflows import CareerAnalysisWorkflow
from skill import NextMoveSkill
from skill.schemas import SkillError


class CareerAnalysisService:
    """Delegate career-analysis requests to the application workflow."""

    def __init__(
        self,
        skill: NextMoveSkill | None = None,
        workflow: CareerAnalysisWorkflow | None = None,
    ):
        self.workflow = workflow or CareerAnalysisWorkflow(skill or NextMoveSkill())

    def analyze(self, request: CareerAnalysisRequest) -> ApplicationResponse:
        """Run career analysis through the configured workflow."""
        try:
            request.validate()
        except ValueError as error:
            message = str(error)
            return ApplicationResponse(
                success=False,
                error_code="APPLICATION_VALIDATION_ERROR",
                failed_step="request_validation",
                message=message,
                error=SkillError(
                    code="APPLICATION_VALIDATION_ERROR",
                    message=message,
                ),
            )

        started_metadata = ExecutionMetadata(
            execution_id=uuid4().hex,
            workflow_name="career_analysis",
            status="started",
            started_at=datetime.now(timezone.utc),
        )
        response = self.workflow.run(
            request.resume, request.normalized_job_description()
        )
        metadata = replace(
            started_metadata,
            status="completed" if response.success else "failed",
            completed_at=datetime.now(timezone.utc),
            failed_step=None if response.success else response.failed_step,
        )
        return replace(response, metadata=metadata)
