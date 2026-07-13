"""Build deterministic runtime and prompt-only NextMove distribution archives."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "distribution"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def read_version() -> str:
    tree = ast.parse((ROOT / "skill" / "__version__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    raise ValueError("authoritative skill version was not found")


def _safe_relative(relative: str) -> str:
    value = PurePosixPath(relative)
    if value.is_absolute() or ".." in value.parts or not value.parts:
        raise ValueError("package path must remain relative")
    return value.as_posix()


def _runtime_files() -> dict[str, Path]:
    files = {
        "SKILL.md": ROOT / "SKILL.md",
        "skill.json": ROOT / "skill.json",
        "LICENSE": ROOT / "LICENSE",
        "pyproject.toml": ROOT / "pyproject.toml",
        "README.md": SOURCE / "runtime" / "README.md",
        "QUICK_START.md": SOURCE / "runtime" / "QUICK_START.md",
        "PROMPTS.md": SOURCE / "common" / "PROMPTS.md",
        "docs/agent-prompt-template.md": SOURCE / "common" / "PROMPTS.md",
        "docs/output-guide.md": SOURCE / "common" / "OUTPUT_GUIDE.md",
        "examples/sample_resume.txt": SOURCE / "common" / "examples" / "sample_resume.txt",
        "examples/sample_job_description.txt": SOURCE / "common" / "examples" / "sample_job_description.txt",
        "scripts/check_skill_package.py": ROOT / "scripts" / "check_skill_package.py",
        "scripts/run_human_career_report.py": ROOT / "scripts" / "run_human_career_report.py",
    }
    for path in sorted((ROOT / "skill").rglob("*")):
        if path.is_file() and path.suffix == ".py" and "__pycache__" not in path.parts:
            files[path.relative_to(ROOT).as_posix()] = path
    return files


def _prompt_files() -> dict[str, Path]:
    return {
        "SKILL.md": ROOT / "SKILL.md",
        "skill.json": ROOT / "skill.json",
        "LICENSE": ROOT / "LICENSE",
        "README.md": SOURCE / "prompt_only" / "README.md",
        "QUICK_START.md": SOURCE / "prompt_only" / "QUICK_START.md",
        "PROMPTS.md": SOURCE / "common" / "PROMPTS.md",
        "docs/agent-prompt-template.md": SOURCE / "common" / "PROMPTS.md",
        "docs/output-guide.md": SOURCE / "prompt_only" / "OUTPUT_GUIDE.md",
        "OUTPUT_GUIDE.md": SOURCE / "prompt_only" / "OUTPUT_GUIDE.md",
        "PRIVACY_AND_FEEDBACK.md": SOURCE / "prompt_only" / "PRIVACY_AND_FEEDBACK.md",
        "examples/sample_resume.txt": SOURCE / "common" / "examples" / "sample_resume.txt",
        "examples/sample_job_description.txt": SOURCE / "common" / "examples" / "sample_job_description.txt",
    }


def _manifest(mode: str, files: dict[str, bytes], version: str) -> bytes:
    checksums = {
        relative: hashlib.sha256(content).hexdigest()
        for relative, content in sorted(files.items())
    }
    fingerprint = hashlib.sha256()
    for relative, digest in checksums.items():
        fingerprint.update(relative.encode("utf-8"))
        fingerprint.update(b"\0")
        fingerprint.update(digest.encode("ascii"))
        fingerprint.update(b"\n")
    runtime = mode == "runtime"
    payload = {
        "package_name": (
            "nextmove-skill-package" if runtime else "nextmove-prompt-kit"
        ),
        "package_version": version,
        "skill_version": version,
        "package_mode": mode,
        "runtime_requirements": (
            ["Python >=3.11", "No third-party runtime dependencies", "Local filesystem access"]
            if runtime
            else ["No Python runtime included", "Reference-file capable Agent"]
        ),
        "skill_entrypoint": "skill.interface:NextMoveSkill.run" if runtime else None,
        "cli_entrypoint": "skill.__main__:main" if runtime else None,
        "included_files": sorted(files),
        "checksums": checksums,
        "build_id": f"sha256:{fingerprint.hexdigest()}",
    }
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _remove_previous(output: Path, package_name: str) -> None:
    output = output.resolve()
    directory = (output / package_name).resolve()
    archive = (output / f"{package_name}.zip").resolve()
    if directory.parent != output or archive.parent != output:
        raise ValueError("build destination escaped output directory")
    if directory.exists():
        shutil.rmtree(directory)
    if archive.exists():
        archive.unlink()


def build(mode: str, output: Path) -> tuple[Path, Path]:
    version = read_version()
    skill_metadata = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
    if skill_metadata.get("version") != version:
        raise ValueError("skill.json version does not match authoritative skill version")
    package_name = (
        f"nextmove-skill-package-{version}"
        if mode == "runtime"
        else f"nextmove-prompt-kit-{version}"
    )
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    _remove_previous(output, package_name)
    sources = _runtime_files() if mode == "runtime" else _prompt_files()
    contents: dict[str, bytes] = {}
    for raw_relative, source in sources.items():
        relative = _safe_relative(raw_relative)
        resolved = source.resolve()
        if not resolved.is_relative_to(ROOT.resolve()) or not source.is_file():
            raise ValueError("package source is missing or outside repository")
        contents[relative] = source.read_bytes()
    contents["PACKAGE_MANIFEST.json"] = _manifest(mode, contents, version)

    package_dir = output / package_name
    for relative, content in sorted(contents.items()):
        destination = package_dir / Path(relative)
        if not destination.resolve().is_relative_to(package_dir.resolve()):
            raise ValueError("package destination escaped package directory")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    archive_path = output / f"{package_name}.zip"
    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for relative, content in sorted(contents.items()):
            info = zipfile.ZipInfo(f"{package_name}/{relative}", FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return package_dir, archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("runtime", "prompt-only", "all"), required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    modes = ("runtime", "prompt_only") if args.mode == "all" else (args.mode.replace("-", "_"),)
    for mode in modes:
        package_dir, archive = build(mode, args.output)
        print(json.dumps({"mode": mode, "directory": str(package_dir), "archive": str(archive)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
