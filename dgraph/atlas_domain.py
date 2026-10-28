"""Diagram primitives whose meaning depends on a dedicated domain model."""

from html import escape
import unicodedata

from .svg import _text


def _rect(x, y, w, h, fill="#fff", stroke="#cbd5e1", rx=4, width=1.5):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')


def risk_matrix_svg(model):
    """Probability × consequence; risk names never become axis labels."""
    x, y, cw, rh = 370, 155, 158, 78
    out = ['<g data-risk-matrix="probability-consequence" data-source-id="risk-matrix">']
    out.append(_text(62, 160, "概率 × 后果 = 风险等级", 16, "#173d73", "start", 700))
    out.append(_text(62, 188, "数字越大，越需要优先处置", 13, "#64748b", "start"))
    for row in range(5):
        probability = 5 - row
        out.append(_text(x - 20, y + row * rh + rh / 2 + 5,
                         model["probability"][probability - 1], 13, "#334155", "end", 600))
        for column in range(5):
            consequence = column + 1
            score = probability * consequence
            fill = "#e4f3ef" if score <= 6 else "#fdf4e1" if score <= 12 else "#fdecea"
            stroke = "#0f766e" if score <= 6 else "#a16207" if score <= 12 else "#b42318"
            cx, cy = x + column * cw, y + row * rh
            out.append(_rect(cx, cy, cw, rh, fill, "#cbd5e1", 0, 1))
            out.append(_text(cx + 12, cy + 20, score, 11, stroke, "start", 700))
            risks = [risk for risk in model["risks"] if risk["probability"] == probability and risk["consequence"] == consequence]
            for index, risk in enumerate(risks[:2]):
                out.append(f'<g data-risk-id="{escape(risk["id"], quote=True)}" data-source-id="{escape(risk.get("sourceId", risk["id"]), quote=True)}">')
                out.append(_text(cx + cw / 2, cy + 42 + 18 * index, f'{risk["id"]} {risk["label"]}', 12, stroke, weight=650))
                out.append('</g>')
    for column, label in enumerate(model["consequence"]):
        out.append(_text(x + (column + .5) * cw, y + 5 * rh + 25, label, 12, "#334155", weight=600))
    out.append(_text(x + 2.5 * cw, y + 5 * rh + 51, "后果 Consequence →", 13, "#173d73", weight=700))
    out.append(_text(x - 195, y + 2.5 * rh, "概率 Probability ↑", 13, "#173d73", weight=700))
    out.append('</g>')
    return ''.join(out)


