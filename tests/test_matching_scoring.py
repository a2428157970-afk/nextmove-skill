import unittest

from skill.matching.schemas import MatchAssessment, MatchConfidence


class MatchingSchemaTests(unittest.TestCase):
    def test_internal_assessment_carries_confidence_and_components(self):
        assessment = MatchAssessment(
            score=87,
            confidence=MatchConfidence.HIGH,
            domain_score=100,
            skill_score=82,
            qualification_score=85,
            strengths=("domain aligned",),
            gaps=("certification not visible",),
        )

        self.assertEqual(assessment.score, 87)
        self.assertEqual(assessment.confidence, MatchConfidence.HIGH)
        self.assertEqual(assessment.domain_score, 100)


if __name__ == "__main__":
    unittest.main()
