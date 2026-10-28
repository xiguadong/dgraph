"""Validation and normalization for the public ViewSpec contract."""

from copy import deepcopy
import math
from pathlib import Path

from .catalog import CATALOG


DOMAIN_FIELDS = {
    "qfd": "qfd", "gantt": "gantt", "fta": "faultTree",
    "c4-container": "c4Container", "class": "umlClass",
    "sequence": "sequenceModel", "n2": "n2Model",
    "dfd": "dfdModel", "bpmn": "bpmnModel",
    "risk-matrix": "riskMatrix", "dmn": "dmnModel",
    "timing": "timingModel", "tradespace": "tradespaceModel",
    "pert": "pertModel",
}


class DgraphError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _require(condition, code, message):
    if not condition:
        raise DgraphError(code, message)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


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
        ids = _ids(_records(model, "classes", code), code, "UML classes")
        _refs(_records(model, "relations", code, False), ids, code, "UML class relation")
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


def validate_spec(spec):
    _require(isinstance(spec, dict), "invalid-spec", "ViewSpec must be an object.")
    result = deepcopy(spec)
    kind = result.get("type")
    entry = next((item for item in CATALOG if item["type"] == kind), None)
    _require(entry and entry["status"] == "renderable", "unsupported-type", f"Diagram type {kind!r} is not renderable.")
    _require(result.get("schema") == "diagram-view/v1", "invalid-schema", "schema must be diagram-view/v1.")
    intent = result.get("intent")
    _require(isinstance(intent, dict) and _text(intent.get("question")), "invalid-intent", "A non-empty intent.question is required.")
    presentation = result.setdefault("presentation", {})
    _require(isinstance(presentation, dict), "invalid-presentation", "presentation must be an object.")
    presentation.setdefault("width", 1280)
    presentation.setdefault("height", 720)
    presentation.setdefault("theme", "dgraph")
    presentation.setdefault("title", intent["question"])
    presentation.setdefault("subtitle", kind)
    width, height = presentation["width"], presentation["height"]
    _require(_number(width) and _number(height) and width > 0 and height > 0, "invalid-presentation", "Canvas width and height must be positive finite numbers.")
    selection = result.get("selection")
    _require(isinstance(selection, dict), "invalid-selection", "selection must be an object.")
    nodes = selection.setdefault("nodes", [])
    edges = selection.setdefault("edges", [])
    _require(isinstance(nodes, list) and (nodes or kind in DOMAIN_FIELDS), "invalid-selection", "selection.nodes must be a non-empty array for this diagram type.")
    _require(isinstance(edges, list), "invalid-selection", "selection.edges must be an array.")
    ids = set()
    for node in nodes:
        _require(isinstance(node, dict), "invalid-node", "Every node must be an object.")
        _require(_text(node.get("id")) and node["id"] not in ids, "invalid-node", "Node IDs must be unique non-empty strings.")
        ids.add(node["id"])
        _require((_text(node.get("label")) or node.get("kind") in {"required-interface", "provided-interface"}) and _text(node.get("sourceId")), "invalid-node", f"Node {node['id']} needs a label and sourceId.")
        for field in ("x", "y", "w", "h"):
            _require(_number(node.get(field)), "invalid-node", f"Node {node['id']} needs finite numeric {field}.")
        _require(node["w"] > 0 and node["h"] > 0 and 0 <= node["x"] and 0 <= node["y"] and node["x"] + node["w"] <= width and node["y"] + node["h"] <= height, "out-of-canvas", f"Node {node['id']} exceeds the canvas.")
    for edge in edges:
        _require(isinstance(edge, dict), "invalid-edge", "Every edge must be an object.")
        _require(edge.get("source") in ids and edge.get("target") in ids, "dangling-edge", f"Edge {edge} has a dangling endpoint.")
        _require(_text(edge.get("kind")), "invalid-edge", "Every edge needs a kind.")
        if "points" in edge:
            points = edge["points"]
            _require(isinstance(points, list) and len(points) >= 2 and all(isinstance(point, (list, tuple)) and len(point) == 2 and _number(point[0]) and _number(point[1]) and 0 <= point[0] <= width and 0 <= point[1] <= height for point in points), "out-of-canvas", "Edge points must lie within the canvas.")
    annotations = selection.setdefault("annotations", [])
    _require(isinstance(annotations, list), "invalid-annotation", "Annotations must be an array.")
    for item in annotations:
        _require(isinstance(item, dict), "invalid-annotation", "Every annotation must be an object.")
        if "x" in item or "y" in item:
            _require(_number(item.get("x")) and _number(item.get("y")) and 0 <= item["x"] <= width and 0 <= item["y"] <= height, "out-of-canvas", "Annotation anchor exceeds the canvas.")
    outputs = result.get("outputs")
    _require(isinstance(outputs, dict) and _text(outputs.get("directory")), "invalid-output", "An explicit output directory is required.")
    _require(Path(outputs["directory"]).is_absolute(), "invalid-output", "The output directory must be absolute.")
    sources = result.setdefault("sources", [])
    _require(isinstance(sources, list) and all(isinstance(source, dict) and source.get("kind") in {"semantic", "sysml"} for source in sources), "invalid-sources", "sources must declare semantic or sysml provenance.")
    for field in ("groups", "matrices", "charts", "timelines"):
        selection.setdefault(field, [])
    outputs.setdefault("formats", ["viewspec", "dsl", "svg", "report"])
    _validate_domain(kind, selection, width, height)
    return result
