"""Strict validation and normalization for the public ViewSpec contract."""

from copy import deepcopy
import math
import os
from pathlib import Path
import re

from .catalog import CATALOG
from .errors import DgraphError


DOMAIN_FIELD_BY_TYPE = {
    "qfd": "qfd", "gantt": "gantt", "fta": "faultTree",
    "c4-container": "c4Container", "class": "umlClass",
    "sequence": "sequenceModel", "n2": "n2Model",
    "dfd": "dfdModel", "bpmn": "bpmnModel",
    "risk-matrix": "riskMatrix", "dmn": "dmnModel",
    "timing": "timingModel", "tradespace": "tradespaceModel",
    "pert": "pertModel",
}
DOMAIN_FIELDS = DOMAIN_FIELD_BY_TYPE
SCHEMA_VERSION = "diagram-view/v1"
MAX_NODES = 500
MAX_EDGES = 2_000
MAX_GROUPS = 250
MAX_ANNOTATIONS = 500
MAX_COLLECTIONS = 100
MAX_SOURCES = 128
MAX_TEXT_LENGTH = 4_096
MAX_LABEL_LENGTH = 1_000
MAX_DIRECTORY_LENGTH = 4_096
ALLOWED_FORMATS = {"viewspec", "dsl", "svg", "report", "manifest", "mmd"}
KNOWN_EDGE_KINDS = {
    "association",
    "aggregation",
    "composition",
    "dependency",
    "flow",
    "control",
    "connection",
    "transition",
    "generalization",
    "satisfy",
    "verify",
    "derive",
    "binding",
    "reference",
    "message",
    "return",
    "extension",
}
AUTHORITIES = {"fact", "view", "inferred"}
TOP_LEVEL_FIELDS = {"schema", "type", "intent", "sources", "selection", "presentation", "outputs"}
INTENT_FIELDS = {"question"}
SELECTION_FIELDS = {
    "layout",
    "nodes",
    "edges",
    "groups",
    "matrices",
    "charts",
    "timelines",
    "annotations",
    "qfd",
    "gantt",
    "faultTree",
    "c4Container",
    "umlClass",
    "sequenceModel",
    "n2Model",
    "dfdModel",
    "bpmnModel",
    "riskMatrix",
    "dmnModel",
    "timingModel",
    "tradespaceModel",
    "pertModel",
    "modelElementRefs",
    "omissions",
}
NODE_FIELDS = {
    "id",
    "label",
    "kind",
    "x",
    "y",
    "w",
    "h",
    "sourceId",
    "color",
    "compartment",
    "stereotype",
    "details",
    "fontSize",
    "fontWeight",
    "authority",
    "sourceKind",
}
EDGE_FIELDS = {
    "source",
    "target",
    "kind",
    "label",
    "color",
    "points",
    "labelPosition",
    "fromSide",
    "toSide",
    "fontSize",
    "authority",
}
GROUP_FIELDS = {"id", "label", "kind", "x", "y", "w", "h", "color", "rx", "dash"}
MATRIX_FIELDS = {"id", "x", "y", "cellWidth", "cellHeight", "columns", "rows", "cells"}
MATRIX_CELL_FIELDS = {"row", "column", "label", "color", "sourceId", "fontSize"}
CHART_FIELDS = {"id", "kind", "x", "y", "w", "h", "series", "xLabel", "yLabel"}
CHART_SERIES_FIELDS = {"id", "label", "color", "points"}
TIMELINE_FIELDS = {"id", "x", "y", "w", "rowHeight", "labelWidth", "rows", "markers"}
TIMELINE_ROW_FIELDS = {"id", "label", "start", "end", "color", "sourceId"}
TIMELINE_MARKER_FIELDS = {"position", "label", "color"}
ANNOTATION_FIELDS = {"x", "y", "text", "fontSize", "color", "anchor", "fontWeight"}
PRESENTATION_FIELDS = {"width", "height", "theme", "title", "subtitle"}
OUTPUT_FIELDS = {"directory", "formats"}
DOMAIN_MODEL_FIELDS = {
    "qfd",
    "gantt",
    "faultTree",
    "c4Container",
    "umlClass",
    "sequenceModel",
    "n2Model",
    "dfdModel",
    "bpmnModel",
    "riskMatrix",
    "dmnModel",
    "timingModel",
    "tradespaceModel",
    "pertModel",
}


def _require(condition, code, message, *, field=None, suggestion=None, related=None):
    if not condition:
        raise DgraphError(code, message, field=field, suggestion=suggestion, related=related)


def _number(value, code=None, field_path=None, message=None):
    valid = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if code is None:
        return valid
    _require(valid, code, message, field=field_path)
    return value


def _text(value, code=None, field_path=None, message=None, *, maximum=MAX_TEXT_LENGTH, empty=False):
    valid = isinstance(value, str) and (empty or bool(value.strip()))
    if code is None:
        return valid
    _require(valid, code, message, field=field_path)
    _require(len(value) <= maximum, "input-limit", f"{field_path} exceeds {maximum} characters.", field=field_path)
    return value


def _records(model, field, code, nonempty=True):
    items = model.get(field)
    _require(isinstance(items, list) and (items or not nonempty), code, f"{field} must be an array{' with entries' if nonempty else ''}.")
    _require(all(isinstance(item, dict) for item in items), code, f"{field} entries must be objects.")
    return items


def _ids(items, code, field):
    values = [item.get("id") for item in items]
    _require(all(_text(value) for value in values) and len(set(values)) == len(values), code, f"{field} IDs must be unique non-empty strings.")
    return set(values)


def _refs(items, ids, code, field, source="source", target="target"):
    for item in items:
        _require(item.get(source) in ids and item.get(target) in ids, code, f"{field} has a dangling endpoint: {item}.")


def _on_rect_boundary(point, box, tolerance=0.5):
    """A relation endpoint must touch its class, rather than start inside it."""
    px, py = point
    x, y, w, h = box
    within_x = x - tolerance <= px <= x + w + tolerance
    within_y = y - tolerance <= py <= y + h + tolerance
    return within_x and within_y and (
        abs(px - x) <= tolerance or abs(px - (x + w)) <= tolerance
        or abs(py - y) <= tolerance or abs(py - (y + h)) <= tolerance
    )


def _segment_crosses_rect_interior(start, end, box):
    """Clip a segment against a slightly inset rectangle to ignore border touches."""
    x, y, w, h = box
    inset = 0.001
    bounds = ((x + inset, x + w - inset), (y + inset, y + h - inset))
    low, high = 0.0, 1.0
    for first, last, (minimum, maximum) in zip(start, end, bounds):
        delta = last - first
        if abs(delta) < 1e-12:
            if not minimum < first < maximum:
                return False
            continue
        entering, leaving = (minimum - first) / delta, (maximum - first) / delta
        low = max(low, min(entering, leaving))
        high = min(high, max(entering, leaving))
        if low >= high:
            return False
    return low < high and high > 0 and low < 1


def _valid_uml_multiplicity(value):
    if not isinstance(value, str) or not re.fullmatch(r"(?:\d+|\*|\d+\.\.(?:\d+|\*))", value):
        return False
    if ".." in value:
        minimum, maximum = value.split("..", 1)
        return maximum == "*" or int(minimum) <= int(maximum)
    return True


