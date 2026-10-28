"""Artifact serialization, hashing, and final-SVG inspection."""

import hashlib
import json
from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET

from .viewspec import DOMAIN_FIELDS, DgraphError


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


def inspect_svg(path, spec=None):
    path = Path(path)
    issues = []
    try:
        root = ET.parse(path).getroot()
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Root element must be SVG.")
        view_box = [float(value) for value in root.attrib["viewBox"].split()]
        if len(view_box) != 4 or view_box[2] <= 0 or view_box[3] <= 0:
            raise ValueError("SVG viewBox must contain a positive width and height.")
        left, top, width, height = view_box
        right, bottom = left + width, top + height
        def inside(x, y, tolerance=0.01):
            return left - tolerance <= x <= right + tolerance and top - tolerance <= y <= bottom + tolerance

        for element in root.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            a = element.attrib
            if tag == "text":
                x, y = float(a.get("x", 0)), float(a.get("y", 0))
                size = float(a.get("font-size", 14))
                content = "".join(element.itertext())
                estimate = sum((1.0 if unicodedata.east_asian_width(char) in "WF" else 0.55) * size for char in content)
                anchor = a.get("text-anchor", "start")
                text_left = x - (estimate if anchor == "end" else estimate / 2 if anchor == "middle" else 0)
                if not inside(x, y) or text_left < left - 2 or text_left + estimate > right + 2 or y - size < top - 2:
                    issues.append({"code": "out-of-canvas", "message": f"Text {content[:40]!r} exceeds the viewBox."})
            elif tag == "rect":
                x, y = float(a.get("x", 0)), float(a.get("y", 0))
                w, h = float(a.get("width", 0)), float(a.get("height", 0))
                if w < 0 or h < 0 or not inside(x, y) or not inside(x + w, y + h):
                    issues.append({"code": "out-of-canvas", "message": f"Rectangle at ({x}, {y}) exceeds the viewBox."})
            elif tag in {"circle", "ellipse"}:
                cx, cy = float(a.get("cx", 0)), float(a.get("cy", 0))
                rx = float(a.get("r", a.get("rx", 0)))
                ry = float(a.get("r", a.get("ry", 0)))
                if rx < 0 or ry < 0 or not inside(cx - rx, cy - ry) or not inside(cx + rx, cy + ry):
                    issues.append({"code": "out-of-canvas", "message": f"{tag} at ({cx}, {cy}) exceeds the viewBox."})
            elif tag == "line":
                if not inside(float(a.get("x1", 0)), float(a.get("y1", 0))) or not inside(float(a.get("x2", 0)), float(a.get("y2", 0))):
                    issues.append({"code": "out-of-canvas", "message": "A line endpoint exceeds the viewBox."})
        source_nodes = [element for element in root.iter() if "data-source-id" in element.attrib]
        if not source_nodes:
            issues.append({"code": "missing-source-identity", "message": "No SVG node retains a source identity."})
        if spec is not None and spec["type"] not in DOMAIN_FIELDS:
            retained = {element.attrib["data-source-id"] for element in source_nodes}
            for node in spec["selection"]["nodes"]:
                if node["sourceId"] not in retained:
                    issues.append({"code": "missing-source-identity", "message": f"Node {node['id']} is absent from SVG source identities."})
    except (ET.ParseError, OSError, ValueError, KeyError) as error:
        issues.append({"code": "invalid-svg", "message": str(error)})
    return {"ok": not issues, "issues": issues, "path": str(path)}


def write_artifacts(spec, svg, ir):
    output = Path(spec["outputs"]["directory"]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "view.yaml").write_text(yaml_dump(spec) + "\n", encoding="utf-8")
    (output / "diagram.dsl.yaml").write_text(yaml_dump(ir) + "\n", encoding="utf-8")
    (output / "diagram.svg").write_text(svg, encoding="utf-8")
    inspection = inspect_svg(output / "diagram.svg", spec)
    report = {"ok": inspection["ok"], "type": spec["type"], "question": spec["intent"]["question"], "issues": inspection["issues"], "omissions": spec["selection"].get("omissions", [])}
    write_json(output / "report.json", report)
    manifest = {"schema": "dgraph-manifest/v1", "type": spec["type"], "inputSha256": hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest(), "files": {}}
    for name in ("view.yaml", "diagram.dsl.yaml", "diagram.svg", "report.json"):
        manifest["files"][name] = sha256(output / name)
    write_json(output / "manifest.json", manifest)
    if not report["ok"]:
        raise DgraphError("visual-inspection", "Generated SVG failed inspection; see report.json.")
    return output, report, manifest
