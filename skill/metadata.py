"""Metadata for Agent discovery of the NextMove Skill."""

import json
import sysconfig
from pathlib import Path
from typing import Any

from skill.__version__ import __version__


def _manifest_paths() -> tuple[Path, ...]:
    return (
        Path(__file__).resolve().parents[1] / "skill.json",
        Path(sysconfig.get_path("data"))
        / "share"
        / "nextmove-skill"
        / "skill.json",
    )


def _load_manifest() -> dict[str, Any]:
    for path in _manifest_paths():
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    raise RuntimeError("installed NextMove skill.json manifest was not found")


SKILL_METADATA = _load_manifest()
SKILL_METADATA["version"] = __version__

CAPABILITY_DESCRIPTIONS = SKILL_METADATA["capability_descriptions"]
CAREER_ANALYSIS_INPUT_SCHEMA = SKILL_METADATA["input_schema"]
CAREER_ANALYSIS_RESPONSE_SCHEMA = SKILL_METADATA["output_schema"]


__all__ = [
    "CAPABILITY_DESCRIPTIONS",
    "CAREER_ANALYSIS_INPUT_SCHEMA",
    "CAREER_ANALYSIS_RESPONSE_SCHEMA",
    "SKILL_METADATA",
]