def _validate_uml_class(model, selection, width, height, code):
    _require(not selection.get("nodes") and not selection.get("edges"), code,
             "UML class uses umlClass only; generic nodes/edges would be ignored by the renderer.")
    classes = _records(model, "classes", code)
    class_ids = _ids(classes, code, "UML classes")
    boxes = {}
    for item in classes:
        x, y, w, h = item.get("x"), item.get("y"), item.get("w", 280), item.get("h", 185)
        _require(all(_number(value) for value in (x, y, w, h)) and w >= 180 and h >= 160
                 and 0 <= x and 0 <= y and x + w <= width and y + h <= height,
                 code, f"UML class {item['id']} must fit the canvas and its three compartments.")
        boxes[item["id"]] = (x, y, w, h)
    relations = _records(model, "relations", code, False)
    _ids(relations, code, "UML relations")
    _refs(relations, class_ids, code, "UML class relation")
    allowed_kinds = {"association", "aggregation", "composition", "generalization", "realization", "dependency"}
    for relation in relations:
        relation_id = relation["id"]
        _require(relation.get("kind", "association") in allowed_kinds, code,
                 f"UML relation {relation_id} has an unsupported kind.")
        points = relation.get("points")
        _require(isinstance(points, list) and len(points) >= 2 and all(
            isinstance(point, (list, tuple)) and len(point) == 2 and all(_number(value) and 0 <= value <= (width if index == 0 else height)
            for index, value in enumerate(point)) for point in points), code,
            f"UML relation {relation_id} needs a route with at least two points inside the canvas.")
        _require(points[0] != points[-1] and all(a != b for a, b in zip(points, points[1:])), code,
                 f"UML relation {relation_id} has a zero-length route.")
        _require(_on_rect_boundary(points[0], boxes[relation["source"]]), code,
                 f"UML relation {relation_id} source endpoint is not on the source class boundary.")
        _require(_on_rect_boundary(points[-1], boxes[relation["target"]]), code,
                 f"UML relation {relation_id} target endpoint is not on the target class boundary.")
        for class_id, box in boxes.items():
            _require(not any(_segment_crosses_rect_interior(a, b, box) for a, b in zip(points, points[1:])),
                     code, f"UML relation {relation_id} crosses the interior of class {class_id}.")
        for field in ("sourceMultiplicity", "targetMultiplicity"):
            if field in relation:
                _require(_valid_uml_multiplicity(relation[field]), code,
                         f"UML relation {relation_id} has an invalid {field}.")


def _tasks(model, code, field, schedule=False):
    tasks = _records(model, "tasks", code)
    ids = _ids(tasks, code, field)
    by_id = {task["id"]: task for task in tasks}
    for task in tasks:
        _require(_text(task.get("label")), code, f"{field} task {task['id']} needs a label.")
        dependencies = task.get("dependencies")
        _require(isinstance(dependencies, list) and len(set(dependencies)) == len(dependencies) and all(dep in ids and dep != task["id"] for dep in dependencies), code, f"{field} task {task['id']} has invalid dependencies.")
        if schedule:
            _require(_number(task.get("start")) and _number(task.get("end")) and 0 <= task["start"] < task["end"], code, f"{field} task {task['id']} has an invalid time interval.")
        else:
            _require(_number(task.get("duration")) and task["duration"] > 0, code, f"{field} task {task['id']} needs positive duration.")
            _require(_number(task.get("x")) and _number(task.get("y")), code, f"{field} task {task['id']} needs numeric coordinates.")
    visiting, visited = set(), set()

    def visit(task_id):
        _require(task_id not in visiting, code, f"{field} contains a dependency cycle at {task_id}.")
        if task_id in visited:
            return
        visiting.add(task_id)
        for parent in by_id[task_id]["dependencies"]:
            visit(parent)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)
    if schedule:
        for task in tasks:
            for parent in task["dependencies"]:
                _require(by_id[parent]["end"] <= task["start"], code, f"{field} task {task['id']} starts before predecessor {parent} ends.")
    return tasks


