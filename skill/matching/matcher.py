"""Domain-aware rule-based job matching for Skill Core."""

from skill.matching.classifier import DomainClassifier
from skill.matching.scoring import MatchScorer
from skill.matching.schemas import JobMatchResult, MatchAssessment, MatchConfidence
from skill.schemas.resume import ResumeProfile


class JobMatcher:
    """Compare a resume profile with a job description using domain-aware rules."""

    def __init__(self) -> None:
        self.classifier = DomainClassifier()
        self.scorer = MatchScorer()

    def match(
        self,
        profile: ResumeProfile,
        job_description: str,
    ) -> JobMatchResult:
        resume_classification = self.classifier.classify_profile(profile)
        job_classification = self.classifier.classify_text(job_description)
        assessment = self.scorer.assess(
            profile,
            job_description,
            resume_classification,
            job_classification,
        )

        return JobMatchResult(
            match_score=assessment.score,
            matched_skills=list(assessment.matched_skills),
            missing_skills=list(assessment.missing_skills),
            strengths=list(assessment.strengths),
            gaps=list(assessment.gaps),
            recommendations=self._recommendations(assessment),
        )

    @staticmethod
    def _recommendations(assessment: MatchAssessment) -> list[str]:
        recommendations: list[str] = []
        if assessment.missing_skills:
            recommendations.append(
                "Add truthful evidence for job requirements not visible in the resume: "
                + ", ".join(assessment.missing_skills)
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
        return recommendations
