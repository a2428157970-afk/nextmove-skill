"""Utility helpers for external Skill consumers."""

from dataclasses import fields, is_dataclass
from typing import Any, Mapping


def to_dict(value: Any) -> dict[str, Any]:
    """Convert a Skill result or response object into a JSON-serializable dict."""
    converted = _to_json_value(value)
    if not isinstance(converted, dict):
        raise TypeError("to_dict() expects a dataclass or mapping value")
    return converted


def _to_json_value(value: Any) -> Any:
    if is_dataclass(value):
        return {
            field.name: _to_json_value(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, Mapping):
        return {str(key): _to_json_value(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_json_value(item) for item in value]

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    raise TypeError(f"{type(value).__name__} is not JSON serializable")


__all__ = ["to_dict"]
