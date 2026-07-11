import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from application.schemas.career import ApplicationResponse, CareerAnalysisReport
from application.services.career_analysis import CareerAnalysisService
from application.workflows.career_analysis import CareerAnalysisWorkflow
from skill.schemas import (
    CareerAdviceResult,
    JobMatchResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
    SkillError,
    SkillResponse,
)


class ApplicationWorkflowTests(unittest.TestCase):
    def test_service_delegates_to_workflow(self):
        expected_response = Mock(spec=ApplicationResponse)
        workflow = Mock()
        workflow.run.return_value = expected_response

        response = CareerAnalysisService(workflow=workflow).analyze("resume", "job")

        workflow.run.assert_called_once_with("resume", "job")
        self.assertIs(response, expected_response)

    def test_skill_does_not_import_application_layer(self):
        skill_root = Path(__file__).resolve().parents[1] / "skill"
        forbidden_imports = []

        for source_file in skill_root.rglob("*.py"):
            for line_number, line in enumerate(
                source_file.read_text(encoding="utf-8").splitlines(), start=1
            ):
                stripped = line.strip()
                if stripped.startswith("from application") or stripped.startswith(
                    "import application"
                ):
                    forbidden_imports.append(f"{source_file}:{line_number}: {stripped}")

        self.assertEqual(forbidden_imports, [])

    def test_application_response_serializes_success_report(self):
        response = ApplicationResponse(
            success=True,
            result=CareerAnalysisReport(
                resume_analysis=ResumeAnalysisResult(strengths=["Python"]),
                improvement=ResumeImprovementResult(),
                job_match=JobMatchResult(),
                career_advice=CareerAdviceResult(),
            ),
        )

        serialized = response.to_dict()

        self.assertTrue(serialized["success"])
        self.assertEqual(
            serialized["result"]["resume_analysis"]["strengths"], ["Python"]
        )
        json.dumps(serialized)

    def test_application_response_serializes_failure_error(self):
        response = ApplicationResponse(
            success=False,
            error_code="INVALID_INPUT",
            failed_step="job_match",
            message="job required",
            error=SkillError(code="INVALID_INPUT", message="job required"),
        )

        serialized = response.to_dict()

        self.assertIsNone(serialized["result"])
        self.assertEqual(serialized["error"]["code"], "INVALID_INPUT")
        json.dumps(serialized)

    def test_workflow_calls_public_skill_api_in_fixed_order(self):
        resume = "Python engineer"
        job_description = "Backend Python engineer"
        analysis = ResumeAnalysisResult(strengths=["Python"])
        improvement = ResumeImprovementResult()
        job_match = JobMatchResult()
        career_advice = CareerAdviceResult()
        skill = Mock()
        skill.run.side_effect = [
            SkillResponse(True, "analyze_resume", result=analysis),
            SkillResponse(True, "improve_resume", result=improvement),
            SkillResponse(True, "match_job", result=job_match),
            SkillResponse(True, "career_advice", result=career_advice),
        ]

        response = CareerAnalysisWorkflow(skill).run(resume, job_description)

        self.assertTrue(response.success)
        self.assertEqual(
            [call.args[0] for call in skill.run.call_args_list],
            ["analyze_resume", "improve_resume", "match_job", "career_advice"],
        )
        self.assertEqual(
            [call.args[1] for call in skill.run.call_args_list],
            [
                {"resume": resume},
                {"resume": resume},
                {"resume": resume, "job_description": job_description},
                {"resume": resume, "analysis": analysis},
            ],
        )
        self.assertIs(response.result.resume_analysis, analysis)
        self.assertIs(response.result.improvement, improvement)
        self.assertIs(response.result.job_match, job_match)
        self.assertIs(response.result.career_advice, career_advice)

    def test_workflow_returns_first_failure_with_original_error(self):
        error = SkillError(code="INVALID_INPUT", message="bad resume")
        skill = Mock()
        skill.run.return_value = SkillResponse(
            False, "analyze_resume", error=error
        )

        response = CareerAnalysisWorkflow(skill).run("resume")

        self.assertEqual(skill.run.call_count, 1)
        self.assertFalse(response.success)
        self.assertEqual(response.error_code, "WORKFLOW_STEP_FAILED")
        self.assertEqual(response.failed_step, "analyze_resume")
        self.assertEqual(response.message, "career analysis workflow failed")
        self.assertIs(response.error, error)
        self.assertIsNone(response.result)

    def test_workflow_stops_after_match_job_failure(self):
        error = SkillError(code="INVALID_INPUT", message="bad job")
        skill = Mock()
        skill.run.side_effect = [
            SkillResponse(True, "analyze_resume", result=ResumeAnalysisResult()),
            SkillResponse(True, "improve_resume", result=ResumeImprovementResult()),
            SkillResponse(False, "match_job", error=error),
        ]

        response = CareerAnalysisWorkflow(skill).run("resume", "job")

        self.assertEqual(skill.run.call_count, 3)
        self.assertEqual(
            [call.args[0] for call in skill.run.call_args_list],
            ["analyze_resume", "improve_resume", "match_job"],
        )
        self.assertEqual(response.failed_step, "match_job")
        self.assertIs(response.error, error)
        self.assertIsNone(response.result)


if __name__ == "__main__":
    unittest.main()
