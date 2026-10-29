"""Artifact serialization, transactional publication, and SVG inspection."""

from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET

from .errors import DgraphError
from .viewspec import DOMAIN_FIELDS


SVG_NS = "http://www.w3.org/2000/svg"
MAX_SVG_BYTES = 32 * 1024 * 1024
MAX_ISSUES = 100
ARTIFACT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CORE_ARTIFACTS = ("view.yaml", "diagram.dsl.yaml", "diagram.svg", "report.json")


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


def atomic_write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def write_json(path, value):
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _finite_float(value, default=None):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _shape_bounds(element):
    tag = element.tag.rsplit("}", 1)[-1]
    if tag == "rect":
        x = _finite_float(element.attrib.get("x"), 0)
        y = _finite_float(element.attrib.get("y"), 0)
        width = _finite_float(element.attrib.get("width"))
        height = _finite_float(element.attrib.get("height"))
        if width is None or height is None or width < 0 or height < 0:
            return None
        return (x, y, x + width, y + height)
    if tag == "circle":
        cx = _finite_float(element.attrib.get("cx"), 0)
        cy = _finite_float(element.attrib.get("cy"), 0)
        radius = _finite_float(element.attrib.get("r"))
        if radius is None or radius < 0:
            return None
        return (cx - radius, cy - radius, cx + radius, cy + radius)
    if tag == "ellipse":
        cx = _finite_float(element.attrib.get("cx"), 0)
        cy = _finite_float(element.attrib.get("cy"), 0)
        rx = _finite_float(element.attrib.get("rx"))
        ry = _finite_float(element.attrib.get("ry"))
        if rx is None or ry is None or rx < 0 or ry < 0:
            return None
        return (cx - rx, cy - ry, cx + rx, cy + ry)
    if tag == "polygon":
        values = [_finite_float(value) for value in re.split(r"[\s,]+", element.attrib.get("points", "").strip()) if value]
        points = list(zip(values[::2], values[1::2]))
        points = [(x, y) for x, y in points if x is not None and y is not None]
        if not points:
            return None
        xs, ys = zip(*points)
        return (min(xs), min(ys), max(xs), max(ys))
    return None


def _text_bounds(element):
    x = _finite_float(element.attrib.get("x"), 0)
    y = _finite_float(element.attrib.get("y"), 0)
    size = _finite_float(element.attrib.get("font-size"), 16) or 16
    text = element.text or ""
    width = sum(size if ord(character) > 127 else size * 0.6 for character in text)
    anchor = element.attrib.get("text-anchor", "start")
    if anchor == "middle":
        left, right = x - width / 2, x + width / 2
    elif anchor == "end":
        left, right = x - width, x
    else:
        left, right = x, x + width
    return (left, y - size, right, y + size * 0.25)


def _union(bounds):
    values = [value for value in bounds if value is not None]
    if not values:
        return None
    return (
        min(value[0] for value in values),
        min(value[1] for value in values),
        max(value[2] for value in values),
        max(value[3] for value in values),
    )


def _overlap(left, right):
    return left[0] < right[2] and right[0] < left[2] and left[1] < right[3] and right[1] < left[3]


def _contains(outer, inner, tolerance=2):
    return (
        inner[0] >= outer[0] - tolerance
        and inner[1] >= outer[1] - tolerance
        and inner[2] <= outer[2] + tolerance
        and inner[3] <= outer[3] + tolerance
    )


