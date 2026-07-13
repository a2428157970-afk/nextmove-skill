import json
import unittest
from dataclasses import FrozenInstanceError, fields

from skill.reporting.schemas import (
    ActionHorizon,
    ActionPlan,
    CapabilityGap,
    CareerStageNarrative,
    CurrentCareerProfile,
    HumanCareerReport,
    JobFitLevel,
    JobFitNarrative,
    ReportAction,
    ReportConfidence,
    ReportConfidenceLevel,
    ReportEvidence,
    ReportRisk,
    ReportStrength,
    TransitionPathNarrative,
)


def sample_report() -> HumanCareerReport:
    evidence = ReportEvidence(
        text="Owned recruitment delivery.",
        source="experience",
        confidence=ReportConfidenceLevel.HIGH,
    )
    return HumanCareerReport(
        career_summary="当前证据显示职业方向与目标岗位较一致。",
        current_profile=CurrentCareerProfile(
            current_domain="human_resources",
            core_capabilities=("Recruitment",),
            profile_summary="当前主要积累在人力资源领域。",
        ),
        career_stage=CareerStageNarrative(
            stage="developing",
            explanation="当前处于能力发展阶段。",
            evidence_signals=("four years",),
            confidence=ReportConfidenceLevel.MEDIUM,
        ),
        strengths=(
            ReportStrength(
                capability="Recruitment",
                explanation="现有经历支持该能力。",
                evidence=(evidence,),
            ),
        ),
        job_fit=JobFitNarrative(
            match_score=82,
            level=JobFitLevel.STRONG,
            summary="当前材料覆盖多数岗位要求。",
            why_fit=("Recruitment",),
            main_gaps=("Administration",),
        ),
        capability_gaps=(
            CapabilityGap(
                capability="Administration",
                status="unknown",
                explanation="尚未看到直接证据。",
                evidence_needed="补充行政事务案例。",
            ),
        ),
        transition_path=TransitionPathNarrative(
            current_domain="human_resources",
            target_domain="human_resources",
            transition_type="same_role",
            summary="职业路径延续性较强。",
            transferable_capabilities=(),
            missing_capabilities=("Administration",),
        ),
        action_plan=ActionPlan(
            immediate=(
                ReportAction(
                    horizon=ActionHorizon.IMMEDIATE,
                    priority=1,
                    related_gap="Administration",
                    objective="补充证据。",
                    steps=("整理案例",),
                    expected_evidence="一个可核验案例",
                ),
            ),
            short_term=(),
            long_term=(),
        ),
        risks=(
            ReportRisk(
                note="部分要求仍需验证。",
                basis=("Administration",),
                verification="建议核对实际职责。",
            ),
        ),
        confidence=ReportConfidence(
            level=ReportConfidenceLevel.MEDIUM,
            explanation="证据基本可用。",
            missing_information=("行政职责细节",),
        ),
    )


class HumanCareerReportSchemaTests(unittest.TestCase):
    def test_report_is_immutable_and_has_exact_top_level_fields(self):
        report = sample_report()

        self.assertEqual(
            [field.name for field in fields(HumanCareerReport)],
            [
                "career_summary",
                "current_profile",
                "career_stage",
                "strengths",
                "job_fit",
                "capability_gaps",
                "transition_path",
                "action_plan",
                "risks",
                "confidence",
            ],
        )
        with self.assertRaises(FrozenInstanceError):
            report.career_summary = "changed"

    def test_to_dict_is_json_serializable_and_normalizes_nested_values(self):
        payload = sample_report().to_dict()

        self.assertEqual(payload["job_fit"]["level"], "strong")
        self.assertEqual(payload["action_plan"]["immediate"][0]["horizon"], "immediate")
        self.assertIsInstance(payload["strengths"], list)
        json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
