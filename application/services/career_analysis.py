"""Thin service entry point for end-to-end career analysis."""

from application.schemas import ApplicationResponse, CareerAnalysisRequest
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

        return self.workflow.run(request.resume, request.normalized_job_description())
