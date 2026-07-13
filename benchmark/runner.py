"""Content-safe runner for the offline Career Intelligence benchmark."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from benchmark.evaluator import (
    ScenarioBenchmarkResult,
    evaluate_scenario,
    observe_scenario,
)
from benchmark.loader import load_scenarios


AGGREGATE_METRICS = (
    "domain_accuracy",
    "career_stage_accuracy",
    "evidence_coverage",
    "explanation_completeness",
    "safety_pass_rate",
    "transition_type_accuracy",
    "transition_gap_grounding",
    "transition_risk_calibration",
    "transition_action_grounding",
    "transition_safety_pass_rate",
)


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    summary: dict[str, int]
    metrics: dict[str, int]
    scenario_results: tuple[ScenarioBenchmarkResult, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_benchmark(scenario_directory: Path | None = None) -> BenchmarkReport:
    directory = scenario_directory or _default_scenario_directory()
    results = tuple(
        evaluate_scenario(scenario, observe_scenario(scenario))
        for scenario in load_scenarios(directory)
    )
    passed = sum(result.passed for result in results)
    return BenchmarkReport(
        summary={
            "scenario_count": len(results),
            "passed_scenarios": passed,
            "failed_scenarios": len(results) - passed,
            "safety_violations": sum(
                len(result.safety_violations) for result in results
            ),
            "network_calls": 0,
        },
        metrics={
            name: _average_metric(results, name) for name in AGGREGATE_METRICS
        },
        scenario_results=results,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the offline Career Intelligence quality benchmark."
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)
    report = run_benchmark()
    payload = report.to_dict()
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_text_report(report)
    return int(report.summary["failed_scenarios"] > 0)


def _default_scenario_directory() -> Path:
    return Path(__file__).resolve().parents[1] / "tests" / "benchmark" / "scenarios"


def _average_metric(
    results: tuple[ScenarioBenchmarkResult, ...],
    metric_name: str,
) -> int:
    scores = [
        metric.score
        for result in results
        for metric in result.metrics
        if metric.name == metric_name
    ]
    return round(sum(scores) / len(scores)) if scores else 0


def _print_text_report(report: BenchmarkReport) -> None:
    print(
        "Career Intelligence Benchmark: "
        f"{report.summary['passed_scenarios']}/"
        f"{report.summary['scenario_count']} scenarios passed"
    )
    for name, score in report.metrics.items():
        print(f"- {name}: {score}")
    for result in report.scenario_results:
        status = "passed" if result.passed else "failed"
        failed = ",".join(result.failed_checks) or "none"
        violations = ",".join(result.safety_violations) or "none"
        print(
            f"- {result.scenario_id}: {status}; "
            f"failed_checks={failed}; safety_violations={violations}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
