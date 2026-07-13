import unittest
from dataclasses import FrozenInstanceError, fields

from skill.career.stages import (
    CareerStage,
    CareerStageAssessment,
    StageConfidence,
    StageSignals,
    legacy_career_level,
)


class CareerStageSchemaTests(unittest.TestCase):
    def test_internal_stage_taxonomy_and_legacy_mapping_are_frozen(self):
        self.assertEqual(
            [stage.value for stage in CareerStage],
            ["entry", "developing", "experienced", "advanced", "unknown"],
        )
        self.assertEqual(
            [confidence.value for confidence in StageConfidence],
            ["high", "medium", "low"],
        )
        self.assertEqual(
            {
                CareerStage.ENTRY: "junior",
                CareerStage.DEVELOPING: "mid",
                CareerStage.EXPERIENCED: "senior",
                CareerStage.ADVANCED: "lead",
                CareerStage.UNKNOWN: "unknown",
            },
            {stage: legacy_career_level(stage) for stage in CareerStage},
        )

    def test_internal_assessment_keeps_typed_signal_categories(self):
        assessment = CareerStageAssessment(
            stage=CareerStage.DEVELOPING,
            signals=StageSignals(
                experience=("3 years",),
                responsibility=("owned process",),
                impact=("reduced turnaround time",),
            ),
            confidence=StageConfidence.HIGH,
        )

        self.assertEqual(
            [field.name for field in fields(CareerStageAssessment)],
            ["stage", "signals", "confidence"],
        )
        self.assertEqual(assessment.signals.experience, ("3 years",))
        with self.assertRaises(FrozenInstanceError):
            assessment.stage = CareerStage.ENTRY


if __name__ == "__main__":
    unittest.main()
