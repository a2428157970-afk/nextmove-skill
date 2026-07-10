import re

from app.schemas.resume import (
    EducationEntry,
    ExperienceEntry,
    PersonalInformation,
    ProjectEntry,
    ResumeProfile,
)

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d ().-]{7,}\d)(?!\w)")
URL_PATTERN = re.compile(r"https?://[^\s,;]+|www\.[^\s,;]+", re.I)
SECTION_ALIASES = {
    "summary": {"summary", "profile", "professional summary"},
    "education": {"education", "academic background"},
    "experience": {"experience", "work experience", "employment"},
    "skills": {"skills", "technical skills", "core competencies"},
    "projects": {"projects", "selected projects"},
    "certifications": {"certifications", "certificates"},
    "languages": {"languages"},
}


class RuleBasedResumeParser:
    def parse(self, text: str) -> ResumeProfile:
        sections = self._sections(text)
        email = self._first(EMAIL_PATTERN, text)
        phone = self._first(PHONE_PATTERN, text)
        links = list(dict.fromkeys(URL_PATTERN.findall(text)))
        return ResumeProfile(
            personal_information=PersonalInformation(
                name=self._name(text),
                email=email,
                phone=phone,
                links=links,
            ),
            summary=self._paragraph(sections.get("summary", [])),
            education=self._education(sections.get("education", [])),
            experience=self._experience(sections.get("experience", [])),
            skills=self._list_values(sections.get("skills", [])),
            projects=self._projects(sections.get("projects", [])),
            certifications=self._list_values(sections.get("certifications", [])),
            languages=self._list_values(sections.get("languages", [])),
            raw_text=text,
        )

    @staticmethod
    def _first(pattern: re.Pattern[str], text: str) -> str | None:
        match = pattern.search(text)
        return match.group(0).strip() if match else None

    def _name(self, text: str) -> str | None:
        headings = {alias for aliases in SECTION_ALIASES.values() for alias in aliases}
        for line in text.splitlines():
            candidate = line.strip()
            if (
                candidate
                and candidate.lower().rstrip(":") not in headings
                and not EMAIL_PATTERN.search(candidate)
                and not URL_PATTERN.search(candidate)
                and not PHONE_PATTERN.fullmatch(candidate)
            ):
                return candidate
        return None

    @staticmethod
    def _sections(text: str) -> dict[str, list[str]]:
        alias_map = {
            alias: section
            for section, aliases in SECTION_ALIASES.items()
            for alias in aliases
        }
        sections: dict[str, list[str]] = {}
        current: str | None = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            heading = alias_map.get(line.lower().rstrip(":"))
            if heading:
                current = heading
                sections.setdefault(current, [])
            elif current is not None and line:
                sections[current].append(line)
        return sections

    @staticmethod
    def _paragraph(lines: list[str]) -> str | None:
        return " ".join(lines) if lines else None

    @staticmethod
    def _list_values(lines: list[str]) -> list[str]:
        values: list[str] = []
        for line in lines:
            values.extend(
                value.strip(" \t-•")
                for value in re.split(r"[,;|]", line)
                if value.strip(" \t-•")
            )
        return list(dict.fromkeys(values))

    @staticmethod
    def _education(lines: list[str]) -> list[EducationEntry]:
        return [EducationEntry(institution=lines[0])] if lines else []

    @staticmethod
    def _experience(lines: list[str]) -> list[ExperienceEntry]:
        if not lines:
            return []
        return [ExperienceEntry(role=lines[0], highlights=lines[1:])]

    @staticmethod
    def _projects(lines: list[str]) -> list[ProjectEntry]:
        if not lines:
            return []
        return [ProjectEntry(name=lines[0], description=" ".join(lines[1:]) or None)]
