import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.main import app
from app.providers.base import AIProvider
from app.resume.service import ResumeUploadService


class UploadRouteTests(unittest.TestCase):
    def test_upload_route_is_registered(self):
        self.assertIn("post", app.openapi()["paths"]["/upload"])

    def test_cors_allows_local_frontend(self):
        cors_middleware = [
            middleware
            for middleware in app.user_middleware
            if middleware.cls is CORSMiddleware
        ]

        self.assertEqual(len(cors_middleware), 1)
        self.assertIn(
            "http://localhost:3000",
            cors_middleware[0].kwargs["allow_origins"],
        )
        self.assertIn(
            "http://127.0.0.1:3000",
            cors_middleware[0].kwargs["allow_origins"],
        )

    def test_upload_saves_file_and_returns_metadata(self):
        content = b"resume content"

        with TemporaryDirectory() as temporary_directory:
            upload_directory = Path(temporary_directory)
            upload = UploadFile(
                file=BytesIO(content),
                filename="resume.pdf",
            )

            response = ResumeUploadService(upload_directory).save(upload)

            self.assertEqual(
                response.model_dump(),
                {
                    "success": True,
                    "filename": "resume.pdf",
                    "size": len(content),
                },
            )
            self.assertEqual(
                (upload_directory / "resume.pdf").read_bytes(),
                content,
            )


class ProviderContractTests(unittest.TestCase):
    def test_provider_contract_exposes_career_intelligence_operations(self):
        self.assertTrue(hasattr(AIProvider, "analyze_resume"))
        self.assertTrue(hasattr(AIProvider, "analyze_job"))
        self.assertTrue(hasattr(AIProvider, "career_advice"))


if __name__ == "__main__":
    unittest.main()
