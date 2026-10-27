"""Thin, public-API-only runners for self-contained examples."""

import json
from pathlib import Path

from dgraph.render import render_diagram
from dgraph.sysml import analyze_sysml


def _input(example_dir):
    return json.loads((example_dir / "input.json").read_text(encoding="utf-8"))


def run_semantic(example_dir):
    example_dir = Path(example_dir).resolve()
    spec = _input(example_dir)
    spec["outputs"]["directory"] = str(example_dir / "output")
    return render_diagram(spec)


def run_sysml(example_dir):
    example_dir = Path(example_dir).resolve()
    spec = _input(example_dir)
    model = example_dir / "model.sysml"
    analysis = analyze_sysml(
        [{"name": model.name, "content": model.read_text(encoding="utf-8")}],
        str(example_dir / "output" / "sysml-analysis"),
    )
    if not analysis["ok"]:
        return {"ok": False, "analysis": analysis}
    spec["outputs"]["directory"] = str(example_dir / "output")
    result = render_diagram(spec)
    result["analysis"] = analysis
    return result