def dmn_svg(model):
    """Decision table with explicit input conditions, rules, and one output."""
    inputs, rules = model["inputs"], model["rules"]
    x, y, rule_w, output_w = 70, 160, 55, 190
    input_w = min(185, 895 / len(inputs))
    total_w = rule_w + input_w * len(inputs) + output_w
    row_h = min(53, 320 / max(len(rules), 1))
    out = ['<g data-dmn="decision-table" data-source-id="decision-table">']
    out.append(_text(x, 132, f'«decision» {model["title"]}', 18, "#7a4b05", "start", 700))
    out.append(_text(x + total_w, 132, f'命中策略 {model["hitPolicy"]}', 13, "#a16207", "end", 600))
    out.append(_rect(x, y, total_w, 76 + row_h * len(rules), "#fff", "#94a3b8", 0, 1.4))
    out.append(_rect(x, y, rule_w + input_w * len(inputs), 32, "#fdf4e1", "#a16207", 0, 0))
    out.append(_rect(x + rule_w + input_w * len(inputs), y, output_w, 32, "#e4f3ef", "#0f766e", 0, 0))
    out.append(_text(x + (rule_w + input_w * len(inputs)) / 2, y + 22, "输入条件", 13, "#7a4b05", weight=700))
    out.append(_text(x + rule_w + input_w * len(inputs) + output_w / 2, y + 22, "决策输出", 13, "#0b5a54", weight=700))
    out.append(_text(x + rule_w / 2, y + 59, "规则", 13, "#334155", weight=650))
    for index, item in enumerate(inputs):
        cx = x + rule_w + (index + .5) * input_w
        out.append(_text(cx, y + 52, item["label"], 13, "#334155", weight=650))
        out.append(_text(cx, y + 70, item.get("unit", ""), 11, "#64748b"))
    out.append(_text(x + rule_w + input_w * len(inputs) + output_w / 2, y + 59,
                     model["output"]["label"], 13, "#334155", weight=650))
    for index, rule in enumerate(rules):
        ry = y + 76 + index * row_h
        out.append(_rect(x, ry, total_w, row_h, "#f8fafc" if index % 2 == 0 else "#fff", "#e2e8f0", 0, .8))
        out.append(f'<g data-dmn-rule="{escape(rule["id"], quote=True)}" data-source-id="{escape(rule.get("sourceId", rule["id"]), quote=True)}">')
        out.append(_text(x + rule_w / 2, ry + row_h / 2 + 5, rule["id"], 12, "#64748b", weight=650))
        for column, condition in enumerate(rule["conditions"]):
            cx = x + rule_w + (column + .5) * input_w
            out.append(_text(cx, ry + row_h / 2 + 5, condition, 12, "#334155"))
        result = rule["result"]
        color = "#0f766e" if result.lower() == "go" else "#b42318" if result.lower() == "no-go" else "#a16207"
        out.append(_text(x + rule_w + input_w * len(inputs) + output_w / 2, ry + row_h / 2 + 5,
                         result, 13, color, weight=700))
        out.append('</g>')
    for column in range(len(inputs) + 1):
        vx = x + rule_w + column * input_w
        out.append(f'<line x1="{vx}" y1="{y+32}" x2="{vx}" y2="{y+76+row_h*len(rules)}" stroke="#cbd5e1"/>')
    out.append('</g>')
    return ''.join(out)


def timing_svg(model):
    """Waveform-like state intervals on a shared clock, not a project timeline."""
    x, y, width, duration = 265, 165, 890, model["durationMs"]
    row_h = 100
    out = ['<g data-timing="state-waves" data-source-id="timing">']
    for tick in model["ticks"]:
        tx = x + width * tick / duration
        out.append(f'<line x1="{tx}" y1="{y-10}" x2="{tx}" y2="{y+row_h*len(model["lifelines"])}" stroke="#e2e8f0" stroke-dasharray="3 4"/>')
        out.append(_text(tx, y - 22, f'{tick} ms', 11, "#64748b"))
    for row, lifeline in enumerate(model["lifelines"]):
        ry = y + row * row_h
        out.append(_text(55, ry + 37, lifeline["label"], 14, "#334155", "start", 650))
        states = list(dict.fromkeys(segment["state"] for segment in lifeline["segments"]))
        out.append(_text(55, ry + 62, " / ".join(states), 11, "#64748b", "start"))
        out.append(f'<line x1="{x}" y1="{ry+84}" x2="{x+width}" y2="{ry+84}" stroke="#e2e8f0" stroke-width="1"/>')
        previous_level = None
        for index, segment in enumerate(lifeline["segments"]):
            sx = x + width * segment["from"] / duration
            ex = x + width * segment["to"] / duration
            active = segment.get("active", segment["state"] not in {"等待", "空闲"})
            level = ry + (24 if active else 68)
            stroke = "#2459a6" if row == 0 else "#0f766e" if row == 1 else "#6d28d9"
            out.append(f'<g data-timing-segment="{escape(lifeline["id"], quote=True)}:{index}" data-source-id="{escape(segment.get("sourceId", lifeline["id"]), quote=True)}">')
            if previous_level is not None and previous_level != level:
                out.append(f'<line x1="{sx}" y1="{previous_level}" x2="{sx}" y2="{level}" stroke="{stroke}" stroke-width="3"/>')
            out.append(f'<line x1="{sx}" y1="{level}" x2="{ex}" y2="{level}" stroke="{stroke}" stroke-width="3"/>')
            if ex - sx > 85:
                out.append(_text((sx + ex) / 2, level - 9, segment["state"], 12, stroke, weight=600))
            out.append('</g>')
            previous_level = level
    for index, constraint in enumerate(model["constraints"]):
        cy = y + row_h * len(model["lifelines"]) + 25 + index * 29
        sx = x + width * constraint["from"] / duration
        ex = x + width * constraint["to"] / duration
        out.append(f'<path d="M {sx},{cy-7} V {cy} H {ex} V {cy-7}" fill="none" stroke="#b42318" stroke-width="1.5"/>')
        out.append(_text((sx + ex) / 2, cy + 17, constraint["label"], 12, "#b42318", weight=650))
    out.append('</g>')
    return ''.join(out)


