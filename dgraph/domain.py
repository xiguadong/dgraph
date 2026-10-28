"""Dedicated semantic renderers for QFD, Gantt, and FTA diagrams."""

from html import escape
from .svg import PALETTE, _text


def _rect(x, y, w, h, fill="#fff", stroke="#cbd5e1", width=1.2, rx=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def qfd_svg(model):
    needs, engineering, relations, roof = model["customerNeeds"], model["engineering"], model["relations"], model["roof"]
    x, y, need_w, imp_w, cw, rh = 40, 250, 150, 70, 140, 60
    out = ['<g data-qfd="house-of-quality" data-source-id="Example.qfd">']
    # Roof correlation matrix.
    out.append('<g data-qfd-roof="engineering-correlation">')
    for item in roof:
        left = next(i for i, value in enumerate(engineering) if value["id"] == item["left"])
        right = next(i for i, value in enumerate(engineering) if value["id"] == item["right"])
        cx = x + need_w + imp_w + (left + 0.5) * cw
        cy = y - 105 + (right - left) * 22
        color = "#0f766e" if item["type"] == "plus" else "#b42318"
        symbol = "+" if item["type"] == "plus" else "−"
        out.append(_rect(cx - 11, cy - 11, 22, 22, "#fdf4e1" if item["type"] == "plus" else "#f8fafc", "#dbe3ec", 1, 3))
        out.append(_text(cx, cy + 5, symbol, 14, color, weight=700))
    out.append('</g>')
    # Headers.
    out.append(_rect(x, y - 40, need_w, 40, "#f4f7fb"))
    out.append(_text(x + need_w / 2, y - 15, "客户需求", 13, "#173d73", weight=700))
    out.append(_rect(x + need_w, y - 40, imp_w, 40, "#f4f7fb"))
    out.append(_text(x + need_w + imp_w / 2, y - 15, "重要度", 12, "#173d73", weight=700))
    for index, item in enumerate(engineering):
        cx = x + need_w + imp_w + index * cw
        out.append(_text(cx + cw / 2, y - 24, item["label"], 13, "#173d73", weight=700))
        out.append(_text(cx + cw / 2, y - 7, item["unit"], 11, "#64748b"))
    symbols = {9: ("●", "#2459a6"), 3: ("○", "#0f766e"), 1: ("△", "#a16207"), 0: ("·", "#94a3b8")}
    for row, need in enumerate(needs):
        ry = y + row * rh
        out.append(_text(x + 12, ry + 35, need["label"], 13, "#334155", "start", 600))
        out.append(_text(x + need_w + imp_w / 2, ry + 35, need["importance"], 14, "#a16207", weight=700))
        for column, item in enumerate(engineering):
            cx = x + need_w + imp_w + column * cw
            out.append(_rect(cx, ry, cw, rh))
            relation = next((value for value in relations if value["need"] == need["id"] and value["engineering"] == item["id"]), None)
            if relation:
                symbol, color = symbols[relation["strength"]]
                out.append(f'<g data-qfd-relation="{escape(need["id"], quote=True)}:{escape(item["id"], quote=True)}">')
                out.append(_text(cx + cw / 2, ry + 38, symbol, 17, color, weight=600))
                out.append('</g>')
    # Targets, weights and ranks are first-class rows, not annotations.
    for row, (label, field) in enumerate((("目标值", "target"), ("权重", "weight"), ("排序", "rank"))):
        ry = y + len(needs) * rh + row * 36
        out.append(_rect(x, ry, need_w + imp_w + len(engineering) * cw, 36, "#f4f7fb" if row != 1 else "#fff"))
        out.append(_text(x + need_w / 2, ry + 23, label, 13, "#173d73", weight=700))
        for column, item in enumerate(engineering):
            cx = x + need_w + imp_w + column * cw
            out.append(_text(cx + cw / 2, ry + 23, item[field], 13, "#2459a6" if field != "rank" else "#a16207", weight=650))
    out.append(_text(1010, 275, "关系度", 13, "#173d73", "start", 700))
    for index, (symbol, text) in enumerate((("●", "强 = 9"), ("○", "中 = 3"), ("△", "弱 = 1"), ("·", "无关 = 0"))):
        out.append(_text(1010, 305 + index * 30, f"{symbol} {text}", 12, "#334155", "start"))
    out.append(_text(1010, 445, "屋顶：+ 增强 / − 冲突", 12, "#64748b", "start"))
    out.append('</g>')
    return "".join(out)


def gantt_svg(model):
    ticks, tasks, milestones = model["ticks"], model["tasks"], model["milestones"]
    x, y, width, rh = 275, 170, 850, 66
    max_time = max(max(task["end"] for task in tasks), max(item["at"] for item in milestones))
    cw = width / max_time
    out = ['<g data-gantt="schedule" data-source-id="Example.gantt">']
    for index, tick in enumerate(ticks):
        tx = x + index * cw
        out.append(_text(tx + cw / 2, y - 22, tick, 12, "#64748b"))
        out.append(f'<line x1="{tx}" y1="{y-10}" x2="{tx}" y2="{y + len(tasks)*rh + 65}" stroke="#e2e8f0"/>')
    for index, task in enumerate(tasks):
        ry = y + index * rh
        out.append(_text(55, ry + 30, task["label"], 13, "#334155", "start", 600))
        bx, bw = x + task["start"] * cw, (task["end"] - task["start"]) * cw
        fill, stroke = PALETTE[task.get("color", "blue")]
        out.append(f'<g data-gantt-task="{escape(task["id"], quote=True)}">')
        out.append(_rect(bx, ry + 8, bw, 28, fill, stroke, 1.5, 4))
        out.append('</g>')
        for dependency in task.get("dependencies", []):
            parent = next(value for value in tasks if value["id"] == dependency)
            parent_index = tasks.index(parent)
            start_x, start_y = x + parent["end"] * cw, y + parent_index * rh + 36
            end_x, end_y = bx, ry + 22
            out.append(f'<path data-gantt-dependency="{escape(dependency, quote=True)}:{escape(task["id"], quote=True)}" d="M {start_x} {start_y} V {start_y+12} H {end_x} V {end_y}" fill="none" stroke="#64748b" stroke-width="1.6" marker-end="url(#arrow)"/>')
    milestone_y = y + len(tasks) * rh + 25
    for item in milestones:
        mx = x + item["at"] * cw
        out.append(f'<g data-gantt-milestone="{escape(item["id"], quote=True)}">')
        out.append(f'<polygon points="{mx},{milestone_y} {mx+10},{milestone_y+10} {mx},{milestone_y+20} {mx-10},{milestone_y+10}" fill="#fdf4e1" stroke="#a16207" stroke-width="1.6"/>')
        out.append(_text(mx, milestone_y + 42, item["label"], 12, "#a16207", weight=600))
        out.append('</g>')
    out.append('</g>')
    return "".join(out)


def fta_svg(model):
    top, gates, events = model["top"], model["gates"], model["events"]
    out = ['<g data-fta="fault-tree" data-source-id="Example.fta">']
    out.append(_rect(500, 130, 280, 70, "#fdecea", "#b42318", 2, 8))
    out.append(_text(640, 158, f"顶事件 {top['id']}", 12, "#b42318"))
    out.append(_text(640, 182, top["label"], 17, "#b42318", weight=700))
    for gate in gates:
        kind = gate["type"]
        gx, gy = 640, 265
        out.append(f'<g data-fta-gate="{escape(kind, quote=True)}">')
        if kind == "or":
            out.append(f'<path d="M {gx-45} {gy-15} Q {gx} {gy-30} {gx+45} {gy-15} C {gx+45} {gy} {gx+15} {gy+25} {gx} {gy+38} C {gx-15} {gy+25} {gx-45} {gy} {gx-45} {gy-15} Z" fill="#fff" stroke="#b42318" stroke-width="2"/>')
        else:
            out.append(f'<path d="M {gx-45} {gy-15} H {gx+45} C {gx+45} {gy+15} {gx+15} {gy+35} {gx} {gy+42} C {gx-15} {gy+35} {gx-45} {gy+15} {gx-45} {gy-15} Z" fill="#fff" stroke="#b42318" stroke-width="2"/>')
        out.append(_text(gx, gy + 8, kind.upper(), 14, "#b42318", weight=700))
        out.append('</g>')
        out.append(f'<line x1="640" y1="200" x2="640" y2="230" stroke="#64748b" stroke-width="1.8"/>')
        out.append(f'<line x1="640" y1="303" x2="640" y2="345" stroke="#64748b" stroke-width="1.8"/>')
    out.append('<line x1="150" y1="345" x2="1130" y2="345" stroke="#64748b" stroke-width="1.8"/>')
    for index, event in enumerate(events):
        ex = 70 + index * 300
        out.append(f'<line x1="{ex+120}" y1="345" x2="{ex+120}" y2="425" stroke="#64748b" stroke-width="1.8"/>')
        out.append(f'<g data-fta-basic-event="{escape(event["id"], quote=True)}">')
        out.append(_rect(ex, 425, 240, 85, "#fff", "#b42318", 1.8, 7))
        out.append(_text(ex + 120, 458, event["label"], 15, "#b42318", weight=700))
        out.append(_text(ex + 120, 485, event["note"], 12, "#64748b"))
        out.append('</g>')
    out.append(_text(70, 570, "OR 门：任一底事件发生即顶事件；底事件可继续映射到 FMEA 失效模式。", 13, "#64748b", "start"))
    out.append('</g>')
    return "".join(out)
