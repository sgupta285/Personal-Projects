import unittest

from app.runner import generate_demo_run


class RunnerTests(unittest.TestCase):
    def test_generate_demo_run_has_required_fields(self):
        payload = generate_demo_run("browser_export_report_v1", mode="success")
        self.assertIn("run_id", payload)
        self.assertEqual(payload["benchmark_id"], "browser_export_report_v1")
        self.assertTrue(len(payload["trajectory"]) >= 1)


if __name__ == "__main__":
    unittest.main()