def _validate_domain(kind, selection, width, height):
    field = DOMAIN_FIELDS.get(kind)
    if field is None:
        return
    model = selection.get(field)
    _require(isinstance(model, dict), f"missing-{field}", f"{field} is required for {kind} diagrams.")
    code = f"invalid-{field}"
    if kind == "qfd":
        needs = _records(model, "customerNeeds", code)
        engineering = _records(model, "engineering", code)
        need_ids = _ids(needs, code, "customerNeeds")
        engineering_ids = _ids(engineering, code, "engineering")
        _require(all(_text(item.get("label")) and _number(item.get("importance")) and item["importance"] > 0 for item in needs), code, "Customer needs require labels and positive importance.")
        _require(all(_text(item.get("label")) for item in engineering), code, "Engineering characteristics require labels.")
        relations = _records(model, "relations", code, False)
        roof = _records(model, "roof", code, False)
        weights = {item_id: 0 for item_id in engineering_ids}
        importance = {need["id"]: need["importance"] for need in needs}
        seen = set()
        for relation in relations:
            pair = (relation.get("need"), relation.get("engineering"))
            _require(pair[0] in need_ids and pair[1] in engineering_ids and pair not in seen, code, f"QFD relation has an invalid or duplicate pair: {pair}.")
            _require(relation.get("strength") in {1, 3, 9}, code, "QFD strength must be 1, 3, or 9.")
            seen.add(pair)
            weights[pair[1]] += importance[pair[0]] * relation["strength"]
        for item in engineering:
            if "weight" in item:
                _require(_number(item["weight"]) and item["weight"] == weights[item["id"]], code, f"QFD weight for {item['id']} does not match its relations.")
        for item in roof:
            _require(item.get("left") in engineering_ids and item.get("right") in engineering_ids and item["left"] != item["right"], code, "QFD roof references invalid characteristics.")
    elif kind == "gantt":
        ticks = model.get("ticks")
        _require(isinstance(ticks, list) and len(ticks) >= 2 and all(_text(tick) for tick in ticks), code, "Gantt needs at least two labeled ticks.")
        _tasks(model, code, "gantt", True)
        for item in _records(model, "milestones", code, False):
            _require(_text(item.get("label")) and _number(item.get("at")) and item["at"] >= 0, code, "Gantt milestones need a label and non-negative time.")
    elif kind == "fta":
        top = model.get("top")
        _require(isinstance(top, dict) and _text(top.get("id")), code, "Fault tree needs an identified top event.")
        gates = _records(model, "gates", code)
        events = _records(model, "events", code)
        ids = [top["id"]] + [item.get("id") for item in gates + events]
        _require(all(_text(item_id) for item_id in ids) and len(ids) == len(set(ids)), code, "Fault-tree IDs must be unique.")
        _require(all(gate.get("type") in {"and", "or"} for gate in gates), code, "Fault-tree gates must be AND or OR.")
        _require(all(_text(item.get("label")) for item in events), code, "Fault-tree events need labels.")
    elif kind == "c4-container":
        boundary = model.get("boundary")
        _require(isinstance(boundary, dict) and _text(boundary.get("label")), code, "C4 container needs a system boundary.")
        ids = _ids(_records(model, "actors", code, False) + _records(model, "containers", code), code, "C4 actors and containers")
        _refs(_records(model, "relations", code, False), ids, code, "C4 relation")
    elif kind == "class":
        _validate_uml_class(model, selection, width, height, code)
    elif kind == "sequence":
        ids = _ids(_records(model, "participants", code), code, "sequence participants")
        _refs(_records(model, "messages", code), ids, code, "sequence message")
    elif kind == "n2":
        ids = _ids(_records(model, "elements", code), code, "N2 elements")
        _refs(_records(model, "links", code, False), ids, code, "N2 link", "from", "to")
    elif kind == "dfd":
        entities = _records(model, "entities", code, False)
        processes = _records(model, "processes", code)
        stores = _records(model, "stores", code)
        ids = _ids(entities + processes + stores, code, "DFD elements")
        flows = _records(model, "flows", code)
        _refs(flows, ids, code, "DFD flow")
        store_ids = {item["id"] for item in stores}
        _require(all(not (flow["source"] in store_ids and flow["target"] in store_ids) for flow in flows), code, "DFD stores cannot exchange data without a process.")
    elif kind == "bpmn":
        lanes = _records(model, "lanes", code)
        lane_ids = _ids(lanes, code, "BPMN lanes")
        for lane in lanes:
            _require(_text(lane.get("label")) and _number(lane.get("y")) and _number(lane.get("height")) and lane["height"] > 0 and 0 <= lane["y"] and lane["y"] + lane["height"] <= height, code, f"BPMN lane {lane['id']} exceeds the canvas.")
        events = _records(model, "events", code)
        tasks = _records(model, "tasks", code)
        gateways = _records(model, "gateways", code, False)
        ids = _ids(events + tasks + gateways, code, "BPMN elements")
        _require(all(item.get("lane") in lane_ids for item in events + tasks + gateways), code, "Every BPMN element must reference a lane.")
        _refs(_records(model, "flows", code), ids, code, "BPMN flow")
        _require(any(item.get("kind") == "start" for item in events) and any(item.get("kind") == "end" for item in events), code, "BPMN needs start and end events.")
    if kind in {"c4-container", "class", "dfd", "bpmn"}:
        relation_field = "relations" if kind in {"c4-container", "class"} else "flows"
        for relation in model[relation_field]:
            if "points" in relation:
                points = relation["points"]
                _require(isinstance(points, list) and len(points) >= 2 and all(isinstance(point, (list, tuple)) and len(point) == 2 and _number(point[0]) and _number(point[1]) and 0 <= point[0] <= width and 0 <= point[1] <= height for point in points), code, f"{relation_field} route exceeds the canvas.")
    if kind == "risk-matrix":
        for axis in ("probability", "consequence"):
            labels = model.get(axis)
            _require(isinstance(labels, list) and len(labels) == 5 and all(_text(label) for label in labels), code, f"Risk matrix {axis} needs five ordered labels.")
        risks = _records(model, "risks", code)
        _ids(risks, code, "risks")
        for risk in risks:
            _require(_text(risk.get("label")) and all(type(risk.get(axis)) is int and 1 <= risk[axis] <= 5 for axis in ("probability", "consequence")), code, f"Risk {risk['id']} needs a label and 1–5 scores.")
    elif kind == "dmn":
        _require(_text(model.get("title")) and _text(model.get("hitPolicy")), code, "DMN needs a title and hit policy.")
        inputs = _records(model, "inputs", code)
        _ids(inputs, code, "DMN inputs")
        _require(all(_text(item.get("label")) for item in inputs), code, "DMN inputs need labels.")
        _require(isinstance(model.get("output"), dict) and _text(model["output"].get("label")), code, "DMN needs an output label.")
        rules = _records(model, "rules", code)
        _ids(rules, code, "DMN rules")
        for rule in rules:
            conditions = rule.get("conditions")
            _require(isinstance(conditions, list) and len(conditions) == len(inputs) and all(_text(value) for value in conditions) and _text(rule.get("result")), code, f"DMN rule {rule['id']} needs one condition per input and a result.")
    elif kind == "timing":
        duration = model.get("durationMs")
        _require(_number(duration) and duration > 0, code, "Timing durationMs must be positive.")
        ticks = model.get("ticks")
        _require(isinstance(ticks, list) and len(ticks) >= 2 and all(_number(tick) and 0 <= tick <= duration for tick in ticks) and ticks == sorted(set(ticks)) and ticks[0] == 0 and ticks[-1] == duration, code, "Timing ticks must increase from 0 to durationMs.")
        lifelines = _records(model, "lifelines", code)
        _ids(lifelines, code, "timing lifelines")
        for lifeline in lifelines:
            segments = _records(lifeline, "segments", code)
            _require(_text(lifeline.get("label")), code, "Timing lifelines need labels.")
            previous = 0
            for segment in segments:
                start, end = segment.get("from"), segment.get("to")
                _require(_number(start) and _number(end) and start == previous and start < end <= duration and _text(segment.get("state")), code, f"Timing lifeline {lifeline['id']} has a gap, overlap, or invalid state.")
                previous = end
            _require(previous == duration, code, f"Timing lifeline {lifeline['id']} does not cover the full duration.")
        for item in _records(model, "constraints", code, False):
            _require(_text(item.get("label")) and _number(item.get("from")) and _number(item.get("to")) and 0 <= item["from"] < item["to"] <= duration, code, "Timing constraint lies outside the timeline.")
    elif kind == "tradespace":
        for axis in ("x", "y"):
            value = model.get(axis)
            _require(isinstance(value, dict) and _text(value.get("label")) and _number(value.get("min")) and _number(value.get("max")) and value["min"] < value["max"], code, f"Tradespace {axis} needs a labeled numeric range.")
        thresholds = model.get("thresholds")
        _require(isinstance(thresholds, dict) and _number(thresholds.get("maxX")) and _number(thresholds.get("minY")) and model["x"]["min"] <= thresholds["maxX"] <= model["x"]["max"] and model["y"]["min"] <= thresholds["minY"] <= model["y"]["max"], code, "Tradespace thresholds must lie within the axes.")
        alternatives = _records(model, "alternatives", code)
        ids = _ids(alternatives, code, "tradespace alternatives")
        for item in alternatives:
            _require(_text(item.get("label")) and _number(item.get("cost")) and item["cost"] >= 0, code, f"Tradespace alternative {item['id']} needs a label and non-negative cost.")
            _require(all(_number(item.get(axis)) and model[axis]["min"] <= item[axis] <= model[axis]["max"] for axis in ("x", "y")), code, f"Tradespace alternative {item['id']} lies outside the axes.")
        pareto_ids = model.get("paretoIds")
        _require(isinstance(pareto_ids, list) and pareto_ids and len(set(pareto_ids)) == len(pareto_ids) and all(item_id in ids for item_id in pareto_ids), code, "Pareto IDs must reference distinct alternatives.")
        by_id = {item["id"]: item for item in alternatives}
        expected = {item["id"] for item in alternatives if not any(other["id"] != item["id"] and other["x"] <= item["x"] and other["y"] >= item["y"] and (other["x"] < item["x"] or other["y"] > item["y"]) for other in alternatives)}
        _require(set(pareto_ids) == expected, code, f"Pareto IDs do not match the non-dominated alternatives: {sorted(expected)}.")
        _require([by_id[item_id]["x"] for item_id in pareto_ids] == sorted(by_id[item_id]["x"] for item_id in pareto_ids), code, "Pareto IDs must be ordered by x.")
    elif kind == "pert":
        _tasks(model, code, "PERT")


