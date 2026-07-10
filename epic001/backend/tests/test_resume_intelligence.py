import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app.main import app
from app.resume.extractor import PdfTextExtractor, ResumeExtractionError
from app.resume.parser import RuleBasedResumeParser
from app.resume.service import ResumeAnalysisService
from tests.pdf_samples import text_pdf


class PdfTextExtractorTests(unittest.TestCase):
    def test_extracts_and_normalizes_text_pdf(self):
        content = text_pdf("Ada Lovelace   ada@example.com")

        text = PdfTextExtractor().extract(content)

        self.assertEqual(text, "Ada Lovelace ada@example.com")

    def test_rejects_pdf_without_readable_text(self):
        with self.assertRaisesRegex(
            ResumeExtractionError,
            "No readable text was found",
        ):
            PdfTextExtractor().extract(text_pdf("   "))


class RuleBasedResumeParserTests(unittest.TestCase):
    def test_extracts_email_and_url_without_inventing_fields(self):
        text = (
            "Ada Lovelace\nada@example.com\n"
            "https://example.com/ada\n\nSkills\nPython, SQL"
        )

        profile = RuleBasedResumeParser().parse(text)

        self.assertEqual(profile.personal_information.name, "Ada Lovelace")
        self.assertEqual(profile.personal_information.email, "ada@example.com")
        self.assertEqual(
            profile.personal_information.links,
            ["https://example.com/ada"],
        )
        self.assertEqual(profile.skills, ["Python", "SQL"])
        self.assertIsNone(profile.personal_information.phone)
        self.assertEqual(profile.raw_text, text)


class ResumeParseApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        service = ResumeAnalysisService(
            upload_directory=Path(self.temporary_directory.name)
        )
        app.state.resume_analysis_service = service
        self.client = TestClient(app)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_returns_structured_profile_and_saves_pdf(self):
        content = text_pdf("Ada Lovelace ada@example.com")

        response = self.client.post(
            "/api/resumes/parse",
            files={"file": ("resume.pdf", content, "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(
            body["profile"]["personal_information"]["email"],
            "ada@example.com",
        )
        self.assertEqual(body["metadata"]["parser"], "rule_based_v1")
        self.assertEqual(body["metadata"]["size"], len(content))
        self.assertTrue((Path(self.temporary_directory.name) / "resume.pdf").exists())

    def test_rejects_non_pdf(self):
        response = self.client.post(
            "/api/resumes/parse",
            files={"file": ("resume.txt", b"hello", "text/plain")},
        )

        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.json()["code"], "UNSUPPORTED_FILE_TYPE")

    def test_rejects_empty_file(self):
        response = self.client.post(
            "/api/resumes/parse",
            files={"file": ("resume.pdf", b"", "application/pdf")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "EMPTY_FILE")

    def test_rejects_pdf_over_ten_megabytes(self):
        response = self.client.post(
            "/api/resumes/parse",
            files={
                "file": (
                    "resume.pdf",
                    b"x" * (10 * 1024 * 1024 + 1),
                    "application/pdf",
                )
            },
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["code"], "FILE_TOO_LARGE")

    def test_rejects_invalid_pdf_without_leaking_exception(self):
        response = self.client.post(
            "/api/resumes/parse",
            files={"file": ("resume.pdf", b"not a pdf", "application/pdf")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "INVALID_PDF")
        self.assertNotIn("Traceback", response.text)

    def test_rejects_pdf_without_extractable_text(self):
        response = self.client.post(
            "/api/resumes/parse",
            files={"file": ("resume.pdf", text_pdf(""), "application/pdf")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "NO_TEXT_EXTRACTED")


if __name__ == "__main__":
    unittest.main()
