import json
import unittest
from pathlib import Path

from benchmark.evaluator import _profile_from_fixture
from benchmark.loader import load_scenarios
from skill.analysis.analyzer import ResumeAnalyzer
from skill.career.stage_assessor import CareerStageAssessor
from skill.career.transition import CareerTransitionAssessor, TargetRoleLevelAssessor
from skill.matching.classifier import DomainClassifier
from skill.matching.matcher import JobMatcher
from skill.reporting.builder import HumanCareerReportBuilder
from skill.reporting.formatter import HumanCareerReportFormatter
from skill.reporting.schemas import JobFitLevel, ReportConfidenceLevel


SCENARIO_DIR = Path(__file__).parent / "benchmark" / "scenarios"


def build_report(
    scenario_id: str,
    *,
    target_role: str | None = None,
    target_jd: str | None = None,
):
    scenario = next(
        item
        for item in load_scenarios(SCENARIO_DIR)
        if item.scenario_id == scenario_id
    )
    profile = _profile_from_fixture(scenario.resume_fixture)
    role = target_role or scenario.target_role
    job_description = target_jd or scenario.target_jd
    matcher = JobMatcher()
    assessment, explanation = matcher._assess_and_explain(profile, job_description)
    classifier = DomainClassifier()
    current = classifier.classify_profile(profile)
    target = classifier.classify_text(job_description)
    stage = CareerStageAssessor().assess(profile)
    transition = CareerTransitionAssessor().assess(
        current,
        target,
        stage,
        assessment.transferability,
        explanation,
        TargetRoleLevelAssessor().classify(f"{role} {job_description}"),
    )
    return HumanCareerReportBuilder().build(
        ResumeAnalyzer().analyze(profile),
        matcher.match(profile, job_description),
        stage,
        explanation,
        transition,
    )


class HumanCareerReportScenarioTests(unittest.TestCase):
    def assert_safe_report(self, report) -> None:
        rendered = json.dumps(report.to_dict(), ensure_ascii=False).casefold()
        for forbidden in (
            "guarantee",
            "impossible",
            "unsuitable",
            "你一定成功",
            "你不适合",
            "你无法转型",
            "保证拿 offer",
        ):
            self.assertNotIn(forbidden.casefold(), rendered)

    def test_hr_specialist_same_role_emphasizes_evidence_backed_strengths(self):
        report = build_report(
            "hr-specialist",
            target_role="Recruitment Specialist",
            target_jd=(
                "Recruitment Specialist role requiring recruitment and attendance."
            ),
        )

        self.assertEqual(report.job_fit.match_score, 100)
        self.assertEqual(report.job_fit.level, JobFitLevel.STRONG)
        self.assertEqual(report.transition_path.transition_type, "same_role")
        self.assertGreaterEqual(len(report.strengths), 2)
        self.assertTrue(all(item.evidence for item in report.strengths))
        self.assertFalse(report.capability_gaps)
        self.assertFalse(report.action_plan.immediate)
        self.assert_safe_report(report)

    def test_sales_to_product_manager_preserves_migration_path_and_action_links(self):
        report = build_report("sales-to-product-manager")

        self.assertEqual(report.transition_path.current_domain, "sales")
        self.assertEqual(report.transition_path.target_domain, "product")
        self.assertEqual(report.transition_path.transition_type, "cross_domain")
        gap_names = {item.capability for item in report.capability_gaps}
        transition_gaps = {
            "Product Planning",
            "PRD",
            "Product Delivery Ownership",
        }
        self.assertTrue(transition_gaps.issubset(gap_names))
        actions = (
            *report.action_plan.immediate,
            *report.action_plan.short_term,
            *report.action_plan.long_term,
        )
        self.assertEqual({item.related_gap for item in actions}, transition_gaps)
        self.assertTrue(all(item.evidence for item in report.strengths))
        rendered = HumanCareerReportFormatter().to_markdown(report).casefold()
        self.assertNotIn("direct product experience", rendered)
        self.assertNotIn("owned a product roadmap", rendered)
        self.assert_safe_report(report)

    def test_information_insufficient_requests_more_information_without_verdicts(self):
        report = build_report("information-insufficient-resume")

        self.assertEqual(report.current_profile.current_domain, "unknown")
        self.assertEqual(report.career_stage.stage, "unknown")
        self.assertEqual(report.job_fit.level, JobFitLevel.INSUFFICIENT_EVIDENCE)
        self.assertEqual(report.confidence.level, ReportConfidenceLevel.LOW)
        self.assertFalse(report.strengths)
        self.assertIn(
            "目标岗位的具体要求",
            report.confidence.missing_information,
        )
        self.assertIn(
            "简历中的职责、技能与成果",
            report.confidence.missing_information,
        )
        self.assert_safe_report(report)


if __name__ == "__main__":
    unittest.main()
