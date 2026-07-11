"""Live AI tests remain disabled unless explicitly enabled by the environment."""

import os
import unittest


@unittest.skipUnless(
    os.getenv("RUN_LIVE_AI_TEST") == "true",
    "Set RUN_LIVE_AI_TEST=true to run live AI tests.",
)
class LiveAITestBoundaryTests(unittest.TestCase):
    """Reserved boundary for externally configured live provider checks."""

    def test_live_test_execution_is_explicitly_enabled(self):
        self.assertEqual(os.getenv("RUN_LIVE_AI_TEST"), "true")


if __name__ == "__main__":
    unittest.main()
