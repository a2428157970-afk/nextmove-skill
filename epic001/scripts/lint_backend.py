from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = (
    ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else ROOT / "backend" / ".venv" / "bin" / "python"
)


def main() -> int:
    python = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
    return subprocess.call(
        [str(python), "-m", "ruff", "check", "backend"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
