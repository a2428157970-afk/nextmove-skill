import importlib
import unittest


class PackageImportTests(unittest.TestCase):
    def test_skill_package_exports_public_api(self):
        skill = importlib.import_module("skill")

        self.assertTrue(hasattr(skill, "NextMoveSkill"))
        self.assertTrue(hasattr(skill, "SkillResponse"))
        self.assertTrue(hasattr(skill, "SkillError"))
        self.assertTrue(hasattr(skill, "__version__"))

    def test_public_api_can_be_imported_directly(self):
        from skill import NextMoveSkill, SkillError, SkillResponse

        self.assertEqual(NextMoveSkill.__name__, "NextMoveSkill")
        self.assertEqual(SkillResponse.__name__, "SkillResponse")
        self.assertEqual(SkillError.__name__, "SkillError")

    def test_metadata_uses_package_version(self):
        from skill import __version__
        from skill.metadata import SKILL_METADATA

        self.assertEqual(SKILL_METADATA["version"], __version__)
        self.assertIn("capabilities", SKILL_METADATA)
        self.assertIn("description", SKILL_METADATA)


if __name__ == "__main__":
    unittest.main()
