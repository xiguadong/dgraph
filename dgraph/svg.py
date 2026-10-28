"""Small deterministic SVG composition layer with engineering-diagram primitives."""

from html import escape


PALETTE = {
    "blue": ("#e8f0ff", "#2459a6"), "teal": ("#e4f3ef", "#0f766e"),
    "amber": ("#fdf4e1", "#a16207"), "violet": ("#f1ebfd", "#6d28d9"),
    "red": ("#fdecea", "#b42318"), "gray": ("#f8fafc", "#64748b"),
}


def _attrs(values):
    return " ".join(f'{key.replace("_", "-")}="{escape(str(value), quote=True)}"' for key, value in values.items() if value is not None)


def _text(x, y, value, size=16, color="#334155", anchor="middle", weight=400, extra=None):
    attrs = {"x": x, "y": y, "font-size": size, "fill": color, "text-anchor": anchor, "font-weight": weight}
    if extra:
        attrs.update(extra)
    return f"<text {_attrs(attrs)}>{escape(str(value))}</text>"


def _multiline(node, color):
    lines = str(node["label"]).split("\n")
    x = node["x"] + node["w"] / 2
    start = node["y"] + node["h"] / 2 - (len(lines) - 1) * 10 + 5
    return "".join(_text(x, start + i * 20, line, node.get("fontSize", 16), color, weight=node.get("fontWeight", 600)) for i, line in enumerate(lines))


def _color(node):
    return PALETTE.get(node.get("color", "blue"), PALETTE["blue"])


def _group(group):
    fill, stroke = _color(group)
    out = [f'<g data-group-id="{escape(group["id"], quote=True)}">']
    out.append(f'<rect {_attrs({"x": group["x"], "y": group["y"], "width": group["w"], "height": group["h"], "rx": group.get("rx", 16), "fill": fill, "fill-opacity": .35, "stroke": stroke, "stroke-width": 1.8, "stroke-dasharray": group.get("dash")})}/>')
    out.append(_text(group["x"] + 16, group["y"] + 28, group.get("label", ""), 15, stroke, "start", 700))
    out.append("</g>")
    return "".join(out)


