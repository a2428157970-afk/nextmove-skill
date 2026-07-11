"""Opt-in OpenAI-compatible transport validation through external assembly."""

import importlib
import os
import unittest


@unittest.skipUnless(
    os.getenv("RUN_LIVE_AI_TEST") == "true",
    "Set RUN_LIVE_AI_TEST=true to run live AI tests.",
)
class OpenAITransportLiveTests(unittest.TestCase):
    """Run only an externally supplied validator without reading credentials."""

    def test_external_transport_validator(self):
        factory_path = os.getenv("NEXTMOVE_LIVE_TRANSPORT_FACTORY")
        if not factory_path:
            self.skipTest("External live transport factory is not configured.")

        try:
            module_name, factory_name = factory_path.rsplit(":", 1)
            module = importlib.import_module(module_name)
            factory = getattr(module, factory_name)
        except (AttributeError, ImportError, ValueError) as exc:
            self.fail(f"Invalid external live transport factory: {type(exc).__name__}")

        validator = factory()
        self.assertTrue(validator())


if __name__ == "__main__":
    unittest.main()
