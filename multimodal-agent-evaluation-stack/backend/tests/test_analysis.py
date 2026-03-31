import unittest

from app.analysis import classify_failure


class AnalysisTests(unittest.TestCase):
    def test_timeout_detection(self):
        result = classify_failure({"status": "timeout", "trajectory": [], "final_output": {}}, None)
        self.assertEqual(result.failure_mode, "timeout")

    def test_hallucinated_completion_detection(self):
        result = classify_failure(
            {
                "status": "completed",
                "success_claimed": True,
                "trajectory": [{"tool_name": "navigate", "success": True}],
                "final_output": {},
            },
            {"success": False},
        )
        self.assertEqual(result.failure_mode, "hallucinated_completion")


if __name__ == "__main__":
    unittest.main()
