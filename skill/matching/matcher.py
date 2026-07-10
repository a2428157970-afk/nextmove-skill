"""Rule-based job matching for Skill Core."""

import re

from skill.matching.schemas import JobMatchResult
from skill.schemas.resume import ResumeProfile


KNOWN_JOB_KEYWORDS = {
    "api": "API",
    "apis": "API",
    "aws": "AWS",
    "azure": "Azure",
    "docker": "Docker",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "gcp": "GCP",
    "java": "Java",
    "javascript": "JavaScript",
    "kubernetes": "Kubernetes",
    "python": "Python",
    "react": "React",
    "sql": "SQL",
    "tableau": "Tableau",
    "typescript": "TypeScript",
}


class JobMatcher:
    """Compare a resume profile with a job description using simple rules."""

    def match(
        self,
        profile: ResumeProfile,
        job_description: str,
    ) -> JobMatchResult:
        resume_skills = self._normalize_profile_skills(profile)
        job_keywords = self._extract_job_keywords(job_description)

        matched_keys = [
            keyword for keyword in job_keywords if keyword.lower() in resume_skills
        ]
        missing_keys = [
            keyword for keyword in job_keywords if keyword.lower() not in resume_skills
        ]

        matched_skills = [KNOWN_JOB_KEYWORDS[keyword.lower()] for keyword in matched_keys]
        missing_skills = [KNOWN_JOB_KEYWORDS[keyword.lower()] for keyword in missing_keys]

        match_score = self._score(profile, job_keywords, matched_keys)
        strengths = self._strengths(matched_skills, profile)
        gaps = self._gaps(missing_skills, profile)
        recommendations = self._recommendations(missing_skills, match_score)

        return JobMatchResult(
            match_score=match_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
        )

    @staticmethod
    def _normalize_profile_skills(profile: ResumeProfile) -> set[str]:
        return {skill.strip().lower() for skill in profile.skills if skill.strip()}

    @staticmethod
    def _extract_job_keywords(job_description: str) -> list[str]:
        words = {
            word.lower()
            for word in re.findall(r"[A-Za-z][A-Za-z0-9+#-]*", job_description)
        }
        return [
            keyword
            for keyword in KNOWN_JOB_KEYWORDS
            if keyword in words and keyword != "apis"
        ]

    @staticmethod
    def _score(
        profile: ResumeProfile,
        job_keywords: list[str],
        matched_keywords: list[str],
    ) -> int:
        if not profile.skills and not profile.experience:
            return 0
        if not job_keywords:
            return 0

        skill_score = len(matched_keywords) / len(job_keywords) * 80
        experience_score = 20 if profile.experience else 0
        return min(100, round(skill_score + experience_score))

    @staticmethod
    def _strengths(
        matched_skills: list[str],
        profile: ResumeProfile,
    ) -> list[str]:
        strengths: list[str] = []
        if matched_skills:
            strengths.append(
                "Resume covers key job skills: " + ", ".join(matched_skills) + "."
            )
        if profile.experience:
            strengths.append("Resume includes work experience relevant to the match.")
        return strengths

    @staticmethod
    def _gaps(
        missing_skills: list[str],
        profile: ResumeProfile,
    ) -> list[str]:
        gaps: list[str] = []
        if missing_skills:
            gaps.append(
                "Job description mentions skills not visible in the resume: "
                + ", ".join(missing_skills)
                + "."
            )
        if not profile.experience:
            gaps.append("Resume does not include work experience for relevance scoring.")
        return gaps

    @staticmethod
    def _recommendations(
        missing_skills: list[str],
        match_score: int,
    ) -> list[str]:
        recommendations: list[str] = []
        if missing_skills:
            recommendations.append(
                "Add evidence for missing job keywords where truthful: "
                + ", ".join(missing_skills)
                + "."
            )
        if match_score < 70:
            recommendations.append(
                "Tailor the resume summary and experience bullets to the target job description."
            )
        else:
            recommendations.append(
                "Keep the resume focused on the matched skills and add quantified impact."
            )
        return recommendations
