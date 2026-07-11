"""Run a content-safe offline pilot simulation; live use is externally assembled."""
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill.ai.application.pilot import AIPilotRun, AIPilotReviewRecord
from skill.ai.application.pilot_report import PilotReport
def main():
 p=argparse.ArgumentParser(); p.add_argument('--format',choices=('json','markdown'),default='markdown'); a=p.parse_args(); now=datetime.now(timezone.utc).isoformat(); r=AIPilotRun('offline-simulation',now,now,'offline','none','none',0,0,0,0,'skipped'); d=PilotReport(r,()).to_dict(); print(json.dumps(d,indent=2) if a.format=='json' else '# AI Pilot\n\n- Status: skipped\n- Network calls: 0'); return 0
if __name__=='__main__': raise SystemExit(main())
