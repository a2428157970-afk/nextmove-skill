"""Domain-aware rule-based job matching for Skill Core."""

from skill.matching.classifier import DomainClassifier
from skill.matching.explanations import MatchExplanationBuilder, MatchExplanationResult
from skill.matching.scoring import MatchScorer
from skill.matching.schemas import (
    JobMatchResult,
    MatchAssessment,
    MatchConfidence,
    RequirementStatus,
)
from skill.schemas.resume import ResumeProfile


class JobMatcher:
    """Compare a resume profile with a job description using domain-aware rules."""

    def __init__(self) -> None:
        self.classifier = DomainClassifier()
        self.scorer = MatchScorer()
        self.explanation_builder = MatchExplanationBuilder()

    def match(
        self,
        profile: ResumeProfile,
        job_description: str,
    ) -> JobMatchResult:
        assessment, explanation = self._assess_and_explain(profile, job_description)

        matched_skills = [
            requirement.requirement
            for requirement in explanation.requirements
            if requirement.kind == "skill"
            and requirement.status == RequirementStatus.MATCHED
        ]
        missing_skills = [
            requirement.requirement
            for requirement in explanation.requirements
            if requirement.kind == "skill"
            and requirement.status == RequirementStatus.MISSING
        ]
        strengths = [item.summary for item in explanation.strengths]
        gaps = [item.summary for item in (*explanation.gaps, *explanation.risks)]
        if not explanation.requirements:
            gaps.extend(assessment.gaps)

        return JobMatchResult(
            match_score=assessment.score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            strengths=strengths,
            gaps=self._dedupe(gaps),
            recommendations=self._recommendations(assessment, explanation),
        )

    def _assess_and_explain(
        self,
        profile: ResumeProfile,
        job_description: str,
    ) -> tuple[MatchAssessment, MatchExplanationResult]:
        resume_classification = self.classifier.classify_profile(profile)
        job_classification = self.classifier.classify_text(job_description)
        assessment = self.scorer.assess(
            profile,
            job_description,
            resume_classification,
            job_classification,
        )
        explanation = self.explanation_builder.build(
            assessment.requirements,
            assessment,
        )
        return assessment, explanation

    @staticmethod
    def _recommendations(
        assessment: MatchAssessment,
        explanation: MatchExplanationResult,
    ) -> list[str]:
        recommendations: list[str] = []
        for gap in explanation.gaps:
            requirements = ", ".join(gap.related_requirements)
            if gap.category == "missing_capability":
                recommendations.append(
                    f"Address the explicit requirement conflict for {requirements} truthfully."
                )
            elif gap.category == "insufficient_evidence":
                recommendations.append(
                    f"Provide truthful evidence for {requirements} if relevant, or clarify the requirement."
                )
        partial_requirements = [
            requirement
            for risk in explanation.risks
            if risk.category == "partial_coverage"
            for requirement in risk.related_requirements
        ]
        if partial_requirements:
            recommendations.append(
                "Clarify direct experience for partially evidenced requirements: "
                + ", ".join(partial_requirements)
                + "."
            )
        if assessment.confidence == MatchConfidence.LOW:
            recommendations.append(
                "Provide more specific job responsibilities and qualifications for a more reliable match."
            )
        elif assessment.score < 70:
            recommendations.append(
                "Tailor the resume summary and experience bullets to the target role using truthful evidence."
            )
        else:
            recommendations.append(
                "Keep the resume focused on the matched requirements and add quantified impact where truthful."
            )
        return JobMatcher._dedupe(recommendations)

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
