"""Deterministic, resume-evidence career-stage assessment."""

import re
import unicodedata

from skill.career.stages import (
    CareerStage,
    CareerStageAssessment,
    StageConfidence,
    StageSignals,
)
from skill.schemas.resume import ResumeProfile


class CareerStageAssessor:
    """Infer an internal career stage without external services or guesses."""

    def assess(self, profile: ResumeProfile) -> CareerStageAssessment:
        experience = self._experience_signals(profile)
        responsibility = self._responsibility_signals(profile)
        impact = self._impact_signals(profile)
        signals = StageSignals(
            experience=tuple(experience),
            responsibility=tuple(responsibility),
            impact=tuple(impact),
        )
        stage = self._stage(signals)
        confidence = self._confidence(signals, stage)
        return CareerStageAssessment(stage=stage, signals=signals, confidence=confidence)

    def _experience_signals(self, profile: ResumeProfile) -> list[str]:
        signals: list[str] = []
        duration = self._max_duration_years(profile)
        if duration >= 1:
            signals.append("dated experience")
        if duration >= 2:
            signals.append("2+ years experience")
        if duration >= 5:
            signals.append("5+ years experience")
        text = self._profile_text(profile)
        if any("intern" in value for value in (text,)) or "实习" in text:
            signals.append("internship evidence")
        if profile.projects:
            signals.append("project evidence")
        if re.search(r"\b\d+\s*\+?\s*years?\b|\d+\s*年", text):
            signals.append("stated experience duration")
        return self._dedupe(signals)

    def _responsibility_signals(self, profile: ResumeProfile) -> list[str]:
        text = self._profile_text(profile)
        signals: list[str] = []
        if self._contains_any(text, ("owned", "owning", "独立负责", "负责")):
            signals.append("owned scope")
        if self._contains_any(
            text,
            ("cross functional", "cross-functional", "stakeholder", "跨部门", "跨团队"),
        ):
            signals.append("cross-functional coordination")
        if self._contains_any(
            text,
            ("managed a team", "managed team", "mentored", "direct reports", "带领", "管理团队", "培养"),
        ):
            signals.append("people leadership")
        if self._contains_any(
            text,
            ("process", "workflow", "流程", "operating model", "standard"),
        ) and self._contains_any(text, ("owned", "improved", "负责", "优化", "独立")):
            signals.append("process responsibility")
        if self._contains_any(
            text,
            ("complex", "migration", "architecture", "platform", "program", "复杂", "系统", "项目"),
        ):
            signals.append("complex initiative")
        if self._contains_any(text, ("strategy", "战略", "portfolio", "组织")):
            signals.append("strategic scope")
        return self._dedupe(signals)

    def _impact_signals(self, profile: ResumeProfile) -> list[str]:
        signals: list[str] = []
        impact_terms = (
            "improved",
            "reduced",
            "increased",
            "saved",
            "delivered",
            "提升",
            "降低",
            "减少",
            "增长",
            "节省",
        )
        scale_terms = ("team of", "budget", "portfolio", "users", "customers", "人团队", "团队", "预算", "客户")
        for highlight in self._highlights(profile):
            normalized = self._normalize(highlight)
            if re.search(r"\d", normalized) and self._contains_any(normalized, impact_terms):
                signals.append("quantified outcome")
            if re.search(r"\d", normalized) and self._contains_any(normalized, scale_terms):
                signals.append("stated scale")
        return self._dedupe(signals)

    @staticmethod
    def _stage(signals: StageSignals) -> CareerStage:
        experience = set(signals.experience)
        responsibility = set(signals.responsibility)
        impact = set(signals.impact)
        if not experience and not responsibility and not impact:
            return CareerStage.UNKNOWN
        has_people_scope = "people leadership" in responsibility
        has_advanced_scope = bool({"strategic scope", "process responsibility"} & responsibility)
        if has_people_scope and has_advanced_scope and impact:
            return CareerStage.ADVANCED
        has_expert_scope = bool(
            {"cross-functional coordination", "complex initiative", "process responsibility"}
            & responsibility
        )
        if has_expert_scope and impact:
            return CareerStage.EXPERIENCED
        if "2+ years experience" in experience or bool(
            {"owned scope", "cross-functional coordination", "process responsibility"}
            & responsibility
        ):
            return CareerStage.DEVELOPING
        if experience:
            return CareerStage.ENTRY
        return CareerStage.UNKNOWN

    @staticmethod
    def _confidence(signals: StageSignals, stage: CareerStage) -> StageConfidence:
        if stage == CareerStage.UNKNOWN:
            return StageConfidence.LOW
        categories = sum(
            bool(category)
            for category in (signals.experience, signals.responsibility, signals.impact)
        )
        if categories >= 3:
            return StageConfidence.HIGH
        if categories == 2:
            return StageConfidence.MEDIUM
        return StageConfidence.LOW

    @classmethod
    def _profile_text(cls, profile: ResumeProfile) -> str:
        values = [profile.summary or "", profile.raw_text, *profile.skills]
        for experience in profile.experience:
            values.extend((experience.role or "", *experience.highlights))
        for project in profile.projects:
            values.extend((project.name or "", project.description or "", *project.technologies))
        return cls._normalize("\n".join(value for value in values if value))

    @staticmethod
    def _highlights(profile: ResumeProfile) -> list[str]:
        return [highlight for entry in profile.experience for highlight in entry.highlights]

    @staticmethod
    def _max_duration_years(profile: ResumeProfile) -> int:
        durations: list[int] = []
        for experience in profile.experience:
            start = CareerStageAssessor._date_month(experience.start_date)
            end = CareerStageAssessor._date_month(experience.end_date)
            if start is not None and end is not None and end >= start:
                durations.append((end - start) // 12)
        return max(durations, default=0)

    @staticmethod
    def _date_month(value: str | None) -> int | None:
        if not value:
            return None
        match = re.fullmatch(r"(\d{4})(?:[-/.](\d{1,2}))?", value.strip())
        if match is None:
            return None
        month = int(match.group(2) or 1)
        if not 1 <= month <= 12:
            return None
        return int(match.group(1)) * 12 + month - 1

    @staticmethod
    def _normalize(value: str) -> str:
        value = unicodedata.normalize("NFKC", value).casefold()
        return " ".join(re.sub(r"[^\w+%\u4e00-\u9fff]+", " ", value).split())

    @staticmethod
    def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
        return any(term.casefold() in value for term in terms)

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
