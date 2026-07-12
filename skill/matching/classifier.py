"""Deterministic domain classification from job and resume evidence."""

import re
import unicodedata
from collections import defaultdict

from skill.matching.schemas import DomainClassification, MatchConfidence
from skill.matching.taxonomy import (
    DOMAIN_SIGNALS,
    OCCUPATIONAL_MARKERS,
    CareerDomain,
    JobFamily,
)
from skill.schemas.resume import ResumeProfile


class DomainClassifier:
    """Classify professional text without a model or external dependency."""

    def classify_text(self, text: str) -> DomainClassification:
        normalized = self._normalize(text)
        if not normalized:
            return self._unknown()

        domain_scores: dict[CareerDomain, int] = defaultdict(int)
        family_scores: dict[JobFamily, int] = defaultdict(int)
        evidence: list[str] = []
        seen: set[str] = set()

        for signal in DOMAIN_SIGNALS:
            if signal.canonical in seen or not self._contains(normalized, signal.alias):
                continue
            seen.add(signal.canonical)
            evidence.append(signal.canonical)
            domain_scores[signal.domain] += signal.weight
            if signal.family is not None:
                family_scores[signal.family] += signal.weight

        if not domain_scores:
            if any(self._contains(normalized, marker) for marker in OCCUPATIONAL_MARKERS):
                return DomainClassification(
                    CareerDomain.OTHER,
                    None,
                    MatchConfidence.LOW,
                    (),
                )
            return self._unknown()

        ranked = sorted(domain_scores.items(), key=lambda item: (-item[1], item[0].value))
        top_domain, top_score = ranked[0]
        runner_up = ranked[1][1] if len(ranked) > 1 else 0
        lead = top_score - runner_up
        if top_score < 4 or lead < 2:
            return DomainClassification(
                CareerDomain.UNKNOWN,
                None,
                MatchConfidence.LOW,
                tuple(evidence),
            )

        family = self._select_family(top_domain, family_scores)
        confidence = (
            MatchConfidence.HIGH
            if top_score >= 8 and lead >= 4
            else MatchConfidence.MEDIUM
        )
        return DomainClassification(
            top_domain,
            family,
            confidence,
            tuple(evidence),
        )

    def classify_profile(self, profile: ResumeProfile) -> DomainClassification:
        return self.classify_text("\n".join(self._profile_evidence(profile)))

    @staticmethod
    def _select_family(
        domain: CareerDomain,
        family_scores: dict[JobFamily, int],
    ) -> JobFamily | None:
        candidates = [
            (family, score)
            for family, score in family_scores.items()
            if family.value and score > 0
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda item: (-item[1], item[0].value))
        winner, score = candidates[0]
        # Domain signals already scope each family; a weight-4 title or two
        # weaker signals are sufficient for the first taxonomy version.
        return winner if score >= 4 else None

    @staticmethod
    def _profile_evidence(profile: ResumeProfile) -> list[str]:
        values: list[str] = [profile.summary or "", profile.raw_text]
        values.extend(profile.skills)
        values.extend(profile.certifications)
        for entry in profile.experience:
            values.append(entry.role or "")
            values.extend(entry.highlights)
        for entry in profile.education:
            values.extend(
                value or ""
                for value in (entry.degree, entry.field, entry.description)
            )
        for entry in profile.projects:
            values.extend((entry.name or "", entry.description or ""))
            values.extend(entry.technologies)
        return [value for value in values if value and value.strip()]

    @staticmethod
    def _normalize(text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text).casefold()
        normalized = re.sub(r"[^\w+#\u4e00-\u9fff]+", " ", normalized)
        return " ".join(normalized.split())

    @classmethod
    def _contains(cls, text: str, phrase: str) -> bool:
        target = cls._normalize(phrase)
        if not target:
            return False
        if re.search(r"[\u4e00-\u9fff]", target):
            return target in text
        return re.search(rf"(?<!\w){re.escape(target)}(?!\w)", text) is not None

    @staticmethod
    def _unknown() -> DomainClassification:
        return DomainClassification(
            CareerDomain.UNKNOWN,
            None,
            MatchConfidence.LOW,
            (),
        )
