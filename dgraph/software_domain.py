"""Dedicated C4, UML class, and UML sequence semantic renderers."""

from html import escape
from .domain import _rect
from .svg import PALETTE, _text
from .routing import relation_label, relation_path, relation_points


def c4_container_svg(model):
    out = [f'<g data-c4="container" data-source-id="{escape(model.get("sourceId", "domain.c4"), quote=True)}">']
    boundary = model["boundary"]
    boundary_source = boundary.get("sourceId", f"c4.boundary.{boundary['id']}")
    out.append(f'<g data-c4-boundary="{escape(boundary["id"], quote=True)}" data-source-id="{escape(boundary_source, quote=True)}">')
    out.append(_rect(300, 125, 690, 485, "#fbfdff", "#94a3b8", 1.8, 14, 'stroke-dasharray="6 4"'))
    out.append(_text(320, 585, boundary["label"] + "（系统边界）", 13, "#64748b", "start"))
    out.append('</g>')
    boxes = {item["id"]: (item["x"], item["y"], 240, 120) for item in model["containers"]}
    boxes.update({item["id"]: (item["x"] - 20, item["y"], 40, 72) for item in model["actors"]})
    for relation_index, relation in enumerate(model["relations"]):
        source_id = relation.get("sourceId", f"c4.relation.{relation_index}.{relation['source']}.{relation['target']}")
        out.append(relation_path(
            relation_points(relation, boxes),
            extra=f'data-source-id="{escape(source_id, quote=True)}"',
        ))
    for actor in model["actors"]:
        x, y = actor["x"], actor["y"]
        source_id = actor.get("sourceId", f"c4.actor.{actor['id']}")
        out.append(f'<g data-c4-actor="{escape(actor["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#fff" stroke="#64748b" stroke-width="2"/>')
        out.append(f'<path d="M{x} {y+12} V {y+45} M {x-20} {y+24} H {x+20} M {x} {y+45} L {x-16} {y+72} M {x} {y+45} L {x+16} {y+72}" fill="none" stroke="#64748b" stroke-width="2"/>')
        out.append(_text(x, y + 100, actor["label"], 16, "#15202b", weight=700))
        out.append(_text(x, y + 122, actor["note"], 12, "#64748b"))
        out.append('</g>')
    for container in model["containers"]:
        x, y = container["x"], container["y"]
        fill, stroke = PALETTE["gray" if container.get("external") else "blue"]
        source_id = container.get("sourceId", f"c4.container.{container['id']}")
        out.append(f'<g data-c4-container="{escape(container["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(x, y, 240, 120, fill, stroke, 2, 7))
        out.append(_text(x + 120, y + 25, "«外部系统»" if container.get("external") else "«container»", 12, stroke))
        out.append(_text(x + 120, y + 58, container["label"], 17, "#173d73", weight=700))
        out.append(_text(x + 120, y + 90, container["note"], 12, "#334155"))
        out.append('</g>')
    for relation in model["relations"]:
        out.append(relation_label(relation_points(relation, boxes), relation["label"]))
    out.append('</g>')
    return "".join(out)


def uml_class_svg(model):
    out = ['<g data-uml="class-diagram">']
    relation_labels = []
    for relation in model["relations"]:
        points = relation["points"]
        kind = relation.get("kind", "association")
        path = "M " + " L ".join(f"{x},{y}" for x, y in points)
        dashed = ' stroke-dasharray="6 4"' if kind in {"dependency", "realization"} else ""
        marker = (' marker-end="url(#triangle)"' if kind in {"generalization", "realization"} else
                  ' marker-end="url(#arrow)"' if kind == "dependency" else "")
        source_id = relation.get("sourceId", f"uml.relation.{relation['id']}")
        out.append(f'<path data-uml-relation="{escape(relation["id"], quote=True)}" data-uml-kind="{escape(kind, quote=True)}" data-source-id="{escape(source_id, quote=True)}" d="{path}" fill="none" stroke="#64748b" stroke-width="1.8"{dashed}{marker}/>')
        if kind in {"composition", "aggregation"}:
            x, y = points[0]
            fill = "#64748b" if kind == "composition" else "#fff"
            out.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" transform="rotate(45 {x} {y})" fill="{fill}" stroke="#64748b"/>')
        relation_labels.append(relation)
    for item in model["classes"]:
        x, y = item["x"], item["y"]
        w, h = item.get("w", 280), item.get("h", 185)
        source_id = item.get("sourceId", f"uml.class.{item['id']}")
        out.append(f'<g data-uml-class="{escape(item["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(x, y, w, h, "#fff", "#2459a6", 1.7, 2))
        out.append(_rect(x, y, w, 38, "#e8f0ff", "#2459a6", 1.7, 2))
        out.append(_text(x + w / 2, y + 25, item["id"], 16, "#15202b", weight=700))
        out.append(f'<line x1="{x}" y1="{y+38}" x2="{x+w}" y2="{y+38}" stroke="#2459a6" stroke-width="1.2"/>')
        for index, attribute in enumerate(item["attributes"]):
            out.append(_text(x + 12, y + 65 + index * 24, "- " + attribute, 13, "#334155", "start"))
        separator = y + 115
        out.append(f'<line x1="{x}" y1="{separator}" x2="{x+w}" y2="{separator}" stroke="#2459a6" stroke-width="1.2"/>')
        for index, operation in enumerate(item["operations"]):
            out.append(_text(x + 12, separator + 28 + index * 24, "+ " + operation, 13, "#334155", "start"))
        out.append('</g>')
    for relation in relation_labels:
        points = relation["points"]
        for endpoint, adjacent, field in ((points[0], points[1], "sourceMultiplicity"), (points[-1], points[-2], "targetMultiplicity")):
            if not relation.get(field):
                continue
            dx, dy = adjacent[0] - endpoint[0], adjacent[1] - endpoint[1]
            if abs(dx) >= abs(dy):
                x, y = endpoint[0] + (11 if dx > 0 else -11), endpoint[1] - 13
                anchor = "start" if dx > 0 else "end"
            else:
                x, y, anchor = endpoint[0] + 11, endpoint[1] + (18 if dy > 0 else -10), "start"
            out.append(_text(x, y, relation[field], 12, "#334155", anchor))
        a, b = max(zip(points, points[1:]), key=lambda pair: abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1]))
        if abs(b[0] - a[0]) >= abs(b[1] - a[1]):
            x, y = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 15
            anchor = "middle"
        else:
            x, y = (a[0] + b[0]) / 2 + 18, (a[1] + b[1]) / 2 + 4
            anchor = "start"
        out.append(_text(x, y, relation.get("label", relation["id"]), 13, "#475569", anchor, 500))
    out.append('</g>')
    return "".join(out)


