from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    filename: str
    size: int
