"""Explainable domain-aware scoring for job matching."""

import re
from dataclasses import dataclass

from skill.matching.classifier import DomainClassifier
from skill.matching.schemas import (
    DomainClassification,
    MatchAssessment,
    MatchConfidence,
)
from skill.matching.taxonomy import ADJACENT_DOMAINS, CareerDomain
from skill.schemas.resume import ResumeProfile


@dataclass(frozen=True, slots=True)
class Requirement:
    canonical: str
    aliases: tuple[str, ...]


DOMAIN_REQUIREMENTS: dict[CareerDomain, tuple[Requirement, ...]] = {
    CareerDomain.HUMAN_RESOURCES: (
        Requirement("招聘", ("招聘", "recruitment", "recruiting")),
        Requirement("考勤", ("考勤", "attendance")),
        Requirement("薪酬", ("薪酬", "payroll", "compensation")),
        Requirement("劳动关系", ("劳动关系", "employee relations", "labor relations")),
    ),
    CareerDomain.TECHNOLOGY: (
        Requirement("Python", ("python",)),
        Requirement("FastAPI", ("fastapi",)),
        Requirement("API", ("api", "apis")),
        Requirement("SQL", ("sql",)),
        Requirement("Docker", ("docker",)),
        Requirement("AWS", ("aws",)),
        Requirement("Azure", ("azure",)),
        Requirement("GCP", ("gcp",)),
        Requirement("Java", ("java",)),
        Requirement("JavaScript", ("javascript",)),
        Requirement("Kubernetes", ("kubernetes",)),
        Requirement("React", ("react",)),
        Requirement("Tableau", ("tableau",)),
        Requirement("TypeScript", ("typescript",)),
    ),
    CareerDomain.FINANCE: (
        Requirement("财务报表", ("财务报表", "financial reporting", "financial statements")),
        Requirement("月度结账", ("月度结账", "month end close", "monthly close")),
        Requirement("账目核对", ("账目核对", "reconciliation", "reconcile")),
        Requirement("预算", ("预算", "budgeting", "budget")),
    ),
    CareerDomain.OPERATIONS: (
        Requirement("办公室管理", ("办公室管理", "office management", "office administration")),
        Requirement("供应商协调", ("供应商协调", "vendor coordination", "vendor management")),
        Requirement("流程优化", ("流程优化", "process improvement", "process optimization")),
        Requirement("项目协调", ("项目协调", "project coordination")),
    ),
    CareerDomain.SUPPLY_CHAIN: (
        Requirement("采购", ("采购", "procurement")),
        Requirement("物流", ("物流", "logistics")),
        Requirement("库存计划", ("库存计划", "inventory planning")),
    ),
    CareerDomain.MANUFACTURING: (
        Requirement("生产", ("生产", "production")),
        Requirement("质量控制", ("质量控制", "quality control")),
        Requirement("设备维护", ("设备维护", "equipment maintenance")),
    ),
    CareerDomain.CUSTOMER_SERVICE: (
        Requirement("客户支持", ("客户支持", "customer support")),
        Requirement("客户成功", ("客户成功", "customer success")),
        Requirement("服务运营", ("服务运营", "service operations")),
    ),
    CareerDomain.SALES: (
        Requirement("业务拓展", ("业务拓展", "business development")),
        Requirement("客户管理", ("客户管理", "account management")),
        Requirement("销售运营", ("销售运营", "sales operations")),
    ),
    CareerDomain.MARKETING: (
        Requirement("内容营销", ("内容营销", "content marketing")),
        Requirement("数字营销", ("数字营销", "digital marketing")),
        Requirement("市场研究", ("市场研究", "market research")),
    ),
}

NEUTRAL_REQUIREMENTS = (
    Requirement("Excel", ("excel",)),
    Requirement("沟通", ("沟通", "communication")),
    Requirement("项目管理", ("项目管理", "project management")),
)


