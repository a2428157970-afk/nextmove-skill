import json, unittest
from skill.ai.application.pilot_artifacts import AIPilotArtifact, PilotArtifactStore, PilotRetentionPolicy, export_pilot_artifacts
class PilotArtifactTests(unittest.TestCase):
 def test_store_review_and_safe_export(self):
  a=AIPilotArtifact('a','r','now','p','m','completed',1,1,1,'pending'); s=PilotArtifactStore(PilotRetentionPolicy(max_records=1)); s.save(a); self.assertEqual(s.update_review_status('a','approved').review_status,'approved'); out=export_pilot_artifacts(s.list()); self.assertNotIn('prompt',out); self.assertEqual(json.loads(out)['artifacts'][0]['artifact_id'],'a')
