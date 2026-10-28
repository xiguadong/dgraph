"""Boundary anchors and clear labels for dedicated diagram relations."""

from .svg import _text


def _center(box):
    x, y, w, h = box
    return x + w / 2, y + h / 2


def _boundary(box, toward):
    x, y, w, h = box
    cx, cy = _center(box)
    dx, dy = toward[0] - cx, toward[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    scale = 1 / max(abs(dx) / (w / 2), abs(dy) / (h / 2))
    return cx + dx * scale, cy + dy * scale


def relation_points(relation, boxes):
    if relation.get("points"):
        return relation["points"]
    source, target = boxes[relation["source"]], boxes[relation["target"]]
    return [_boundary(source, _center(target)), _boundary(target, _center(source))]


def relation_path(points, stroke="#64748b", width=1.8, marker=True, extra=""):
    path = "M " + " L ".join(f"{x},{y}" for x, y in points)
    end = ' marker-end="url(#arrow)"' if marker else ""
    return f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="{width}"{end} {extra}/>'


def relation_label(points, label, color="#475569"):
    if not label:
        return ""
    segments = list(zip(points, points[1:]))
    if not segments:
        return ""
    a, b = max(segments, key=lambda segment: abs(segment[1][0] - segment[0][0]) + abs(segment[1][1] - segment[0][1]))
    x, y = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horizontal = abs(b[0] - a[0]) >= abs(b[1] - a[1])
    return _text(x if horizontal else x + 9, y - 10 if horizontal else y - 2,
                 label, 12, color, "middle" if horizontal else "start", 550,
                 {"paint-order": "stroke", "stroke": "#fff", "stroke-width": 5, "stroke-linejoin": "round"})
