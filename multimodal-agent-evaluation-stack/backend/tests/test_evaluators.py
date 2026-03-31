import unittest

from app.evaluators import dispatch_evaluator


class EvaluatorTests(unittest.TestCase):
    def test_exact_match_success(self):
        result = dispatch_evaluator(
            evaluator_type="exact_match",
            expected_output={
                "expected_payload": {"status": "exported", "artifact": "report.csv"},
                "required_fields": ["status", "artifact"],
            },
            expected_tools=["navigate", "download"],
            actual_output={"status": "exported", "artifact": "report.csv"},
            trajectory=[
                {"tool_name": "navigate", "success": True},
                {"tool_name": "download", "success": True},
            ],
        )
        self.assertTrue(result.success)
        self.assertEqual(result.score, 1.0)

    def test_rubric_scores_partial_credit(self):
        result = dispatch_evaluator(
            evaluator_type="rubric",
            expected_output={
                "required_fields": ["recommendation", "justification"],
                "preferred_answer": "enterprise",
                "ideal_max_steps": 4,
                "success_threshold": 0.8,
            },
            expected_tools=["knowledge_lookup"],
            actual_output={"recommendation": "pro", "justification": "Cheaper", "format_valid": True},
            trajectory=[{"tool_name": "knowledge_lookup", "success": True}],
        )
        self.assertGreater(result.score, 0.0)
        self.assertLess(result.score, 1.0)


if __name__ == "__main__":
    unittest.main()