def _require_non_overlapping(boxes, code, field):
    for index, (left_id, left) in enumerate(boxes):
        for right_id, right in boxes[index + 1:]:
            _require(
                left[2] <= right[0] or right[2] <= left[0] or left[3] <= right[1] or right[3] <= left[1],
                "invalid-geometry",
                f"Semantic nodes {left_id} and {right_id} overlap.",
                field=field,
            )


def _validate_supplemental_domain(kind, selection, width, height):
    """Additional invariants that complement the diagram-specific validators."""
    if kind == "n2":
        pairs = set()
        for index, link in enumerate(selection["n2Model"]["links"]):
            pair = (link["from"], link["to"])
            _require(pair not in pairs, "duplicate-relation", f"Duplicate directional N² link: {pair[0]}:{pair[1]}", field=f"selection.n2Model.links[{index}]")
            pairs.add(pair)
        return
    if kind == "c4-container":
        model = selection["c4Container"]
        boxes = [(item["id"], (item["x"] - 20, item["y"], item["x"] + 20, item["y"] + 72)) for item in model["actors"]]
        boxes += [(item["id"], (item["x"], item["y"], item["x"] + 240, item["y"] + 120)) for item in model["containers"]]
        _require_non_overlapping(boxes, "invalid-geometry", "selection.c4Container")
        return
    if kind == "dfd":
        model = selection["dfdModel"]
        boxes = []
        for field, box_width, box_height in (("entities", 200, 100), ("processes", 230, 110), ("stores", 260, 90)):
            boxes += [(item["id"], (item["x"], item["y"], item["x"] + box_width, item["y"] + box_height)) for item in model[field]]
        _require_non_overlapping(boxes, "invalid-geometry", "selection.dfdModel")
        return
    if kind == "class":
        boxes = []
        for item in selection["umlClass"]["classes"]:
            box_width, box_height = item.get("w", 280), item.get("h", 185)
            boxes.append((item["id"], (item["x"], item["y"], item["x"] + box_width, item["y"] + box_height)))
        _require_non_overlapping(boxes, "invalid-geometry", "selection.umlClass.classes")
        return
    if kind != "bpmn":
        return
    model = selection["bpmnModel"]
    boxes = []
    for event in model["events"]:
        boxes.append((event["id"], (event["x"] - 22, event["y"] - 22, event["x"] + 22, event["y"] + 22)))
    for task in model["tasks"]:
        boxes.append((task["id"], (task["x"], task["y"], task["x"] + 210, task["y"] + 84)))
    for gateway in model["gateways"]:
        boxes.append((gateway["id"], (gateway["x"], gateway["y"], gateway["x"] + 130, gateway["y"] + 84)))
    _require_non_overlapping(boxes, "invalid-geometry", "selection.bpmnModel")

    graph = {item_id: set() for item_id, _ in boxes}
    for flow in model["flows"]:
        graph[flow["source"]].add(flow["target"])
    starts = {event["id"] for event in model["events"] if event.get("kind") == "start"}
    reachable = set(starts)
    pending = list(starts)
    while pending:
        source = pending.pop()
        for target in graph[source]:
            if target not in reachable:
                reachable.add(target)
                pending.append(target)
    unreachable = sorted(set(graph) - reachable)
    _require(
        not unreachable,
        "disconnected-graph",
        f"BPMN nodes are unreachable from a start event: {', '.join(unreachable)}",
        field="selection.bpmnModel.flows",
    )


def _object(value, code, field_path, message, *, allowed=None):
    _require(isinstance(value, dict), code, message, field=field_path)
    if allowed is not None:
        unknown = sorted(set(value) - set(allowed))
        _require(not unknown, "unknown-field", f"Unknown field(s) at {field_path}: {', '.join(unknown)}", field=field_path)
    return value


def _array(value, code, field_path, message, *, minimum=0, maximum=None):
    _require(isinstance(value, list), code, message, field=field_path)
    _require(len(value) >= minimum, code, message, field=field_path)
    if maximum is not None:
        _require(len(value) <= maximum, "input-limit", f"{field_path} exceeds the limit of {maximum} items.", field=field_path)
    return value


def _identifier(value, code, field_path, message):
    return _text(value, code, field_path, message, maximum=256)


def _inside_canvas(x, y, width, height, canvas_width, canvas_height, *, field_path):
    _require(
        x >= 0 and y >= 0 and x + width <= canvas_width and y + height <= canvas_height,
        "invalid-geometry",
        f"{field_path} is outside the {canvas_width}x{canvas_height} canvas.",
        field=field_path,
        suggestion="Move or resize the item so it remains inside the presentation canvas.",
    )


def _safe_output_directory(value):
    _text(value, "invalid-output", "outputs.directory", "An explicit output directory is required.", maximum=MAX_DIRECTORY_LENGTH)
    path = Path(value)
    _require(path.is_absolute(), "invalid-output", "The output directory must be absolute.", field="outputs.directory")
    try:
        resolved = path.resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as error:
        raise DgraphError("invalid-output", f"Invalid output directory: {error}", field="outputs.directory") from error
    forbidden = {Path("/"), Path.cwd().resolve(), Path(__file__).resolve().parent.parent, Path.home().resolve()}
    _require(resolved not in forbidden, "invalid-output", "The output directory must not be a filesystem, home, or project root.", field="outputs.directory")
    protected_roots = {
        Path("/etc"),
        Path("/usr"),
        Path("/bin"),
        Path("/sbin"),
        Path("/var"),
        Path("/dev"),
        Path("/proc"),
        Path("/sys"),
        Path("/System"),
        Path("/Library"),
        Path("/Applications"),
    }
    _require(
        not any(resolved == root or root in resolved.parents for root in protected_roots),
        "invalid-output",
        "The output directory must not be inside a protected system directory.",
        field="outputs.directory",
    )
    allowed_root = os.environ.get("DGRAPH_OUTPUT_ROOT")
    if allowed_root:
        root = Path(allowed_root).resolve(strict=False)
        _require(root != Path("/"), "invalid-output", "DGRAPH_OUTPUT_ROOT must not be the filesystem root.", field="outputs.directory")
        _require(resolved == root or root in resolved.parents, "invalid-output", f"Output directory must be inside DGRAPH_OUTPUT_ROOT ({root}).", field="outputs.directory")
    _require(not (resolved.exists() and not resolved.is_dir()), "invalid-output", "The output path exists and is not a directory.", field="outputs.directory")
    return resolved


def validate_output_directory(value):
    """Validate an absolute output directory and optional configured root."""
    return _safe_output_directory(value)


