"""Rule-based resume improvement for Skill Core."""

from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.resume import ResumeProfile
from skill.improvement.schemas import ResumeImprovementResult


class ResumeImprover:
    """Generate actionable resume improvements from analysis weaknesses."""

    def improve(
        self,
        profile: ResumeProfile,
        analysis: ResumeAnalysisResult,
    ) -> ResumeImprovementResult:
        suggestions: list[str] = []
        improved_sections: dict[str, list[str]] = {}

        for weakness in analysis.weaknesses:
            normalized = weakness.lower()

            if "missing a summary" in normalized:
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "summary",
                    "Add a concise summary that states your target role, core strengths, and career positioning.",
                )

            if "quantified outcomes" in normalized:
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "experience",
                    "Rewrite experience bullets to include measurable impact, such as revenue, efficiency, scale, or time saved.",
                )

            if "skills section is present but limited" in normalized:
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "skills",
                    "Expand the skills section with relevant tools, domains, and role-specific keywords.",
                )

            if "missing a skills section" in normalized:
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "skills",
                    "Add a dedicated skills section with tools, domains, and role-specific keywords.",
                )

            if "missing work experience" in normalized:
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "experience",
                    "Add relevant work, internship, volunteer, or practical experience with clear responsibilities and outcomes.",
                )

            if "missing project experience" in normalized:
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "projects",
                    "Add project entries that show the problem, your contribution, technologies used, and final result.",
                )

        for gap in analysis.skill_assessment.gaps:
            if "skills section" in gap.lower() or "keywords" in gap.lower():
                self._add_suggestion(
                    suggestions,
                    improved_sections,
                    "skills",
                    "Expand the skills section with relevant tools, domains, and role-specific keywords.",
                )

        if not suggestions:
            suggestions.append(
                "Resume analysis did not find major issues. Keep tailoring the resume to the target role."
            )

        return ResumeImprovementResult(
            issues=list(analysis.weaknesses),
            suggestions=suggestions,
            improved_sections=improved_sections,
        )

    @staticmethod
    def _add_suggestion(
        suggestions: list[str],
        improved_sections: dict[str, list[str]],
        section: str,
        suggestion: str,
    ) -> None:
        if suggestion not in suggestions:
            suggestions.append(suggestion)
        section_suggestions = improved_sections.setdefault(section, [])
        if suggestion not in section_suggestions:
            section_suggestions.append(suggestion)
