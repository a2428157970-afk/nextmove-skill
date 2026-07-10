"""Provider-neutral resume analysis for Skill Core."""

import re

from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment
from skill.schemas.resume import ResumeProfile

TECHNICAL_KEYWORDS = {
    "api",
    "aws",
    "azure",
    "docker",
    "fastapi",
    "flask",
    "gcp",
    "java",
    "javascript",
    "kubernetes",
    "python",
    "react",
    "sql",
    "typescript",
}
MIN_STRONG_SKILL_COUNT = 5


class ResumeAnalyzer:
    """Rule-based analyzer that works only with structured resume profiles."""

    def analyze(self, profile: ResumeProfile) -> ResumeAnalysisResult:
        strengths: list[str] = []
        weaknesses: list[str] = []
        skill_strengths: list[str] = []
        skill_gaps: list[str] = []

        if profile.summary:
            strengths.append("Resume includes a clear summary.")
        else:
            weaknesses.append("Resume is missing a summary.")

        if not profile.skills:
            weaknesses.append("Resume is missing a skills section.")
            skill_gaps.append("Add a skills section with relevant tools and domains.")
        elif len(profile.skills) < MIN_STRONG_SKILL_COUNT:
            weaknesses.append("Skills section is present but limited.")
            skill_gaps.append("Expand the skills section with more relevant keywords.")
        else:
            strengths.append("Resume lists a solid set of skills.")

        if self._has_technical_keywords(profile):
            strengths.append("Resume includes relevant technical keywords.")
            skill_strengths.append("Technical keywords are visible in the profile.")

        if profile.experience:
            strengths.append("Resume includes work experience.")
        else:
            weaknesses.append("Resume is missing work experience.")

        if profile.projects:
            strengths.append("Resume includes project experience.")
        else:
            weaknesses.append("Resume is missing project experience.")

        if profile.experience and not self._has_quantified_impact(profile):
            weaknesses.append("Experience does not show quantified outcomes.")

        return ResumeAnalysisResult(
            strengths=strengths,
            weaknesses=weaknesses,
            skill_assessment=SkillAssessment(
                strengths=skill_strengths,
                gaps=skill_gaps,
            ),
            career_level=self._career_level(profile),
        )

    @staticmethod
    def _career_level(profile: ResumeProfile) -> str:
        experience_count = len(profile.experience)
        if experience_count == 0:
            return "unknown"
        if experience_count == 1:
            return "junior"
        if experience_count == 2:
            return "mid"
        return "senior"

    @staticmethod
    def _has_quantified_impact(profile: ResumeProfile) -> bool:
        return any(
            re.search(r"\d", highlight)
            for experience in profile.experience
            for highlight in experience.highlights
        )

    @staticmethod
    def _has_technical_keywords(profile: ResumeProfile) -> bool:
        values = [
            profile.summary or "",
            profile.raw_text,
            *profile.skills,
            *(
                technology
                for project in profile.projects
                for technology in project.technologies
            ),
        ]
        words = {
            word.lower()
            for value in values
            for word in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]*", value)
        }
        return bool(words & TECHNICAL_KEYWORDS)
