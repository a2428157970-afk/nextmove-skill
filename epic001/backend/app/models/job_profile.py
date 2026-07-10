from dataclasses import dataclass


@dataclass(frozen=True)
class JobProfile:
    id: str
