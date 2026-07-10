from fastapi import APIRouter

from app.resume.router import router as resume_router

api_router = APIRouter()


@api_router.get("/")
def read_root() -> dict[str, str]:
    return {"project": "NextMove", "status": "running"}


api_router.include_router(resume_router)
