import json
import tempfile
import unittest
from pathlib import Path

import sync_models
import sync_sources


class CatalogTests(unittest.TestCase):
    def test_source_validate_entry_requires_fields(self):
        with self.assertRaises(ValueError):
            sync_sources.validate_entry({"id": "x"})

    def test_model_validate_entry_requires_fields(self):
        with self.assertRaises(ValueError):
            sync_models.validate_entry({"id": "x"})

    def test_source_should_include_noncommercial_rules(self):
        entry = {
            "id": "test",
            "filename": "a.pdf",
            "url": "https://example.com/a.pdf",
            "license": "CC BY-NC-ND 3.0",
            "enabled_by_default": True,
        }
        self.assertFalse(sync_sources.should_include(entry, include_noncommercial=False, include_all=False))
        self.assertTrue(sync_sources.should_include(entry, include_noncommercial=True, include_all=False))

    def test_model_should_include_default_rules(self):
        entry = {
            "id": "tiny",
            "filename": "tiny.gguf",
            "url": "https://example.com/tiny.gguf",
            "provider": "local_small",
            "enabled_by_default": False,
        }
        self.assertFalse(sync_models.should_include(entry, include_all=False))
        self.assertTrue(sync_models.should_include(entry, include_all=True))

    def test_load_catalog_rejects_non_array(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text(json.dumps({"not": "array"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                sync_sources.load_catalog(path)


if __name__ == "__main__":
    unittest.main()
