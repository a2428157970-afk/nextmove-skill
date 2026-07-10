import json
import unittest

from skill.metadata import SKILL_METADATA
from skill.schemas.analysis import ResumeAnalysisResult, SkillAssessment
from skill.schemas.api import SkillError, SkillResponse
from skill.utils import to_dict


class SkillSerializationTests(unittest.TestCase):
    def test_result_to_dict_converts_nested_dataclasses(self):
        result = ResumeAnalysisResult(
            strengths=["Clear summary"],
            weaknesses=["Missing metrics"],
            skill_assessment=SkillAssessment(
                strengths=["Python"],
                gaps=["Docker"],
                notes="Needs deployment examples.",
            ),
            career_level="mid",
        )

        serialized = to_dict(result)

        self.assertEqual(
            serialized,
            {
                "strengths": ["Clear summary"],
                "weaknesses": ["Missing metrics"],
                "skill_assessment": {
                    "strengths": ["Python"],
                    "gaps": ["Docker"],
                    "notes": "Needs deployment examples.",
                },
                "career_level": "mid",
            },
        )
        json.dumps(serialized)

    def test_skill_response_to_dict_converts_result_and_error(self):
        success = SkillResponse(
            success=True,
            capability="analyze_resume",
            result=ResumeAnalysisResult(strengths=["Has skills"]),
        )
        failure = SkillResponse(
            success=False,
            capability="match_job",
            error=SkillError(
                code="INVALID_INPUT",
                message="payload requires 'job_description'",
                details={"field": "job_description"},
            ),
        )

        success_dict = to_dict(success)
        failure_dict = to_dict(failure)

        self.assertTrue(success_dict["success"])
        self.assertEqual(success_dict["result"]["strengths"], ["Has skills"])
        self.assertIsNone(success_dict["error"])
        self.assertFalse(failure_dict["success"])
        self.assertEqual(failure_dict["error"]["code"], "INVALID_INPUT")
        self.assertEqual(
            failure_dict["error"]["details"],
            {"field": "job_description"},
        )
        json.dumps(success_dict)
        json.dumps(failure_dict)

    def test_metadata_is_readable(self):
        self.assertEqual(SKILL_METADATA["name"], "NextMove")
        self.assertIsInstance(SKILL_METADATA["version"], str)
        self.assertIn("analyze_resume", SKILL_METADATA["capabilities"])
        self.assertIn("match_job", SKILL_METADATA["capabilities"])
        self.assertIn("description", SKILL_METADATA)


if __name__ == "__main__":
    unittest.main()
