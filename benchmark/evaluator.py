"""Evaluate existing Career Intelligence behavior against synthetic scenarios."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

from benchmark.schemas import BenchmarkScenario
from skill.career.stage_assessor import CareerStageAssessor
from skill.career.stages import CareerStageAssessment
from skill.career.transition import (
    CareerTransitionAssessment,
    CareerTransitionAssessor,
    TargetRoleLevelAssessor,
)
from skill.matching.classifier import DomainClassifier
from skill.matching.explanations import MatchExplanationResult
from skill.matching.matcher import JobMatcher
from skill.matching.schemas import DomainClassification, JobMatchResult, MatchAssessment
from skill.schemas.resume import EducationEntry, ExperienceEntry, ProjectEntry, ResumeProfile


@dataclass(frozen=True, slots=True)
class BenchmarkObservation:
    resume_domain: DomainClassification
    target_domain: DomainClassification
    career_stage: CareerStageAssessment
    match_assessment: MatchAssessment
    explanation: MatchExplanationResult
    public_result: JobMatchResult
    professional_evidence: tuple[str, ...]
    career_transition: CareerTransitionAssessment | None


@dataclass(frozen=True, slots=True)
class BenchmarkCheck:
    name: str
    category: str
    passed: bool
    safety: bool = False


@dataclass(frozen=True, slots=True)
class QualityMetric:
    name: str
    score: int


@dataclass(frozen=True, slots=True)
class ScenarioBenchmarkResult:
    scenario_id: str
    passed: bool
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    safety_violations: tuple[str, ...]
    metrics: tuple[QualityMetric, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def observe_scenario(scenario: BenchmarkScenario) -> BenchmarkObservation:
    profile = _profile_from_fixture(scenario.resume_fixture)
    classifier = DomainClassifier()
    matcher = JobMatcher()
    assessment, explanation = matcher._assess_and_explain(
        profile,
        scenario.target_jd,
    )
    resume_domain = classifier.classify_profile(profile)
    target_domain = classifier.classify_text(scenario.target_jd)
    career_stage = CareerStageAssessor().assess(profile)
    transition = None
    if scenario.expected.transition is not None:
        transition = CareerTransitionAssessor().assess(
            resume_domain,
            target_domain,
            career_stage,
            assessment.transferability,
            explanation,
            TargetRoleLevelAssessor().classify(
                f"{scenario.target_role} {scenario.target_jd}"
            ),
        )
    return BenchmarkObservation(
        resume_domain=resume_domain,
        target_domain=target_domain,
        career_stage=career_stage,
        match_assessment=assessment,
        explanation=explanation,
        public_result=matcher.match(profile, scenario.target_jd),
        professional_evidence=_professional_evidence(profile),
        career_transition=transition,
    )


def evaluate_scenario(
    scenario: BenchmarkScenario,
    observation: BenchmarkObservation,
) -> ScenarioBenchmarkResult:
    checks: list[BenchmarkCheck] = []

    def add(
        name: str,
        category: str,
        passed: bool,
        *,
        safety: bool = False,
    ) -> None:
        checks.append(BenchmarkCheck(name, category, passed, safety))

    expected = scenario.expected
    add(
        "domain.resume",
        "domain_accuracy",
        observation.resume_domain.domain.value == expected.resume_domain,
    )
    add(
        "domain.target",
        "domain_accuracy",
        observation.target_domain.domain.value == expected.domain,
    )
    if expected.resume_family is not None:
        add(
            "domain.resume_family",
            "domain_accuracy",
            observation.resume_domain.job_family is not None
            and observation.resume_domain.job_family.value == expected.resume_family,
        )
    if expected.target_family is not None:
        add(
            "domain.target_family",
            "domain_accuracy",
            observation.target_domain.job_family is not None
            and observation.target_domain.job_family.value == expected.target_family,
        )
    add(
        "career_stage.value",
        "career_stage_accuracy",
        observation.career_stage.stage.value == expected.career_stage,
    )

    actual_requirements = {
        item.requirement: item for item in observation.explanation.requirements
    }
    for index, requirement in enumerate(expected.requirements, start=1):
        actual = actual_requirements.get(requirement.requirement)
        add(
            f"evidence.requirement.{index}.status",
            "requirement_coverage",
            actual is not None and actual.status.value == requirement.status,
        )
        if requirement.evidence_concepts:
            evidence_texts = tuple(
                item.text for item in actual.evidence
            ) if actual is not None else ()
            add(
                f"evidence.requirement.{index}.relevance",
                "evidence_relevance",
                all(
                    _contains(evidence_texts, concept)
                    for concept in requirement.evidence_concepts
                ),
            )
    if not expected.requirements:
        add(
            "evidence.requirements.none_unexpected",
            "requirement_coverage",
            not observation.explanation.requirements,
        )

    retained_evidence = tuple(
        item
        for requirement in observation.explanation.requirements
        for item in requirement.evidence
    )
    allowed_sources = {
        "summary",
        "experience",
        "project",
        "skill",
        "education",
        "certification",
        "language",
    }
    add(
        "evidence.grounded",
        "evidence_grounding",
        all(
            item.source in allowed_sources
            and item.text in observation.professional_evidence
            for item in retained_evidence
        ),
    )
    if not any(check.category == "evidence_relevance" for check in checks):
        add(
            "evidence.relevance.not_applicable",
            "evidence_relevance",
            True,
        )

    strength_values = tuple(
        value
        for item in observation.explanation.strengths
        for value in (item.summary, *item.related_requirements)
    )
    gap_values = tuple(
        value
        for item in observation.explanation.gaps
        for value in (item.summary, *item.related_requirements)
    ) + tuple(observation.public_result.gaps)
    risk_categories = tuple(item.category for item in observation.explanation.risks)

    _add_concept_checks(
        checks,
        prefix="explanation.strength",
        category="strength_correctness",
        expected_values=expected.strengths,
        actual_values=strength_values,
    )
    _add_concept_checks(
        checks,
        prefix="explanation.gap",
        category="gap_correctness",
        expected_values=expected.gaps,
        actual_values=gap_values,
    )
    if expected.risks:
        for index, risk in enumerate(expected.risks, start=1):
            add(
                f"explanation.risk.{index}",
                "risk_correctness",
                risk in risk_categories,
            )
    else:
        add(
            "explanation.risk.none_unexpected",
            "risk_correctness",
            not risk_categories,
        )

    expected_unknown = {
        item.requirement
        for item in expected.requirements
        if item.status == "unknown"
    }
    actual_unknown = {
        item.requirement
        for item in observation.explanation.requirements
        if item.status.value == "unknown"
    }
    unknown_requirements = expected_unknown | actual_unknown
    add(
        "safety.unknown_not_missing",
        "safety",
        not unknown_requirements.intersection(
            observation.public_result.missing_skills
        )
        and not any(
            item.category == "missing_capability"
            and unknown_requirements.intersection(item.related_requirements)
            for item in observation.explanation.gaps
        ),
        safety=True,
    )
    add(
        "safety.no_invented_experience",
        "safety",
        all(item.text in observation.professional_evidence for item in retained_evidence),
        safety=True,
    )
    searchable_output = " ".join(
        (
            *strength_values,
            *gap_values,
            *risk_categories,
            *observation.public_result.matched_skills,
            *observation.public_result.missing_skills,
            *observation.public_result.recommendations,
        )
    )
    add(
        "safety.no_unsupported_claims",
        "safety",
        not any(
            conclusion.casefold() in searchable_output.casefold()
            for conclusion in expected.forbidden_conclusions
        ),
        safety=True,
    )

    transition_expected = expected.transition
    if transition_expected is None:
        for name, category in (
            ("transition.type.not_applicable", "transition_type_accuracy"),
            ("transition.gaps.not_applicable", "transition_gap_grounding"),
            ("transition.risk.not_applicable", "transition_risk_calibration"),
            ("transition.actions.not_applicable", "transition_action_grounding"),
            ("transition.safety.not_applicable", "transition_safety"),
        ):
            add(name, category, True, safety=category == "transition_safety")
    else:
        transition = observation.career_transition
        if transition is None:
            raise ValueError("Transition expectation requires a transition observation.")
        add(
            "transition.type",
            "transition_type_accuracy",
            transition.transition_type.value == transition_expected.transition_type,
        )
        if transition_expected.transferable_skills:
            _add_concept_checks(
                checks,
                prefix="transition.transferable",
                category="transition_gap_grounding",
                expected_values=transition_expected.transferable_skills,
                actual_values=transition.transferable_skills,
            )
        _add_concept_checks(
            checks,
            prefix="transition.gap",
            category="transition_gap_grounding",
            expected_values=transition_expected.missing_capabilities,
            actual_values=tuple(gap.capability for gap in transition.missing_capabilities),
        )
        add(
            "transition.risk",
            "transition_risk_calibration",
            transition.transition_risk.level.value in transition_expected.risk_levels,
        )
        _add_concept_checks(
            checks,
            prefix="transition.action",
            category="transition_action_grounding",
            expected_values=transition_expected.action_gaps,
            actual_values=tuple(action.related_gap for action in transition.recommended_actions),
        )
        actual_action_gaps = tuple(
            action.related_gap for action in transition.recommended_actions
        )
        add(
            "transition.action.exact",
            "transition_action_grounding",
            len(actual_action_gaps) == len(set(actual_action_gaps))
            and len(actual_action_gaps) == len(transition_expected.action_gaps)
            and set(actual_action_gaps) == set(transition_expected.action_gaps),
        )
        add(
            "transition.action.linked",
            "transition_action_grounding",
            all(
                action_gap in {gap.capability for gap in transition.missing_capabilities}
                for action_gap in actual_action_gaps
            ),
        )
        transition_text = " ".join((
            *transition.transferable_skills,
            *(gap.capability for gap in transition.missing_capabilities),
            *transition.transition_risk.factors,
            *(action.objective for action in transition.recommended_actions),
            *(step for action in transition.recommended_actions for step in action.steps),
            *(action.expected_evidence for action in transition.recommended_actions),
        ))
        add(
            "transition.safety.no_forbidden_conclusions",
            "transition_safety",
            not any(
                value.casefold() in transition_text.casefold()
                for value in transition_expected.forbidden_conclusions
            ),
            safety=True,
        )

    base_metric_names = (
        "domain_accuracy",
        "career_stage_accuracy",
        "requirement_coverage",
        "evidence_relevance",
        "evidence_grounding",
        "strength_correctness",
        "gap_correctness",
        "risk_correctness",
    )
    transition_metric_names = (
        "transition_type_accuracy",
        "transition_gap_grounding",
        "transition_risk_calibration",
        "transition_action_grounding",
    )
    detailed_scores = {
        name: _score(checks, (name,))
        for name in (*base_metric_names, *transition_metric_names)
    }
    metrics = tuple(
        QualityMetric(name, detailed_scores[name]) for name in base_metric_names
    ) + (
        QualityMetric(
            "evidence_coverage",
            _average(
                detailed_scores[name]
                for name in (
                    "requirement_coverage",
                    "evidence_relevance",
                    "evidence_grounding",
                )
            ),
        ),
        QualityMetric(
            "explanation_completeness",
            _average(
                detailed_scores[name]
                for name in (
                    "strength_correctness",
                    "gap_correctness",
                    "risk_correctness",
                )
            ),
        ),
        QualityMetric("safety_pass_rate", _score(checks, ("safety",))),
    ) + tuple(
        QualityMetric(name, detailed_scores[name]) for name in transition_metric_names
    ) + (
        QualityMetric("transition_safety_pass_rate", _score(checks, ("transition_safety",))),
    )
    passed_checks = tuple(check.name for check in checks if check.passed)
    failed_checks = tuple(check.name for check in checks if not check.passed)
    safety_violations = tuple(
        check.name.removeprefix("safety.")
        for check in checks
        if check.safety and not check.passed
    )
    return ScenarioBenchmarkResult(
        scenario_id=scenario.scenario_id,
        passed=not failed_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        safety_violations=safety_violations,
        metrics=metrics,
    )


def _profile_from_fixture(payload: dict[str, Any]) -> ResumeProfile:
    return ResumeProfile(
        summary=payload.get("summary"),
        skills=list(payload.get("skills", [])),
        experience=[
            ExperienceEntry(**item) for item in payload.get("experience", [])
        ],
        education=[
            EducationEntry(**item) for item in payload.get("education", [])
        ],
        projects=[ProjectEntry(**item) for item in payload.get("projects", [])],
        certifications=list(payload.get("certifications", [])),
        languages=list(payload.get("languages", [])),
    )


def _professional_evidence(profile: ResumeProfile) -> tuple[str, ...]:
    values: list[str] = [profile.summary or "", *profile.skills]
    for entry in profile.experience:
        values.extend((entry.role or "", *entry.highlights))
    for entry in profile.education:
        values.extend(
            value or "" for value in (entry.degree, entry.field, entry.description)
        )
    for entry in profile.projects:
        values.extend(
            (entry.name or "", entry.description or "", *entry.technologies)
        )
    values.extend(profile.certifications)
    values.extend(profile.languages)
    return tuple(value for value in values if value)


def _contains(values: tuple[str, ...], concept: str) -> bool:
    target = concept.casefold()
    return any(target in value.casefold() for value in values)


def _add_concept_checks(
    checks: list[BenchmarkCheck],
    *,
    prefix: str,
    category: str,
    expected_values: tuple[str, ...],
    actual_values: tuple[str, ...],
) -> None:
    if expected_values:
        checks.extend(
            BenchmarkCheck(
                name=f"{prefix}.{index}",
                category=category,
                passed=_contains(actual_values, concept),
            )
            for index, concept in enumerate(expected_values, start=1)
        )
    else:
        checks.append(
            BenchmarkCheck(
                name=f"{prefix}.none_unexpected",
                category=category,
                passed=not actual_values,
            )
        )


def _score(checks: list[BenchmarkCheck], categories: tuple[str, ...]) -> int:
    applicable = [check.passed for check in checks if check.category in categories]
    if not applicable:
        return 100
    return round(100 * sum(applicable) / len(applicable))


def _average(scores: Iterable[int]) -> int:
    values = list(scores)
    return round(sum(values) / len(values)) if values else 100
