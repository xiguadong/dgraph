"""Dedicated C4, UML class, and UML sequence semantic renderers."""

from html import escape
from .domain import _rect
from .svg import PALETTE, _text


def c4_container_svg(model):
    out = ['<g data-c4="container">']
    boundary = model["boundary"]
    out.append(f'<g data-c4-boundary="{escape(boundary["id"], quote=True)}" data-source-id="Example.c4.boundary">')
    out.append(_rect(300, 125, 720, 485, "#fbfdff", "#94a3b8", 1.8, 14, 'stroke-dasharray="6 4"'))
    out.append(_text(320, 585, boundary["label"] + "（系统边界）", 13, "#64748b", "start"))
    out.append('</g>')
    for actor in model["actors"]:
        x, y = actor["x"], actor["y"]
        out.append(f'<g data-c4-actor="{escape(actor["id"], quote=True)}" data-source-id="Example.c4.{escape(actor["id"], quote=True)}">')
        out.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#fff" stroke="#64748b" stroke-width="2"/>')
        out.append(f'<path d="M{x} {y+12} V {y+45} M {x-20} {y+24} H {x+20} M {x} {y+45} L {x-16} {y+72} M {x} {y+45} L {x+16} {y+72}" fill="none" stroke="#64748b" stroke-width="2"/>')
        out.append(_text(x, y + 100, actor["label"], 16, "#15202b", weight=700))
        out.append(_text(x, y + 122, actor["note"], 12, "#64748b"))
        out.append('</g>')
    for container in model["containers"]:
        x, y = container["x"], container["y"]
        fill, stroke = PALETTE["gray" if container.get("external") else "blue"]
        out.append(f'<g data-c4-container="{escape(container["id"], quote=True)}" data-source-id="Example.c4.{escape(container["id"], quote=True)}">')
        out.append(_rect(x, y, 240, 120, fill, stroke, 2, 7))
        out.append(_text(x + 120, y + 25, "«外部系统»" if container.get("external") else "«container»", 12, stroke))
        out.append(_text(x + 120, y + 58, container["label"], 17, "#173d73", weight=700))
        out.append(_text(x + 120, y + 90, container["note"], 12, "#334155"))
        out.append('</g>')
    positions = {item["id"]: (item["x"] + 120, item["y"] + 60) for item in model["containers"]}
    positions.update({item["id"]: (item["x"], item["y"] + 45) for item in model["actors"]})
    for relation in model["relations"]:
        source, target = positions[relation["source"]], positions[relation["target"]]
        out.append(f'<path d="M {source[0]} {source[1]} L {target[0]} {target[1]}" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow)"/>')
        lx, ly = (source[0] + target[0]) / 2, (source[1] + target[1]) / 2 - 12
        out.append(_text(lx, ly, relation["label"], 12, "#475569", weight=500))
    out.append('</g>')
    return "".join(out)


def uml_class_svg(model):
    out = ['<g data-uml="class-diagram">']
    positions = {}
    for item in model["classes"]:
        x, y, w, h = item["x"], item["y"], 280, 185
        positions[item["id"]] = (x, y, w, h)
        out.append(f'<g data-uml-class="{escape(item["id"], quote=True)}" data-source-id="Example.uml.{escape(item["id"], quote=True)}">')
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
    for relation in model["relations"]:
        source, target = relation["source"], relation["target"]
        points = relation["points"]
        path = "M " + " L ".join(f"{x},{y}" for x, y in points)
        out.append(f'<path data-uml-relation="{escape(relation["id"], quote=True)}" d="{path}" fill="none" stroke="#64748b" stroke-width="1.8"/>')
        out.append(_text(points[0][0] + 12, points[0][1] - 12, relation["sourceMultiplicity"], 12, "#334155", "start"))
        out.append(_text(points[-1][0] - 12, points[-1][1] - 12, relation["targetMultiplicity"], 12, "#334155", "end"))
        mid = ((points[0][0] + points[-1][0]) / 2, (points[0][1] + points[-1][1]) / 2)
        out.append(_text(mid[0], mid[1] - 14, relation["id"], 13, "#475569", weight=500))
    out.append('</g>')
    return "".join(out)


def sequence_svg(model):
    out = ['<g data-sequence="interaction">']
    positions = {item["id"]: item["x"] for item in model["participants"]}
    for participant in model["participants"]:
        x = participant["x"]
        out.append(f'<g data-sequence-lifeline="{escape(participant["id"], quote=True)}" data-source-id="Example.sequence.{escape(participant["id"], quote=True)}">')
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
        out.append(f'<path data-sequence-return="{str(dashed).lower()}" d="{path}" fill="none" stroke="#2459a6" stroke-width="1.8" stroke-dasharray="{("6 4" if dashed else None)}" marker-end="url(#arrow)"/>')
        if source == target:
            out.append(_text(source + 18, y - 12, message["label"], 13, "#334155", "start"))
        else:
            out.append(_text((source + target) / 2, y - 12, message["label"], 13, "#334155", weight=500))
    out.append('</g>')
    return "".join(out)
