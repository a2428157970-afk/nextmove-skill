"""Internal, evidence-grounded career transition assessment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from skill.career.stages import CareerStageAssessment
from skill.matching.classifier import DomainClassifier
from skill.matching.explanations import MatchExplanationResult
from skill.matching.schemas import (
    DomainClassification,
    EvidenceItem,
    RequirementStatus,
)
from skill.matching.taxonomy import (
    PRODUCT_CAPABILITIES,
    CareerDomain,
    JobFamily,
    ProductCapabilityCategory,
)
from skill.matching.transfer import TransferableSkillAssessment


class TransitionType(str, Enum):
    SAME_ROLE = "same_role"
    SAME_DOMAIN = "same_domain"
    ADJACENT_ROLE = "adjacent_role"
    CROSS_DOMAIN = "cross_domain"
    UNKNOWN = "unknown"


class TargetRoleLevel(str, Enum):
    PEER = "peer"
    MANAGEMENT = "management"
    UNKNOWN = "unknown"


class TransitionRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class TransitionConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TransitionGapKind(str, Enum):
    DIRECT_CAPABILITY = "missing_direct_capability"
    TRANSFERABLE_CAPABILITY = "transferable_capability"
    DEVELOPMENT_AREA = "development_area"


@dataclass(frozen=True, slots=True)
class TransitionCapabilityGap:
    capability: str
    kind: TransitionGapKind
    evidence_status: RequirementStatus
    reason: str
    core: bool


@dataclass(frozen=True, slots=True)
class TransitionRiskAssessment:
    level: TransitionRiskLevel
    factors: tuple[str, ...]
    evidence_gaps: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TransitionAction:
    related_gap: str
    objective: str
    steps: tuple[str, ...]
    expected_evidence: str
    priority: int


@dataclass(frozen=True, slots=True)
class CareerTransitionAssessment:
    current_domain: CareerDomain
    target_domain: CareerDomain
    transition_type: TransitionType
    transferable_skills: tuple[str, ...]
    direct_evidence: tuple[EvidenceItem, ...]
    transferable_evidence: tuple[EvidenceItem, ...]
    missing_capabilities: tuple[TransitionCapabilityGap, ...]
    transition_risk: TransitionRiskAssessment
    recommended_actions: tuple[TransitionAction, ...]
    confidence: TransitionConfidence


_ADJACENT_FAMILIES = frozenset(
    {(JobFamily.ADMINISTRATION, JobFamily.HR_GENERALIST)}
)
_UNKNOWN_DOMAINS = {CareerDomain.UNKNOWN, CareerDomain.OTHER}
_CORE_CAPABILITIES = {
    CareerDomain.PRODUCT: {
        "Product Planning", "Requirement Management", "PRD",
        "Delivery Collaboration", "Product Delivery Ownership",
        "产品规划", "需求管理", "交付协作",
    },
    CareerDomain.HUMAN_RESOURCES: {
        "Recruitment", "Labor Relations", "Payroll",
        "招聘", "劳动关系", "薪酬",
    },
}


class TargetRoleLevelAssessor:
    MANAGEMENT_SIGNALS = (
        "manager", "head", "people leadership", "team management",
        "经理", "负责人", "团队管理", "人员管理",
    )
    PEER_SIGNALS = ("specialist", "assistant", "专员", "助理")
    PRODUCT_PEOPLE_MANAGEMENT_SIGNALS = (
        "people leadership", "team management", "managing a team",
        "manages a team", "manages people", "direct reports",
        "团队管理", "人员管理", "直属下属",
    )

    def classify(self, text: str) -> TargetRoleLevel:
        normalized = DomainClassifier._normalize(text)
        if DomainClassifier._contains(normalized, "product manager"):
            if any(
                DomainClassifier._contains(normalized, term)
                for term in self.PRODUCT_PEOPLE_MANAGEMENT_SIGNALS
            ):
                return TargetRoleLevel.MANAGEMENT
            return TargetRoleLevel.PEER
        if any(DomainClassifier._contains(normalized, term) for term in self.MANAGEMENT_SIGNALS):
            return TargetRoleLevel.MANAGEMENT
        if any(DomainClassifier._contains(normalized, term) for term in self.PEER_SIGNALS):
            return TargetRoleLevel.PEER
        return TargetRoleLevel.UNKNOWN


class CareerTransitionAssessor:
    """Compose existing internal assessments without changing public match APIs."""

    def transition_type(
        self,
        current: DomainClassification,
        target: DomainClassification,
        target_role_level: TargetRoleLevel,
    ) -> TransitionType:
        if current.domain in _UNKNOWN_DOMAINS or target.domain in _UNKNOWN_DOMAINS:
            return TransitionType.UNKNOWN
        if current.domain == target.domain:
            if current.job_family == target.job_family:
                if target_role_level == TargetRoleLevel.MANAGEMENT:
                    return TransitionType.SAME_DOMAIN
                return TransitionType.SAME_ROLE
            return TransitionType.SAME_DOMAIN
        if (current.job_family, target.job_family) in _ADJACENT_FAMILIES:
            return TransitionType.ADJACENT_ROLE
        return TransitionType.CROSS_DOMAIN

    def assess(
        self,
        current: DomainClassification,
        target: DomainClassification,
        career_stage: CareerStageAssessment,
        transferability: TransferableSkillAssessment | None,
        explanation: MatchExplanationResult,
        target_role_level: TargetRoleLevel = TargetRoleLevel.UNKNOWN,
    ) -> CareerTransitionAssessment:
        direct = self._direct_evidence(explanation, transferability)
        transferable = self._transferable_evidence(transferability, direct)
        gaps = self._capability_gaps(target, target_role_level, explanation)
        transition_type = self.transition_type(current, target, target_role_level)
        from skill.career.transition_actions import TransitionActionBuilder
        from skill.career.transition_risk import TransitionRiskAssessor

        return CareerTransitionAssessment(
            current.domain,
            target.domain,
            transition_type,
            self._transferable_skills(transferability, direct),
            direct,
            transferable,
            gaps,
            TransitionRiskAssessor().assess(transition_type, direct, transferable, gaps),
            TransitionActionBuilder().build(gaps),
            self._confidence(current, target, career_stage, explanation, direct, transferable),
        )

    @staticmethod
    def _dedupe(items: tuple[EvidenceItem, ...]) -> tuple[EvidenceItem, ...]:
        return tuple(dict.fromkeys(items))

    def _direct_evidence(
        self,
        explanation: MatchExplanationResult,
        transferability: TransferableSkillAssessment | None,
    ) -> tuple[EvidenceItem, ...]:
        items = tuple(
            item
            for requirement in explanation.requirements
            if requirement.status == RequirementStatus.MATCHED
            for item in requirement.evidence
        )
        if transferability is not None:
            items += transferability.direct_evidence
        return self._dedupe(items)

    def _transferable_evidence(
        self,
        transferability: TransferableSkillAssessment | None,
        direct: tuple[EvidenceItem, ...],
    ) -> tuple[EvidenceItem, ...]:
        if transferability is None:
            return ()
        return self._dedupe(tuple(item for item in transferability.transferable_evidence if item not in direct))

    @staticmethod
    def _transferable_skills(
        transferability: TransferableSkillAssessment | None,
        direct: tuple[EvidenceItem, ...],
    ) -> tuple[str, ...]:
        if transferability is None:
            return ()
        skills = list(dict.fromkeys(
            capability.target_capability
            for capability in transferability.capabilities
            if any(item not in direct for item in capability.evidence)
        ))
        if transferability.target_domain == CareerDomain.HUMAN_RESOURCES:
            evidence_text = " ".join(item.text for item in transferability.transferable_evidence).casefold()
            if "coordination" in evidence_text:
                skills.append("Coordination")
            if "document" in evidence_text:
                skills.append("Documentation")
        return tuple(dict.fromkeys(skills))

    def _capability_gaps(
        self,
        target: DomainClassification,
        target_role_level: TargetRoleLevel,
        explanation: MatchExplanationResult,
    ) -> tuple[TransitionCapabilityGap, ...]:
        gaps: list[TransitionCapabilityGap] = []
        for requirement in explanation.requirements:
            if requirement.status == RequirementStatus.MATCHED:
                continue
            kind = (
                TransitionGapKind.TRANSFERABLE_CAPABILITY
                if requirement.status == RequirementStatus.PARTIAL
                else TransitionGapKind.DIRECT_CAPABILITY
            )
            reason = {
                RequirementStatus.UNKNOWN: f"Direct evidence for {requirement.requirement} is not available.",
                RequirementStatus.MISSING: f"Supplied evidence does not demonstrate {requirement.requirement}.",
                RequirementStatus.PARTIAL: f"Transferable evidence for {requirement.requirement} needs further verification.",
            }[requirement.status]
            gaps.append(TransitionCapabilityGap(
                requirement.requirement,
                kind,
                requirement.status,
                reason,
                requirement.requirement in _CORE_CAPABILITIES.get(target.domain, set()),
            ))
            if target.domain == CareerDomain.PRODUCT:
                category = next(
                    (
                        definition.category
                        for definition in PRODUCT_CAPABILITIES
                        if definition.canonical == requirement.requirement
                    ),
                    None,
                )
                derived = {
                    ProductCapabilityCategory.PRODUCT_PLANNING: "Product Planning",
                    ProductCapabilityCategory.REQUIREMENT_MANAGEMENT: "PRD",
                    ProductCapabilityCategory.DELIVERY_COLLABORATION: "Product Delivery Ownership",
                }.get(category)
                if derived is not None:
                    if category == ProductCapabilityCategory.PRODUCT_PLANNING:
                        gaps.pop()
                    gaps.append(TransitionCapabilityGap(
                        derived,
                        TransitionGapKind.DIRECT_CAPABILITY,
                        requirement.status,
                        f"Direct evidence for {derived} is not available.",
                        True,
                    ))
            if target.domain == CareerDomain.HUMAN_RESOURCES:
                normalized = DomainClassifier._normalize(requirement.requirement)
                derived = None
                if DomainClassifier._contains(normalized, "招聘"):
                    derived = "Recruitment"
                elif DomainClassifier._contains(normalized, "劳动关系"):
                    derived = "Labor Relations"
                if derived is not None:
                    gaps.pop()
                    gaps.append(TransitionCapabilityGap(
                        derived,
                        TransitionGapKind.DIRECT_CAPABILITY,
                        requirement.status,
                        f"Direct evidence for {derived} is not available.",
                        True,
                    ))
        has_leadership = any(
            requirement.status == RequirementStatus.MATCHED
            and any(term in requirement.requirement.lower() for term in ("leadership", "team management", "团队管理"))
            for requirement in explanation.requirements
        )
        if target_role_level == TargetRoleLevel.MANAGEMENT and not has_leadership:
            gaps.append(TransitionCapabilityGap(
                "People Leadership", TransitionGapKind.DEVELOPMENT_AREA,
                RequirementStatus.UNKNOWN,
                "Direct evidence for people leadership is not available.", True,
            ))
        return tuple(dict.fromkeys(gaps))

    @staticmethod
    def _confidence(current, target, career_stage, explanation, direct, transferable):
        if current.domain in _UNKNOWN_DOMAINS or target.domain in _UNKNOWN_DOMAINS:
            return TransitionConfidence.LOW
        if career_stage.stage.value != "unknown" and explanation.requirements and len((*direct, *transferable)) >= 2:
            return TransitionConfidence.HIGH
        if explanation.requirements or direct or transferable:
            return TransitionConfidence.MEDIUM
        return TransitionConfidence.LOW
