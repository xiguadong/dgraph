import hashlib
import sys
import tempfile
import time
import unittest
from pathlib import Path

from dgraph.sysml import _run, analyze_sysml, compiler_supported
from dgraph.viewspec import DgraphError


COMMON = "package Common { part def Power; }\n"
MODEL = "package Model { import Common::*; part def System { part power : Power; } }\n"


@unittest.skipUnless(compiler_supported(), "pinned SysML compiler is not executable on this host")
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


class SysMLInputValidationTests(unittest.TestCase):
    def test_unsafe_or_duplicate_names_are_rejected_before_compilation(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                [{"name": "../escape.sysml", "content": MODEL}],
                [{"name": "model.sysml", "content": MODEL}, {"name": "./model.sysml", "content": MODEL}],
                [{"name": "Model.sysml", "content": MODEL}, {"name": "model.sysml", "content": MODEL}],
                [{"name": "model.txt", "content": MODEL}],
            ]
            for files in cases:
                with self.subTest(files=files):
                    with self.assertRaises(DgraphError):
                        analyze_sysml(files, tmp)

    @unittest.skipIf(compiler_supported(), "host can execute the pinned compiler")
    def test_incompatible_compiler_is_reported_as_structured_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DgraphError) as caught:
                analyze_sysml([{"name": "model.sysml", "content": MODEL}], tmp)
            self.assertEqual("compiler-unavailable", caught.exception.code)
            self.assertEqual("compilation", caught.exception.phase)
            self.assertTrue(caught.exception.suggestion)

    def test_compiler_timeout_kills_the_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            started = time.monotonic()
            with self.assertRaises(DgraphError) as caught:
                _run([sys.executable, "-c", "import time; time.sleep(5)"], tmp, timeout=0.1)
            self.assertEqual("compiler-timeout", caught.exception.code)
            self.assertLess(time.monotonic() - started, 2)


if __name__ == "__main__":
    unittest.main()
