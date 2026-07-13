"""Load stable synthetic Career Intelligence benchmark scenarios."""

from __future__ import annotations

import json
from pathlib import Path

from benchmark.schemas import (
    BenchmarkScenario,
    ExpectedRequirement,
    ScenarioExpectation,
)


def load_scenarios(directory: Path) -> list[BenchmarkScenario]:
    scenarios: list[BenchmarkScenario] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("fictional") is not True:
            raise ValueError(f"Benchmark scenario must be fictional: {path.name}")
        expected = payload["expected"]
        scenarios.append(
            BenchmarkScenario(
                scenario_id=payload["scenario_id"],
                title=payload["title"],
                fictional=True,
                resume_fixture=payload["resume_fixture"],
                target_role=payload["target"]["role"],
                target_jd=payload["target"]["job_description"],
                expected=ScenarioExpectation(
                    resume_domain=expected["resume_domain"],
                    domain=expected["domain"],
                    resume_family=expected.get("resume_family"),
                    target_family=expected.get("target_family"),
                    career_stage=expected["career_stage"],
                    requirements=tuple(
                        ExpectedRequirement(
                            requirement=item["requirement"],
                            status=item["status"],
                            evidence_concepts=tuple(
                                item.get("evidence_concepts", [])
                            ),
                        )
                        for item in expected["requirements"]
                    ),
                    strengths=tuple(expected["strengths"]),
                    gaps=tuple(expected["gaps"]),
                    risks=tuple(expected["risks"]),
                    forbidden_conclusions=tuple(
                        expected["forbidden_conclusions"]
                    ),
                ),
            )
        )
    return scenarios
