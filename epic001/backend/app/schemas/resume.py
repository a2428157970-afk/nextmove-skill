from typing import Literal

from pydantic import BaseModel, Field


class PersonalInformation(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class ExperienceEntry(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    highlights: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    personal_information: PersonalInformation = Field(
        default_factory=PersonalInformation
    )
    summary: str | None = None
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    raw_text: str = ""


class ResumeParseMetadata(BaseModel):
    filename: str
    size: int
    parser: Literal["rule_based_v1"] = "rule_based_v1"


class ResumeParseResponse(BaseModel):
    success: Literal[True] = True
    profile: ResumeProfile
    metadata: ResumeParseMetadata


class ResumeErrorResponse(BaseModel):
    success: Literal[False] = False
    code: str
    message: str
