"""Render a Human Career Report from a fictional package scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _scenario(text: str, name: str) -> str:
    start = f"[SCENARIO:{name}]"
    end = "[/SCENARIO]"
    if start not in text:
        raise ValueError("fictional scenario was not found")
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def build_report(resume_text: str, job_description: str):
    from skill.analysis.analyzer import ResumeAnalyzer
    from skill.career.stage_assessor import CareerStageAssessor
    from skill.career.transition import CareerTransitionAssessor, TargetRoleLevelAssessor
    from skill.matching.classifier import DomainClassifier
    from skill.matching.matcher import JobMatcher
    from skill.reporting.builder import HumanCareerReportBuilder
    from skill.resume import RuleBasedResumeParser

    profile = RuleBasedResumeParser().parse(resume_text)
    matcher = JobMatcher()
    assessment, explanation = matcher._assess_and_explain(profile, job_description)
    classifier = DomainClassifier()
    stage = CareerStageAssessor().assess(profile)
    transition = CareerTransitionAssessor().assess(
        classifier.classify_profile(profile),
        classifier.classify_text(job_description),
        stage,
        assessment.transferability,
        explanation,
        TargetRoleLevelAssessor().classify(job_description),
    )
    return HumanCareerReportBuilder().build(
        ResumeAnalyzer().analyze(profile),
        matcher.match(profile, job_description),
        stage,
        explanation,
        transition,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("hr", "technology", "transition"), default="transition")
    parser.add_argument("--resume", type=Path, default=ROOT / "examples" / "sample_resume.txt")
    parser.add_argument("--job-description", type=Path, default=ROOT / "examples" / "sample_job_description.txt")
    args = parser.parse_args()
    resume = _scenario(args.resume.read_text(encoding="utf-8"), args.scenario)
    job = _scenario(args.job_description.read_text(encoding="utf-8"), args.scenario)
    from skill.reporting.formatter import HumanCareerReportFormatter

    print(HumanCareerReportFormatter().to_markdown(build_report(resume, job)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