class MatchScorer:
    """Calculate bounded domain, skill, and qualification components."""

    @staticmethod
    def domain_score(
        resume: DomainClassification,
        job: DomainClassification,
        has_resume_evidence: bool,
        has_transferable_evidence: bool = False,
    ) -> int:
        if not has_resume_evidence:
            return 0
        if resume.domain == job.domain and resume.domain not in {
            CareerDomain.UNKNOWN,
            CareerDomain.OTHER,
        }:
            if resume.job_family is not None and resume.job_family == job.job_family:
                return 100
            if resume.job_family is None or job.job_family is None:
                return 90
            return 75
        if (resume.domain, job.domain) in ADJACENT_DOMAINS:
            return 55
        if resume.domain in {CareerDomain.UNKNOWN, CareerDomain.OTHER} or job.domain in {
            CareerDomain.UNKNOWN,
            CareerDomain.OTHER,
        }:
            return 30 if has_transferable_evidence else 10
        return 10

    def assess(
        self,
        profile: ResumeProfile,
        job_description: str,
        resume_classification: DomainClassification,
        job_classification: DomainClassification,
    ) -> MatchAssessment:
        skill_requirements = self._extract_skill_requirements(
            job_description, job_classification.domain
        )
        qualifications = self._extract_qualifications(job_description)
        if (
            job_classification.domain == CareerDomain.UNKNOWN
            and not skill_requirements
            and not qualifications
        ):
            return MatchAssessment(
                score=0,
                confidence=MatchConfidence.LOW,
                domain_score=None,
                skill_score=None,
                qualification_score=None,
                gaps=("Insufficient job information for a reliable match.",),
            )

        profile_text = "\n".join(DomainClassifier._profile_evidence(profile))
        normalized_profile = DomainClassifier._normalize(profile_text)
        matched, missing, skill_score = self._score_skills(
            normalized_profile, job_description, skill_requirements
        )
        qualification_score, qualification_gaps = self._score_qualifications(
            profile, qualifications
        )
        has_resume_evidence = bool(profile_text.strip())
        transferable = bool(matched)
        domain_score = self.domain_score(
            resume_classification,
            job_classification,
            has_resume_evidence,
            transferable,
        )

        components = (
            (domain_score, 0.30),
            (skill_score, 0.50),
            (qualification_score, 0.20),
        )
        available = [(value, weight) for value, weight in components if value is not None]
        score = (
            round(sum(value * weight for value, weight in available) / sum(weight for _, weight in available))
            if available
            else 0
        )
        score = max(0, min(100, score))

        strengths: list[str] = []
        gaps: list[str] = []
        if domain_score >= 75:
            strengths.append(
                f"Domain match: {job_classification.domain.value}"
                + (
                    f" / {job_classification.job_family.value}"
                    if job_classification.job_family is not None
                    else ""
                )
                + "."
            )
        elif domain_score < 55:
            gaps.append("Resume and job domain evidence is limited or different.")
        if matched:
            strengths.append("Resume shows evidence for: " + ", ".join(matched) + ".")
        if missing:
            gaps.append("Not visible in the resume: " + ", ".join(missing) + ".")
        gaps.extend(qualification_gaps)

        requirement_count = len(skill_requirements) + len(qualifications)
        component_count = len(available)
        if (
            job_classification.confidence == MatchConfidence.HIGH
            and requirement_count >= 3
            and component_count >= 2
        ):
            confidence = MatchConfidence.HIGH
        elif (
            job_classification.domain not in {CareerDomain.UNKNOWN, CareerDomain.OTHER}
            and requirement_count >= 1
            and component_count >= 2
        ):
            confidence = MatchConfidence.MEDIUM
        else:
            confidence = MatchConfidence.LOW

        return MatchAssessment(
            score=score,
            confidence=confidence,
            domain_score=domain_score,
            skill_score=skill_score,
            qualification_score=qualification_score,
            strengths=tuple(strengths),
            gaps=tuple(gaps),
            matched_skills=tuple(matched),
            missing_skills=tuple(missing),
        )

    @staticmethod
    def _extract_skill_requirements(
        job_description: str,
        domain: CareerDomain,
    ) -> list[Requirement]:
        candidates = DOMAIN_REQUIREMENTS.get(domain, ()) + NEUTRAL_REQUIREMENTS
        normalized = DomainClassifier._normalize(job_description)
        return [
            requirement
            for requirement in candidates
            if any(
                DomainClassifier._contains(normalized, alias)
                and not MatchScorer._is_negated(normalized, alias)
                for alias in requirement.aliases
            )
        ]

    @staticmethod
    def _score_skills(
        normalized_profile: str,
        job_description: str,
        requirements: list[Requirement],
    ) -> tuple[list[str], list[str], int | None]:
        if not requirements:
            return [], [], None
        matched: list[str] = []
        missing: list[str] = []
        matched_weight = 0
        total_weight = 0
        normalized_job = DomainClassifier._normalize(job_description)
        required_markers = ("require", "required", "must", "要求", "必须", "需要")
        for requirement in requirements:
            positions = [
                normalized_job.find(DomainClassifier._normalize(alias))
                for alias in requirement.aliases
                if normalized_job.find(DomainClassifier._normalize(alias)) >= 0
            ]
            position = min(positions) if positions else 0
            context = normalized_job[max(0, position - 30) : position + 5]
            weight = 2 if any(marker in context for marker in required_markers) else 1
            total_weight += weight
            present = any(
                DomainClassifier._contains(normalized_profile, alias)
                for alias in requirement.aliases
            )
            if present:
                matched.append(requirement.canonical)
                matched_weight += weight
            else:
                missing.append(requirement.canonical)
        return matched, missing, round(matched_weight / total_weight * 100)

    @staticmethod
    def _extract_qualifications(job_description: str) -> list[tuple[str, object]]:
        normalized = DomainClassifier._normalize(job_description)
        qualifications: list[tuple[str, object]] = []
        years = re.search(r"(\d+)\s*(?:\+\s*)?(?:years?|年)", normalized)
        if years:
            qualifications.append(("years", int(years.group(1))))
        if any(
            term in normalized and not MatchScorer._is_negated(normalized, term)
            for term in ("bachelor", "本科")
        ):
            qualifications.append(("bachelor", True))
        if DomainClassifier._contains(normalized, "cpa") and not MatchScorer._is_negated(normalized, "cpa"):
            qualifications.append(("cpa", True))
        if (
            DomainClassifier._contains(normalized, "english")
            and not MatchScorer._is_negated(normalized, "english")
        ) or ("英语" in normalized and not MatchScorer._is_negated(normalized, "英语")):
            qualifications.append(("english", True))
        return qualifications

    @staticmethod
    def _score_qualifications(
        profile: ResumeProfile,
        qualifications: list[tuple[str, object]],
    ) -> tuple[int | None, list[str]]:
        if not qualifications:
            return None, []
        profile_text = DomainClassifier._normalize(
            "\n".join(DomainClassifier._profile_evidence(profile))
        )
        satisfied = 0
        gaps: list[str] = []
        for name, value in qualifications:
            present = False
            if name == "years":
                found = [int(item) for item in re.findall(r"(\d+)\s*(?:\+\s*)?(?:years?|年)", profile_text)]
                stated_years = max(found) if found else 0
                dated_years = MatchScorer._experience_years(profile)
                present = max(stated_years, dated_years) >= int(value)
            elif name == "bachelor":
                present = "bachelor" in profile_text or "本科" in profile_text
            elif name == "cpa":
                present = DomainClassifier._contains(profile_text, "cpa")
            elif name == "english":
                present = "english" in profile_text or "英语" in profile_text
            if present:
                satisfied += 1
            else:
                gaps.append(f"Qualification not visible in the resume: {name}.")
        return round(satisfied / len(qualifications) * 100), gaps

    @staticmethod
    def _is_negated(text: str, phrase: str) -> bool:
        normalized = DomainClassifier._normalize(text)
        target = DomainClassifier._normalize(phrase)
        position = normalized.find(target)
        if position < 0:
            return False
        before = normalized[max(0, position - 24) : position]
        after = normalized[position + len(target) : position + len(target) + 24]
        before = before.rstrip()
        after = after.lstrip()
        return before.endswith(("no", "without", "无需", "不要求", "不需要")) or (
            re.match(r"^(?:is\s+)?not\s+required\b", after) is not None
        )

    @staticmethod
    def _experience_years(profile: ResumeProfile) -> int:
        durations: list[int] = []
        for entry in profile.experience:
            start = MatchScorer._date_month(entry.start_date)
            end = MatchScorer._date_month(entry.end_date)
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
        year = int(match.group(1))
        month = int(match.group(2) or 1)
        if not 1 <= month <= 12:
            return None
        return year * 12 + month - 1
