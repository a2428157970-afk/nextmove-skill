import unittest

from skill.adapters.agent import BaseAgentAdapter, GenericAgentAdapter
from skill.agent import AgentTool, get_agent_tools


class AgentAdapterTests(unittest.TestCase):
    def test_adapter_can_be_loaded(self):
        adapter = GenericAgentAdapter()

        self.assertIsInstance(adapter, BaseAgentAdapter)

    def test_agent_tool_can_be_converted_to_generic_dict(self):
        tool = AgentTool(
            name="example_tool",
            description="Example provider-neutral tool.",
            input_schema={
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
            },
            output_schema={
                "type": "object",
                "properties": {"result": {"type": "string"}},
            },
        )

        exported = GenericAgentAdapter().export_tools([tool])

        self.assertEqual(
            exported,
            [
                {
                    "name": "example_tool",
                    "description": "Example provider-neutral tool.",
                    "input_schema": tool.input_schema,
                    "output_schema": tool.output_schema,
                }
            ],
        )

    def test_exported_structure_is_stable_for_all_agent_tools(self):
        exported = GenericAgentAdapter().export_tools(get_agent_tools())

        self.assertEqual(len(exported), 4)
        for item in exported:
            with self.subTest(tool=item["name"]):
                self.assertEqual(
                    list(item.keys()),
                    ["name", "description", "input_schema", "output_schema"],
                )
                self.assertIsInstance(item["name"], str)
                self.assertIsInstance(item["description"], str)
                self.assertIsInstance(item["input_schema"], dict)
                self.assertIsInstance(item["output_schema"], dict)


if __name__ == "__main__":
    unittest.main()