def _validate_node(node, index, ids, source_ids, width, height):
    path = f"selection.nodes[{index}]"
    _object(node, "invalid-node", path, "Every node must be an object.", allowed=NODE_FIELDS)
    node_id = _identifier(node.get("id"), "invalid-node", f"{path}.id", "Node IDs must be non-empty strings.")
    _require(node_id not in ids, "duplicate-node-id", f"Duplicate node ID: {node_id}", field=f"{path}.id")
    ids.add(node_id)
    kind = _text(node.get("kind"), "invalid-node", f"{path}.kind", f"Node {node_id} needs a kind.")
    _text(
        node.get("label"),
        "invalid-node",
        f"{path}.label",
        f"Node {node_id} needs a label.",
        maximum=MAX_LABEL_LENGTH,
        empty=kind in {"required-interface", "provided-interface"},
    )
    source_id = _identifier(node.get("sourceId"), "invalid-node", f"{path}.sourceId", f"Node {node_id} needs a sourceId.")
    _require(source_id not in source_ids, "duplicate-source-id", f"Duplicate node sourceId: {source_id}", field=f"{path}.sourceId")
    source_ids.add(source_id)
    for name in ("x", "y", "w", "h"):
        _number(node.get(name), "invalid-node", f"{path}.{name}", f"Node {node_id} needs a finite numeric {name}.")
    _require(node["w"] > 0 and node["h"] > 0, "invalid-node", f"Node {node_id} needs positive dimensions.", field=path)
    _inside_canvas(node["x"], node["y"], node["w"], node["h"], width, height, field_path=path)
    for name in ("fontSize", "fontWeight"):
        if name in node:
            _number(node[name], "invalid-node", f"{path}.{name}", f"{path}.{name} must be finite.")
    for name in ("kind", "color", "compartment", "stereotype", "details"):
        if name in node:
            _text(node[name], "invalid-node", f"{path}.{name}", f"{path}.{name} must be a string.", maximum=MAX_TEXT_LENGTH)
    if "authority" in node:
        authority = _text(node["authority"], "invalid-node", f"{path}.authority", "Node authority must be fact, view, or inferred.", maximum=32)
        _require(authority in AUTHORITIES, "invalid-node", "Node authority must be fact, view, or inferred.", field=f"{path}.authority")
    if "sourceKind" in node:
        source_kind = _text(node["sourceKind"], "invalid-node", f"{path}.sourceKind", "Node sourceKind must be semantic or sysml.", maximum=32)
        _require(source_kind in {"semantic", "sysml"}, "invalid-node", "Node sourceKind must be semantic or sysml.", field=f"{path}.sourceKind")


def _validate_edge(edge, index, ids, width, height):
    path = f"selection.edges[{index}]"
    _object(edge, "invalid-edge", path, "Every edge must be an object.", allowed=EDGE_FIELDS)
    source = _identifier(edge.get("source"), "invalid-edge", f"{path}.source", "Edge source must be a non-empty node ID.")
    target = _identifier(edge.get("target"), "invalid-edge", f"{path}.target", "Edge target must be a non-empty node ID.")
    _require(source in ids and target in ids, "dangling-edge", f"Edge {index} has a dangling endpoint.", field=path, related=[source, target])
    kind = _text(edge.get("kind"), "invalid-edge", f"{path}.kind", "Every edge needs a kind.")
    _require(kind in KNOWN_EDGE_KINDS, "invalid-edge", f"Unknown edge kind: {kind}", field=f"{path}.kind")
    if "label" in edge:
        _text(edge["label"], "invalid-edge", f"{path}.label", "Edge label must be a string.", maximum=MAX_LABEL_LENGTH, empty=True)
    if "points" in edge:
        points = _array(edge["points"], "invalid-edge", f"{path}.points", "Edge points must be an array.", minimum=2, maximum=100)
        for point_index, point in enumerate(points):
            _require(isinstance(point, (list, tuple)) and len(point) == 2, "invalid-edge", f"{path}.points[{point_index}] must contain x and y.", field=f"{path}.points")
            x = _number(point[0], "invalid-edge", f"{path}.points[{point_index}][0]", "Point x must be finite.")
            y = _number(point[1], "invalid-edge", f"{path}.points[{point_index}][1]", "Point y must be finite.")
            _inside_canvas(x, y, 0, 0, width, height, field_path=f"{path}.points[{point_index}]")
    if "labelPosition" in edge:
        point = edge["labelPosition"]
        _require(isinstance(point, (list, tuple)) and len(point) == 2, "invalid-edge", f"{path}.labelPosition must contain x and y.", field=f"{path}.labelPosition")
        x = _number(point[0], "invalid-edge", f"{path}.labelPosition[0]", "Label x must be finite.")
        y = _number(point[1], "invalid-edge", f"{path}.labelPosition[1]", "Label y must be finite.")
        _inside_canvas(x, y, 0, 0, width, height, field_path=f"{path}.labelPosition")
    for name in ("color", "fromSide", "toSide"):
        if name in edge:
            _text(edge[name], "invalid-edge", f"{path}.{name}", f"{path}.{name} must be a string.")
    if "fontSize" in edge:
        _number(edge["fontSize"], "invalid-edge", f"{path}.fontSize", "Edge fontSize must be finite.")
    if "authority" in edge:
        authority = _text(edge["authority"], "invalid-edge", f"{path}.authority", "Edge authority must be fact, view, or inferred.", maximum=32)
        _require(authority in AUTHORITIES, "invalid-edge", "Edge authority must be fact, view, or inferred.", field=f"{path}.authority")


def _validate_groups(groups, width, height):
    _array(groups, "invalid-selection", "selection.groups", "selection.groups must be an array.", maximum=MAX_GROUPS)
    ids = set()
    for index, group in enumerate(groups):
        path = f"selection.groups[{index}]"
        _object(group, "invalid-group", path, "Every group must be an object.", allowed=GROUP_FIELDS)
        group_id = _identifier(group.get("id"), "invalid-group", f"{path}.id", "Every group needs a unique non-empty ID.")
        _require(group_id not in ids, "duplicate-group-id", f"Duplicate group ID: {group_id}", field=f"{path}.id")
        ids.add(group_id)
        for name in ("x", "y", "w", "h"):
            _number(group.get(name), "invalid-group", f"{path}.{name}", f"Group {group_id} needs a finite numeric {name}.")
        _require(group["w"] > 0 and group["h"] > 0, "invalid-group", f"Group {group_id} needs positive dimensions.", field=path)
        _inside_canvas(group["x"], group["y"], group["w"], group["h"], width, height, field_path=path)
        for name in ("label", "kind", "color", "dash"):
            if name in group:
                _text(group[name], "invalid-group", f"{path}.{name}", f"{path}.{name} must be a string.", maximum=MAX_LABEL_LENGTH, empty=name == "dash")
        if "rx" in group:
            _number(group["rx"], "invalid-group", f"{path}.rx", "Group rx must be finite.")


