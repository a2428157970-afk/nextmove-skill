"""Public interface for the NextMove Skill Core."""

from typing import Any

from skill.analysis import ResumeAnalyzer
from skill.career import CareerAdvisor
from skill.improvement import ResumeImprover
from skill.matching import JobMatcher
from skill.resume import RuleBasedResumeParser
from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.api import SkillError, SkillResponse
from skill.schemas.career import CareerAdviceResult
from skill.schemas.improvement import ResumeImprovementResult
from skill.schemas.matching import JobMatchResult
from skill.schemas.resume import ResumeProfile


class NextMoveSkill:
    """Unified entry point for AI Career Intelligence capabilities."""

    def __init__(self):
        self.parser = RuleBasedResumeParser()
        self.analyzer = ResumeAnalyzer()
        self.advisor = CareerAdvisor()
        self.improver = ResumeImprover()
        self.matcher = JobMatcher()

    def analyze_resume(self, resume: ResumeProfile | str) -> ResumeAnalysisResult:
        if isinstance(resume, str):
            resume = self.parser.parse(resume)

        if isinstance(resume, ResumeProfile):
            return self.analyzer.analyze(resume)

        raise TypeError("resume must be a ResumeProfile or str")

    def improve_resume(self, resume: ResumeProfile | str) -> ResumeImprovementResult:
        if isinstance(resume, str):
            resume = self.parser.parse(resume)

        if isinstance(resume, ResumeProfile):
            analysis = self.analyzer.analyze(resume)
            return self.improver.improve(resume, analysis)

        raise TypeError("resume must be a ResumeProfile or str")

    def match_job(
        self,
        resume: ResumeProfile | str,
        job_description: str,
    ) -> JobMatchResult:
        if isinstance(resume, str):
            resume = self.parser.parse(resume)

        if not isinstance(resume, ResumeProfile):
            raise TypeError("resume must be a ResumeProfile or str")

        if not isinstance(job_description, str):
            raise TypeError("job_description must be a string")

        return self.matcher.match(resume, job_description)

    def career_advice(
        self,
        profile: ResumeProfile | str,
        analysis: ResumeAnalysisResult | None = None,
    ) -> CareerAdviceResult:
        if isinstance(profile, str):
            profile = self.parser.parse(profile)

        if not isinstance(profile, ResumeProfile):
            raise TypeError("profile must be a ResumeProfile or str")

        if analysis is None:
            analysis = self.analyzer.analyze(profile)
        elif not isinstance(analysis, ResumeAnalysisResult):
            raise TypeError("analysis must be a ResumeAnalysisResult or None")

        return self.advisor.advise(profile, analysis)

    def run(self, capability: str, payload: dict[str, Any]) -> SkillResponse:
        try:
            if not isinstance(payload, dict):
                raise TypeError("payload must be a dict")

            result = self._run_capability(capability, payload)
            return SkillResponse(
                success=True,
                capability=capability,
                result=result,
                error=None,
            )
        except ValueError as exc:
            return SkillResponse(
                success=False,
                capability=capability,
                result=None,
                error=SkillError(code="UNKNOWN_CAPABILITY", message=str(exc)),
            )
        except (KeyError, TypeError) as exc:
            return SkillResponse(
                success=False,
                capability=capability,
                result=None,
                error=SkillError(code="INVALID_INPUT", message=str(exc)),
            )

    def _run_capability(self, capability: str, payload: dict[str, Any]) -> Any:
        if capability == "analyze_resume":
            return self.analyze_resume(self._required(payload, "resume"))

        if capability == "improve_resume":
            return self.improve_resume(self._required(payload, "resume"))

        if capability == "match_job":
            return self.match_job(
                self._required(payload, "resume"),
                self._required(payload, "job_description"),
            )

        if capability == "career_advice":
            resume = self._required(payload, "resume")
            analysis = payload.get("analysis")
            return self.career_advice(resume, analysis)

        raise ValueError(f"unsupported capability: {capability}")

    @staticmethod
    def _required(payload: dict[str, Any], key: str) -> Any:
        if key not in payload:
            raise KeyError(f"payload requires '{key}'")
        return payload[key]
