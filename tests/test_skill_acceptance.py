import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from skill import NextMoveSkill, __version__
from skill.__main__ import main
from skill.metadata import SKILL_METADATA


ROOT = Path(__file__).resolve().parents[1]


class SkillOperationalAcceptanceTests(unittest.TestCase):
    def test_agent_discovers_entrypoint_and_career_analysis(self):
        manifest = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "NextMove")
        self.assertEqual(manifest["version"], __version__)
        self.assertEqual(manifest["entrypoint"], "skill.__main__:main")
        self.assertIn("career_analysis", manifest["capabilities"])
        self.assertIn("input_schema", manifest)
        self.assertIn("output_schema", manifest)
        self.assertEqual(SKILL_METADATA["version"], __version__)
        self.assertEqual(SKILL_METADATA["entrypoint"], manifest["entrypoint"])
        self.assertEqual(SKILL_METADATA["capabilities"], manifest["capabilities"])
        self.assertEqual(
            SKILL_METADATA["capability_descriptions"],
            manifest["capability_descriptions"],
        )
        self.assertIn("input_schema", SKILL_METADATA)
        self.assertIn("output_schema", SKILL_METADATA)
        self.assertEqual(SKILL_METADATA["input_schema"], manifest["input_schema"])
        self.assertEqual(SKILL_METADATA["output_schema"], manifest["output_schema"])

    def test_console_script_binding_invokes_same_offline_cli(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            project["project"]["scripts"]["nextmove"],
            "skill.__main__:main",
        )

        with tempfile.TemporaryDirectory() as directory:
            resume_path = Path(directory) / "resume.txt"
            resume_path.write_text("Python engineer with SQL experience.", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(["analyze", "--resume", str(resume_path)])

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["result"]["success"])

    def test_cli_invokes_career_analysis_with_job_description(self):
        completed = self._run_cli(
            "Python backend engineer with SQL experience.",
            "--job-description",
            "Backend role requiring Python, SQL, and Docker.",
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["capability"], "career_analysis")
        self.assertTrue(payload["result"]["success"])

    def test_cli_normalizes_missing_job_description_to_empty_string(self):
        completed = self._run_cli("Python backend engineer.")

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["result"]["job_match"]["match_score"], 0)

    def test_cli_returns_json_failure_for_missing_resume_file(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "skill",
                "analyze",
                "--resume",
                str(ROOT / "missing-resume.txt"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["capability"], "career_analysis")
        self.assertEqual(payload["error"]["code"], "INVALID_INPUT")

    def test_skill_api_still_rejects_missing_job_description(self):
        response = NextMoveSkill().run(
            "career_analysis",
            {"resume": "Python backend engineer."},
        )

        serialized = json.dumps(
            {
                "success": response.success,
                "capability": response.capability,
                "error": {
                    "code": response.error.code,
                    "message": response.error.message,
                },
            }
        )
        self.assertFalse(response.success)
        self.assertEqual(response.error.code, "INVALID_INPUT")
        self.assertIsInstance(serialized, str)

    def _run_cli(self, resume_text, *extra_args):
        with tempfile.TemporaryDirectory() as directory:
            resume_path = Path(directory) / "resume.txt"
            resume_path.write_text(resume_text, encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skill",
                    "analyze",
                    "--resume",
                    str(resume_path),
                    *extra_args,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )


if __name__ == "__main__":
    unittest.main()