def _validate_matrices(matrices, width, height):
    _array(matrices, "invalid-selection", "selection.matrices", "selection.matrices must be an array.", maximum=MAX_COLLECTIONS)
    ids = set()
    for index, matrix in enumerate(matrices):
        path = f"selection.matrices[{index}]"
        _object(matrix, "invalid-matrix", path, "Every matrix must be an object.", allowed=MATRIX_FIELDS)
        matrix_id = _identifier(matrix.get("id"), "invalid-matrix", f"{path}.id", "Every matrix needs a non-empty ID.")
        _require(matrix_id not in ids, "duplicate-matrix-id", f"Duplicate matrix ID: {matrix_id}", field=f"{path}.id")
        ids.add(matrix_id)
        x = _number(matrix.get("x"), "invalid-matrix", f"{path}.x", "Matrix x must be finite.")
        y = _number(matrix.get("y"), "invalid-matrix", f"{path}.y", "Matrix y must be finite.")
        cell_width = _number(matrix.get("cellWidth", 110), "invalid-matrix", f"{path}.cellWidth", "Cell width must be finite.")
        cell_height = _number(matrix.get("cellHeight", 60), "invalid-matrix", f"{path}.cellHeight", "Cell height must be finite.")
        _require(cell_width > 0 and cell_height > 0, "invalid-matrix", "Matrix cell dimensions must be positive.", field=path)
        columns = _array(matrix.get("columns"), "invalid-matrix", f"{path}.columns", "Matrix columns must be an array.", minimum=1, maximum=100)
        rows = _array(matrix.get("rows"), "invalid-matrix", f"{path}.rows", "Matrix rows must be an array.", minimum=1, maximum=100)
        for axis, values in (("columns", columns), ("rows", rows)):
            for item_index, value in enumerate(values):
                _text(value, "invalid-matrix", f"{path}.{axis}[{item_index}]", f"Matrix {axis} labels must be non-empty strings.", maximum=MAX_LABEL_LENGTH)
        _inside_canvas(x, y, (len(columns) + 1) * cell_width, (len(rows) + 1) * cell_height, width, height, field_path=path)
        cells = _array(matrix.get("cells", []), "invalid-matrix", f"{path}.cells", "Matrix cells must be an array.", maximum=10_000)
        occupied = set()
        for cell_index, cell in enumerate(cells):
            cell_path = f"{path}.cells[{cell_index}]"
            _object(cell, "invalid-matrix", cell_path, "Every matrix cell must be an object.", allowed=MATRIX_CELL_FIELDS)
            row = cell.get("row")
            column = cell.get("column")
            _require(isinstance(row, int) and not isinstance(row, bool) and 0 <= row < len(rows), "invalid-matrix", f"{cell_path}.row is outside the matrix.", field=f"{cell_path}.row")
            _require(isinstance(column, int) and not isinstance(column, bool) and 0 <= column < len(columns), "invalid-matrix", f"{cell_path}.column is outside the matrix.", field=f"{cell_path}.column")
            _require((row, column) not in occupied, "duplicate-matrix-cell", f"Duplicate matrix cell: {row}:{column}", field=cell_path)
            occupied.add((row, column))
            _text(cell.get("label"), "invalid-matrix", f"{cell_path}.label", "Matrix cells need labels.", maximum=MAX_LABEL_LENGTH, empty=True)
            if "sourceId" in cell:
                _identifier(cell["sourceId"], "invalid-matrix", f"{cell_path}.sourceId", "Matrix cell sourceId must be a non-empty string.")
            if "color" in cell:
                _text(cell["color"], "invalid-matrix", f"{cell_path}.color", "Cell color must be a string.")
            if "fontSize" in cell:
                _number(cell["fontSize"], "invalid-matrix", f"{cell_path}.fontSize", "Cell fontSize must be finite.")


def _validate_charts(charts, width, height):
    _array(charts, "invalid-selection", "selection.charts", "selection.charts must be an array.", maximum=MAX_COLLECTIONS)
    ids = set()
    for index, chart in enumerate(charts):
        path = f"selection.charts[{index}]"
        _object(chart, "invalid-chart", path, "Every chart must be an object.", allowed=CHART_FIELDS)
        chart_id = _identifier(chart.get("id"), "invalid-chart", f"{path}.id", "Every chart needs a non-empty ID.")
        _require(chart_id not in ids, "duplicate-chart-id", f"Duplicate chart ID: {chart_id}", field=f"{path}.id")
        ids.add(chart_id)
        values = {name: _number(chart.get(name), "invalid-chart", f"{path}.{name}", f"Chart {name} must be finite.") for name in ("x", "y", "w", "h")}
        _require(values["w"] > 0 and values["h"] > 0, "invalid-chart", "Chart dimensions must be positive.", field=path)
        _inside_canvas(values["x"], values["y"], values["w"] + 20, values["h"] + 55, width, height, field_path=path)
        chart_kind = chart.get("kind", "line")
        chart_kind = _text(chart_kind, "invalid-chart", f"{path}.kind", "Chart kind must be line or scatter.", maximum=32)
        _require(chart_kind in {"line", "scatter"}, "invalid-chart", f"Unsupported chart kind: {chart_kind}", field=f"{path}.kind")
        series = _array(chart.get("series"), "invalid-chart", f"{path}.series", "Chart series must be an array.", minimum=1, maximum=100)
        series_ids = set()
        for series_index, item in enumerate(series):
            item_path = f"{path}.series[{series_index}]"
            _object(item, "invalid-chart", item_path, "Every chart series must be an object.", allowed=CHART_SERIES_FIELDS)
            series_id = _identifier(item.get("id"), "invalid-chart", f"{item_path}.id", "Chart series need non-empty IDs.")
            _require(series_id not in series_ids, "duplicate-chart-series-id", f"Duplicate chart series ID: {series_id}", field=f"{item_path}.id")
            series_ids.add(series_id)
            points = _array(item.get("points"), "invalid-chart", f"{item_path}.points", "Series points must be an array.", minimum=2 if chart_kind == "line" else 1, maximum=1_000)
            for point_index, point in enumerate(points):
                _require(isinstance(point, (list, tuple)) and len(point) == 2, "invalid-chart", f"{item_path}.points[{point_index}] must contain x and y.", field=f"{item_path}.points")
                px = _number(point[0], "invalid-chart", f"{item_path}.points[{point_index}][0]", "Point x must be finite.")
                py = _number(point[1], "invalid-chart", f"{item_path}.points[{point_index}][1]", "Point y must be finite.")
                _require(0 <= px <= 100 and 0 <= py <= 100, "invalid-chart", "Chart points must use normalized coordinates from 0 to 100.", field=f"{item_path}.points[{point_index}]")
            for name in ("label", "color"):
                if name in item:
                    _text(item[name], "invalid-chart", f"{item_path}.{name}", f"Series {name} must be a string.", maximum=MAX_LABEL_LENGTH, empty=True)
        for name in ("xLabel", "yLabel"):
            if name in chart:
                _text(chart[name], "invalid-chart", f"{path}.{name}", f"{name} must be a string.", maximum=MAX_LABEL_LENGTH, empty=True)