def sequence_svg(model):
    out = [f'<g data-sequence="interaction" data-source-id="{escape(model.get("sourceId", "domain.sequence"), quote=True)}">']
    positions = {item["id"]: item["x"] for item in model["participants"]}
    for participant in model["participants"]:
        x = participant["x"]
        source_id = participant.get("sourceId", f"sequence.participant.{participant['id']}")
        out.append(f'<g data-sequence-lifeline="{escape(participant["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(x - 85, 130, 170, 58, "#e8f0ff", "#2459a6", 1.8, 3))
        out.append(_text(x, 165, participant["label"], 15, "#15202b", weight=650))
        out.append(f'<line x1="{x}" y1="188" x2="{x}" y2="625" stroke="#94a3b8" stroke-dasharray="5 5"/>')
        out.append('</g>')
    activations = set()
    for index, message in enumerate(model["messages"]):
        y = 230 + index * 65
        source, target = positions[message["source"]], positions[message["target"]]
        if message["source"] not in activations:
            out.append(f'<rect data-sequence-activation="{escape(message["source"], quote=True)}" x="{source-6}" y="{y-12}" width="12" height="52" fill="#e4f3ef" stroke="#0f766e" stroke-width="1.5"/>')
            activations.add(message["source"])
        if source == target:
            path = f'M {source} {y} H {source+105} V {y+32} H {source}'
        else:
            path = f'M {source} {y} H {target}'
        dashed = message["kind"] == "return"
        source_id = message.get("sourceId", f"sequence.message.{index + 1}")
        out.append(f'<path data-sequence-return="{str(dashed).lower()}" data-source-id="{escape(source_id, quote=True)}" d="{path}" fill="none" stroke="#2459a6" stroke-width="1.8" stroke-dasharray="{("6 4" if dashed else None)}" marker-end="url(#arrow)"/>')
        if source == target:
            out.append(_text(source + 18, y - 12, message["label"], 13, "#334155", "start"))
        else:
            out.append(_text((source + target) / 2, y - 12, message["label"], 13, "#334155", weight=500))
    out.append('</g>')
    return "".join(out)
