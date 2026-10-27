import hashlib
import tempfile
import unittest
from pathlib import Path

from dgraph.sysml import analyze_sysml


COMMON = "package Common { part def Power; }\n"
MODEL = "package Model { import Common::*; part def System { part power : Power; } }\n"


class SysMLIntegrationTests(unittest.TestCase):
    def test_valid_multifile_model_is_checked_and_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze_sysml([
                {"name": "common.sysml", "content": COMMON},
                {"name": "model.sysml", "content": MODEL},
            ], tmp)
            self.assertTrue(result["ok"], result.get("diagnostics"))
            self.assertEqual("v0.1.4", result["compiler"]["version"])
            self.assertGreater(result["model"]["totalElements"], 0)
            self.assertTrue(Path(result["artifacts"]["export"]).is_file())

    def test_invalid_model_returns_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze_sysml([{"name": "broken.sysml", "content": "package Broken {"}], tmp)
            self.assertFalse(result["ok"])
            self.assertTrue(result["diagnostics"])

    def test_input_content_and_snapshots_are_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = {"name": "model.sysml", "content": MODEL}
            before = hashlib.sha256(source["content"].encode()).hexdigest()
            result = analyze_sysml([source, {"name": "common.sysml", "content": COMMON}], tmp)
            self.assertEqual(before, hashlib.sha256(source["content"].encode()).hexdigest())
            snapshot = Path(result["artifacts"]["sources"]) / "model.sysml"
            self.assertEqual(before, hashlib.sha256(snapshot.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
