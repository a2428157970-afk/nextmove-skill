import unittest
from dataclasses import fields

from skill import NextMoveSkill
from skill.matching import JobMatcher
from skill.matching.explanations import MatchExplanationResult
from skill.matching.schemas import (
    EvidenceConfidence,
    EvidenceItem,
    JobMatchResult,
    MatchAssessment,
    MatchConfidence,
    RequirementEvidence,
    RequirementStatus,
)
from skill.schemas.resume import ExperienceEntry, ResumeProfile
from skill.utils import to_dict


class FixedAssessmentScorer:
    def __init__(self, assessment):
        self.assessment = assessment

    def assess(self, profile, job_description, resume_classification, job_classification):
        return self.assessment


class JobMatcherExplanationFacadeTests(unittest.TestCase):
    @staticmethod
    def requirement(
        name,
        status,
        confidence=EvidenceConfidence.LOW,
        evidence=(),
        kind="skill",
    ):
        return RequirementEvidence(
            requirement=name,
            kind=kind,
            status=status,
            evidence=tuple(
                EvidenceItem(text=text, source=source)
                for text, source in evidence
            ),
            confidence=confidence,
        )

    @staticmethod
    def assessment(requirements, domain_score=100):
        return MatchAssessment(
            score=72,
            confidence=MatchConfidence.MEDIUM,
            domain_score=domain_score,
            skill_score=72,
            qualification_score=None,
            requirements=tuple(requirements),
        )

    def matcher_with_assessment(self, assessment):
        matcher = JobMatcher()
        matcher.scorer = FixedAssessmentScorer(assessment)
        return matcher

    def test_hr_facade_builds_internal_explanation_from_real_scorer(self):
        profile = ResumeProfile(
            skills=["Recruitment", "Attendance"],
            experience=[
                ExperienceEntry(
                    role="Recruitment Specialist",
                    highlights=["Led campus recruitment and employee attendance."],
                )
            ],
        )
        job_description = (
            "Recruitment specialist requiring recruitment, attendance, "
            "and administrative affairs."
        )
        matcher = JobMatcher()

        assessment, explanation = matcher._assess_and_explain(
            profile,
            job_description,
        )

        self.assertIsInstance(explanation, MatchExplanationResult)
        self.assertEqual(explanation.requirements, assessment.requirements)
        administrative = next(
            item
            for item in explanation.requirements
            if item.requirement == "行政事务"
        )
        self.assertEqual(administrative.kind, "responsibility")
        strength_text = " ".join(item.summary for item in explanation.strengths)
        gap_text = " ".join(item.summary for item in explanation.gaps)
        self.assertIn("招聘", strength_text)
        self.assertIn("考勤", strength_text)
        self.assertIn("行政事务", gap_text)
        self.assertIn("not evidenced", gap_text)

    def test_sales_to_product_facade_maps_career_transition_risk(self):
        requirements = (
            self.requirement(
                "客户洞察",
                RequirementStatus.MATCHED,
                EvidenceConfidence.MEDIUM,
                (("分析客户需求", "experience"),),
            ),
            self.requirement(
                "商业理解",
                RequirementStatus.MATCHED,
                EvidenceConfidence.MEDIUM,
                (("制定区域销售策略", "experience"),),
            ),
            self.requirement("产品规划", RequirementStatus.UNKNOWN),
            self.requirement(
                "产品交付",
                RequirementStatus.PARTIAL,
                EvidenceConfidence.LOW,
                (("跨部门协调客户方案", "experience"),),
            ),
        )
        matcher = self.matcher_with_assessment(
            self.assessment(requirements, domain_score=10)
        )
        profile = ResumeProfile(summary="Sales manager focused on customer needs.")

        assessment, explanation = matcher._assess_and_explain(
            profile,
            "Product manager responsible for planning and delivery.",
        )
        result = matcher.match(
            profile,
            "Product manager responsible for planning and delivery.",
        )

        self.assertEqual(explanation.requirements, assessment.requirements)
        self.assertTrue(
            any(item.category == "career_transition" for item in explanation.risks)
        )
        self.assertTrue(any("产品交付" in item for item in result.gaps))
        self.assertNotIn("产品规划", result.missing_skills)

    def test_unknown_requirement_never_pollutes_missing_skills(self):
        requirements = (
            self.requirement("employee file management", RequirementStatus.UNKNOWN),
        )
        matcher = self.matcher_with_assessment(self.assessment(requirements))

        result = matcher.match(
            ResumeProfile(skills=["Recruitment"]),
            "HR role requiring employee file management.",
        )

        self.assertNotIn("employee file management", result.missing_skills)
        self.assertTrue(
            any("employee file management" in item for item in result.gaps)
        )
        self.assertTrue(any("not evidenced" in item for item in result.gaps))

    def test_only_explicit_missing_skill_enters_missing_skills(self):
        requirements = (
            self.requirement(
                "PMP",
                RequirementStatus.MISSING,
                EvidenceConfidence.HIGH,
                (("Not PMP certified", "certification"),),
            ),
            self.requirement("Docker", RequirementStatus.UNKNOWN),
        )
        matcher = self.matcher_with_assessment(self.assessment(requirements))

        result = matcher.match(
            ResumeProfile(),
            "Role requiring PMP and Docker.",
        )

        self.assertEqual(result.missing_skills, ["PMP"])

    def test_nextmove_run_keeps_exact_six_field_result_contract(self):
        response = NextMoveSkill().run(
            "match_job",
            {
                "resume": ResumeProfile(skills=["Python"]),
                "job_description": "Backend role requiring Python and Docker.",
            },
        )
        expected = [
            "match_score",
            "matched_skills",
            "missing_skills",
            "strengths",
            "gaps",
            "recommendations",
        ]

        self.assertTrue(response.success)
        self.assertIsInstance(response.result, JobMatchResult)
        self.assertEqual([field.name for field in fields(JobMatchResult)], expected)
        self.assertEqual(list(to_dict(response.result)), expected)
        self.assertFalse(
            {"explanation", "requirements", "risks", "confidence"}
            & set(to_dict(response.result))
        )


if __name__ == "__main__":
    unittest.main()
