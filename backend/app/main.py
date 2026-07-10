import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"


@app.get("/")
def read_root():
    return {
        "project": "NextMove",
        "status": "running",
    }


@app.post("/upload")
def upload_resume(file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename or "upload").name
    destination = UPLOAD_DIR / filename

    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    return {
        "success": True,
        "filename": filename,
        "size": destination.stat().st_size,
    }
