"""Run deterministic, offline-only AI enhancement quality evaluation."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skill.ai import AIProviderSettings, MockProviderAdapter, ProviderUnavailableError, ResumeAIEnhancer
from skill.improvement.schemas import ResumeImprovementResult
from tests.quality.evaluator import AIQualityCase, evaluate_enhancement, load_cases


class FixedResponseProvider(MockProviderAdapter):
    """Return a fixed synthetic response without network or credential access."""

    def __init__(self, settings: AIProviderSettings, response: str | Exception):
        super().__init__(settings)
        self.response = response

    def generate(self, prompt: str, context: dict) -> str:
        del prompt, context
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def _response_for(case: AIQualityCase, scenario: str) -> str | Exception:
    """Create a stable synthetic provider response for the requested scenario."""
    if scenario == "empty":
        return ""
    if scenario == "provider-error":
        return ProviderUnavailableError()
    if scenario == "invalid-json":
        return "not json"
    if scenario == "wrong-version":
        return '{"contract_version":"wrong"}'
    if scenario == "fenced-json":
        return "```json\n{}\n```"

    safe_output = json.dumps({"contract_version":"resume-improvement.v1","summary":f"Focus on {case.expected_directions[0]}.","rewritten_content":f"{' '.join(case.original_facts)} Keep every claim factual.","improvement_points":[case.expected_directions[0]],"keyword_suggestions":list(case.keywords),"factual_warnings":[]})
    if scenario == "fabricated":
        return f"{safe_output} {case.prohibited_content[0]}."
    return safe_output


def _improvement_result(case: AIQualityCase) -> ResumeImprovementResult:
    """Convert fixture data to the existing structured Core result type."""
    return ResumeImprovementResult(**case.improvement_result)


def run_evaluation(scenario: str = "pass") -> dict[str, Any]:
    """Evaluate all fixture cases and return a content-safe summary."""
    fixture_directory = PROJECT_ROOT / "tests" / "fixtures" / "ai_quality"
    settings = AIProviderSettings(provider_name="quality-mock", model_name="offline")
    evaluations = []

    for case in load_cases(fixture_directory):
        core_result = _improvement_result(case)
        source_snapshot = asdict(core_result)
        provider = FixedResponseProvider(settings, _response_for(case, scenario))
        enhancement = ResumeAIEnhancer(provider).enhance(core_result)
        evaluations.append(evaluate_enhancement(case, enhancement, asdict(core_result)))
        if source_snapshot != asdict(core_result):
            raise RuntimeError("Rule-based result was modified during evaluation")

    passed = sum(result.success for result in evaluations)
    return {
        "summary": {
            "total_cases": len(evaluations),
            "passed_cases": passed,
            "failed_cases": len(evaluations) - passed,
            "network_calls": 0,
        },
        "results": [result.to_dict() for result in evaluations],
    }


def _render_markdown(report: dict[str, Any]) -> str:
    """Render a summary that intentionally excludes model and resume content."""
    summary = report["summary"]
    lines = [
        "# AI Quality Evaluation",
        "",
        f"- Cases: {summary['total_cases']}",
        f"- Passed: {summary['passed_cases']}",
        f"- Failed: {summary['failed_cases']}",
        f"- Network calls: {summary['network_calls']}",
        "",
        "| Case | Status | Score | Output length | Failed checks |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for result in report["results"]:
        failures = ", ".join(result["failures"]) or "—"
        status = "PASS" if result["success"] else "FAIL"
        lines.append(
            f"| {result['case_id']} | {status} | {result['score']} | "
            f"{result['output_length']} | {failures} |"
        )
    return "\n".join(lines)


def main() -> int:
    """Run the requested offline scenario and return a documented exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--scenario",
        choices=("pass", "fabricated", "empty", "provider-error", "invalid-json", "wrong-version", "fenced-json"),
        default="pass",
    )
    args = parser.parse_args()
    try:
        report = run_evaluation(args.scenario)
    except (KeyError, TypeError, ValueError, OSError) as error:
        print(f"AI quality evaluation configuration error: {error}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_render_markdown(report))
    return 0 if report["summary"]["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
