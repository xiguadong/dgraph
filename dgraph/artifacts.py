"""Artifact serialization, hashing, and final-SVG inspection."""

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from .viewspec import DgraphError


def yaml_dump(value, indent=0):
    """Serialize the JSON-compatible ViewSpec subset as readable YAML."""
    space = " " * indent
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{space}{key}:")
                lines.append(yaml_dump(item, indent + 2))
            else:
                lines.append(f"{space}{key}: {yaml_dump(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return space + "[]"
        lines = []
        for item in value:
            if isinstance(item, dict):
                first = True
                for key, child in item.items():
                    prefix = space + "- " if first else space + "  "
                    first = False
                    if isinstance(child, (dict, list)) and child:
                        lines.append(f"{prefix}{key}:")
                        lines.append(yaml_dump(child, indent + 4))
                    else:
                        lines.append(f"{prefix}{key}: {yaml_dump(child)}")
            else:
                lines.append(space + "- " + yaml_dump(item))
        return "\n".join(lines)
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inspect_svg(path):
    path = Path(path)
    issues = []
    try:
        root = ET.parse(path).getroot()
        view_box = [float(value) for value in root.attrib.get("viewBox", "0 0 1280 720").split()]
        width, height = view_box[2], view_box[3]
        for element in root.iter("{http://www.w3.org/2000/svg}text"):
            x, y = float(element.attrib.get("x", 0)), float(element.attrib.get("y", 0))
            if not 0 <= x <= width or not 0 <= y <= height:
                issues.append({"code": "out-of-canvas", "message": f"Text at ({x}, {y}) exceeds {width}x{height}."})
        source_nodes = [element for element in root.iter() if "data-source-id" in element.attrib]
        if not source_nodes:
            issues.append({"code": "missing-source-identity", "message": "No SVG node retains a source identity."})
    except (ET.ParseError, OSError, ValueError) as error:
        issues.append({"code": "invalid-svg", "message": str(error)})
    return {"ok": not issues, "issues": issues, "path": str(path)}


def write_artifacts(spec, svg, ir):
    output = Path(spec["outputs"]["directory"]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "view.yaml").write_text(yaml_dump(spec) + "\n", encoding="utf-8")
    (output / "diagram.dsl.yaml").write_text(yaml_dump(ir) + "\n", encoding="utf-8")
    (output / "diagram.svg").write_text(svg, encoding="utf-8")
    inspection = inspect_svg(output / "diagram.svg")
    report = {"ok": inspection["ok"], "type": spec["type"], "question": spec["intent"]["question"], "issues": inspection["issues"], "omissions": spec["selection"].get("omissions", [])}
    write_json(output / "report.json", report)
    manifest = {"schema": "dgraph-manifest/v1", "type": spec["type"], "inputSha256": hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest(), "files": {}}
    for name in ("view.yaml", "diagram.dsl.yaml", "diagram.svg", "report.json"):
        manifest["files"][name] = sha256(output / name)
    write_json(output / "manifest.json", manifest)
    if not report["ok"]:
        raise DgraphError("visual-inspection", "Generated SVG failed inspection; see report.json.")
    return output, report, manifest
