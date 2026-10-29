"""Public deterministic rendering service."""

from copy import deepcopy

from .artifacts import inspect_svg, write_artifacts
from .svg import render_svg
from .viewspec import validate_spec


def to_ir(spec):
    selection = deepcopy(spec["selection"])
    return {
        "schema": "diagram-ir/v1",
        "type": spec["type"],
        "layout": selection.get("layout", spec["type"]),
        "nodes": selection["nodes"],
        "edges": selection.get("edges", []),
        "groups": selection.get("groups", []),
        "matrices": selection.get("matrices", []),
        "charts": selection.get("charts", []),
        "timelines": selection.get("timelines", []),
        "qfd": selection.get("qfd"),
        "gantt": selection.get("gantt"),
        "faultTree": selection.get("faultTree"),
        "c4Container": selection.get("c4Container"),
        "umlClass": selection.get("umlClass"),
        "sequenceModel": selection.get("sequenceModel"),
        "n2Model": selection.get("n2Model"),
        "dfdModel": selection.get("dfdModel"),
        "bpmnModel": selection.get("bpmnModel"),
        "riskMatrix": selection.get("riskMatrix"),
        "dmnModel": selection.get("dmnModel"),
        "timingModel": selection.get("timingModel"),
        "tradespaceModel": selection.get("tradespaceModel"),
        "pertModel": selection.get("pertModel"),
        "annotations": selection.get("annotations", []),
    }


def mermaid_source(spec):
    """Emit Mermaid only for graph semantics that survive the conversion."""
    if spec["type"] not in {"activity", "state-machine", "package", "block-definition"}:
        return None
    lines = ["flowchart TD"]
    id_map = {node["id"]: f"n{index}" for index, node in enumerate(spec["selection"]["nodes"])}
    for node in spec["selection"]["nodes"]:
        label = node["label"].replace("\n", "<br/>").replace('"', "'")
        lines.append(f'  {id_map[node["id"]]}["{label}"]')
    for edge in spec["selection"].get("edges", []):
        arrow = "-.->" if edge["kind"] in {"dependency", "derive", "verify", "satisfy"} else "-->"
        label = ""
        if edge.get("label"):
            safe_label = edge["label"].replace("\n", " ").replace("|", r"\|")
            label = f"|{safe_label}|"
        lines.append(f'  {id_map[edge["source"]]} {arrow}{label} {id_map[edge["target"]]}')
    return "\n".join(lines) + "\n"


def render_diagram(spec):
    normalized = validate_spec(spec)
    ir = to_ir(normalized)
    svg = render_svg(normalized)
    mermaid = mermaid_source(normalized)
    output, report, manifest = write_artifacts(normalized, svg, ir, mermaid=mermaid)
    artifacts = {
        "viewspec": str(output / "view.yaml"),
        "dsl": str(output / "diagram.dsl.yaml"),
        "svg": str(output / "diagram.svg"),
        "report": str(output / "report.json"),
        "manifest": str(output / "manifest.json"),
    }
    if mermaid:
        artifacts["mmd"] = str(output / "diagram.mmd")
    return {"ok": True, "type": normalized["type"], "outputDir": str(output), "artifacts": artifacts, "report": report, "manifest": manifest}


__all__ = ["render_diagram", "inspect_svg", "to_ir", "mermaid_source"]
