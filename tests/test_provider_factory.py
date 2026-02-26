import importlib.util
import unittest


class ProviderFactoryTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("langchain") is not None, "langchain not installed")
    def test_factory_rejects_unknown_provider(self):
        from backend.config import AppConfig
        from backend.providers.factory import get_chat_provider

        config = AppConfig(model_provider="unknown")
        with self.assertRaises(ValueError):
            get_chat_provider(config)

    @unittest.skipUnless(importlib.util.find_spec("langchain") is not None, "langchain not installed")
    def test_factory_openai_provider(self):
        from backend.config import AppConfig
        from backend.providers.factory import get_chat_provider

        config = AppConfig(
            model_provider="openai",
            chat_model="gpt-4o-mini",
            openai_api_key="test-key",
        )
        provider = get_chat_provider(config)
        self.assertEqual(provider.name, "openai")
        self.assertEqual(provider.model, "gpt-4o-mini")


if __name__ == "__main__":
    unittest.main()
