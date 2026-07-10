import shutil
from pathlib import Path

from fastapi import UploadFile

from app.resume.errors import ResumeParseError
from app.resume.extractor import PdfTextExtractor
from app.resume.parser import RuleBasedResumeParser
from app.schemas.resume import ResumeParseMetadata, ResumeParseResponse
from app.schemas.upload import UploadResponse

DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024


class ResumeUploadService:
    def __init__(self, upload_directory: Path = DEFAULT_UPLOAD_DIR) -> None:
        self._upload_directory = upload_directory

    def save(self, file: UploadFile) -> UploadResponse:
        self._upload_directory.mkdir(parents=True, exist_ok=True)
        filename = Path(file.filename or "upload").name
        destination = self._upload_directory / filename

        with destination.open("wb") as output:
            shutil.copyfileobj(file.file, output)

        return UploadResponse(
            success=True,
            filename=filename,
            size=destination.stat().st_size,
        )


class ResumeAnalysisService:
    def __init__(
        self,
        upload_directory: Path = DEFAULT_UPLOAD_DIR,
        extractor: PdfTextExtractor | None = None,
        parser: RuleBasedResumeParser | None = None,
    ) -> None:
        self._upload_directory = upload_directory
        self._extractor = extractor or PdfTextExtractor()
        self._parser = parser or RuleBasedResumeParser()

    def parse(self, filename: str, content: bytes) -> ResumeParseResponse:
        safe_filename = Path(filename or "resume.pdf").name
        if Path(safe_filename).suffix.lower() != ".pdf":
            raise ResumeParseError(
                "UNSUPPORTED_FILE_TYPE",
                "Only PDF files can be analyzed.",
                415,
            )
        if not content:
            raise ResumeParseError(
                "EMPTY_FILE",
                "The uploaded PDF is empty.",
                400,
            )
        if len(content) > MAX_FILE_SIZE:
            raise ResumeParseError(
                "FILE_TOO_LARGE",
                "File size must be 10 MB or less.",
                413,
            )

        self._upload_directory.mkdir(parents=True, exist_ok=True)
        (self._upload_directory / safe_filename).write_bytes(content)
        text = self._extractor.extract(content)
        return ResumeParseResponse(
            profile=self._parser.parse(text),
            metadata=ResumeParseMetadata(
                filename=safe_filename,
                size=len(content),
            ),
        )
