"""Deterministic, offline quality checks for optional AI enhancement output."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from skill.ai.schemas import AIEnhancementResult


@dataclass(frozen=True, slots=True)
class AIQualityCase:
    """A fully synthetic contract for one resume enhancement evaluation."""

    case_id: str
    improvement_result: dict[str, Any]
    original_facts: tuple[str, ...]
    prohibited_content: tuple[str, ...]
    expected_directions: tuple[str, ...]
    keywords: tuple[str, ...]
    min_output_length: int
    max_output_length: int


@dataclass(frozen=True, slots=True)
class AIQualityCheck:
    """A single deterministic quality gate result."""

    name: str
    passed: bool


@dataclass(frozen=True, slots=True)
class AIQualityEvaluationResult:
    """Serializable, offline-only evaluation summary."""

    case_id: str
    success: bool
    checks: tuple[AIQualityCheck, ...]
    score: int
    failures: list[str]
    output_length: int

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation without model output."""
        return asdict(self)


def load_cases(directory: Path) -> list[AIQualityCase]:
    """Load stable synthetic cases in filename order."""
    cases: list[AIQualityCase] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        cases.append(
            AIQualityCase(
                case_id=payload["case_id"],
                improvement_result=payload["improvement_result"],
                original_facts=tuple(payload["original_facts"]),
                prohibited_content=tuple(payload["prohibited_content"]),
                expected_directions=tuple(payload["expected_directions"]),
                keywords=tuple(payload.get("keywords", [])),
                min_output_length=payload["output_length"]["min"],
                max_output_length=payload["output_length"]["max"],
            )
        )
    return cases


def evaluate_enhancement(
    case: AIQualityCase,
    enhancement: AIEnhancementResult,
    source_result: dict[str, Any],
) -> AIQualityEvaluationResult:
    """Evaluate a structured provider result without exposing its error detail."""
    output = enhancement.enhanced_content if enhancement.success else ""
    return _evaluate(case, output, source_result, enhancement.success)


def evaluate_case(
    case: AIQualityCase,
    output: str | None,
    source_result: dict[str, Any],
) -> AIQualityEvaluationResult:
    """Evaluate deterministic text while treating a non-empty string as success."""
    return _evaluate(case, output, source_result, bool(output))


def _evaluate(
    case: AIQualityCase,
    output: str | None,
    source_result: dict[str, Any],
    provider_success: bool,
) -> AIQualityEvaluationResult:
    text = output if isinstance(output, str) else ""
    lowered = text.lower()
    checks = (
        AIQualityCheck("provider_success", provider_success),
        AIQualityCheck("non_empty_output", bool(text.strip())),
        AIQualityCheck(
            "output_length",
            case.min_output_length <= len(text) <= case.max_output_length,
        ),
        AIQualityCheck(
            "expected_direction",
            any(direction.lower() in lowered for direction in case.expected_directions),
        ),
        AIQualityCheck(
            "facts_preserved",
            all(fact.lower() in lowered for fact in case.original_facts),
        ),
        AIQualityCheck(
            "prohibited_content",
            not any(content.lower() in lowered for content in case.prohibited_content),
        ),
        AIQualityCheck(
            "sensitive_information",
            not any(marker in lowered for marker in ("authorization:", "bearer ", "api key", "endpoint", "http://", "https://", "sk-")),
        ),
        AIQualityCheck(
            "provider_internal_error",
            not any(marker in lowered for marker in ("traceback", "providererror", "exception", "stack trace")),
        ),
        AIQualityCheck("serializable", _is_serializable(case.case_id, text)),
        AIQualityCheck("core_unchanged", source_result == case.improvement_result),
    )
    failures = [check.name for check in checks if not check.passed]
    return AIQualityEvaluationResult(
        case_id=case.case_id,
        success=not failures,
        checks=checks,
        score=sum(check.passed for check in checks),
        failures=failures,
        output_length=len(text),
    )


def _is_serializable(case_id: str, output: str) -> bool:
    """Check the result shape without retaining or reporting generated text."""
    try:
        json.dumps({"case_id": case_id, "output_length": len(output)})
    except (TypeError, ValueError):
        return False
    return True
