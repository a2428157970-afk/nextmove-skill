import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import main
from app.main import app


class UploadRouteTests(unittest.TestCase):
    def test_upload_route_is_registered(self):
        upload_routes = [
            route
            for route in app.routes
            if getattr(route, "path", None) == "/upload"
            and "POST" in getattr(route, "methods", set())
        ]

        self.assertEqual(len(upload_routes), 1)

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

            with patch.object(
                main,
                "UPLOAD_DIR",
                upload_directory,
                create=True,
            ):
                response = main.upload_resume(upload)

            self.assertEqual(
                response,
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


if __name__ == "__main__":
    unittest.main()
