"""N², DFD, and BPMN dedicated semantic renderers."""

from html import escape
from .domain import _rect
from .svg import PALETTE, _text


N2_COLORS = {"electrical": ("#e8f0ff", "#2459a6"), "data": ("#e4f3ef", "#0f766e"), "rf": ("#f1ebfd", "#6d28d9"), "mechanical": ("#eef2f7", "#475569"), "thermal": ("#fdf4e1", "#a16207")}


def n2_svg(model):
    elements = model["elements"]
    x, y, cw, rh = 330, 205, 140, 65
    out = ['<g data-n2="interface-matrix" data-source-id="Example.n2">']
    out.append(_text(330, 145, "行 = 提供方（from） · 列 = 接收方（to）", 13, "#64748b", "start"))
    for column, element in enumerate(elements):
        out.append(_text(x + (column + 0.5) * cw, y - 22, element["label"], 13, "#173d73", weight=700))
        out.append(_text(250, y + (column + 0.5) * rh + 5, element["label"], 13, "#173d73", "end", 700))
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
        out.append(f'<g data-n2-link="{escape(link["from"], quote=True)}:{escape(link["to"], quote=True)}">')
        out.append(_rect(cx + 20, cy + 15, cw - 40, rh - 30, fill, stroke, 1.5, 5))
        out.append(_text(cx + cw / 2, cy + rh / 2 + 5, link["label"], 12, stroke, weight=650))
        if link.get("strong"):
            out.append(f'<rect x="{cx+14}" y="{cy+9}" width="{cw-28}" height="{rh-18}" rx="8" fill="none" stroke="#b42318" stroke-width="1.8"/>')
        out.append('</g>')
    out.append(_text(330, 625, "红框 = 强耦合 · 双向接口在两侧各占一格 · 地面站为外部列", 12, "#64748b", "start"))
    out.append('</g>')
    return "".join(out)


def dfd_svg(model):
    out = ['<g data-dfd="data-flow" data-source-id="Example.dfd">']
    positions = {}
    for entity in model["entities"]:
        x, y = entity["x"], entity["y"]
        positions[entity["id"]] = (x + 100, y + 50)
        out.append(_rect(x, y, 200, 100, "#f8fafc", "#64748b", 1.8, 5))
        out.append(_text(x + 100, y + 55, entity["label"], 15, "#334155", weight=650))
    for process in model["processes"]:
        x, y = process["x"], process["y"]
        positions[process["id"]] = (x + 115, y + 55)
        out.append(f'<g data-dfd-process="{escape(process["id"], quote=True)}">')
        out.append(f'<ellipse cx="{x+115}" cy="{y+55}" rx="115" ry="55" fill="#e4f3ef" stroke="#0f766e" stroke-width="2"/>')
        out.append(_text(x + 115, y + 60, process["label"], 15, "#334155", weight=650))
        out.append('</g>')
    for store in model["stores"]:
        x, y = store["x"], store["y"]
        positions[store["id"]] = (x + 130, y + 45)
        out.append(f'<g data-dfd-store="{escape(store["id"], quote=True)}">')
        out.append(f'<path d="M {x} {y+12} H {x+260} M {x} {y+78} H {x+260} M {x+12} {y} V {y+90} M {x+248} {y} V {y+90}" fill="none" stroke="#a16207" stroke-width="2"/>')
        out.append(_text(x + 130, y + 52, store["label"], 15, "#334155", weight=650))
        out.append('</g>')
    for flow in model["flows"]:
        source, target = positions[flow["source"]], positions[flow["target"]]
        out.append(f'<path d="M {source[0]} {source[1]} L {target[0]} {target[1]}" fill="none" stroke="#0f766e" stroke-width="1.8" marker-end="url(#arrow)"/>')
        out.append(_text((source[0] + target[0]) / 2, (source[1] + target[1]) / 2 - 12, flow["label"], 12, "#0f766e", weight=500))
    out.append('</g>')
    return "".join(out)


def bpmn_svg(model):
    out = ['<g data-bpmn="process" data-source-id="Example.bpmn">']
    out.append(_rect(40, 135, 1200, 465, "#fbfdff", "#2459a6", 1.8, 14))
    out.append(_text(60, 165, model["pool"], 15, "#2459a6", "start", 700))
    positions = {}
    for event in model["events"]:
        x, y = event["x"], event["y"]
        positions[event["id"]] = (x, y)
        out.append(f'<g data-bpmn-event="{escape(event["id"], quote=True)}">')
        color = "#0f766e" if event["kind"] == "start" else "#b42318"
        out.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{color}"/>')
        if event["kind"] == "end":
            out.append(f'<circle cx="{x}" cy="{y}" r="15" fill="#fff" stroke="{color}" stroke-width="3"/>')
        out.append(_text(x, y + 45, event["label"], 13, "#334155"))
        out.append('</g>')
    for task in model["tasks"]:
        x, y = task["x"], task["y"]
        positions[task["id"]] = (x + 105, y + 42)
        out.append(_rect(x, y, 210, 84, "#e4f3ef", "#0f766e", 2, 16))
        out.append(_text(x + 105, y + 48, task["label"], 15, "#334155", weight=650))
    for gateway in model["gateways"]:
        x, y = gateway["x"], gateway["y"]
        positions[gateway["id"]] = (x + 65, y + 42)
        out.append(f'<g data-bpmn-gateway="{escape(gateway["id"], quote=True)}">')
        out.append(f'<polygon points="{x+65},{y} {x+130},{y+42} {x+65},{y+84} {x},{y+42}" fill="#fdf4e1" stroke="#a16207" stroke-width="2"/>')
        out.append(_text(x + 65, y + 48, gateway["label"], 14, "#334155", weight=650))
        out.append('</g>')
    for flow in model["flows"]:
        source, target = positions[flow["source"]], positions[flow["target"]]
        branch = f' data-bpmn-branch="{escape(flow["branch"], quote=True)}"' if flow.get("branch") else ""
        out.append(f'<path{branch} d="M {source[0]} {source[1]} L {target[0]} {target[1]}" fill="none" stroke="#0f766e" stroke-width="1.8" marker-end="url(#arrow)"/>')
        if flow.get("label"):
            out.append(_text((source[0] + target[0]) / 2, (source[1] + target[1]) / 2 - 12, flow["label"], 12, "#0f766e", weight=500))
    out.append('</g>')
    return "".join(out)
