from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.resume.errors import ResumeParseError
from app.resume.service import (
    MAX_FILE_SIZE,
    ResumeAnalysisService,
    ResumeUploadService,
)
from app.schemas.resume import ResumeParseResponse
from app.schemas.upload import UploadResponse

router = APIRouter(tags=["resume"])
upload_service = ResumeUploadService()
analysis_service = ResumeAnalysisService()


@router.post("/upload", response_model=UploadResponse)
def upload_resume(file: UploadFile = File(...)) -> UploadResponse:
    return upload_service.save(file)


@router.post(
    "/api/resumes/parse",
    response_model=ResumeParseResponse,
    responses={400: {}, 413: {}, 415: {}, 422: {}},
)
async def parse_resume(
    request: Request,
    file: UploadFile = File(...),
) -> ResumeParseResponse | JSONResponse:
    content = await file.read(MAX_FILE_SIZE + 1)
    service = getattr(request.app.state, "resume_analysis_service", analysis_service)
    try:
        return service.parse(file.filename or "resume.pdf", content)
    except ResumeParseError as error:
        return JSONResponse(
            status_code=error.status_code,
            content=error.as_response(),
        )