def _node(node):
    fill, stroke = _color(node)
    x, y, w, h = (node[key] for key in ("x", "y", "w", "h"))
    kind = node.get("kind", "block")
    out = [f'<g data-node-id="{escape(node["id"], quote=True)}" data-source-id="{escape(node["sourceId"], quote=True)}" data-kind="{escape(kind, quote=True)}">']
    out.append(f"<title>{escape(node.get('details', node['label']))}</title>")
    if kind == "gate":
        out.append(f'<circle cx="{x+w/2}" cy="{y+h/2}" r="{min(w,h)/2}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(_multiline(node, stroke))
    elif kind == "datastore":
        out.append(f'<path d="M {x} {y+12} H {x+w} M {x} {y+h-12} H {x+w} M {x+12} {y} V {y+h} M {x+w-12} {y} V {y+h}" fill="none" stroke="{stroke}" stroke-width="2"/>')
        out.append(_multiline(node, "#334155"))
    elif kind == "stock":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="3"/><rect x="{x+7}" y="{y+7}" width="{w-14}" height="{h-14}" fill="none" stroke="{stroke}" stroke-width="1"/>')
        out.append(_multiline(node, "#334155"))
    elif kind == "object":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>')
        out.append(_multiline(node, "#334155"))
        out.append(f'<line x1="{x+18}" y1="{y+h/2+15}" x2="{x+w-18}" y2="{y+h/2+15}" stroke="{stroke}" stroke-width="1.4"/>')
    elif kind == "component":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(_multiline(node, "#334155"))
        out.append(f'<path d="M {x+w-38} {y+12} h 24 v 20 h -24 Z M {x+w-44} {y+16} h 6 v 5 h -6 Z M {x+w-44} {y+25} h 6 v 5 h -6 Z" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
    elif kind == "node3d":
        out.append(f'<path d="M {x} {y+15} L {x+18} {y} H {x+w-18} L {x+w} {y+15} V {y+h-12} L {x+w-18} {y+h} H {x+18} L {x} {y+h-12} Z" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(f'<path d="M {x} {y+15} H {x+w-18} L {x+w} {y+15} M {x+w-18} {y+15} V {y+h}" fill="none" stroke="{stroke}" stroke-width="1.4"/>')
        out.append(_multiline(node, "#334155"))
    elif kind == "actor":
        cx = x + w / 2
        out.append(f'<circle cx="{cx}" cy="{y + 14}" r="12" fill="#fff" stroke="{stroke}" stroke-width="2"/>')
        out.append(f'<path d="M {cx} {y + 26} V {y + 60} M {cx - 20} {y + 38} H {cx + 20} M {cx} {y + 60} L {cx - 16} {y + 86} M {cx} {y + 60} L {cx + 16} {y + 86}" fill="none" stroke="{stroke}" stroke-width="2"/>')
        out.append(_text(cx, y + 110, node["label"], 15, "#334155"))
    elif kind in {"usecase", "ellipse"}:
        out.append(f'<ellipse {_attrs({"cx": x + w / 2, "cy": y + h / 2, "rx": w / 2, "ry": h / 2, "fill": fill, "stroke": stroke, "stroke-width": 2})}/>')
        out.append(_multiline(node, "#334155"))
    elif kind in {"decision", "diamond"}:
        points = f"{x + w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"
        out.append(f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(_multiline(node, "#334155"))
    elif kind in {"initial", "final"}:
        cx, cy = x + w / 2, y + h / 2
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{min(w,h)/2}" fill="{stroke}"/>')
        if kind == "final":
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{min(w,h)/2-6}" fill="#fff" stroke="{stroke}" stroke-width="3"/>')
        out.append(_text(cx, y + h + 24, node["label"], 14, "#334155"))
    elif kind == "port":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{stroke}" stroke-width="2"/>')
        out.append(_text(x + w + 6, y + h / 2 + 5, node["label"], 12, stroke, "start"))
    else:
        dash = "6 4" if kind in {"reference", "interface"} else None
        rx = 18 if kind in {"state", "action"} else 6
        out.append(f'<rect {_attrs({"x": x, "y": y, "width": w, "height": h, "rx": rx, "fill": fill, "stroke": stroke, "stroke-width": 2, "stroke-dasharray": dash})}/>')
        if kind == "package":
            out.append(f'<path d="M {x} {y} H {x + min(90,w*.45)} V {y-20} H {x} Z" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        if node.get("stereotype"):
            out.append(_text(x + w / 2, y + 20, f"«{node['stereotype']}»", 11, stroke, weight=500))
        out.append(_multiline(node, "#173d73" if node.get("color", "blue") == "blue" else "#334155"))
        if node.get("compartment"):
            cy = y + h - 28
            out.append(f'<line x1="{x}" y1="{cy}" x2="{x+w}" y2="{cy}" stroke="{stroke}" stroke-width="1"/>')
            out.append(_text(x + 10, cy + 19, node["compartment"], 12, "#475569", "start", 400))
    out.append("</g>")
    return "".join(out)


def _endpoint(node, toward, side=None):
    x, y, w, h = (node[key] for key in ("x", "y", "w", "h"))
    if side == "left": return x, y + h / 2
    if side == "right": return x + w, y + h / 2
    if side == "top": return x + w / 2, y
    if side == "bottom": return x + w / 2, y + h
    tx, ty = toward
    cx, cy = x + w / 2, y + h / 2
    dx, dy = tx - cx, ty - cy
    if abs(dx) * h > abs(dy) * w:
        return (x + w if dx > 0 else x, cy + (h/2) * dy / max(abs(dx)*h/w, 1e-9))
    return (cx + (w/2) * dx / max(abs(dy)*w/h, 1e-9), y + h if dy > 0 else y)


def _edge_geometry(edge, nodes):
    source, target = nodes[edge["source"]], nodes[edge["target"]]
    if edge.get("points"):
        return edge["points"]
    tc = (target["x"] + target["w"] / 2, target["y"] + target["h"] / 2)
    sc = (source["x"] + source["w"] / 2, source["y"] + source["h"] / 2)
    return [_endpoint(source, tc, edge.get("fromSide")), _endpoint(target, sc, edge.get("toSide"))]


def _edge(edge, nodes):
    points = _edge_geometry(edge, nodes)
    _, stroke = _color(edge)
    path = "M " + " L ".join(f"{x},{y}" for x, y in points)
    dashed = edge["kind"] in {"dependency", "verify", "satisfy", "derive", "return", "reference"}
    marker = "none" if edge["kind"] in {"composition", "aggregation", "association", "binding"} else "url(#arrow)"
    out = [f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="2" stroke-dasharray="{("6 4" if dashed else None)}" marker-end="{marker}"/>']
    if edge["kind"] in {"composition", "aggregation"}:
        x, y = points[0]
        out.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" transform="rotate(45 {x} {y})" fill="{stroke if edge["kind"] == "composition" else "#fff"}" stroke="{stroke}"/>')
    return "".join(out)


def _edge_label(edge, nodes):
    if not edge.get("label"):
        return ""
    points = _edge_geometry(edge, nodes)
    _, stroke = _color(edge)
    default_position = ((points[0][0] + points[-1][0]) / 2, (points[0][1] + points[-1][1]) / 2)
    lx, ly = edge.get("labelPosition", default_position)
    return f'<rect x="{lx-5}" y="{ly-16}" width="{len(edge["label"])*8+10}" height="21" rx="4" fill="#fff" fill-opacity=".94"/>' + _text(lx + len(edge["label"])*4, ly, edge["label"], edge.get("fontSize", 13), stroke, "middle", 500)


def _matrix(matrix):
    x, y = matrix["x"], matrix["y"]
    cw, ch = matrix.get("cellWidth", 110), matrix.get("cellHeight", 60)
    out = [f'<g data-matrix="{escape(matrix["id"], quote=True)}">']
    for column, label in enumerate(matrix["columns"]):
        out.append(_text(x + (column + 1.5) * cw, y + 22, label, 13, "#475569", weight=600))
    for row, label in enumerate(matrix["rows"]):
        out.append(_text(x + cw - 12, y + (row + 1.5) * ch + 5, label, 13, "#475569", "end", 600))
    for row in range(len(matrix["rows"])):
        for column in range(len(matrix["columns"])):
            rx, ry = x + (column + 1) * cw, y + (row + 1) * ch
            cell = next((item for item in matrix.get("cells", []) if item["row"] == row and item["column"] == column), {})
            fill, stroke = _color(cell)
            out.append(f'<rect x="{rx}" y="{ry}" width="{cw}" height="{ch}" fill="{fill if cell else "#fff"}" stroke="#cbd5e1" stroke-width="1.2"/>')
            if cell:
                out.append(f'<g data-matrix-cell="{row}:{column}" data-source-id="{escape(cell.get("sourceId", matrix["id"] + f":{row}:{column}"), quote=True)}">')
                out.append(_text(rx + cw / 2, ry + ch / 2 + 5, cell.get("label", ""), cell.get("fontSize", 14), stroke, weight=600))
                out.append("</g>")
    out.append("</g>")
    return "".join(out)


def _chart(chart):
    x, y, w, h = (chart[key] for key in ("x", "y", "w", "h"))
    out = [f'<g data-chart="{escape(chart["id"], quote=True)}">', f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fbfdff" stroke="#cbd5e1"/>']
    for step in range(5):
        gy = y + h * step / 4
        out.append(f'<line x1="{x}" y1="{gy}" x2="{x+w}" y2="{gy}" stroke="#e2e8f0"/>')
    for series in chart.get("series", []):
        _, stroke = _color(series)
        points = [(x + px * w / 100, y + h - py * h / 100) for px, py in series["points"]]
        path = "M " + " L ".join(f"{px},{py}" for px, py in points)
        out.append(f'<g data-chart-series="{escape(series["id"], quote=True)}">')
        if chart.get("kind", "line") != "scatter":
            out.append(f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="3"/>')
        for px, py in points:
            out.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{stroke}"/>')
        if series.get("label"):
            lx, ly = points[-1]
            out.append(_text(lx - 8, ly - 12, series["label"], 13, stroke, "end", 600))
        out.append("</g>")
    out.append(_text(x + w / 2, y + h + 34, chart.get("xLabel", ""), 13, "#64748b"))
    out.append(_text(x - 14, y + h / 2, chart.get("yLabel", ""), 13, "#64748b", "end"))
    out.append("</g>")
    return "".join(out)


def _timeline(timeline):
    x, y, w = timeline["x"], timeline["y"], timeline["w"]
    rh = timeline.get("rowHeight", 64)
    label_width = timeline.get("labelWidth", 170)
    out = [f'<g data-timeline="{escape(timeline["id"], quote=True)}">']
    for index, row in enumerate(timeline["rows"]):
        ry = y + index * rh
        fill, stroke = _color(row)
        out.append(_text(x, ry + rh / 2 + 5, row["label"], 14, "#334155", "start", 600))
        bx = x + label_width + row["start"] * (w - label_width) / 100
        bw = (row["end"] - row["start"]) * (w - label_width) / 100
        out.append(f'<rect data-timeline-bar="{escape(row["id"], quote=True)}" data-source-id="{escape(row.get("sourceId", timeline["id"] + ":" + row["id"]), quote=True)}" x="{bx}" y="{ry + 10}" width="{bw}" height="{rh - 22}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>')
    for marker in timeline.get("markers", []):
        mx = x + label_width + marker["position"] * (w - label_width) / 100
        bottom = y + len(timeline["rows"]) * rh
        out.append(f'<line x1="{mx}" y1="{y}" x2="{mx}" y2="{bottom}" stroke="#a16207" stroke-dasharray="4 4"/>')
        out.append(_text(mx + 5, bottom + 24, marker["label"], 13, "#a16207", "start", 600))
    out.append("</g>")
    return "".join(out)


from .domain import fta_svg, gantt_svg, qfd_svg


def render_svg(spec):
    p = spec["presentation"]
    width, height = p["width"], p["height"]
    selection = spec["selection"]
    nodes = {node["id"]: node for node in selection["nodes"]}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="-apple-system, PingFang SC, Hiragino Sans GB, Noto Sans SC, sans-serif" data-layout="{escape(selection.get("layout", spec["type"]), quote=True)}">']
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>')
    out.append(f'<rect width="{width}" height="{height}" fill="#fff"/>')
    out.append(_text(48, 52, p["title"], 28, "#15202b", "start", 750))
    out.append(_text(48, 80, p.get("subtitle", ""), 14, "#64748b", "start", 400))
    out.append(f'<line x1="48" y1="102" x2="{width-48}" y2="102" stroke="#e2e8f0"/>')
    if spec["type"] == "qfd":
        out.append(qfd_svg(selection["qfd"]))
    elif spec["type"] == "gantt":
        out.append(gantt_svg(selection["gantt"]))
    elif spec["type"] == "fta":
        out.append(fta_svg(selection["faultTree"]))
    else:
        out.extend(_group(group) for group in selection.get("groups", []))
        out.extend(_matrix(matrix) for matrix in selection.get("matrices", []))
        out.extend(_chart(chart) for chart in selection.get("charts", []))
        out.extend(_timeline(timeline) for timeline in selection.get("timelines", []))
        if spec["type"] == "sequence":
            out.extend(f'<line x1="{n["x"]+n["w"]/2}" y1="{n["y"]+n["h"]}" x2="{n["x"]+n["w"]/2}" y2="{height-85}" stroke="#94a3b8" stroke-dasharray="5 5"/>' for n in selection["nodes"])
        out.extend(_edge(edge, nodes) for edge in selection.get("edges", []))
        out.extend(_node(node) for node in selection["nodes"])
        out.extend(_edge_label(edge, nodes) for edge in selection.get("edges", []))
    for note in selection.get("annotations", []):
        out.append(_text(note["x"], note["y"], note["text"], note.get("fontSize", 13), note.get("color", "#64748b"), note.get("anchor", "start"), note.get("fontWeight", 400)))
    out.append(_text(48, height - 30, spec["intent"]["question"], 13, "#64748b", "start", 400))
    out.append(_text(width - 48, height - 30, "dgraph · semantic projection", 12, "#94a3b8", "end", 400))
    out.append("</svg>")
    return "\n".join(out) + "\n"
