"""Provider-neutral resume profile schema."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class PersonalInformation:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = field(default_factory=list)


BasicInformation = PersonalInformation


@dataclass(slots=True)
class EducationEntry:
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


@dataclass(slots=True)
class ExperienceEntry:
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    highlights: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectEntry:
    name: str | None = None
    description: str | None = None
    technologies: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CertificationEntry:
    name: str
    issuer: str | None = None
    issued_date: str | None = None
    expires_date: str | None = None


@dataclass(slots=True)
class ResumeProfile:
    personal_information: PersonalInformation = field(
        default_factory=PersonalInformation
    )
    summary: str | None = None
    education: list[EducationEntry] = field(default_factory=list)
    experience: list[ExperienceEntry] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    projects: list[ProjectEntry] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    raw_text: str = ""
