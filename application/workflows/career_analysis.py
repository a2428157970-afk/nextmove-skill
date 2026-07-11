"""Fail-fast career-analysis workflow through the public Skill API."""

from typing import Any

from application.schemas import ApplicationResponse, CareerAnalysisReport
from skill import NextMoveSkill
from skill.schemas import SkillResponse


class CareerAnalysisWorkflow:
    """Orchestrate the four public career Skill capabilities."""

    def __init__(self, skill: NextMoveSkill):
        self.skill = skill

    def run(
        self, resume: Any, job_description: str | None = None
    ) -> ApplicationResponse:
        """Run the fixed career-analysis sequence, stopping at first failure."""
        analysis_response = self.skill.run("analyze_resume", {"resume": resume})
        failure = self._failure_response(analysis_response, "analyze_resume")
        if failure is not None:
            return failure

        improvement_response = self.skill.run("improve_resume", {"resume": resume})
        failure = self._failure_response(improvement_response, "improve_resume")
        if failure is not None:
            return failure

        match_response = self.skill.run(
            "match_job",
            {"resume": resume, "job_description": job_description},
        )
        failure = self._failure_response(match_response, "match_job")
        if failure is not None:
            return failure

        advice_response = self.skill.run(
            "career_advice",
            {"resume": resume, "analysis": analysis_response.result},
        )
        failure = self._failure_response(advice_response, "career_advice")
        if failure is not None:
            return failure

        return ApplicationResponse(
            success=True,
            result=CareerAnalysisReport(
                resume_analysis=analysis_response.result,
                improvement=improvement_response.result,
                job_match=match_response.result,
                career_advice=advice_response.result,
            ),
        )

    @staticmethod
    def _failure_response(
        response: SkillResponse, capability: str
    ) -> ApplicationResponse | None:
        if response.success:
            return None

        return ApplicationResponse(
            success=False,
            error_code="WORKFLOW_STEP_FAILED",
            failed_step=capability,
            message="career analysis workflow failed",
            error=response.error,
            result=None,
        )
