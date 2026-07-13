"""Internal, directional career-capability transfer assessment."""

from __future__ import annotations

from dataclasses import dataclass

from skill.matching.classifier import DomainClassifier
from skill.matching.schemas import (
    DomainClassification,
    EvidenceConfidence,
    EvidenceItem,
)
from skill.matching.taxonomy import (
    PRODUCT_CAPABILITIES,
    CareerDomain,
    JobFamily,
)


@dataclass(frozen=True, slots=True)
class TransferableCapability:
    target_capability: str
    evidence: tuple[EvidenceItem, ...]
    limitation: str
    confidence: EvidenceConfidence


@dataclass(frozen=True, slots=True)
class TransferableSkillAssessment:
    source_domain: CareerDomain
    target_domain: CareerDomain
    direct_evidence: tuple[EvidenceItem, ...]
    transferable_evidence: tuple[EvidenceItem, ...]
    limitations: tuple[str, ...]
    confidence: EvidenceConfidence
    capabilities: tuple[TransferableCapability, ...] = ()


@dataclass(frozen=True, slots=True)
class _TransferRule:
    source_domain: CareerDomain
    target_domain: CareerDomain
    target_capability: str
    source_aliases: tuple[str, ...]
    limitation: str
    source_families: tuple[JobFamily, ...] = ()
    target_families: tuple[JobFamily, ...] = ()


_TRANSFER_RULES = (
    _TransferRule(
        CareerDomain.SALES,
        CareerDomain.PRODUCT,
        "用户理解",
        (
            "customer research",
            "customer discovery",
            "customer feedback",
            "客户需求分析",
            "客户反馈整理",
        ),
        "Customer insight does not prove Product discovery ownership.",
        (
            JobFamily.BUSINESS_DEVELOPMENT,
            JobFamily.ACCOUNT_MANAGEMENT,
            JobFamily.SALES_OPERATIONS,
        ),
        (JobFamily.PRODUCT_MANAGER, JobFamily.PRODUCT_ANALYST),
    ),
    _TransferRule(
        CareerDomain.SALES,
        CareerDomain.PRODUCT,
        "需求管理",
        ("requirement collection", "requirements gathering", "需求收集"),
        "Requirement collection does not prove PRD or Product requirement ownership.",
        (
            JobFamily.BUSINESS_DEVELOPMENT,
            JobFamily.ACCOUNT_MANAGEMENT,
            JobFamily.SALES_OPERATIONS,
        ),
        (JobFamily.PRODUCT_MANAGER, JobFamily.PRODUCT_ASSISTANT),
    ),
    _TransferRule(
        CareerDomain.SALES,
        CareerDomain.PRODUCT,
        "产品数据分析",
        ("commercial analysis", "customer data analysis", "商业分析"),
        "Commercial analysis does not prove Product metric ownership.",
        (
            JobFamily.BUSINESS_DEVELOPMENT,
            JobFamily.ACCOUNT_MANAGEMENT,
            JobFamily.SALES_OPERATIONS,
        ),
        (JobFamily.PRODUCT_MANAGER, JobFamily.PRODUCT_ANALYST),
    ),
    _TransferRule(
        CareerDomain.SALES,
        CareerDomain.PRODUCT,
        "交付协作",
        (
            "stakeholder coordination",
            "cross-functional coordination",
            "cross-team coordination",
            "跨团队协调",
        ),
        "Stakeholder coordination does not prove Product delivery ownership.",
        (
            JobFamily.BUSINESS_DEVELOPMENT,
            JobFamily.ACCOUNT_MANAGEMENT,
            JobFamily.SALES_OPERATIONS,
        ),
        (
            JobFamily.PRODUCT_MANAGER,
            JobFamily.PRODUCT_OPERATIONS,
            JobFamily.PRODUCT_ASSISTANT,
        ),
    ),
    _TransferRule(
        CareerDomain.OPERATIONS,
        CareerDomain.HUMAN_RESOURCES,
        "入职行政",
        (
            "onboarding document coordination",
            "onboarding documents",
            "onboarding coordination",
            "入职材料协调",
        ),
        "Administrative onboarding support does not prove HR process ownership.",
        (JobFamily.ADMINISTRATION,),
        (JobFamily.HR_GENERALIST,),
    ),
    _TransferRule(
        CareerDomain.OPERATIONS,
        CareerDomain.HUMAN_RESOURCES,
        "员工档案",
        (
            "process documentation",
            "document coordination",
            "documentation",
            "文档协调",
        ),
        "Documentation support does not prove employee-file ownership.",
        (JobFamily.ADMINISTRATION,),
        (JobFamily.HR_GENERALIST,),
    ),
    _TransferRule(
        CareerDomain.OPERATIONS,
        CareerDomain.HUMAN_RESOURCES,
        "员工支持",
        ("employee support", "employee service", "员工支持"),
        "Employee support does not prove labor-relations expertise.",
        (JobFamily.ADMINISTRATION,),
        (JobFamily.HR_GENERALIST, JobFamily.EMPLOYEE_RELATIONS),
    ),
    _TransferRule(
        CareerDomain.OPERATIONS,
        CareerDomain.HUMAN_RESOURCES,
        "HR流程支持",
        (
            "process management",
            "process coordination",
            "process workflow",
            "process workflows",
            "流程管理",
        ),
        "Administrative process support does not prove HR process ownership.",
        (JobFamily.ADMINISTRATION,),
        (JobFamily.HR_GENERALIST,),
    ),
)


