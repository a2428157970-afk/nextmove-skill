"""Internal schemas for synthetic Career Intelligence benchmark scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExpectedRequirement:
    requirement: str
    status: str
    evidence_concepts: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScenarioExpectation:
    resume_domain: str
    domain: str
    resume_family: str | None
    target_family: str | None
    career_stage: str
    requirements: tuple[ExpectedRequirement, ...]
    strengths: tuple[str, ...]
    gaps: tuple[str, ...]
    risks: tuple[str, ...]
    forbidden_conclusions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BenchmarkScenario:
    scenario_id: str
    title: str
    fictional: bool
    resume_fixture: dict[str, Any]
    target_role: str
    target_jd: str
    expected: ScenarioExpectation
