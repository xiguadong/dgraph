"""Verify that every saved example matches its source and current renderer."""

import hashlib
import json
from pathlib import Path

from dgraph.catalog import CATALOG
from dgraph.artifacts import inspect_svg, yaml_dump
from dgraph.render import to_ir
from dgraph.svg import render_svg
from dgraph.sysml import EXPECTED_SHA256
from dgraph.viewspec import DOMAIN_FIELDS, validate_spec
from examples._shared.runner import check_view_provenance
from examples._shared.scaffold import ROOT, SYSML_TYPES


EXAMPLES = ROOT / "examples"


def _verify_manifest(folder):
    output = folder / "output"
    manifest = json.loads((output / "manifest.json").read_text())
    report = json.loads((output / "report.json").read_text())
    assert report["ok"] is True, folder
    source = json.loads((folder / "input.json").read_text(encoding="utf-8"))
    source["outputs"]["directory"] = str(output.resolve())
    spec = validate_spec(source)
    assert manifest["type"] == spec["type"], folder
    expected_input_hash = hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    assert manifest["inputSha256"] == expected_input_hash, folder
    assert (output / "view.yaml").read_text(encoding="utf-8") == yaml_dump(spec) + "\n", folder
    ir = to_ir(spec)
    field = DOMAIN_FIELDS.get(spec["type"])
    if field:
        assert ir.get(field) == spec["selection"][field], f"{folder}: {field} is absent from the IR"
    assert (output / "diagram.dsl.yaml").read_text(encoding="utf-8") == yaml_dump(ir) + "\n", folder
    assert (output / "diagram.svg").read_text(encoding="utf-8") == render_svg(spec), f"{folder}: SVG is stale or unrelated to input.json"
    inspection = inspect_svg(output / "diagram.svg", spec)
    assert inspection["ok"] and not report["issues"], f"{folder}: {inspection['issues']}"
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
        analysis = json.loads((folder / "output/sysml-analysis/report.json").read_text())
        assert analysis["ok"] is True, folder
        assert analysis["compiler"]["sha256"] == EXPECTED_SHA256, folder
        assert (folder / "output/sysml-analysis/sources/model.sysml").read_bytes() == (folder / "model.sysml").read_bytes(), folder
        source = json.loads((folder / "input.json").read_text(encoding="utf-8"))
        provenance = check_view_provenance(source, analysis)
        assert provenance["ok"], f"{folder}: {provenance['unresolved']}"
        assert json.loads((folder / "output/sysml-analysis/view-provenance.json").read_text()) == provenance, folder
    assert not (ROOT / "output").exists(), "legacy output/ still exists"
    print(f"verified {len(CATALOG)} semantic + {len(SYSML_TYPES)} SysML examples; {checked} hashed artifacts")


if __name__ == "__main__":
    main()
