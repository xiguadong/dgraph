"""Thin, public-API-only runners for self-contained examples."""

import json
from pathlib import Path

from dgraph.artifacts import write_json
from dgraph.render import render_diagram
from dgraph.sysml import analyze_sysml
from dgraph.viewspec import DgraphError, validate_spec


def _input(example_dir):
    return json.loads((example_dir / "input.json").read_text(encoding="utf-8"))


def run_semantic(example_dir):
    example_dir = Path(example_dir).resolve()
    spec = _input(example_dir)
    if any(source.get("kind") == "sysml" for source in spec.get("sources", [])):
        raise DgraphError("unverified-sysml-source", "A semantic example cannot claim SysML model provenance without model analysis.")
    spec["outputs"]["directory"] = str(example_dir / "output")
    return render_diagram(spec)


def check_view_provenance(spec, analysis):
    """Check every SysML claim against exported compiler elements.

    A semantic source in a SysML example explicitly means that the compiler
    gates the model file while the diagram uses teaching example semantics.
    """
    sources = spec.get("sources", [])
    if not sources:
        return {"ok": False, "mode": "undeclared", "checked": [], "unresolved": ["sources"]}
    kinds = {source.get("kind") for source in sources}
    if not kinds <= {"semantic", "sysml"}:
        return {"ok": False, "mode": "invalid", "checked": [], "unresolved": ["sources"]}
    if kinds == {"semantic"}:
        return {"ok": True, "mode": "semantic-overlay", "checked": [], "unresolved": []}
    references = set()
    for element in (analysis.get("model") or {}).get("elements", []):
        for field in ("id", "qualifiedName"):
            if element.get(field):
                references.add(element[field])
    nodes = spec.get("selection", {}).get("nodes", [])
    claims = list(spec.get("selection", {}).get("modelElementRefs", []))
    mixed = "semantic" in kinds
    for node in nodes:
        source_kind = node.get("sourceKind")
        if mixed and source_kind not in {"sysml", "semantic"}:
            return {"ok": False, "mode": "mixed", "checked": [], "unresolved": [f"{node.get('id')}:sourceKind"]}
        if source_kind == "sysml" or not mixed:
            claims.append(node.get("sourceId"))
    checked = [claim for claim in claims if claim in references]
    unresolved = [claim for claim in claims if claim not in references]
    if not claims:
        unresolved.append("no SysML element references")
    return {"ok": not unresolved, "mode": "sysml-referenced" if not mixed else "mixed", "checked": checked, "unresolved": unresolved}


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
    spec = validate_spec(spec)
    provenance = check_view_provenance(spec, analysis)
    write_json(example_dir / "output" / "sysml-analysis" / "view-provenance.json", provenance)
    if not provenance["ok"]:
        return {"ok": False, "analysis": analysis, "provenance": provenance}
    result = render_diagram(spec)
    result["analysis"] = analysis
    result["provenance"] = provenance
    return result