def tradespace_svg(model):
    """Physical objective space with feasibility limits and a Pareto frontier."""
    x, y, w, h = 245, 160, 830, 390
    xaxis, yaxis = model["x"], model["y"]
    px = lambda value: x + w * (value - xaxis["min"]) / (xaxis["max"] - xaxis["min"])
    py = lambda value: y + h - h * (value - yaxis["min"]) / (yaxis["max"] - yaxis["min"])
    out = ['<g data-tradespace="objective-space" data-source-id="tradespace">']
    out.append(_rect(x, y, w, h, "#fbfdff", "#cbd5e1", 0, 1))
    threshold = model.get("thresholds", {})
    if "maxX" in threshold and "minY" in threshold:
        fx, fy = px(threshold["maxX"]), py(threshold["minY"])
        out.append(_rect(x, y, max(0, fx-x), max(0, fy-y), "#e4f3ef", "none", 0, 0))
        out.append(f'<path d="M {fx},{y} V {y+h} M {x},{fy} H {x+w}" fill="none" stroke="#a16207" stroke-dasharray="6 4"/>')
        out.append(_text(fx + 8, y + 20, f'{xaxis.get("symbol", "x")} ≤ {threshold["maxX"]}', 11, "#a16207", "start"))
        out.append(_text(x + 8, fy - 8, f'{yaxis.get("symbol", "y")} ≥ {threshold["minY"]}', 11, "#a16207", "start"))
    for index in range(5):
        xv = xaxis["min"] + (xaxis["max"] - xaxis["min"]) * index / 4
        yv = yaxis["min"] + (yaxis["max"] - yaxis["min"]) * index / 4
        tx, ty = px(xv), py(yv)
        out.append(f'<line x1="{tx}" y1="{y}" x2="{tx}" y2="{y+h}" stroke="#e2e8f0"/>')
        out.append(f'<line x1="{x}" y1="{ty}" x2="{x+w}" y2="{ty}" stroke="#e2e8f0"/>')
        out.append(_text(tx, y+h+22, f'{xv:g}', 11, "#64748b"))
        out.append(_text(x-14, ty+4, f'{yv:g}', 11, "#64748b", "end"))
    alternatives = {a["id"]: a for a in model["alternatives"]}
    front = [alternatives[key] for key in model.get("paretoIds", [])]
    front.sort(key=lambda a: a["x"])
    if front:
        path = 'M ' + ' L '.join(f'{px(a["x"])},{py(a["y"])}' for a in front)
        out.append(f'<path data-pareto-front="true" d="{path}" fill="none" stroke="#b42318" stroke-width="2.5"/>')
    for index, a in enumerate(model["alternatives"]):
        cx, cy = px(a["x"]), py(a["y"])
        color = "#0f766e" if a["id"] in model.get("paretoIds", []) else "#64748b"
        out.append(f'<g data-alternative="{escape(a["id"], quote=True)}" data-source-id="{escape(a.get("sourceId", a["id"]), quote=True)}">')
        dx, dy = a.get("labelDx", 10), a.get("labelDy", -10 - (index % 2) * 12)
        if abs(dx) > 40 or abs(dy) > 30:
            label_width = sum((12 if unicodedata.east_asian_width(char) in "WF" else 7) for char in a["label"])
            to_x = cx + dx + (label_width if dx < 0 else 0)
            to_y = cy + dy - 4
            out.append(f'<path d="M {cx},{cy} L {to_x},{to_y}" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="3 3"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{min(12, 5 + a.get("cost", 0)/300)}" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        out.append(_text(cx + dx, cy + dy,
                         a["label"], 12, color, a.get("labelAnchor", "start"), 600))
        out.append('</g>')
    out.append(_text(x+w/2, y+h+52, xaxis["label"], 13, "#334155", weight=650))
    out.append(_text(x-12, y-17, yaxis["label"], 13, "#334155", "start", 650))
    out.append('</g>')
    return ''.join(out)


