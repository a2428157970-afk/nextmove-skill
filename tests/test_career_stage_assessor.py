import unittest
from dataclasses import FrozenInstanceError, fields

from skill.career.stages import (
    CareerStage,
    CareerStageAssessment,
    StageConfidence,
    StageSignals,
    legacy_career_level,
)
from skill.career.stage_assessor import CareerStageAssessor
from skill.schemas.resume import ExperienceEntry, ProjectEntry, ResumeProfile


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


class CareerStageAssessorTests(unittest.TestCase):
    def setUp(self):
        self.assessor = CareerStageAssessor()

    def test_new_graduate_with_project_evidence_is_entry(self):
        profile = ResumeProfile(
            summary="Recent graduate seeking a junior analyst role.",
            skills=["Excel", "SQL"],
            projects=[
                ProjectEntry(
                    name="Campus service project",
                    description="Built a reporting dashboard for a student organisation.",
                )
            ],
        )

        result = self.assessor.assess(profile)

        self.assertEqual(result.stage, CareerStage.ENTRY)
        self.assertTrue(result.signals.experience)

    def test_independent_two_to_three_year_professional_is_developing(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Operations Specialist",
                    start_date="2022-01",
                    end_date="2025-01",
                    highlights=[
                        "Owned the onboarding workflow and coordinated cross-functional stakeholders."
                    ],
                )
            ]
        )

        result = self.assessor.assess(profile)

        self.assertEqual(result.stage, CareerStage.DEVELOPING)
        self.assertIn("owned scope", result.signals.responsibility)

    def test_five_year_expert_with_complex_impact_is_experienced(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Senior Engineer",
                    start_date="2017-01",
                    end_date="2024-01",
                    highlights=[
                        "Led a complex platform migration across product and finance teams.",
                        "Improved service reliability by 35%.",
                    ],
                )
            ]
        )

        result = self.assessor.assess(profile)

        self.assertEqual(result.stage, CareerStage.EXPERIENCED)
        self.assertTrue(result.signals.impact)

    def test_management_scope_and_impact_are_advanced(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Engineering Manager",
                    start_date="2016-01",
                    end_date="2024-01",
                    highlights=[
                        "Managed a team of 8 and mentored engineering leads.",
                        "Owned platform strategy and reduced annual infrastructure cost by 20%.",
                    ],
                )
            ]
        )

        result = self.assessor.assess(profile)

        self.assertEqual(result.stage, CareerStage.ADVANCED)
        self.assertIn("people leadership", result.signals.responsibility)

    def test_career_changer_retains_transferable_experienced_stage(self):
        profile = ResumeProfile(
            summary="Transitioning from finance operations into business operations.",
            experience=[
                ExperienceEntry(
                    role="Finance Manager",
                    start_date="2015-01",
                    end_date="2024-01",
                    highlights=[
                        "Owned a cross-functional reporting process for regional teams.",
                        "Reduced monthly close time by 25%.",
                    ],
                )
            ],
        )

        result = self.assessor.assess(profile)

        self.assertGreaterEqual(
            [CareerStage.ENTRY, CareerStage.DEVELOPING, CareerStage.EXPERIENCED, CareerStage.ADVANCED].index(result.stage),
            2,
        )

    def test_title_or_duration_alone_cannot_inflate_stage(self):
        title_only = self.assessor.assess(
            ResumeProfile(experience=[ExperienceEntry(role="Engineering Manager")])
        )
        duration_only = self.assessor.assess(
            ResumeProfile(
                experience=[
                    ExperienceEntry(
                        role="Engineer",
                        start_date="2010-01",
                        end_date="2024-01",
                    )
                ]
            )
        )

        self.assertNotEqual(title_only.stage, CareerStage.ADVANCED)
        self.assertEqual(duration_only.stage, CareerStage.DEVELOPING)

    def test_repeated_bare_roles_cannot_inflate_to_advanced(self):
        result = self.assessor.assess(
            ResumeProfile(
                experience=[
                    ExperienceEntry(role="Specialist"),
                    ExperienceEntry(role="Specialist"),
                    ExperienceEntry(role="Specialist"),
                ]
            )
        )

        self.assertNotEqual(result.stage, CareerStage.ADVANCED)

    def test_empty_and_invalid_date_profiles_do_not_invent_evidence(self):
        empty = self.assessor.assess(ResumeProfile())
        invalid_dates = self.assessor.assess(
            ResumeProfile(
                experience=[
                    ExperienceEntry(
                        role="Specialist",
                        start_date="2025-01",
                        end_date="2022-01",
                    )
                ]
            )
        )

        self.assertEqual(empty.stage, CareerStage.UNKNOWN)
        self.assertEqual(empty.confidence, StageConfidence.LOW)
        self.assertNotIn("dated experience", invalid_dates.signals.experience)

    def test_single_responsibility_claim_without_experience_stays_unknown(self):
        result = self.assessor.assess(ResumeProfile(summary="Owned a workflow."))

        self.assertEqual(result.stage, CareerStage.UNKNOWN)
        self.assertEqual(result.confidence, StageConfidence.LOW)

    def test_cumulative_valid_dates_and_stated_duration_support_developing(self):
        dated = self.assessor.assess(
            ResumeProfile(
                experience=[
                    ExperienceEntry(role="Analyst", start_date="2021-01", end_date="2022-01"),
                    ExperienceEntry(role="Analyst", start_date="2022-01", end_date="2023-01"),
                    ExperienceEntry(role="Analyst", start_date="2023-01", end_date="2024-01"),
                ]
            )
        )
        stated = self.assessor.assess(ResumeProfile(summary="3 years of experience."))

        self.assertEqual(dated.stage, CareerStage.DEVELOPING)
        self.assertIn("2+ years experience", dated.signals.experience)
        self.assertEqual(stated.stage, CareerStage.DEVELOPING)
        self.assertIn("2+ years experience", stated.signals.experience)

    def test_internal_is_not_internship_evidence(self):
        result = self.assessor.assess(ResumeProfile(raw_text="Built internal reporting tools."))

        self.assertEqual(result.stage, CareerStage.UNKNOWN)
        self.assertNotIn("internship evidence", result.signals.experience)

    def test_chinese_responsibility_and_impact_signals_are_recognized(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="运营经理",
                    start_date="2018-01",
                    end_date="2024-01",
                    highlights=[
                        "独立负责跨部门运营流程，带领6人团队。",
                        "将处理时效提升30%。",
                    ],
                )
            ]
        )

        result = self.assessor.assess(profile)

        self.assertEqual(result.stage, CareerStage.ADVANCED)
        self.assertTrue(result.signals.responsibility)
        self.assertTrue(result.signals.impact)


if __name__ == "__main__":
    unittest.main()
