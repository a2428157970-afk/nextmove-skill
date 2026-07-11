"""In-memory, content-safe retention for pilot result summaries."""
from dataclasses import asdict, dataclass
import json

@dataclass(frozen=True, slots=True)
class AIPilotArtifact:
    artifact_id: str; run_id: str; created_at: str; provider_name: str; model_name: str; status: str; case_count: int; success_count: int; validator_pass_count: int; review_status: str
    def to_dict(self): return asdict(self)

@dataclass(frozen=True, slots=True)
class PilotRetentionPolicy:
    enabled: bool = True; max_records: int = 100; retention_days: int | None = None; allow_export: bool = True

class PilotArtifactStore:
    def __init__(self, policy=PilotRetentionPolicy()): self.policy=policy; self._records={}
    def save(self, artifact):
        if self.policy.enabled:
            if artifact.artifact_id not in self._records and len(self._records) >= self.policy.max_records: raise ValueError('pilot artifact limit exceeded')
            self._records[artifact.artifact_id]=artifact
        return artifact
    def get(self, artifact_id): return self._records.get(artifact_id)
    def list(self, review_status=None): return [a for a in self._records.values() if review_status is None or a.review_status==review_status]
    def update_review_status(self, artifact_id, status):
        if status not in ('pending','approved','rejected'): raise ValueError('invalid review status')
        artifact=self.get(artifact_id)
        if artifact is None: return None
        return self.save(AIPilotArtifact(**{**artifact.to_dict(), 'review_status':status}))

def export_pilot_artifacts(artifacts, fmt='json'):
    payload={'artifacts':[a.to_dict() for a in artifacts], 'review_summary':{s:sum(a.review_status==s for a in artifacts) for s in ('pending','approved','rejected')}}
    if fmt=='json': return json.dumps(payload, sort_keys=True)
    if fmt=='markdown': return '\n'.join(['# Pilot Export','',f"- Artifacts: {len(payload['artifacts'])}",f"- Pending: {payload['review_summary']['pending']}"])
    raise ValueError('unsupported export format')
