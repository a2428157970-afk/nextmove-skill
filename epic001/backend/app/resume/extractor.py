import re
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.resume.errors import ResumeParseError


class ResumeExtractionError(ResumeParseError):
    pass


class PdfTextExtractor:
    def extract(self, content: bytes) -> str:
        if not content.lstrip().startswith(b"%PDF-") or b"%%EOF" not in content[-1024:]:
            raise ResumeExtractionError(
                "INVALID_PDF",
                "The uploaded PDF could not be read.",
                422,
            )
        try:
            reader = PdfReader(BytesIO(content))
            page_text = [page.extract_text() or "" for page in reader.pages]
        except (PdfReadError, ValueError, TypeError, OSError) as error:
            raise ResumeExtractionError(
                "INVALID_PDF",
                "The uploaded PDF could not be read.",
                422,
            ) from error

        text = self._normalize("\n\n".join(page_text))
        if not text:
            raise ResumeExtractionError(
                "NO_TEXT_EXTRACTED",
                "No readable text was found in this PDF.",
                422,
            )
        return text

    @staticmethod
    def _normalize(text: str) -> str:
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        normalized: list[str] = []
        for line in lines:
            if line:
                normalized.append(line)
            elif normalized and normalized[-1] != "":
                normalized.append("")
        return "\n".join(normalized).strip()
