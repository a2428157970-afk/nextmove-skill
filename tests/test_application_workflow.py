import json
import unittest

from application.schemas.career import ApplicationResponse, CareerAnalysisReport
from skill.schemas import (
    CareerAdviceResult,
    JobMatchResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
    SkillError,
)


class ApplicationWorkflowTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