def _validate_timelines(timelines, width, height):
    _array(timelines, "invalid-selection", "selection.timelines", "selection.timelines must be an array.", maximum=MAX_COLLECTIONS)
    ids = set()
    for index, timeline in enumerate(timelines):
        path = f"selection.timelines[{index}]"
        _object(timeline, "invalid-timeline", path, "Every timeline must be an object.", allowed=TIMELINE_FIELDS)
        timeline_id = _identifier(timeline.get("id"), "invalid-timeline", f"{path}.id", "Every timeline needs a non-empty ID.")
        _require(timeline_id not in ids, "duplicate-timeline-id", f"Duplicate timeline ID: {timeline_id}", field=f"{path}.id")
        ids.add(timeline_id)
        x = _number(timeline.get("x"), "invalid-timeline", f"{path}.x", "Timeline x must be finite.")
        y = _number(timeline.get("y"), "invalid-timeline", f"{path}.y", "Timeline y must be finite.")
        timeline_width = _number(timeline.get("w"), "invalid-timeline", f"{path}.w", "Timeline width must be finite.")
        row_height = _number(timeline.get("rowHeight", 64), "invalid-timeline", f"{path}.rowHeight", "Timeline rowHeight must be finite.")
        label_width = _number(timeline.get("labelWidth", 170), "invalid-timeline", f"{path}.labelWidth", "Timeline labelWidth must be finite.")
        _require(timeline_width > label_width > 0 and row_height > 0, "invalid-timeline", "Timeline width and row dimensions are invalid.", field=path)
        rows = _array(timeline.get("rows"), "invalid-timeline", f"{path}.rows", "Timeline rows must be an array.", minimum=1, maximum=100)
        _inside_canvas(x, y, timeline_width, len(rows) * row_height + 35, width, height, field_path=path)
        row_ids = set()
        for row_index, row in enumerate(rows):
            row_path = f"{path}.rows[{row_index}]"
            _object(row, "invalid-timeline", row_path, "Every timeline row must be an object.", allowed=TIMELINE_ROW_FIELDS)
            row_id = _identifier(row.get("id"), "invalid-timeline", f"{row_path}.id", "Timeline rows need non-empty IDs.")
            _require(row_id not in row_ids, "duplicate-timeline-row-id", f"Duplicate timeline row ID: {row_id}", field=f"{row_path}.id")
            row_ids.add(row_id)
            _text(row.get("label"), "invalid-timeline", f"{row_path}.label", "Timeline rows need labels.", maximum=MAX_LABEL_LENGTH)
            start = _number(row.get("start"), "invalid-timeline", f"{row_path}.start", "Timeline row start must be finite.")
            end = _number(row.get("end"), "invalid-timeline", f"{row_path}.end", "Timeline row end must be finite.")
            _require(0 <= start < end <= 100, "invalid-timeline", "Timeline rows must satisfy 0 <= start < end <= 100.", field=row_path)
            if "sourceId" in row:
                _identifier(row["sourceId"], "invalid-timeline", f"{row_path}.sourceId", "Timeline row sourceId must be a non-empty string.")
            if "color" in row:
                _text(row["color"], "invalid-timeline", f"{row_path}.color", "Timeline row color must be a string.")
        markers = _array(timeline.get("markers", []), "invalid-timeline", f"{path}.markers", "Timeline markers must be an array.", maximum=100)
        for marker_index, marker in enumerate(markers):
            marker_path = f"{path}.markers[{marker_index}]"
            _object(marker, "invalid-timeline", marker_path, "Every timeline marker must be an object.", allowed=TIMELINE_MARKER_FIELDS)
            position = _number(marker.get("position"), "invalid-timeline", f"{marker_path}.position", "Marker position must be finite.")
            _require(0 <= position <= 100, "invalid-timeline", "Marker position must be between 0 and 100.", field=f"{marker_path}.position")
            _text(marker.get("label"), "invalid-timeline", f"{marker_path}.label", "Timeline markers need labels.", maximum=MAX_LABEL_LENGTH)
            if "color" in marker:
                _text(marker["color"], "invalid-timeline", f"{marker_path}.color", "Marker color must be a string.")


def _validate_annotations(annotations, width, height):
    _array(annotations, "invalid-selection", "selection.annotations", "selection.annotations must be an array.", maximum=MAX_ANNOTATIONS)
    for index, note in enumerate(annotations):
        path = f"selection.annotations[{index}]"
        _object(note, "invalid-annotation", path, "Every annotation must be an object.", allowed=ANNOTATION_FIELDS)
        x = _number(note.get("x"), "invalid-annotation", f"{path}.x", "Annotation x must be finite.")
        y = _number(note.get("y"), "invalid-annotation", f"{path}.y", "Annotation y must be finite.")
        _inside_canvas(x, y, 0, 0, width, height, field_path=path)
        _text(note.get("text"), "invalid-annotation", f"{path}.text", "Every annotation needs text.")
        if "fontSize" in note:
            size = _number(note["fontSize"], "invalid-annotation", f"{path}.fontSize", "Annotation fontSize must be finite.")
            _require(6 <= size <= 100, "invalid-annotation", "Annotation fontSize must be between 6 and 100.", field=f"{path}.fontSize")
        if "anchor" in note:
            anchor = _text(note["anchor"], "invalid-annotation", f"{path}.anchor", "Annotation anchor must be start, middle, or end.", maximum=16)
            _require(anchor in {"start", "middle", "end"}, "invalid-annotation", "Annotation anchor must be start, middle, or end.", field=f"{path}.anchor")
        if "color" in note:
            _text(note["color"], "invalid-annotation", f"{path}.color", "Annotation color must be a string.")
        if "fontWeight" in note:
            _number(note["fontWeight"], "invalid-annotation", f"{path}.fontWeight", "Annotation fontWeight must be finite.")


def _validate_outputs(outputs):
    _object(outputs, "invalid-output", "outputs", "outputs must be an object.", allowed=OUTPUT_FIELDS)
    outputs["directory"] = str(_safe_output_directory(outputs.get("directory")))
    formats = outputs.setdefault("formats", ["viewspec", "dsl", "svg", "report"])
    _array(formats, "invalid-output", "outputs.formats", "outputs.formats must be an array.", minimum=1, maximum=len(ALLOWED_FORMATS))
    for index, value in enumerate(formats):
        _text(value, "unsupported-format", f"outputs.formats[{index}]", "Output formats must be non-empty strings.", maximum=64)
    _require(len(set(formats)) == len(formats), "invalid-output", "outputs.formats must not contain duplicates.", field="outputs.formats")
    unknown = sorted(set(formats) - ALLOWED_FORMATS)
    _require(not unknown, "unsupported-format", f"Unsupported output format(s): {', '.join(unknown)}", field="outputs.formats")


def _validate_source_identities(value, field_path, seen, *, depth=0, budget=None):
    if budget is None:
        budget = [20_000]
    budget[0] -= 1
    _require(budget[0] >= 0, "input-limit", "selection exceeds the source-identity value budget.", field=field_path)
    _require(depth <= 40, "input-limit", "selection exceeds the maximum nesting depth.", field=field_path)
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{field_path}.{key}" if field_path else key
            if key == "sourceId":
                source_id = _identifier(item, "invalid-source-identity", child_path, "sourceId must be a non-empty string.")
                _require(source_id not in seen, "duplicate-source-id", f"Duplicate sourceId: {source_id}", field=child_path)
                seen.add(source_id)
            else:
                _validate_source_identities(item, child_path, seen, depth=depth + 1, budget=budget)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_source_identities(item, f"{field_path}[{index}]", seen, depth=depth + 1, budget=budget)


