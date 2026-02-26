import importlib.util
import unittest
from unittest.mock import patch

FASTAPI_READY = importlib.util.find_spec("fastapi") is not None
LANGCHAIN_READY = importlib.util.find_spec("langchain") is not None


@unittest.skipUnless(FASTAPI_READY and LANGCHAIN_READY, "fastapi/langchain not installed")
class ApiSmokeTests(unittest.TestCase):
    def test_health_and_config(self):
        import backend.api as api

        health = api.health()
        cfg = api.config()

        self.assertEqual(health["status"], "ok")
        self.assertIn("model_provider", cfg)

    def test_ask_endpoint_calls_service(self):
        import backend.api as api

        payload = api.AskRequest(question="How do buffers work?", skill_level="beginner")
        with patch("backend.api.ask_emacs", return_value={"answer": "x", "sources": []}):
            result = api.ask(payload)

        self.assertIn("answer", result)

    def test_explain_region_endpoint_calls_service(self):
        import backend.api as api

        payload = api.ExplainRegionRequest(
            code="(setq x 1)",
            language="elisp",
            context="",
            skill_level="beginner",
        )
        with patch("backend.api.explain_region", return_value={"answer": "x", "sources": []}):
            result = api.explain(payload)

        self.assertIn("answer", result)


if __name__ == "__main__":
    unittest.main()