def inspect_svg(path, spec=None):
    path = Path(path).resolve(strict=False)
    issues = []

    def issue(code, message, **details):
        if len(issues) < MAX_ISSUES:
            value = {"code": code, "message": message}
            value.update(details)
            issues.append(value)

    metrics = {"textCount": 0, "sourceIdentityCount": 0, "nodeCount": 0}
    source_ids = []
    try:
        _require_inspect(path.is_file(), "invalid-svg", f"SVG file not found: {path}")
        size = path.stat().st_size
        _require_inspect(size <= MAX_SVG_BYTES, "svg-too-large", f"SVG exceeds {MAX_SVG_BYTES} bytes.")
        root = ET.parse(path).getroot()
        _require_inspect(root.tag.rsplit("}", 1)[-1] == "svg", "invalid-svg", "Document root is not an SVG element.")
        view_box = [_finite_float(value) for value in root.attrib.get("viewBox", "0 0 1280 720").split()]
        _require_inspect(len(view_box) == 4 and all(value is not None for value in view_box), "invalid-viewbox", "SVG viewBox must contain four finite numbers.")
        left, top, width, height = view_box
        right, bottom = left + width, top + height
        _require_inspect(width > 0 and height > 0, "invalid-viewbox", "SVG viewBox width and height must be positive.")

        def outside(bounds, tolerance=0.5):
            return (
                bounds[0] < left - tolerance
                or bounds[1] < top - tolerance
                or bounds[2] > right + tolerance
                or bounds[3] > bottom + tolerance
            )

        for element in root.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            if tag == "text":
                bounds = _text_bounds(element)
            elif tag in {"rect", "circle", "ellipse", "polygon"}:
                bounds = _shape_bounds(element)
            elif tag == "line":
                x1 = _finite_float(element.attrib.get("x1"))
                y1 = _finite_float(element.attrib.get("y1"))
                x2 = _finite_float(element.attrib.get("x2"))
                y2 = _finite_float(element.attrib.get("y2"))
                bounds = None if None in {x1, y1, x2, y2} else (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            else:
                bounds = None
            if bounds is not None and outside(bounds):
                issue("out-of-canvas", f"{tag} exceeds the {width:g}x{height:g} canvas.", element=tag)

        source_elements = [element for element in root.iter() if "data-source-id" in element.attrib]
        metrics["sourceIdentityCount"] = len(source_elements)
        source_ids = [element.attrib["data-source-id"] for element in source_elements]
        if not source_ids:
            issue("missing-source-identity", "No SVG element retains a source identity.")
        if spec is not None and spec["type"] not in DOMAIN_FIELDS:
            retained = set(source_ids)
            for node in spec["selection"]["nodes"]:
                if node["sourceId"] not in retained:
                    issue("missing-source-identity", f"Node {node['id']} is absent from SVG source identities.", nodeId=node["id"])

        texts = list(root.iter(f"{{{SVG_NS}}}text"))
        metrics["textCount"] = len(texts)

        node_bounds = []
        node_ids = []
        for group in root.iter(f"{{{SVG_NS}}}g"):
            if "data-node-id" not in group.attrib:
                continue
            node_id = group.attrib["data-node-id"]
            node_ids.append(node_id)
            if not group.attrib.get("data-source-id"):
                issue("missing-node-source-identity", f"Node {node_id} has no data-source-id.", nodeId=node_id)
            shape_bounds = _union(_shape_bounds(element) for element in group)
            text_bounds = _union(
                _text_bounds(element) for element in group if element.tag == f"{{{SVG_NS}}}text"
            )
            bounds = shape_bounds
            if bounds is None:
                bounds = text_bounds
            if bounds is None:
                kind = group.attrib.get("data-kind", "")
                if kind != "required-interface":
                    issue("missing-node-geometry", f"Node {node_id} has no inspectable geometry.", nodeId=node_id)
                continue
            node_bounds.append((node_id, bounds))
            if outside(bounds):
                issue("node-out-of-canvas", f"Node {node_id} exceeds the {width:g}x{height:g} canvas.", nodeId=node_id)
            kind = group.attrib.get("data-kind", "")
            if (
                shape_bounds is not None
                and text_bounds is not None
                and kind not in {"actor", "port", "initial", "final", "parallel", "valve", "provided-interface", "required-interface"}
                and not _contains(shape_bounds, text_bounds)
            ):
                issue("node-text-overflow", f"Text in node {node_id} exceeds its shape.", nodeId=node_id)
        metrics["nodeCount"] = len(node_ids)
        duplicate_nodes = sorted({value for value in node_ids if node_ids.count(value) > 1})
        for value in duplicate_nodes:
            issue("duplicate-node-id", f"Node ID is emitted more than once: {value}", nodeId=value)
        for index, (left_id, left) in enumerate(node_bounds):
            for right_id, right in node_bounds[index + 1:]:
                if _overlap(left, right):
                    issue("node-overlap", f"Nodes {left_id} and {right_id} overlap.", nodes=[left_id, right_id])
    except (ET.ParseError, OSError, UnicodeError, ValueError, KeyError) as error:
        issue("invalid-svg", str(error))
    return {
        "ok": not issues,
        "issues": issues,
        "path": str(path),
        "metrics": metrics,
        "sourceIds": sorted(set(source_ids)),
    }


def _require_inspect(condition, code, message):
    if not condition:
        raise ValueError(f"{code}: {message}")


@contextmanager
def _output_lock(output):
    stream = None
    try:
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(output / ".dgraph.lock", flags, 0o600)
        stream = os.fdopen(descriptor, "a+", encoding="utf-8")
        try:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        except (ImportError, OSError):
            pass
        yield
    finally:
        if stream is not None:
            try:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            except (ImportError, OSError):
                pass
            stream.close()


def publish_items(staging, output, names, remove=()):
    """Publish one-level artifacts with rollback on a failed commit."""
    staging = Path(staging)
    output = Path(output)
    names = list(dict.fromkeys(names))
    remove = list(dict.fromkeys(remove))
    for name in names + remove:
        if not ARTIFACT_NAME.fullmatch(name):
            raise DgraphError("output-commit", f"Unsafe artifact name: {name}", field="artifacts")
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DgraphError("output-io", f"Cannot create output directory: {error}", path=output) from error
    backup = Path(tempfile.mkdtemp(prefix=".dgraph-backup-", dir=output.parent))
    backed_up = []
    published = []
    ordered_names = [name for name in names if name != "manifest.json" and name != "report.json"]
    ordered_names += [name for name in ("report.json", "manifest.json") if name in names]
    try:
        with _output_lock(output):
            for name in remove + ordered_names:
                target = output / name
                if os.path.lexists(target):
                    os.replace(target, backup / name)
                    backed_up.append(name)
            for name in ordered_names:
                source = staging / name
                if not source.exists():
                    raise DgraphError("output-commit", f"Staged artifact is missing: {name}", path=source)
                os.replace(source, output / name)
                published.append(name)
    except BaseException as error:
        for name in reversed(published):
            target = output / name
            if os.path.lexists(target):
                os.replace(target, staging / name)
        for name in reversed(backed_up):
            source = backup / name
            if os.path.lexists(source):
                os.replace(source, output / name)
        if isinstance(error, DgraphError):
            raise
        raise DgraphError("output-commit", f"Could not commit generated artifacts: {error}", path=output, retryable=True) from error
    finally:
        shutil.rmtree(backup, ignore_errors=True)
    return output


def write_artifacts(spec, svg, ir, mermaid=None):
    output = Path(spec["outputs"]["directory"]).resolve()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".dgraph-render-", dir=output.parent))
    except OSError as error:
        raise DgraphError("output-io", f"Cannot create staging directory: {error}", path=output) from error
    try:
        (staging / "view.yaml").write_text(yaml_dump(spec) + "\n", encoding="utf-8")
        (staging / "diagram.dsl.yaml").write_text(yaml_dump(ir) + "\n", encoding="utf-8")
        (staging / "diagram.svg").write_text(svg, encoding="utf-8")
        if mermaid is not None:
            (staging / "diagram.mmd").write_text(mermaid, encoding="utf-8")
        inspection = inspect_svg(staging / "diagram.svg", spec)
        declared_authorities = {"fact": 0, "view": 0, "inferred": 0}
        for item in spec["selection"]["nodes"] + spec["selection"].get("edges", []):
            authority = item.get("authority")
            if authority in declared_authorities:
                declared_authorities[authority] += 1
        report = {
            "ok": inspection["ok"],
            "status": "ok" if inspection["ok"] else "inspection-failed",
            "type": spec["type"],
            "question": spec["intent"]["question"],
            "checks": [
                {"name": "schema", "ok": True},
                {"name": "semantics", "ok": True},
                {"name": "svg-geometry-and-identity", "ok": inspection["ok"]},
            ],
            "metrics": inspection["metrics"],
            "provenance": {
                "scope": "selection.nodes and selection.edges",
                "declared": declared_authorities,
                "undeclaredNodes": sum(1 for node in spec["selection"]["nodes"] if "authority" not in node),
                "undeclaredEdges": sum(1 for edge in spec["selection"].get("edges", []) if "authority" not in edge),
            },
            "issues": inspection["issues"],
            "omissions": spec["selection"].get("omissions", []),
            "sourceIds": inspection["sourceIds"],
        }
        write_json(staging / "report.json", report)
        names = list(CORE_ARTIFACTS)
        if mermaid is not None:
            names.append("diagram.mmd")
        manifest = {
            "schema": "dgraph-manifest/v1",
            "producer": "dgraph-mcp",
            "type": spec["type"],
            "inputSha256": hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
            "files": {name: sha256(staging / name) for name in names},
        }
        write_json(staging / "manifest.json", manifest)
        names.append("manifest.json")
        old_manifest = output / "manifest.json"
        remove = []
        if mermaid is None and old_manifest.is_file():
            try:
                old = json.loads(old_manifest.read_text(encoding="utf-8"))
                if old.get("schema") == "dgraph-manifest/v1" and "diagram.mmd" in old.get("files", {}):
                    remove.append("diagram.mmd")
            except (OSError, ValueError):
                pass
        publish_items(staging, output, names, remove=remove)
        if not report["ok"]:
            raise DgraphError(
                "visual-inspection",
                "Generated SVG failed inspection; see report.json.",
                path=output / "report.json",
                suggestion="Fix the reported geometry or source-identity issue, then render again.",
            )
        return output, report, manifest
    except OSError as error:
        raise DgraphError("output-io", f"Could not write generated artifacts: {error}", path=output, retryable=True) from error
    finally:
        shutil.rmtree(staging, ignore_errors=True)