def _validate_json_value(value, field_path, *, depth=0, budget=None):
    if budget is None:
        budget = [20_000]
    budget[0] -= 1
    _require(budget[0] >= 0, "input-limit", "sources exceed the JSON value budget.", field=field_path)
    _require(depth <= 40, "input-limit", "sources exceed the maximum nesting depth.", field=field_path)
    if isinstance(value, dict):
        for key, item in value.items():
            _require(isinstance(key, str), "invalid-source", "Source object keys must be strings.", field=field_path)
            _require(len(key) <= MAX_LABEL_LENGTH, "input-limit", f"{field_path} contains an overlong key.", field=field_path)
            _validate_json_value(item, f"{field_path}.{key}", depth=depth + 1, budget=budget)
    elif isinstance(value, list):
        _require(len(value) <= MAX_COLLECTIONS, "input-limit", f"{field_path} exceeds {MAX_COLLECTIONS} items.", field=field_path)
        for index, item in enumerate(value):
            _validate_json_value(item, f"{field_path}[{index}]", depth=depth + 1, budget=budget)
    elif isinstance(value, str):
        _require(len(value) <= MAX_TEXT_LENGTH, "input-limit", f"{field_path} exceeds {MAX_TEXT_LENGTH} characters.", field=field_path)
    elif isinstance(value, bool) or value is None:
        return
    elif isinstance(value, int):
        return
    elif isinstance(value, float):
        _require(math.isfinite(value), "invalid-source", f"{field_path} must be finite.", field=field_path)
    else:
        raise DgraphError("invalid-source", f"{field_path} is not JSON-compatible.", field=field_path)


def validate_spec(spec):
    _require(isinstance(spec, dict), "invalid-spec", "ViewSpec must be an object.", field="$")
    _object(spec, "invalid-spec", "$", "ViewSpec must be an object.", allowed=TOP_LEVEL_FIELDS)
    raw_sources = spec.get("sources", [])
    if isinstance(raw_sources, list):
        _require(len(raw_sources) <= MAX_SOURCES, "input-limit", f"sources exceeds {MAX_SOURCES} items.", field="sources")
        for index, source in enumerate(raw_sources[:MAX_SOURCES + 1]):
            if isinstance(source, dict):
                _validate_json_value(source, f"sources[{index}]")
    result = deepcopy(spec)
    kind = result.get("type")
    entry = next((item for item in CATALOG if item["type"] == kind), None)
    _require(entry and entry["status"] == "renderable", "unsupported-type", f"Diagram type {kind!r} is not renderable.", field="type")
    _require(result.get("schema") == SCHEMA_VERSION, "invalid-schema", f"schema must be {SCHEMA_VERSION}.", field="schema")
    intent = _object(result.get("intent"), "invalid-intent", "intent", "intent must be an object.", allowed=INTENT_FIELDS)
    _text(intent.get("question"), "invalid-intent", "intent.question", "A non-empty intent.question is required.")
    selection = _object(result.get("selection"), "invalid-selection", "selection", "selection must be an object.", allowed=SELECTION_FIELDS)
    nodes = _array(selection.get("nodes"), "invalid-selection", "selection.nodes", "selection.nodes must be an array.", maximum=MAX_NODES)
    _require(nodes or kind in DOMAIN_FIELDS, "invalid-selection", "selection.nodes must be non-empty for this diagram type.", field="selection.nodes")
    edges = _array(selection.get("edges", []), "invalid-selection", "selection.edges", "selection.edges must be an array.", maximum=MAX_EDGES)
    sources = _array(result.setdefault("sources", []), "invalid-sources", "sources", "sources must be an array.", maximum=MAX_SOURCES)
    for index, source in enumerate(sources):
        _object(source, "invalid-source", f"sources[{index}]", "Every source must be an object.")
        _require(source.get("kind") in {"semantic", "sysml"}, "invalid-sources", "sources must declare semantic or sysml provenance.", field=f"sources[{index}].kind")
    presentation = _object(result.setdefault("presentation", {}), "invalid-presentation", "presentation", "presentation must be an object.", allowed=PRESENTATION_FIELDS)
    presentation.setdefault("width", 1280)
    presentation.setdefault("height", 720)
    presentation.setdefault("theme", "dgraph")
    presentation.setdefault("title", intent["question"])
    presentation.setdefault("subtitle", kind)
    width = _number(presentation["width"], "invalid-presentation", "presentation.width", "presentation.width must be finite.")
    height = _number(presentation["height"], "invalid-presentation", "presentation.height", "presentation.height must be finite.")
    _require(320 <= width <= 10_000 and 240 <= height <= 10_000, "invalid-presentation", "Canvas dimensions must be between 320x240 and 10000x10000.", field="presentation")
    for name in ("title", "subtitle", "theme"):
        _text(presentation[name], "invalid-presentation", f"presentation.{name}", f"presentation.{name} must be a string.", maximum=MAX_LABEL_LENGTH)
    ids, source_ids = set(), set()
    for index, node in enumerate(nodes):
        _validate_node(node, index, ids, source_ids, width, height)
    for index, edge in enumerate(edges):
        _validate_edge(edge, index, ids, width, height)
    outputs = _object(result.get("outputs"), "invalid-output", "outputs", "An explicit outputs object is required.", allowed=OUTPUT_FIELDS)
    _validate_outputs(outputs)
    if kind not in {"activity", "state-machine", "package", "block-definition"}:
        _require("mmd" not in outputs["formats"], "unsupported-format", f"Mermaid is not a lossless output for {kind}.", field="outputs.formats")
    selection.setdefault("groups", [])
    selection.setdefault("matrices", [])
    selection.setdefault("charts", [])
    selection.setdefault("timelines", [])
    selection.setdefault("annotations", [])
    if "modelElementRefs" in selection:
        refs = _array(selection["modelElementRefs"], "invalid-selection", "selection.modelElementRefs", "modelElementRefs must be an array.", maximum=MAX_EDGES)
        for index, value in enumerate(refs):
            _identifier(value, "invalid-selection", f"selection.modelElementRefs[{index}]", "Model element references must be non-empty strings.")
    if "omissions" in selection:
        omissions = _array(selection["omissions"], "invalid-selection", "selection.omissions", "omissions must be an array.", maximum=MAX_ANNOTATIONS)
        for index, value in enumerate(omissions):
            _object(value, "invalid-selection", f"selection.omissions[{index}]", "Every omission must be an object.")
            _validate_json_value(value, f"selection.omissions[{index}]")
    _validate_source_identities(selection, "selection", set())
    _validate_groups(selection["groups"], width, height)
    _validate_matrices(selection["matrices"], width, height)
    _validate_charts(selection["charts"], width, height)
    _validate_timelines(selection["timelines"], width, height)
    _validate_annotations(selection["annotations"], width, height)
    active_domain = DOMAIN_FIELD_BY_TYPE.get(kind)
    irrelevant = sorted(
        field
        for field in DOMAIN_MODEL_FIELDS
        if field != active_domain and selection.get(field) is not None
    )
    _require(
        not irrelevant,
        "irrelevant-domain-model",
        f"selection contains models not used by {kind}: {', '.join(irrelevant)}",
        field="selection",
        suggestion="Remove unused domain models or change the diagram type.",
    )
    _validate_domain(kind, selection, width, height)
    _validate_supplemental_domain(kind, selection, width, height)
    return result


__all__ = ["DgraphError", "SCHEMA_VERSION", "validate_output_directory", "validate_spec"]
