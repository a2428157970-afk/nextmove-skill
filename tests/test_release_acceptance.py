import json, subprocess, sys, unittest
from pathlib import Path
from skill import NextMoveSkill, __version__
from skill.ai import ResumeAIEnhancer
class ReleaseAcceptanceTests(unittest.TestCase):
 def test_public_api_and_offline_runners(self):
  self.assertEqual(__version__, '0.7.0'); self.assertTrue(NextMoveSkill and ResumeAIEnhancer)
  root=Path(__file__).parents[1]
  for name in ('run_ai_quality_evaluation.py','run_ai_pilot.py'):
   p=subprocess.run([sys.executable,str(root/'scripts'/name),'--format','json'],capture_output=True,text=True); self.assertEqual(p.returncode,0); json.loads(p.stdout)