class TransferableSkillAssessor:
    """Assess approved transfer paths without inferring target-role experience."""

    def assess(
        self,
        source: DomainClassification,
        target: DomainClassification,
        evidence: tuple[EvidenceItem, ...],
    ) -> TransferableSkillAssessment:
        direct = self._direct_target_evidence(target.domain, evidence)
        capabilities: list[TransferableCapability] = []

        for rule in _TRANSFER_RULES:
            if not self._applies(rule, source, target):
                continue
            matched = self._matching_evidence(evidence, rule.source_aliases)
            if not matched:
                continue
            capabilities.append(
                TransferableCapability(
                    target_capability=rule.target_capability,
                    evidence=matched,
                    limitation=rule.limitation,
                    confidence=self._confidence(matched),
                )
            )

        transferable = self._dedupe_evidence(
            item for capability in capabilities for item in capability.evidence
        )
        limitations = tuple(
            dict.fromkeys(capability.limitation for capability in capabilities)
        )
        return TransferableSkillAssessment(
            source_domain=source.domain,
            target_domain=target.domain,
            direct_evidence=direct,
            transferable_evidence=transferable,
            limitations=limitations,
            confidence=self._confidence((*direct, *transferable)),
            capabilities=tuple(capabilities),
        )

    @staticmethod
    def _applies(
        rule: _TransferRule,
        source: DomainClassification,
        target: DomainClassification,
    ) -> bool:
        if source.domain != rule.source_domain or target.domain != rule.target_domain:
            return False
        if rule.source_families and source.job_family not in rule.source_families:
            return False
        if rule.target_families and target.job_family not in rule.target_families:
            return False
        return True

    @classmethod
    def _direct_target_evidence(
        cls,
        target_domain: CareerDomain,
        evidence: tuple[EvidenceItem, ...],
    ) -> tuple[EvidenceItem, ...]:
        if target_domain != CareerDomain.PRODUCT:
            return ()
        aliases = tuple(
            alias
            for capability in PRODUCT_CAPABILITIES
            for alias in capability.direct_aliases
        )
        return cls._matching_evidence(evidence, aliases)

    @staticmethod
    def _matching_evidence(
        evidence: tuple[EvidenceItem, ...],
        aliases: tuple[str, ...],
    ) -> tuple[EvidenceItem, ...]:
        return TransferableSkillAssessor._dedupe_evidence(
            item
            for item in evidence
            if any(
                DomainClassifier._contains(
                    DomainClassifier._normalize(item.text), alias
                )
                for alias in aliases
            )
        )

    @staticmethod
    def _dedupe_evidence(items) -> tuple[EvidenceItem, ...]:
        return tuple(dict.fromkeys(items))

    @staticmethod
    def _confidence(evidence: tuple[EvidenceItem, ...]) -> EvidenceConfidence:
        if len(evidence) >= 2:
            return EvidenceConfidence.HIGH
        if evidence:
            return EvidenceConfidence.MEDIUM
        return EvidenceConfidence.LOW
