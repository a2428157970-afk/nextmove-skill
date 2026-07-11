"""Internal JSON contract for validated resume AI enhancement output."""

from dataclasses import asdict, dataclass, field
import json

RESUME_IMPROVEMENT_CONTRACT_VERSION = "resume-improvement.v1"

@dataclass(frozen=True, slots=True)
class ResumeAIOutput:
    contract_version: str
    summary: str
    rewritten_content: str
    improvement_points: list[str] = field(default_factory=list)
    keyword_suggestions: list[str] = field(default_factory=list)
    factual_warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

def parse_resume_ai_output(raw: str) -> ResumeAIOutput | None:
    if not isinstance(raw, str) or not raw.strip() or raw.strip() != raw:
        return None
    lowered = raw.lower()
    if raw.startswith("```") or any(marker in lowered for marker in ("traceback", "exception", "stack trace", "providererror")):
        return None
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return None
    required = {"contract_version", "summary", "rewritten_content", "improvement_points", "keyword_suggestions", "factual_warnings"}
    if not isinstance(payload, dict) or set(payload) != required or payload.get("contract_version") != RESUME_IMPROVEMENT_CONTRACT_VERSION:
        return None
    if not isinstance(payload["summary"], str) or not isinstance(payload["rewritten_content"], str):
        return None
    if not payload["summary"].strip() and not payload["rewritten_content"].strip():
        return None
    lists = ("improvement_points", "keyword_suggestions", "factual_warnings")
    if any(not isinstance(payload[name], list) or not all(isinstance(item, str) for item in payload[name]) for name in lists):
        return None
    return ResumeAIOutput(**payload)
