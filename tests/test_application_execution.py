"""Tests for application execution metadata."""

import json
from datetime import datetime, timedelta, timezone
import unittest

from application.schemas import ExecutionMetadata


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


if __name__ == "__main__":
    unittest.main()
