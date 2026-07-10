from pydantic import BaseModel


class ResumeProfile(BaseModel):
    id: str


class CareerProfile(BaseModel):
    id: str


class JobProfile(BaseModel):
    id: str
