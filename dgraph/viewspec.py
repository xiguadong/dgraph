"""Validation and normalization for the public ViewSpec contract."""

from copy import deepcopy
from pathlib import Path

from .catalog import CATALOG


class DgraphError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _require(condition, code, message):
    if not condition:
        raise DgraphError(code, message)


def validate_spec(spec):
    _require(isinstance(spec, dict), "invalid-spec", "ViewSpec must be an object.")
    result = deepcopy(spec)
    kind = result.get("type")
    entry = next((item for item in CATALOG if item["type"] == kind), None)
    _require(entry and entry["status"] == "renderable", "unsupported-type", f"Diagram type {kind!r} is not renderable.")
    _require(result.get("schema") == "diagram-view/v1", "invalid-schema", "schema must be diagram-view/v1.")
    intent = result.get("intent")
    _require(isinstance(intent, dict) and isinstance(intent.get("question"), str) and intent["question"].strip(), "invalid-intent", "A non-empty intent.question is required.")
    selection = result.get("selection")
    _require(isinstance(selection, dict), "invalid-selection", "selection must be an object.")
    nodes = selection.get("nodes")
    edges = selection.get("edges", [])
    _require(isinstance(nodes, list) and nodes, "invalid-selection", "selection.nodes must be a non-empty array.")
    _require(isinstance(edges, list), "invalid-selection", "selection.edges must be an array.")
    ids = set()
    for node in nodes:
        _require(isinstance(node, dict), "invalid-node", "Every node must be an object.")
        _require(isinstance(node.get("id"), str) and node["id"] and node["id"] not in ids, "invalid-node", "Node IDs must be unique non-empty strings.")
        ids.add(node["id"])
        _require(isinstance(node.get("label"), str) and node["label"], "invalid-node", f"Node {node['id']} needs a label.")
        _require(isinstance(node.get("sourceId"), str) and node["sourceId"], "invalid-node", f"Node {node['id']} needs a sourceId.")
        for field in ("x", "y", "w", "h"):
            _require(isinstance(node.get(field), (int, float)) and not isinstance(node.get(field), bool), "invalid-node", f"Node {node['id']} needs numeric {field}.")
        _require(node["w"] > 0 and node["h"] > 0, "invalid-node", f"Node {node['id']} needs positive dimensions.")
    for edge in edges:
        _require(isinstance(edge, dict), "invalid-edge", "Every edge must be an object.")
        _require(edge.get("source") in ids and edge.get("target") in ids, "dangling-edge", f"Edge {edge} has a dangling endpoint.")
        _require(isinstance(edge.get("kind"), str) and edge["kind"], "invalid-edge", "Every edge needs a kind.")
    outputs = result.get("outputs")
    _require(isinstance(outputs, dict) and isinstance(outputs.get("directory"), str) and outputs["directory"].strip(), "invalid-output", "An explicit output directory is required.")
    _require(Path(outputs["directory"]).is_absolute(), "invalid-output", "The output directory must be absolute.")
    presentation = result.setdefault("presentation", {})
    presentation.setdefault("width", 1280)
    presentation.setdefault("height", 720)
    presentation.setdefault("theme", "lesson")
    presentation.setdefault("title", intent["question"])
    presentation.setdefault("subtitle", kind)
    selection.setdefault("groups", [])
    selection.setdefault("matrices", [])
    selection.setdefault("charts", [])
    selection.setdefault("timelines", [])
    selection.setdefault("annotations", [])
    result.setdefault("sources", [])
    outputs.setdefault("formats", ["viewspec", "dsl", "svg", "report"])
    return result
