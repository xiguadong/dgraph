"""MCP-facing tool definitions and dispatch."""

import json
from pathlib import Path

from .artifacts import inspect_svg
from .catalog import CATALOG
from .render import render_diagram
from .sysml import analyze_sysml
from .viewspec import DgraphError, validate_spec


def _schema(kind):
    properties = {
        "list_diagram_types": {},
        "analyze_sysml": {"files": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "content": {"type": "string"}}, "required": ["name", "content"]}}, "outputDir": {"type": "string"}},
        "validate_viewspec": {"spec": {"type": "object"}},
        "render_diagram": {"spec": {"type": "object"}},
        "inspect_diagram": {"path": {"type": "string"}},
    }[kind]
    required = {"analyze_sysml": ["files", "outputDir"], "validate_viewspec": ["spec"], "render_diagram": ["spec"], "inspect_diagram": ["path"]}.get(kind, [])
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


def tool_definitions():
    descriptions = {
        "list_diagram_types": "List renderable and catalog-only engineering diagram types.",
        "analyze_sysml": "Parse, check, and export a frozen multi-file SysML v2 workspace with the pinned Rust compiler.",
        "validate_viewspec": "Validate and normalize a diagram-view/v1 ViewSpec without rendering.",
        "render_diagram": "Render a ViewSpec to SVG, YAML DSL, report, and hash manifest.",
        "inspect_diagram": "Inspect a generated SVG for canvas and source-identity defects.",
    }
    return [{"name": name, "description": description, "inputSchema": _schema(name)} for name, description in descriptions.items()]


def resources():
    result = [{"uri": "dgraph://catalog", "name": "Diagram capability catalog", "mimeType": "application/json"}]
    result += [{"uri": item["schema"], "name": f"{item['type']} ViewSpec guidance", "mimeType": "application/json"} for item in CATALOG]
    return result


def read_resource(uri):
    if uri == "dgraph://catalog":
        value = {"types": CATALOG}
    elif uri.startswith("dgraph://schema/"):
        kind = uri.rsplit("/", 1)[-1]
        entry = next((item for item in CATALOG if item["type"] == kind), None)
        if not entry:
            raise DgraphError("resource-not-found", f"Unknown resource: {uri}")
        value = {"schema": "diagram-view/v1", "type": kind, "status": entry["status"], "question": entry["question"], "required": ["schema", "type", "intent", "selection", "outputs"], "sourceAuthority": "Current user intent selects the view; existing SysML views are references only.", "nodeFields": ["id", "label", "kind", "x", "y", "w", "h", "sourceId"], "edgeFields": ["source", "target", "kind", "label"]}
    else:
        raise DgraphError("resource-not-found", f"Unknown resource: {uri}")
    return json.dumps(value, ensure_ascii=False, indent=2)


def call_tool(name, arguments):
    if name == "list_diagram_types":
        return {"types": CATALOG}
    if name == "analyze_sysml":
        return analyze_sysml(arguments.get("files"), arguments.get("outputDir", ""))
    if name == "validate_viewspec":
        return {"ok": True, "spec": validate_spec(arguments.get("spec"))}
    if name == "render_diagram":
        return render_diagram(arguments.get("spec"))
    if name == "inspect_diagram":
        return inspect_svg(Path(arguments.get("path", "")))
    raise DgraphError("unknown-tool", f"Unknown tool: {name}")
