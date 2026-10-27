"""Verify example completeness, reports, and manifest hashes."""

import hashlib
import json
from pathlib import Path

from dgraph.catalog import CATALOG
from examples._shared.scaffold import ROOT, SYSML_TYPES


EXAMPLES = ROOT / "examples"


def _verify_manifest(folder):
    output = folder / "output"
    manifest = json.loads((output / "manifest.json").read_text())
    assert json.loads((output / "report.json").read_text())["ok"] is True
    count = 0
    for name, expected in manifest["files"].items():
        path = output / name
        assert path.is_file(), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
        count += 1
    return count


def main():
    checked = 0
    for entry in CATALOG:
        folder = EXAMPLES / entry["type"] / "semantic"
        for name in ("README.md", "draw.py", "input.json"):
            assert (folder / name).is_file(), folder / name
        checked += _verify_manifest(folder)
    for kind in sorted(SYSML_TYPES):
        folder = EXAMPLES / kind / "sysml"
        for name in ("README.md", "draw.py", "input.json", "model.sysml"):
            assert (folder / name).is_file(), folder / name
        checked += _verify_manifest(folder)
        assert json.loads((folder / "output/sysml-analysis/report.json").read_text())["ok"] is True
    assert not (ROOT / "output").exists(), "legacy output/ still exists"
    print(f"verified {len(CATALOG)} semantic + {len(SYSML_TYPES)} SysML examples; {checked} hashed artifacts")


if __name__ == "__main__":
    main()
