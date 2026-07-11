import json, unittest
from skill.ai.application.pilot import AIPilotRun, AIPilotReviewRecord
from skill.ai.application.pilot_report import PilotReport
class PilotReportTests(unittest.TestCase):
 def test_safe_report(self):
  run=AIPilotRun('r','s','e','offline','p','m',1,1,0,1,'completed'); record=AIPilotReviewRecord('c','resume-improvement.v1','p','m',True,0.1,10,True)
  payload=json.loads(json.dumps(PilotReport(run,(record,)).to_dict())); self.assertNotIn('prompt',str(payload)); self.assertEqual(payload['validation_summary']['validator_passed'],1)
