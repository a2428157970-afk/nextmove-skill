"""Tests for application execution metadata."""

import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import Mock

from application.schemas import (
    ApplicationResponse,
    CareerAnalysisRequest,
    ExecutionMetadata,
)
from application.schemas.career import CareerAnalysisReport
from application.services import CareerAnalysisService
from skill.schemas import (
    CareerAdviceResult,
    JobMatchResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
    SkillError,
)


UTC = timezone.utc
STARTED_AT = datetime(2026, 7, 11, 10, 0, tzinfo=UTC)
COMPLETED_AT = datetime(2026, 7, 11, 10, 5, tzinfo=UTC)


class ExecutionMetadataTests(unittest.TestCase):
    def test_started_metadata_serializes_to_json_safe_isoformat_payload(self):
        metadata = ExecutionMetadata(
            execution_id="execution-123",
            workflow_name="career-analysis",
            status="started",
            started_at=STARTED_AT,
        )

        payload = metadata.to_dict()

        self.assertEqual(
            payload,
            {
                "execution_id": "execution-123",
                "workflow_name": "career-analysis",
                "status": "started",
                "started_at": "2026-07-11T10:00:00+00:00",
                "completed_at": None,
                "failed_step": None,
            },
        )
        self.assertEqual(json.loads(json.dumps(payload)), payload)

    def test_completed_metadata_serializes_completion_as_isoformat(self):
        metadata = ExecutionMetadata(
            execution_id="execution-123",
            workflow_name="career-analysis",
            status="completed",
            started_at=STARTED_AT,
            completed_at=COMPLETED_AT,
        )

        self.assertEqual(
            metadata.to_dict()["completed_at"], "2026-07-11T10:05:00+00:00"
        )

    def test_failed_metadata_requires_and_preserves_failed_step(self):
        metadata = ExecutionMetadata(
            execution_id="execution-123",
            workflow_name="career-analysis",
            status="failed",
            started_at=STARTED_AT,
            completed_at=COMPLETED_AT,
            failed_step="job_match",
        )

        self.assertEqual(metadata.to_dict()["failed_step"], "job_match")

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata("execution-123", "career-analysis", "pending", STARTED_AT)

    def test_rejects_naive_datetime(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "started",
                datetime(2026, 7, 11, 10, 0),
            )

    def test_rejects_non_utc_datetime(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "started",
                datetime(2026, 7, 11, 18, 0, tzinfo=timezone(timedelta(hours=8))),
            )

    def test_rejects_naive_completed_at_for_completed_and_failed_lifecycles(self):
        for status, failed_step in (("completed", None), ("failed", "job_match")):
            with self.subTest(status=status):
                with self.assertRaises(ValueError):
                    ExecutionMetadata(
                        "execution-123",
                        "career-analysis",
                        status,
                        STARTED_AT,
                        completed_at=datetime(2026, 7, 11, 10, 5),
                        failed_step=failed_step,
                    )

    def test_rejects_non_utc_completed_at_for_completed_and_failed_lifecycles(
        self,
    ):
        non_utc_completion = datetime(
            2026,
            7,
            11,
            18,
            5,
            tzinfo=timezone(timedelta(hours=8)),
        )
        for status, failed_step in (("completed", None), ("failed", "job_match")):
            with self.subTest(status=status):
                with self.assertRaises(ValueError):
                    ExecutionMetadata(
                        "execution-123",
                        "career-analysis",
                        status,
                        STARTED_AT,
                        completed_at=non_utc_completion,
                        failed_step=failed_step,
                    )

    def test_metadata_is_frozen_and_slot_based(self):
        metadata = ExecutionMetadata(
            "execution-123", "career-analysis", "started", STARTED_AT
        )

        self.assertEqual(
            set(ExecutionMetadata.__slots__),
            {
                "execution_id",
                "workflow_name",
                "status",
                "started_at",
                "completed_at",
                "failed_step",
            },
        )
        with self.assertRaises(FrozenInstanceError):
            metadata.status = "completed"

    def test_started_rejects_completion_or_failed_step(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "started",
                STARTED_AT,
                completed_at=COMPLETED_AT,
            )
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "started",
                STARTED_AT,
                failed_step="job_match",
            )

    def test_completed_requires_completion_and_rejects_failed_step(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata("execution-123", "career-analysis", "completed", STARTED_AT)
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "completed",
                STARTED_AT,
                completed_at=COMPLETED_AT,
                failed_step="job_match",
            )

    def test_failed_requires_completion_and_failed_step(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata("execution-123", "career-analysis", "failed", STARTED_AT)
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "failed",
                STARTED_AT,
                completed_at=COMPLETED_AT,
            )

    def test_rejects_completion_before_start(self):
        with self.assertRaises(ValueError):
            ExecutionMetadata(
                "execution-123",
                "career-analysis",
                "completed",
                STARTED_AT,
                completed_at=datetime(2026, 7, 11, 9, 59, tzinfo=UTC),
            )


class CareerAnalysisServiceExecutionMetadataTests(unittest.TestCase):
    def test_successful_execution_returns_completed_utc_metadata(self):
        workflow = Mock()
        expected_result = CareerAnalysisReport(
            resume_analysis=ResumeAnalysisResult(),
            improvement=ResumeImprovementResult(),
            job_match=JobMatchResult(),
            career_advice=CareerAdviceResult(),
        )
        workflow.run.return_value = ApplicationResponse(
            success=True,
            result=expected_result,
        )

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume="resume", job_description="job")
        )

        workflow.run.assert_called_once_with("resume", "job")
        self.assertTrue(response.success)
        self.assertIs(response.result, expected_result)
        self.assertIsNotNone(response.metadata)
        self.assertTrue(response.metadata.execution_id)
        self.assertEqual(response.metadata.workflow_name, "career_analysis")
        self.assertEqual(response.metadata.status, "completed")
        self.assertIs(response.metadata.started_at.tzinfo, timezone.utc)
        self.assertIs(response.metadata.completed_at.tzinfo, timezone.utc)
        self.assertGreaterEqual(response.metadata.completed_at, response.metadata.started_at)
        self.assertIsNone(response.metadata.failed_step)
        self.assertEqual(json.loads(json.dumps(response.to_dict())), response.to_dict())

    def test_failed_execution_preserves_workflow_failed_step_in_metadata(self):
        workflow = Mock()
        workflow.run.return_value = ApplicationResponse(
            success=False,
            error_code="WORKFLOW_STEP_FAILED",
            failed_step="match_job",
            message="career analysis workflow failed",
            error=SkillError(code="INVALID_INPUT", message="bad job"),
        )

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume="resume", job_description="job")
        )

        self.assertFalse(response.success)
        self.assertEqual(response.failed_step, "match_job")
        self.assertEqual(response.metadata.status, "failed")
        self.assertEqual(response.metadata.failed_step, "match_job")

    def test_validation_failure_returns_no_metadata_and_does_not_run_workflow(self):
        workflow = Mock()

        response = CareerAnalysisService(workflow=workflow).analyze(
            CareerAnalysisRequest(resume=" \t")
        )

        workflow.run.assert_not_called()
        self.assertFalse(response.success)
        self.assertIsNone(response.metadata)


if __name__ == "__main__":
    unittest.main()
