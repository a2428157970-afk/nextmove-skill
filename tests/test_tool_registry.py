import unittest

from skill import NextMoveSkill
from skill.agent import AgentTool
from skill.agent.registry import (
    SkillToolBinding,
    SkillToolRegistry,
    UnknownToolError,
    get_default_tool_registry,
)
from skill.schemas.analysis import ResumeAnalysisResult
from skill.schemas.resume import ExperienceEntry, ResumeProfile


class SkillToolRegistryTests(unittest.TestCase):
    def setUp(self):
        self.profile = ResumeProfile(
            summary="Backend engineer focused on Python APIs.",
            skills=["Python", "FastAPI", "SQL"],
            experience=[
                ExperienceEntry(
                    role="Backend Engineer",
                    highlights=["Built Python APIs with FastAPI."],
                )
            ],
        )

    def test_registry_loads_all_agent_tools(self):
        registry = get_default_tool_registry()

        self.assertEqual(
            [binding.tool.name for binding in registry.list_tools()],
            [
                "analyze_resume",
                "improve_resume",
                "match_job",
                "career_advice",
            ],
        )
        self.assertEqual(
            [binding.capability for binding in registry.list_tools()],
            [
                "analyze_resume",
                "improve_resume",
                "match_job",
                "career_advice",
            ],
        )

    def test_get_returns_tool_metadata_and_invocation_capability(self):
        registry = get_default_tool_registry()

        binding = registry.get("match_job")

        self.assertIsInstance(binding, SkillToolBinding)
        self.assertIsInstance(binding.tool, AgentTool)
        self.assertEqual(binding.tool.name, "match_job")
        self.assertEqual(binding.capability, "match_job")

    def test_registered_tool_capability_can_execute_with_nextmove_skill(self):
        registry = get_default_tool_registry()
        binding = registry.get("analyze_resume")

        response = NextMoveSkill().run(
            binding.capability,
            {"resume": self.profile},
        )

        self.assertTrue(response.success)
        self.assertEqual(response.capability, "analyze_resume")
        self.assertIsInstance(response.result, ResumeAnalysisResult)

    def test_unknown_tool_returns_clear_error(self):
        registry = get_default_tool_registry()

        with self.assertRaisesRegex(UnknownToolError, "unknown tool: missing_tool"):
            registry.get("missing_tool")

    def test_register_adds_custom_binding(self):
        registry = SkillToolRegistry()
        tool = AgentTool(
            name="custom_tool",
            description="Custom test tool.",
            input_schema={"type": "object", "properties": {}, "required": []},
            output_schema={"type": "object", "properties": {}},
        )

        registry.register(tool, capability="custom_capability")

        binding = registry.get("custom_tool")
        self.assertEqual(binding.tool, tool)
        self.assertEqual(binding.capability, "custom_capability")


if __name__ == "__main__":
    unittest.main()
