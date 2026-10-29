"""N², DFD, and BPMN dedicated semantic renderers."""

from html import escape
from .domain import _rect
from .svg import PALETTE, _text
from .routing import relation_label, relation_path, relation_points


N2_COLORS = {"electrical": ("#e8f0ff", "#2459a6"), "data": ("#e4f3ef", "#0f766e"), "rf": ("#f1ebfd", "#6d28d9"), "mechanical": ("#eef2f7", "#475569"), "thermal": ("#fdf4e1", "#a16207")}


def n2_svg(model):
    elements = model["elements"]
    x, y, cw, rh = 330, 205, 140, 65
    out = [f'<g data-n2="interface-matrix" data-source-id="{escape(model.get("sourceId", "domain.n2"), quote=True)}">']
    out.append(_text(330, 145, "行 = 提供方（from） · 列 = 接收方（to）", 13, "#64748b", "start"))
    for column, element in enumerate(elements):
        out.append(_text(x + (column + 0.5) * cw, y - 22, element["label"], 13, "#173d73", weight=700))
        source_id = element.get("sourceId", f"n2.element.{element['id']}")
        out.append(f'<g data-source-id="{escape(source_id, quote=True)}">')
        out.append(_text(250, y + (column + 0.5) * rh + 5, element["label"], 13, "#173d73", "end", 700))
        out.append('</g>')
    for row in range(len(elements)):
        for column in range(len(elements)):
            rx, ry = x + column * cw, y + row * rh
            element = elements[column]
            out.append(_rect(rx, ry, cw, rh, "#faf8fe" if element.get("external") else "#fff", "#cbd5e1"))
            if element.get("external"):
                out.append(f'<g data-n2-external="{escape(element["id"], quote=True)}"><rect x="{rx}" y="{ry}" width="{cw}" height="{rh}" fill="none" stroke="#6d28d9" stroke-width="1.4" stroke-dasharray="5 4"/></g>')
            if row == column:
                out.append(f'<line x1="{rx+12}" y1="{ry+12}" x2="{rx+cw-12}" y2="{ry+rh-12}" stroke="#cbd5e1"/>')
    for link in model["links"]:
        row = next(index for index, item in enumerate(elements) if item["id"] == link["from"])
        column = next(index for index, item in enumerate(elements) if item["id"] == link["to"])
        cx, cy = x + column * cw, y + row * rh
        fill, stroke = N2_COLORS[link["kind"]]
        source_id = link.get("sourceId", f"n2.link.{link['from']}.{link['to']}")
        out.append(f'<g data-n2-link="{escape(link["from"], quote=True)}:{escape(link["to"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(cx + 20, cy + 15, cw - 40, rh - 30, fill, stroke, 1.5, 5))
        out.append(_text(cx + cw / 2, cy + rh / 2 + 5, link["label"], 12, stroke, weight=650))
        if link.get("strong"):
            out.append(f'<rect x="{cx+14}" y="{cy+9}" width="{cw-28}" height="{rh-18}" rx="8" fill="none" stroke="#b42318" stroke-width="1.8"/>')
        out.append('</g>')
    out.append(_text(330, 625, "红框 = 强耦合 · 双向接口在两侧各占一格 · 地面站为外部列", 12, "#64748b", "start"))
    out.append('</g>')
    return "".join(out)


def dfd_svg(model):
    out = [f'<g data-dfd="data-flow" data-source-id="{escape(model.get("sourceId", "domain.dfd"), quote=True)}">']
    boxes = {}
    for entity in model["entities"]:
        x, y = entity["x"], entity["y"]
        boxes[entity["id"]] = (x, y, 200, 100)
    for process in model["processes"]:
        boxes[process["id"]] = (process["x"], process["y"], 230, 110)
    for store in model["stores"]:
        boxes[store["id"]] = (store["x"], store["y"], 260, 90)
    for flow_index, flow in enumerate(model["flows"]):
        source_id = flow.get("sourceId", f"dfd.flow.{flow_index}.{flow['source']}.{flow['target']}")
        out.append(relation_path(
            relation_points(flow, boxes),
            "#0f766e",
            extra=f'data-source-id="{escape(source_id, quote=True)}"',
        ))
    for entity in model["entities"]:
        x, y = entity["x"], entity["y"]
        source_id = entity.get("sourceId", f"dfd.entity.{entity['id']}")
        out.append(f'<g data-dfd-entity="{escape(entity["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(x, y, 200, 100, "#f8fafc", "#64748b", 1.8, 5))
        out.append(_text(x + 100, y + 55, entity["label"], 15, "#334155", weight=650))
        out.append('</g>')
    for process in model["processes"]:
        x, y = process["x"], process["y"]
        source_id = process.get("sourceId", f"dfd.process.{process['id']}")
        out.append(f'<g data-dfd-process="{escape(process["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(f'<ellipse cx="{x+115}" cy="{y+55}" rx="115" ry="55" fill="#e4f3ef" stroke="#0f766e" stroke-width="2"/>')
        out.append(_text(x + 115, y + 60, process["label"], 15, "#334155", weight=650))
        out.append('</g>')
    for store in model["stores"]:
        x, y = store["x"], store["y"]
        source_id = store.get("sourceId", f"dfd.store.{store['id']}")
        out.append(f'<g data-dfd-store="{escape(store["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(f'<path d="M {x} {y+12} H {x+260} M {x} {y+78} H {x+260} M {x+12} {y} V {y+90} M {x+248} {y} V {y+90}" fill="none" stroke="#a16207" stroke-width="2"/>')
        out.append(_text(x + 130, y + 52, store["label"], 15, "#334155", weight=650))
        out.append('</g>')
    for flow in model["flows"]:
        out.append(relation_label(relation_points(flow, boxes), flow["label"], "#0f766e"))
    out.append('</g>')
    return "".join(out)


def bpmn_svg(model):
    out = [f'<g data-bpmn="process" data-source-id="{escape(model.get("sourceId", "domain.bpmn"), quote=True)}">']
    out.append(_rect(40, 135, 1200, 465, "#fbfdff", "#2459a6", 1.8, 14))
    out.append(_text(60, 165, model["pool"], 15, "#2459a6", "start", 700))
    for index, lane in enumerate(model.get("lanes", [])):
        ly, lh = lane["y"], lane["height"]
        source_id = lane.get("sourceId", f"bpmn.lane.{lane['id']}")
        out.append(f'<g data-bpmn-lane="{escape(lane["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(41, ly, 1198, lh, "#f8fafc" if index % 2 else "#fff", "#cbd5e1", 1, 0))
        out.append(f'<line x1="205" y1="{ly}" x2="205" y2="{ly+lh}" stroke="#cbd5e1"/>')
        for line_no, line in enumerate(lane["label"].split("\n")):
            out.append(_text(122, ly + lh / 2 - 8 + line_no * 22, line, 13, "#334155", weight=650 if line_no == 0 else 400))
        out.append('</g>')
    boxes = {}
    for event in model["events"]:
        boxes[event["id"]] = (event["x"] - 22, event["y"] - 22, 44, 44)
    for task in model["tasks"]:
        boxes[task["id"]] = (task["x"], task["y"], 210, 84)
    for gateway in model["gateways"]:
        boxes[gateway["id"]] = (gateway["x"], gateway["y"], 130, 84)
    for flow_index, flow in enumerate(model["flows"]):
        branch = f' data-bpmn-branch="{escape(flow["branch"], quote=True)}"' if flow.get("branch") else ""
        source_id = flow.get("sourceId", f"bpmn.flow.{flow_index}.{flow['source']}.{flow['target']}")
        extra = f'{branch} data-source-id="{escape(source_id, quote=True)}"'
        out.append(relation_path(relation_points(flow, boxes), "#0f766e", extra=extra))
    for event in model["events"]:
        x, y = event["x"], event["y"]
        source_id = event.get("sourceId", f"bpmn.event.{event['id']}")
        out.append(f'<g data-bpmn-event="{escape(event["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        color = "#0f766e" if event["kind"] == "start" else "#b42318"
        out.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{color}"/>')
        if event["kind"] == "end":
            out.append(f'<circle cx="{x}" cy="{y}" r="15" fill="#fff" stroke="{color}" stroke-width="3"/>')
        out.append(_text(x, y + 45, event["label"], 13, "#334155"))
        out.append('</g>')
    for task in model["tasks"]:
        x, y = task["x"], task["y"]
        source_id = task.get("sourceId", f"bpmn.task.{task['id']}")
        out.append(f'<g data-bpmn-task="{escape(task["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(_rect(x, y, 210, 84, "#e4f3ef", "#0f766e", 2, 16))
        out.append(_text(x + 105, y + 48, task["label"], 15, "#334155", weight=650))
        out.append('</g>')
    for gateway in model["gateways"]:
        x, y = gateway["x"], gateway["y"]
        source_id = gateway.get("sourceId", f"bpmn.gateway.{gateway['id']}")
        out.append(f'<g data-bpmn-gateway="{escape(gateway["id"], quote=True)}" data-source-id="{escape(source_id, quote=True)}">')
        out.append(f'<polygon points="{x+65},{y} {x+130},{y+42} {x+65},{y+84} {x},{y+42}" fill="#fdf4e1" stroke="#a16207" stroke-width="2"/>')
        out.append(_text(x + 65, y + 48, gateway["label"], 14, "#334155", weight=650))
        out.append('</g>')
    for flow in model["flows"]:
        if flow.get("label"):
            out.append(relation_label(relation_points(flow, boxes), flow["label"], "#0f766e"))
    out.append('</g>')
    return "".join(out)
