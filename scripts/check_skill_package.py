"""Validate a NextMove package and execute the runtime smoke test when present."""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import sys
import tempfile
import urllib.request
import zipfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath


REQUIRED_MANIFEST_KEYS = {
    "package_name",
    "package_version",
    "skill_version",
    "package_mode",
    "runtime_requirements",
    "skill_entrypoint",
    "cli_entrypoint",
    "included_files",
    "checksums",
    "build_id",
}


def _root(directory: Path) -> Path:
    if (directory / "PACKAGE_MANIFEST.json").is_file():
        return directory
    candidates = list(directory.glob("*/PACKAGE_MANIFEST.json"))
    if len(candidates) != 1:
        raise ValueError("package must contain exactly one manifest")
    return candidates[0].parent


def _validate(root: Path) -> dict:
    manifest = json.loads((root / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    if not REQUIRED_MANIFEST_KEYS.issubset(manifest):
        raise ValueError("manifest is missing required fields")
    if manifest["package_mode"] not in {"runtime", "prompt_only"}:
        raise ValueError("manifest package mode is invalid")
    included = manifest["included_files"]
    if len(included) != len(set(included)):
        raise ValueError("manifest contains duplicate files")
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "PACKAGE_MANIFEST.json"
    }
    if set(included) != actual or set(manifest["checksums"]) != actual:
        raise ValueError("manifest inventory does not match package")
    for relative in included:
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError("manifest path escaped package root")
        digest = hashlib.sha256((root / Path(relative)).read_bytes()).hexdigest()
        if digest != manifest["checksums"][relative]:
            raise ValueError("package checksum validation failed")
    return manifest


@contextmanager
def _blocked_network():
    calls = {"count": 0}
    original_socket = socket.socket
    original_connection = socket.create_connection
    original_urlopen = urllib.request.urlopen

    def blocked(*args, **kwargs):
        calls["count"] += 1
        raise RuntimeError("network access is disabled during readiness preflight")

    socket.socket = blocked
    socket.create_connection = blocked
    urllib.request.urlopen = blocked
    try:
        yield calls
    finally:
        socket.socket = original_socket
        socket.create_connection = original_connection
        urllib.request.urlopen = original_urlopen


def _runtime_smoke(root: Path) -> dict:
    required = ("skill", "pyproject.toml", "examples/sample_resume.txt", "examples/sample_job_description.txt")
    if not all((root / item).exists() for item in required):
        raise ValueError("runtime package is incomplete")
    original_path = list(sys.path)
    sys.path.insert(0, str(root))
    for name in tuple(sys.modules):
        if name == "skill" or name.startswith("skill."):
            del sys.modules[name]
    try:
        with _blocked_network() as calls:
            from skill import NextMoveSkill
            from skill.utils import to_dict

            resume = (root / "examples" / "sample_resume.txt").read_text(encoding="utf-8")
            job = (root / "examples" / "sample_job_description.txt").read_text(encoding="utf-8")
            response = NextMoveSkill().run(
                "career_analysis", {"resume": resume, "job_description": job}
            )
            payload = to_dict(response)
            json.dumps(payload, ensure_ascii=False)
        if not response.success or response.capability != "career_analysis":
            raise ValueError("runtime career analysis smoke test failed")
        if calls["count"] != 0:
            raise ValueError("runtime attempted network access")
        return {
            "mode": "runtime",
            "manifest_valid": True,
            "skill_imported": True,
            "smoke_executed": True,
            "response_serializable": True,
            "network_calls": calls["count"],
        }
    finally:
        sys.path[:] = original_path


def check(package: Path) -> tuple[dict, str]:
    with tempfile.TemporaryDirectory() as temporary:
        candidate = package.resolve()
        if candidate.is_dir():
            root = _root(candidate)
            manifest = _validate(root)
            if manifest["package_mode"] == "prompt_only":
                return {"mode": "prompt_only", "manifest_valid": True, "smoke_executed": False}, "NEXTMOVE_PROMPT_ONLY"
            return _runtime_smoke(root), "NEXTMOVE_READY"
        if not candidate.is_file() or not zipfile.is_zipfile(candidate):
            raise ValueError("package is not a valid directory or ZIP archive")
        with zipfile.ZipFile(candidate) as archive:
            for name in archive.namelist():
                pure = PurePosixPath(name)
                if pure.is_absolute() or ".." in pure.parts:
                    raise ValueError("archive path escaped extraction directory")
            archive.extractall(temporary)
        root = _root(Path(temporary))
        manifest = _validate(root)
        if manifest["package_mode"] == "prompt_only":
            return {"mode": "prompt_only", "manifest_valid": True, "smoke_executed": False}, "NEXTMOVE_PROMPT_ONLY"
        return _runtime_smoke(root), "NEXTMOVE_READY"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    try:
        result, marker = check(args.package)
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": type(exc).__name__, "message": "package readiness validation failed"}), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print(marker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
