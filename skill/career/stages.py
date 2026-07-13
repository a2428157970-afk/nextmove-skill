"""Internal career-stage contracts and legacy output mapping."""

from dataclasses import dataclass
from enum import Enum


class CareerStage(str, Enum):
    ENTRY = "entry"
    DEVELOPING = "developing"
    EXPERIENCED = "experienced"
    ADVANCED = "advanced"
    UNKNOWN = "unknown"


class StageConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class StageSignals:
    experience: tuple[str, ...] = ()
    responsibility: tuple[str, ...] = ()
    impact: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CareerStageAssessment:
    stage: CareerStage
    signals: StageSignals
    confidence: StageConfidence


_LEGACY_CAREER_LEVELS = {
    CareerStage.ENTRY: "junior",
    CareerStage.DEVELOPING: "mid",
    CareerStage.EXPERIENCED: "senior",
    CareerStage.ADVANCED: "lead",
    CareerStage.UNKNOWN: "unknown",
}


def legacy_career_level(stage: CareerStage) -> str:
    """Map an internal stage to the frozen public career-level contract."""

    return _LEGACY_CAREER_LEVELS[stage]
