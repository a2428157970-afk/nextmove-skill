import unittest

from application.schemas import CareerAnalysisRequest
from skill.schemas import ResumeProfile


class CareerAnalysisRequestTests(unittest.TestCase):
    def test_validates_non_empty_string_resume(self):
        request = CareerAnalysisRequest(
            resume="Experienced Python engineer", job_description="Backend engineer"
        )

        request.validate()

        self.assertEqual(request.normalized_job_description(), "Backend engineer")

    def test_validates_resume_profile(self):
        request = CareerAnalysisRequest(resume=ResumeProfile())

        request.validate()

    def test_rejects_empty_string_resume(self):
        request = CareerAnalysisRequest(resume="")

        with self.assertRaisesRegex(ValueError, "^resume must not be empty$"):
            request.validate()

    def test_rejects_whitespace_only_string_resume(self):
        request = CareerAnalysisRequest(resume=" \t\n ")

        with self.assertRaisesRegex(ValueError, "^resume must not be empty$"):
            request.validate()

    def test_rejects_invalid_resume_type(self):
        request = CareerAnalysisRequest(resume=object())

        with self.assertRaisesRegex(
            ValueError, "^resume must be a ResumeProfile or str$"
        ):
            request.validate()

    def test_rejects_invalid_job_description_type(self):
        request = CareerAnalysisRequest(resume="resume", job_description=object())

        with self.assertRaisesRegex(
            ValueError, "^job_description must be a str or None$"
        ):
            request.validate()

    def test_normalizes_only_none_job_description_to_empty_string(self):
        self.assertEqual(
            CareerAnalysisRequest(resume="resume").normalized_job_description(), ""
        )
        self.assertEqual(
            CareerAnalysisRequest(resume="resume", job_description="  ").normalized_job_description(),
            "  ",
        )


if __name__ == "__main__":
    unittest.main()
