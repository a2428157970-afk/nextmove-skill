import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from scripts import build_skill_package as package_builder


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_skill_package.py"
CHECK_SCRIPT = ROOT / "scripts" / "check_skill_package.py"
VERSION = "0.8.0"


class SkillDistributionPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls._temporary.name)
        completed = subprocess.run(
            [
                sys.executable,
                str(BUILD_SCRIPT),
                "--mode",
                "all",
                "--output",
                str(cls.output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)
        cls.runtime_zip = cls.output / f"nextmove-skill-package-{VERSION}.zip"
        cls.prompt_zip = cls.output / f"nextmove-prompt-kit-{VERSION}.zip"

    @classmethod
    def tearDownClass(cls):
        cls._temporary.cleanup()

    def _members(self, package: Path) -> tuple[str, ...]:
        with zipfile.ZipFile(package) as archive:
            return tuple(name for name in archive.namelist() if not name.endswith("/"))

    def _read_json_member(self, package: Path, suffix: str) -> dict:
        with zipfile.ZipFile(package) as archive:
            name = next(item for item in archive.namelist() if item.endswith(suffix))
            return json.loads(archive.read(name).decode("utf-8"))

    def _read_text_members(self, package: Path) -> str:
        values = []
        with zipfile.ZipFile(package) as archive:
            for name in archive.namelist():
                if name.endswith((".md", ".txt", ".json")):
                    values.append(archive.read(name).decode("utf-8"))
        return "\n".join(values)

    def _check(self, package: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--package", str(package)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_runtime_zip_has_required_files(self):
        members = self._members(self.runtime_zip)
        suffixes = {
            "SKILL.md",
            "skill.json",
            "PACKAGE_MANIFEST.json",
            "QUICK_START.md",
            "README.md",
            "PROMPTS.md",
            "LICENSE",
            "pyproject.toml",
            "examples/sample_resume.txt",
            "examples/sample_job_description.txt",
            "scripts/check_skill_package.py",
            "scripts/run_human_career_report.py",
        }
        for suffix in suffixes:
            self.assertTrue(any(name.endswith(suffix) for name in members), suffix)

    def test_prompt_only_zip_has_required_files(self):
        members = self._members(self.prompt_zip)
        for suffix in (
            "SKILL.md",
            "skill.json",
            "PACKAGE_MANIFEST.json",
            "QUICK_START.md",
            "PROMPTS.md",
            "OUTPUT_GUIDE.md",
            "PRIVACY_AND_FEEDBACK.md",
            "examples/sample_resume.txt",
            "examples/sample_job_description.txt",
        ):
            self.assertTrue(any(name.endswith(suffix) for name in members), suffix)

    def test_runtime_package_contains_importable_skill_implementation(self):
        members = self._members(self.runtime_zip)
        self.assertTrue(any(name.endswith("skill/interface.py") for name in members))
        self.assertTrue(any(name.endswith("skill/__init__.py") for name in members))

    def test_prompt_only_package_contains_no_runtime_code(self):
        members = self._members(self.prompt_zip)
        self.assertFalse(any("/skill/" in name for name in members))
        self.assertFalse(any(name.endswith("pyproject.toml") for name in members))

    def test_manifests_use_authoritative_skill_version_and_modes(self):
        runtime = self._read_json_member(self.runtime_zip, "PACKAGE_MANIFEST.json")
        prompt = self._read_json_member(self.prompt_zip, "PACKAGE_MANIFEST.json")
        self.assertEqual(runtime["skill_version"], VERSION)
        self.assertEqual(prompt["skill_version"], VERSION)
        self.assertEqual(runtime["package_mode"], "runtime")
        self.assertEqual(prompt["package_mode"], "prompt_only")
        self.assertEqual(runtime["skill_entrypoint"], "skill.interface:NextMoveSkill.run")
        self.assertEqual(runtime["cli_entrypoint"], "skill.__main__:main")
        self.assertIsNone(prompt["skill_entrypoint"])
        self.assertIsNone(prompt["cli_entrypoint"])
        self.assertTrue(runtime["build_id"].startswith("sha256:"))

    def test_manifest_checksums_cover_every_non_manifest_file(self):
        for package in (self.runtime_zip, self.prompt_zip):
            manifest = self._read_json_member(package, "PACKAGE_MANIFEST.json")
            with zipfile.ZipFile(package) as archive:
                root = archive.namelist()[0].split("/", 1)[0]
                actual = {
                    name.removeprefix(root + "/")
                    for name in archive.namelist()
                    if not name.endswith("/") and not name.endswith("PACKAGE_MANIFEST.json")
                }
                self.assertEqual(set(manifest["included_files"]), actual)
                for relative, expected in manifest["checksums"].items():
                    content = archive.read(f"{root}/{relative}")
                    self.assertEqual(hashlib.sha256(content).hexdigest(), expected)

    def test_forbidden_paths_are_not_packaged(self):
        forbidden = (
            "/.git/",
            "/.worktrees/",
            "/tmp/",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "benchmark/",
            "tests/",
        )
        for package in (self.runtime_zip, self.prompt_zip):
            for name in self._members(package):
                normalized = "/" + name.casefold()
                self.assertFalse(any(item in normalized for item in forbidden), name)

    def test_packages_contain_no_obvious_secret_or_credential(self):
        secret_pattern = re.compile(
            r"(?:sk-[a-z0-9_-]{12,}|-----BEGIN [A-Z ]+PRIVATE KEY-----|"
            r"(?:api[_ -]?key|access[_ -]?token|password)\s*[:=]\s*[^<\s]+)",
            re.IGNORECASE,
        )
        for package in (self.runtime_zip, self.prompt_zip):
            self.assertIsNone(secret_pattern.search(self._read_text_members(package)))

    def test_runtime_preflight_executes_skill_and_serializes_response(self):
        completed = self._check(self.runtime_zip)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lines = completed.stdout.strip().splitlines()
        result = json.loads(lines[-2])
        self.assertTrue(result["smoke_executed"])
        self.assertTrue(result["response_serializable"])
        self.assertEqual(lines[-1], "NEXTMOVE_READY")

    def test_runtime_preflight_records_zero_network_calls(self):
        completed = self._check(self.runtime_zip)
        result = json.loads(completed.stdout.strip().splitlines()[-2])
        self.assertEqual(result["network_calls"], 0)

    def test_clean_room_runtime_generates_human_career_report(self):
        with tempfile.TemporaryDirectory() as directory:
            with zipfile.ZipFile(self.runtime_zip) as archive:
                archive.extractall(directory)
            package = Path(directory) / f"nextmove-skill-package-{VERSION}"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_human_career_report.py",
                    "--scenario",
                    "transition",
                ],
                cwd=package,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("## 你的职业画像", completed.stdout)
        self.assertIn("## 岗位匹配", completed.stdout)
        self.assertIn("## 下一步行动", completed.stdout)

    def test_invalid_runtime_never_outputs_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "invalid.zip"
            with zipfile.ZipFile(invalid, "w") as archive:
                archive.writestr("invalid/SKILL.md", "not a runtime")
            completed = self._check(invalid)
        self.assertNotEqual(completed.returncode, 0)
        self.assertNotIn("NEXTMOVE_READY", completed.stdout)

    def test_prompt_only_preflight_has_only_prompt_marker(self):
        completed = self._check(self.prompt_zip)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("NEXTMOVE_READY", completed.stdout)
        self.assertEqual(completed.stdout.strip().splitlines()[-1], "NEXTMOVE_PROMPT_ONLY")

    def test_prompt_only_docs_never_claim_runtime_execution(self):
        text = self._read_text_members(self.prompt_zip)
        self.assertIn("NEXTMOVE_PROMPT_ONLY", text)
        self.assertIn("will not execute local Python Skill", text)
        self.assertNotIn("已调用 NextMoveSkill.run()", text)

    def test_samples_are_explicitly_fictional_and_contact_free(self):
        text = self._read_text_members(self.prompt_zip)
        self.assertGreaterEqual(text.count("FICTIONAL SAMPLE"), 2)
        self.assertNotRegex(text, r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
        self.assertNotRegex(text, r"\b1[3-9]\d{9}\b")

    def test_three_prompts_cover_truthfulness_and_safety_rules(self):
        text = self._read_text_members(self.prompt_zip)
        for heading in ("## 完整职业分析", "## 岗位匹配", "## 职业转型"):
            self.assertIn(heading, text)
        for rule in ("不得编造", "可迁移", "信息不足", "不保证", "敏感信息"):
            self.assertIn(rule, text)

    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as second_directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(BUILD_SCRIPT),
                    "--mode",
                    "all",
                    "--output",
                    second_directory,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            for first in (self.runtime_zip, self.prompt_zip):
                second = Path(second_directory) / first.name
                self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_text_package_content_is_identical_for_lf_and_crlf_checkouts(self):
        lf = b"first line\nsecond line\n"
        crlf = b"first line\r\nsecond line\r\n"
        expected = b"first line\nsecond line\n"

        self.assertEqual(
            package_builder._normalized_package_content("docs/example.md", lf),
            expected,
        )
        self.assertEqual(
            package_builder._normalized_package_content("docs/example.md", crlf),
            expected,
        )

    def test_prompt_archive_and_manifest_are_identical_across_line_endings(self):
        relative_files = (
            "SKILL.md",
            "LICENSE",
            "distribution/prompt_only/README.md",
            "distribution/prompt_only/QUICK_START.md",
            "distribution/common/PROMPTS.md",
            "distribution/prompt_only/OUTPUT_GUIDE.md",
            "distribution/prompt_only/PRIVACY_AND_FEEDBACK.md",
            "distribution/common/examples/sample_resume.txt",
            "distribution/common/examples/sample_job_description.txt",
        )

        def build_fixture(root: Path, newline: bytes) -> tuple[bytes, dict]:
            for relative in relative_files:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(newline.join((b"first line", b"second line", b"")))
            (root / "skill").mkdir()
            (root / "skill" / "__version__.py").write_bytes(
                newline.join((b'__version__ = "0.8.0"', b""))
            )
            (root / "skill.json").write_bytes(
                newline.join((b'{"version": "0.8.0"}', b""))
            )
            with (
                mock.patch.object(package_builder, "ROOT", root),
                mock.patch.object(package_builder, "SOURCE", root / "distribution"),
            ):
                _, archive_path = package_builder.build("prompt_only", root / "dist")
            archive_bytes = archive_path.read_bytes()
            with zipfile.ZipFile(archive_path) as archive:
                manifest_name = next(
                    name for name in archive.namelist() if name.endswith("PACKAGE_MANIFEST.json")
                )
                manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
            return archive_bytes, manifest

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lf_archive, lf_manifest = build_fixture(root / "lf", b"\n")
            crlf_archive, crlf_manifest = build_fixture(root / "crlf", b"\r\n")

        self.assertEqual(lf_manifest["checksums"], crlf_manifest["checksums"])
        self.assertEqual(lf_manifest["build_id"], crlf_manifest["build_id"])
        self.assertEqual(lf_archive, crlf_archive)

    def test_binary_package_content_is_preserved_byte_for_byte(self):
        binary = b"\x89PNG\r\n\x1a\n\x00payload\r\n\xff"

        self.assertEqual(
            package_builder._normalized_package_content("assets/example.png", binary),
            binary,
        )

    def test_public_contract_files_are_unchanged_in_runtime_archive(self):
        with zipfile.ZipFile(self.runtime_zip) as archive:
            root = archive.namelist()[0].split("/", 1)[0]
            for relative in ("SKILL.md", "skill.json"):
                expected = package_builder._normalized_package_content(
                    relative,
                    (ROOT / relative).read_bytes(),
                )
                self.assertEqual(archive.read(f"{root}/{relative}"), expected)


if __name__ == "__main__":
    unittest.main()
