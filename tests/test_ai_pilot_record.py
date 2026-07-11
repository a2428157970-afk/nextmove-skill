import json
import unittest

from skill.ai.application.pilot import AIPilotReviewRecord


class AIPilotReviewRecordTests(unittest.TestCase):
    def test_record_is_serializable_and_content_safe(self):
        record = AIPilotReviewRecord("synthetic-tech", "resume-improvement.v1", "external", "external-model", True, 0.2, 120, True)
        payload = json.loads(json.dumps(record.to_dict()))
        self.assertEqual(payload["reviewer_status"], "pending")
        self.assertNotIn("prompt", payload)
        self.assertNotIn("response", payload)

