"""Rule-based career advice for Skill Core."""

import re

from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.resume import ResumeProfile
from skill.career.schemas import CareerAdviceResult


DATA_KEYWORDS = {"python", "sql", "data", "analytics", "analysis", "tableau"}
TECH_KEYWORDS = {"api", "backend", "docker", "fastapi", "java", "react", "typescript"}
MANAGEMENT_KEYWORDS = {"lead", "leader", "leadership", "manager", "managed", "management"}


class CareerAdvisor:
    """Generate simple career direction advice from a resume profile."""

    def advise(
        self,
        profile: ResumeProfile,
        analysis: ResumeAnalysisResult | None = None,
    ) -> CareerAdviceResult:
        current_level = self._current_level(profile, analysis)
        possible_paths = self._possible_paths(profile)
        skill_gaps = self._skill_gaps(analysis)
        recommended_actions = self._recommended_actions(profile, analysis, possible_paths)

        return CareerAdviceResult(
            current_level=current_level,
            possible_paths=possible_paths,
            skill_gaps=skill_gaps,
            recommended_actions=recommended_actions,
        )

    @staticmethod
    def _current_level(
        profile: ResumeProfile,
        analysis: ResumeAnalysisResult | None,
    ) -> str:
        if analysis is not None and analysis.career_level != "unknown":
            return analysis.career_level

        experience_count = len(profile.experience)
        if experience_count == 0:
            return "unknown"
        if experience_count == 1:
            return "junior"
        if experience_count == 2:
            return "mid"
        return "senior"

    def _possible_paths(self, profile: ResumeProfile) -> list[str]:
        words = self._profile_words(profile)
        paths: list[str] = []

        if words & DATA_KEYWORDS:
            paths.extend(["data analyst", "data engineer"])

        if words & TECH_KEYWORDS:
            paths.extend(["software engineer", "backend engineer"])

        if words & MANAGEMENT_KEYWORDS:
            paths.extend(["team lead", "engineering manager"])

        if not paths:
            paths.append("general career development")

        return self._dedupe(paths)

    @staticmethod
    def _skill_gaps(analysis: ResumeAnalysisResult | None) -> list[str]:
        if analysis is None:
            return []

        gaps = list(analysis.skill_assessment.gaps)
        for weakness in analysis.weaknesses:
            normalized = weakness.lower()
            if "skills" in normalized:
                gaps.append("Strengthen the skills section with role-relevant keywords.")
            if "summary" in normalized:
                gaps.append("Clarify career positioning in the resume summary.")
            if "quantified outcomes" in normalized:
                gaps.append("Show measurable outcomes in experience bullets.")
            if "project experience" in normalized:
                gaps.append("Add projects that demonstrate practical capability.")
            if "work experience" in normalized:
                gaps.append("Add practical experience, internships, freelance work, or volunteer work.")

        return CareerAdvisor._dedupe(gaps)

    @staticmethod
    def _recommended_actions(
        profile: ResumeProfile,
        analysis: ResumeAnalysisResult | None,
        possible_paths: list[str],
    ) -> list[str]:
        actions: list[str] = []
        weaknesses = analysis.weaknesses if analysis is not None else []
        weakness_text = " ".join(weaknesses).lower()

        if not profile.summary or "summary" in weakness_text:
            actions.append("Improve resume career positioning in the summary.")

        if "quantified outcomes" in weakness_text:
            actions.append("Add measurable achievements.")

        if not profile.projects or "project experience" in weakness_text:
            actions.append("Build projects that demonstrate practical skills.")

        if not profile.skills or "skills" in weakness_text:
            actions.append("Learn and add missing role-relevant skills.")

        if set(possible_paths) & {"team lead", "engineering manager"}:
            actions.append(
                "Strengthen leadership examples with team, scope, and business impact."
            )

        if not actions:
            actions.append("Keep tailoring the resume to the most relevant target roles.")

        return CareerAdvisor._dedupe(actions)

    @staticmethod
    def _profile_words(profile: ResumeProfile) -> set[str]:
        values = [
            profile.summary or "",
            profile.raw_text,
            *profile.skills,
            *(
                value
                for experience in profile.experience
                for value in [
                    experience.role or "",
                    *experience.highlights,
                ]
            ),
        ]
        return {
            word.lower()
            for value in values
            for word in re.findall(r"[A-Za-z][A-Za-z0-9+#-]*", value)
        }

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        return deduped
