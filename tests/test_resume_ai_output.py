import json
import unittest

from skill.ai.enhancement.resume_output import ResumeAIOutput, parse_resume_ai_output


def valid_payload():
    return {"contract_version":"resume-improvement.v1","summary":"Keep existing facts.","rewritten_content":"Rewrite only supplied content.","improvement_points":["Add metrics only when verified."],"keyword_suggestions":["Python"],"factual_warnings":["Do not invent metrics."]}


class ResumeAIOutputTests(unittest.TestCase):
    def test_parses_valid_contract(self):
        output = parse_resume_ai_output(json.dumps(valid_payload()))
        self.assertIsInstance(output, ResumeAIOutput)
        self.assertEqual(output.contract_version, "resume-improvement.v1")
        self.assertEqual(output.to_dict()["summary"], "Keep existing facts.")

    def test_rejects_invalid_provider_outputs(self):
        invalid = ["not json", "[]", "text {}", "```json\n{}\n```", json.dumps({}), json.dumps({**valid_payload(), "contract_version":"wrong"}), json.dumps({key: value for key, value in valid_payload().items() if key != "summary"}), json.dumps({**valid_payload(), "improvement_points":[1]}), json.dumps({**valid_payload(), "summary":"", "rewritten_content":""}), "Traceback: debug"]
        for raw in invalid:
            with self.subTest(raw=raw):
                self.assertIsNone(parse_resume_ai_output(raw))


if __name__ == "__main__":
    unittest.main()
