import unittest
from dataclasses import FrozenInstanceError

from skill.matching.scoring import MatchScorer
from skill.matching.schemas import (
    DomainClassification,
    EvidenceConfidence,
    EvidenceItem,
    MatchConfidence,
    RequirementEvidence,
    RequirementStatus,
)
from skill.matching.taxonomy import CareerDomain, JobFamily
from skill.schemas.resume import (
    EducationEntry,
    ExperienceEntry,
    PersonalInformation,
    ProjectEntry,
    ResumeProfile,
)


class RequirementEvidenceSchemaTests(unittest.TestCase):
    def test_internal_requirement_evidence_contract_is_typed_and_immutable(self):
        self.assertEqual(
            [status.value for status in RequirementStatus],
            ["matched", "partial", "missing", "unknown"],
        )
        self.assertEqual(
            [confidence.value for confidence in EvidenceConfidence],
            ["high", "medium", "low"],
        )

        item = EvidenceItem(text="Built Python APIs.", source="experience")
        requirement = RequirementEvidence(
            requirement="Python",
            kind="skill",
            status=RequirementStatus.MATCHED,
            evidence=(item,),
            confidence=EvidenceConfidence.MEDIUM,
        )

        self.assertEqual(requirement.evidence, (item,))
        with self.assertRaises(FrozenInstanceError):
            requirement.requirement = "Java"


class RequirementEvidenceMappingTests(unittest.TestCase):
    def setUp(self):
        self.scorer = MatchScorer()

    @staticmethod
    def classification(domain, family=None):
        return DomainClassification(domain, family, MatchConfidence.HIGH, ())

    def test_direct_evidence_uses_professional_source_order_and_deduplicates(self):
        profile = ResumeProfile(
            personal_information=PersonalInformation(
                name="Python Candidate",
                email="python@example.com",
                phone="13800000000",
                location="Python City",
            ),
            summary="Python backend engineer.",
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built Python services."],
                )
            ],
            projects=[ProjectEntry(description="Created a Python API.")],
            skills=["Python", "python"],
        )
        technology = self.classification(CareerDomain.TECHNOLOGY, JobFamily.BACKEND)

        assessment = self.scorer.assess(
            profile,
            "Backend Engineer. Python is required.",
            technology,
            technology,
        )

        python = next(
            item for item in assessment.requirements if item.requirement == "Python"
        )
        self.assertEqual(python.status, RequirementStatus.MATCHED)
        self.assertEqual(python.confidence, EvidenceConfidence.HIGH)
        self.assertEqual(
            [item.source for item in python.evidence],
            ["summary", "experience", "project", "skill"],
        )
        self.assertEqual(
            [item.text for item in python.evidence],
            [
                "Python backend engineer.",
                "Built Python services.",
                "Created a Python API.",
                "Python",
            ],
        )
        evidence_text = " ".join(item.text for item in python.evidence)
        self.assertNotIn("python@example.com", evidence_text)
        self.assertNotIn("13800000000", evidence_text)
        self.assertNotIn("Python City", evidence_text)

    def test_unmentioned_requirement_is_unknown_instead_of_missing(self):
        profile = ResumeProfile(skills=["Python"])
        technology = self.classification(CareerDomain.TECHNOLOGY, JobFamily.BACKEND)

        assessment = self.scorer.assess(
            profile,
            "Backend Engineer requiring Python and Docker.",
            technology,
            technology,
        )

        docker = next(
            item for item in assessment.requirements if item.requirement == "Docker"
        )
        self.assertEqual(docker.status, RequirementStatus.UNKNOWN)
        self.assertEqual(docker.evidence, ())
        self.assertEqual(docker.confidence, EvidenceConfidence.LOW)

    def test_explicit_qualification_conflict_is_missing(self):
        profile = ResumeProfile(summary="Accountant who is not CPA certified.")
        finance = self.classification(CareerDomain.FINANCE, JobFamily.ACCOUNTING)

        assessment = self.scorer.assess(
            profile,
            "Accountant. CPA certification required.",
            finance,
            finance,
        )

        cpa = next(
            item for item in assessment.requirements if item.requirement == "CPA"
        )
        self.assertEqual(cpa.kind, "qualification")
        self.assertEqual(cpa.status, RequirementStatus.MISSING)
        self.assertEqual(cpa.confidence, EvidenceConfidence.HIGH)
        self.assertEqual(cpa.evidence[0].source, "summary")
        self.assertEqual(cpa.evidence[0].text, "Accountant who is not CPA certified.")

    def test_structured_qualification_evidence_keeps_professional_sources(self):
        profile = ResumeProfile(
            experience=[
                ExperienceEntry(
                    role="Accountant",
                    start_date="2018-01",
                    end_date="2024-01",
                )
            ],
            education=[EducationEntry(degree="Bachelor")],
            certifications=["CPA"],
            languages=["English"],
        )
        finance = self.classification(CareerDomain.FINANCE, JobFamily.ACCOUNTING)

        assessment = self.scorer.assess(
            profile,
            "Accountant requiring 3 years experience, bachelor degree, CPA, and English.",
            finance,
            finance,
        )

        self.assertEqual(
            [item.requirement for item in assessment.requirements],
            ["3+ years experience", "Bachelor's degree", "CPA", "English"],
        )
        self.assertTrue(
            all(
                item.status == RequirementStatus.MATCHED
                for item in assessment.requirements
            )
        )
        self.assertEqual(
            [item.evidence[0].source for item in assessment.requirements],
            ["experience", "education", "certification", "language"],
        )
        self.assertEqual(
            assessment.requirements[0].evidence[0].text,
            "2018-01 to 2024-01",
        )

    def test_adjacent_framework_evidence_is_partial(self):
        profile = ResumeProfile(summary="Built backend services with Flask.")
        technology = self.classification(CareerDomain.TECHNOLOGY, JobFamily.BACKEND)

        assessment = self.scorer.assess(
            profile,
            "Backend Engineer requiring FastAPI.",
            technology,
            technology,
        )

        fastapi = next(
            item for item in assessment.requirements if item.requirement == "FastAPI"
        )
        self.assertEqual(fastapi.status, RequirementStatus.PARTIAL)
        self.assertEqual(fastapi.confidence, EvidenceConfidence.LOW)
        self.assertEqual(fastapi.evidence[0].text, "Built backend services with Flask.")


if __name__ == "__main__":
    unittest.main()
