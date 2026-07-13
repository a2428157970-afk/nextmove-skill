import unittest

from skill.agent import AGENT_TOOLS, AgentTool, get_agent_tools


class AgentToolSchemaTests(unittest.TestCase):
    def test_tools_can_be_loaded(self):
        tools = get_agent_tools()

        self.assertEqual(len(tools), 5)
        self.assertTrue(all(isinstance(tool, AgentTool) for tool in tools))
        self.assertIsNot(tools, AGENT_TOOLS)

    def test_tools_match_supported_capabilities(self):
        tools = get_agent_tools()

        self.assertEqual(
            [tool.name for tool in tools],
            [
                "analyze_resume",
                "improve_resume",
                "match_job",
                "career_advice",
                "career_analysis",
            ],
        )

    def test_each_tool_has_complete_metadata(self):
        for tool in get_agent_tools():
            with self.subTest(tool=tool.name):
                self.assertTrue(tool.name)
                self.assertTrue(tool.description)
                self.assertEqual(tool.input_schema["type"], "object")
                self.assertIn("properties", tool.input_schema)
                self.assertIn("required", tool.input_schema)
                self.assertEqual(tool.output_schema["type"], "object")
                self.assertIn("properties", tool.output_schema)

    def test_capability_inputs_are_correct(self):
        tools = {tool.name: tool for tool in get_agent_tools()}

        self.assertEqual(tools["analyze_resume"].input_schema["required"], ["resume"])
        self.assertEqual(tools["improve_resume"].input_schema["required"], ["resume"])
        self.assertEqual(
            tools["match_job"].input_schema["required"],
            ["resume", "job_description"],
        )
        self.assertEqual(tools["career_advice"].input_schema["required"], ["resume"])
        self.assertIn("analysis", tools["career_advice"].input_schema["properties"])
        self.assertEqual(
            tools["career_analysis"].input_schema["required"],
            ["resume", "job_description"],
        )

    def test_career_level_agent_enum_remains_legacy_contract(self):
        tool = {tool.name: tool for tool in get_agent_tools()}["analyze_resume"]

        self.assertEqual(
            tool.output_schema["properties"]["career_level"]["enum"],
            ["intern", "junior", "mid", "senior", "lead", "unknown"],
        )


if __name__ == "__main__":
    unittest.main()