def _schedule(tasks):
    by_id = {task["id"]: task for task in tasks}
    remaining = set(by_id)
    order = []
    while remaining:
        ready = sorted(key for key in remaining if all(dep in order for dep in by_id[key]["dependencies"]))
        if not ready:
            raise ValueError("PERT dependencies contain a cycle or unknown task")
        order.extend(ready)
        remaining.difference_update(ready)
    es, ef = {}, {}
    for key in order:
        task = by_id[key]
        es[key] = max((ef[dep] for dep in task["dependencies"]), default=0)
        ef[key] = es[key] + task["duration"]
    project = max(ef.values())
    successors = {key: [] for key in by_id}
    for task in tasks:
        for dep in task["dependencies"]:
            successors[dep].append(task["id"])
    ls, lf = {}, {}
    for key in reversed(order):
        lf[key] = min((ls[child] for child in successors[key]), default=project)
        ls[key] = lf[key] - by_id[key]["duration"]
    return es, ef, ls, lf, project


def pert_svg(model):
    tasks = model["tasks"]
    es, ef, ls, lf, project = _schedule(tasks)
    by_id = {task["id"]: task for task in tasks}
    out = ['<g data-pert="activity-on-node" data-source-id="pert">']
    for task in tasks:
        for dep in task["dependencies"]:
            parent = by_id[dep]
            x1, y1 = parent["x"] + 140, parent["y"] + 44
            x2, y2 = task["x"], task["y"] + 44
            critical = ls[dep] == es[dep] and ls[task["id"]] == es[task["id"]] and ef[dep] == es[task["id"]]
            stroke = "#b42318" if critical else "#64748b"
            mid = (x1 + x2) / 2
            out.append(f'<path data-pert-dependency="{escape(dep, quote=True)}:{escape(task["id"], quote=True)}" d="M {x1},{y1} H {mid} V {y2} H {x2}" fill="none" stroke="{stroke}" stroke-width="2" marker-end="url(#arrow)"/>')
    for task in tasks:
        key, x, y = task["id"], task["x"], task["y"]
        critical = ls[key] == es[key]
        color, fill = ("#b42318", "#fdecea") if critical else ("#2459a6", "#e8f0ff")
        out.append(f'<g data-pert-task="{escape(key, quote=True)}" data-source-id="{escape(task.get("sourceId", key), quote=True)}">')
        out.append(_rect(x, y, 140, 88, fill, color, 6, 1.7))
        out.append(_text(x+70, y+29, task["label"], 13, color, weight=700))
        out.append(_text(x+70, y+51, f'工期 {task["duration"]} 周', 12, "#334155"))
        out.append(_text(x+70, y+73, f'ES {es[key]} · EF {ef[key]} · 浮动 {ls[key]-es[key]}', 11, "#64748b"))
        out.append('</g>')
    out.append(_text(65, 630, f'红色 = 关键路径 · 项目最短工期 {project} 周', 14, "#b42318", "start", 650))
    out.append('</g>')
    return ''.join(out)
