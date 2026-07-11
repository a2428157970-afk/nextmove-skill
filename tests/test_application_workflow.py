import ast
import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from application.schemas import CareerAnalysisRequest
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


PUBLIC_SKILL_IMPORT_MODULES = ("skill", "skill.schemas", "skill.utils")


def find_nonpublic_skill_imports(source_files: list[tuple[Path, str]]) -> list[str]:
    forbidden_imports = []

    for source_file, source in source_files:
        source_lines = source.splitlines()
        for node in ast.walk(ast.parse(source, filename=str(source_file))):
            if isinstance(node, ast.Import):
                imported_modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules = [node.module]
            else:
                continue

            for module in imported_modules:
                is_public_skill_import = module in PUBLIC_SKILL_IMPORT_MODULES or module.startswith(
                    ("skill.schemas.", "skill.utils.")
                )
                is_skill_import = module == "skill" or module.startswith("skill.")
                if is_skill_import and not is_public_skill_import:
                    line = source_lines[node.lineno - 1].strip()
                    forbidden_imports.append(
                        f"{source_file.as_posix()}:{node.lineno}: {line}"
                    )

    return forbidden_imports


class ApplicationWorkflowTests(unittest.TestCase):
    def test_service_delegates_valid_request_to_workflow(self):
        expected_response = Mock(spec=ApplicationResponse)
        workflow = Mock()
        workflow.run.return_value = expected_response

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume="resume", job_description="job")
        )

        workflow.run.assert_called_once_with("resume", "job")
        self.assertIs(response, expected_response)

    def test_service_normalizes_missing_job_description_before_workflow(self):
        expected_response = Mock(spec=ApplicationResponse)
        workflow = Mock()
        workflow.run.return_value = expected_response

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume="resume")
        )

        workflow.run.assert_called_once_with("resume", "")
        self.assertIs(response, expected_response)

    def test_service_returns_validation_error_without_calling_workflow(self):
        workflow = Mock()

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume=" \t")
        )

        workflow.run.assert_not_called()
        self.assertFalse(response.success)
        self.assertEqual(response.error_code, "APPLICATION_VALIDATION_ERROR")
        self.assertEqual(response.failed_step, "request_validation")
        self.assertEqual(response.message, "resume must not be empty")
        self.assertEqual(response.error.code, "APPLICATION_VALIDATION_ERROR")
        self.assertEqual(response.error.message, "resume must not be empty")

    def test_service_passes_workflow_failure_response_through_unchanged(self):
        expected_response = ApplicationResponse(
            success=False,
            error_code="WORKFLOW_STEP_FAILED",
            failed_step="match_job",
            message="career analysis workflow failed",
            error=SkillError(code="INVALID_INPUT", message="bad job"),
        )
        workflow = Mock()
        workflow.run.return_value = expected_response

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume="resume", job_description="job")
        )

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

    def test_static_scan_rejects_direct_skill_implementation_imports(self):
        source_file = Path("application/example.py")
        source = "from skill.analysis import ResumeAnalyzer\n"

        forbidden_imports = find_nonpublic_skill_imports([(source_file, source)])

        self.assertEqual(
            forbidden_imports,
            ["application/example.py:1: from skill.analysis import ResumeAnalyzer"],
        )

    def test_application_imports_only_public_skill_interfaces(self):
        application_root = Path(__file__).resolve().parents[1] / "application"
        source_files = [
            (source_file, source_file.read_text(encoding="utf-8"))
            for source_file in application_root.rglob("*.py")
        ]

        self.assertEqual(find_nonpublic_skill_imports(source_files), [])

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

        self.assertEqual(
            serialized,
            {
                "success": True,
                "result": response.result.to_dict(),
            },
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

        self.assertEqual(
            serialized,
            {
                "success": False,
                "error_code": "INVALID_INPUT",
                "failed_step": "job_match",
                "message": "job required",
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "job required",
                    "details": {},
                },
            },
        )
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

    def test_workflow_normalizes_none_job_description_for_match_job(self):
        skill = Mock()
        skill.run.side_effect = [
            SkillResponse(True, "analyze_resume", result=ResumeAnalysisResult()),
            SkillResponse(True, "improve_resume", result=ResumeImprovementResult()),
            SkillResponse(True, "match_job", result=JobMatchResult()),
            SkillResponse(True, "career_advice", result=CareerAdviceResult()),
        ]

        CareerAnalysisWorkflow(skill).run("resume", None)

        self.assertEqual(
            [call.args[0] for call in skill.run.call_args_list],
            ["analyze_resume", "improve_resume", "match_job", "career_advice"],
        )
        self.assertEqual(
            skill.run.call_args_list[2].args[1],
            {"resume": "resume", "job_description": ""},
        )

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
