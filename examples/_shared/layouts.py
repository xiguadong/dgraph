"""Diagram-specific semantic layouts with independent dgraph identities."""

from dgraph.catalog import CATALOG
from examples._shared.domain_examples import FTA_MODEL, GANTT_MODEL, QFD_MODEL


QUESTIONS = {entry["type"]: entry["question"] for entry in CATALOG}
COLORS = ["blue", "teal", "amber", "violet", "gray"]


def N(slug, index, label, x, y, w=230, h=85, color="blue", kind="block", compartment=None):
    node = {"id": f"n{index}", "label": label, "kind": kind, "x": x, "y": y, "w": w, "h": h, "color": color, "sourceId": f"Example.{slug}.n{index}"}
    if compartment:
        node["compartment"] = compartment
    return node


def E(source, target, kind="flow", label=None, color="teal", points=None, label_position=None):
    edge = {"source": source, "target": target, "kind": kind, "color": color}
    if label:
        edge["label"] = label
    if points:
        edge["points"] = points
    if label_position:
        edge["labelPosition"] = label_position
    return edge


def CHAIN(count, kind="flow", labels=None):
    result = []
    for index in range(count - 1):
        result.append(E(f"n{index}", f"n{index+1}", kind, labels[index] if labels and index < len(labels) else None))
    return result


def TREE(slug, labels, relation="composition", node_kind="block"):
    nodes = [N(slug, 0, labels[0], 500, 135, 280, 85, "violet", node_kind)]
    nodes += [N(slug, i + 1, label, 80 + i * 400, 410, 300, 100, "blue", node_kind) for i, label in enumerate(labels[1:4])]
    return nodes, [E("n0", f"n{i}", relation, "1" if relation == "composition" else None, "blue") for i in range(1, 4)]


def FLOW(slug, labels, node_kind="block", edge_labels=None):
    nodes = [N(slug, i, label, 45 + i * 305, 290, 240, 105, COLORS[i], node_kind) for i, label in enumerate(labels[:4])]
    return nodes, CHAIN(4, "flow", edge_labels)


def LAYERS(slug, labels, relation="dependency"):
    nodes = [N(slug, i, label, 340, 130 + i * 125, 600, 78, COLORS[i]) for i, label in enumerate(labels[:4])]
    return nodes, CHAIN(4, relation)


def CONTEXT(slug, labels, actors=False):
    groups = [{"id": "boundary", "label": labels[1], "kind": "boundary", "x": 330, "y": 150, "w": 620, "h": 400, "color": "blue"}]
    nodes = [N(slug, 0, labels[0], 65, 260, 200, 90, "gray", "actor" if actors else "block"), N(slug, 1, labels[1], 500, 285, 280, 110), N(slug, 2, labels[2], 1010, 260, 200, 90, "teal"), N(slug, 3, labels[3], 500, 455, 280, 70, "violet")]
    edges = [E("n0", "n1", "association"), E("n1", "n2", "flow", "interface"), E("n3", "n1", "dependency")]
    return nodes, edges, groups


def MATRIX(slug, labels, kind):
    axis = labels[:4] if kind == "n2" else labels[1:4]
    cell_width = 160 if kind == "n2" else 210
    node = N(slug, 0, "矩阵读法", 55, 145, 190, 75, "gray")
    cells = [
        {"row": 0, "column": 1, "label": "I-01" if kind == "n2" else labels[0], "color": "amber", "sourceId": f"Example.{slug}.cell01"},
        {"row": 1, "column": 2, "label": "I-02" if kind == "n2" else "相关", "color": "teal", "sourceId": f"Example.{slug}.cell12"},
        {"row": 2, "column": 0, "label": "I-03" if kind == "n2" else "追溯", "color": "violet", "sourceId": f"Example.{slug}.cell20"},
    ]
    matrix = {"id": f"{slug}-matrix", "x": 300 if kind == "n2" else 320, "y": 150, "cellWidth": cell_width, "cellHeight": 75 if kind == "n2" else 85, "columns": axis, "rows": axis, "cells": cells}
    return [node], matrix


def CHART(slug, labels, scatter):
    nodes = [N(slug, 0, labels[0], 90, 555, 240, 65), N(slug, 1, labels[1], 950, 555, 240, 65, "teal")]
    series = [
        {"id": "planned", "label": labels[0], "color": "gray", "points": [[20, 80], [50, 60], [85, 35]] if scatter else [[0, 100], [50, 50], [100, 0]]},
        {"id": "actual", "label": labels[1], "color": "teal", "points": [[15, 30], [45, 55], [70, 75], [90, 88]] if scatter else [[0, 95], [35, 65], [70, 30], [100, 12]]},
    ]
    chart = {"id": f"{slug}-chart", "kind": "scatter" if scatter else "line", "x": 170, "y": 150, "w": 900, "h": 340, "xLabel": "质量 / 成本 →" if scatter else labels[2], "yLabel": "能量 / 低温性能 →" if scatter else labels[3], "series": series}
    return nodes, chart


def TIMELINE(slug, labels):
    rows = [{"id": f"row{i}", "label": label, "start": i * 14, "end": min(95, i * 14 + 45), "color": COLORS[i], "sourceId": f"Example.{slug}.row{i}"} for i, label in enumerate(labels[:4])]
    timeline = {"id": f"{slug}-timeline", "x": 95, "y": 150, "w": 1060, "rowHeight": 82, "labelWidth": 210, "rows": rows, "markers": [{"position": 58, "label": "PDR / 评审"}]}
    return [N(slug, 0, "里程碑 / 验收点", 90, 555, 250, 65, "amber")], timeline


def DELIVERY(slug, labels):
    count = len(labels)
    xs = [25, 275, 525, 775, 1025] if count == 5 else [45, 350, 655, 960]
    width = 220 if count == 5 else 240
    nodes = [N(slug, i, labels[i], xs[i], 265, width, 105, COLORS[i]) for i in range(count)]
    relations = ["builds", "produces", "publishes", "deploys / runs"]
    edges = CHAIN(count, "flow", relations)
    for index, edge in enumerate(edges):
        label = edge["label"]
        edge["labelPosition"] = [(xs[index] + width + xs[index + 1]) / 2 - len(label) * 4, 230]
    matrix = {"id": "delivery-map", "x": 240, "y": 450, "cellWidth": 230, "cellHeight": 48, "columns": ["交付物", "存放位置", "部署目标"], "rows": ["应用包", "文档"], "cells": [
        {"row": 0, "column": 0, "label": "app-0.1.0", "color": "amber", "sourceId": f"Example.{slug}.artifact"},
        {"row": 0, "column": 1, "label": "Release registry", "color": "violet", "sourceId": f"Example.{slug}.registry"},
        {"row": 0, "column": 2, "label": "本地 MCP 进程", "color": "teal", "sourceId": f"Example.{slug}.runtime"},
        {"row": 1, "column": 1, "label": "docs/site", "color": "blue", "sourceId": f"Example.{slug}.docs"},
    ]}
    return nodes, edges, matrix


def layout(entry):
    slug, kind, labels = entry["slug"], entry["type"], entry["labels"]
    nodes, edges, groups, matrices, charts, timelines, annotations = [], [], [], [], [], [], []
    if kind == "opm":
        nodes = [N(slug, 0, labels[0], 55, 280, 240, 100, "blue"), N(slug, 1, labels[1], 360, 280, 230, 100, "teal", "usecase"), N(slug, 2, labels[2], 670, 280, 240, 100, "blue"), N(slug, 3, labels[3], 980, 280, 230, 100, "violet", "usecase")]
        edges = CHAIN(4, "flow", ["输入", "生成", "支撑"])
    elif kind == "c4":
        groups = [{"id": "context", "label": labels[0], "kind": "boundary", "x": 80, "y": 130, "w": 1120, "h": 470, "color": "gray"}, {"id": "container", "label": labels[1], "kind": "boundary", "x": 160, "y": 200, "w": 960, "h": 360, "color": "blue"}, {"id": "component", "label": labels[2], "kind": "boundary", "x": 250, "y": 275, "w": 780, "h": 240, "color": "teal"}]
        nodes = [N(slug, 0, labels[3], 480, 355, 320, 90, "violet", "class", "fields + methods")]
        annotations = [{"x": 285, "y": 585, "text": "逐层缩放：系统 → 容器 → 组件 → 代码"}]
    elif kind == "ffbd":
        groups = [{"id": "parallel", "label": "并行功能", "kind": "boundary", "x": 350, "y": 175, "w": 610, "h": 330, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 45, 290, 210, 90), N(slug, 1, labels[1], 420, 210, 220, 80, "teal"), N(slug, 2, labels[2], 420, 385, 220, 80, "teal"), N(slug, 3, labels[3], 1010, 290, 210, 90, "violet"), N(slug, 4, "并行开始", 690, 210, 170, 70, "gray", "decision"), N(slug, 5, "并行汇合", 690, 385, 170, 70, "gray", "decision")]
        edges = [E("n0", "n1"), E("n0", "n2"), E("n1", "n4"), E("n2", "n5"), E("n4", "n3"), E("n5", "n3")]
    elif kind == "n2":
        nodes, matrix = MATRIX(slug, labels, kind)
        matrices = [matrix]
    elif kind == "idef0":
        nodes = [N(slug, 0, labels[0], 45, 290, 220, 90, "gray"), N(slug, 1, labels[1], 500, 290, 280, 100, "teal"), N(slug, 2, labels[2], 500, 135, 280, 80, "amber"), N(slug, 3, labels[3], 500, 480, 280, 80), N(slug, 4, "遥测数据", 1000, 290, 220, 90, "violet")]
        edges = [E("n0", "n1", "flow", "input"), E("n2", "n1", "dependency", "control"), E("n3", "n1", "association", "mechanism"), E("n1", "n4", "flow", "output")]
    elif kind == "dfd":
        nodes = [N(slug, 0, labels[0], 55, 280, 210, 95, "gray"), N(slug, 1, labels[1], 370, 280, 230, 100, "teal", "usecase"), N(slug, 2, labels[2], 680, 280, 220, 95, "amber", "datastore"), N(slug, 3, labels[3], 1000, 280, 210, 95, "violet")]
        edges = CHAIN(4, "flow", ["原始采样", "遥测帧", "回放 / 下传"])
    elif kind == "qfd":
        nodes, matrix = MATRIX(slug, labels, kind)
    elif kind == "tradespace":
        nodes, chart = CHART(slug, labels, True)
        charts = [chart]
    elif kind == "fta":
        nodes = [N(slug, 0, labels[0], 500, 125, 280, 75, "red"), N(slug, 1, "OR", 565, 235, 150, 65, "amber", "gate"), N(slug, 2, labels[1], 280, 390, 250, 85, "red"), N(slug, 3, labels[2], 750, 390, 250, 85, "red"), N(slug, 4, "AND", 815, 505, 120, 60, "amber", "gate"), N(slug, 5, labels[3], 770, 590, 210, 55, "gray")]
        edges = [E("n0", "n1", "flow", None, "red"), E("n1", "n2", "flow", None, "red"), E("n1", "n3", "flow", None, "red"), E("n3", "n4", "flow", None, "red"), E("n4", "n5", "flow", None, "red")]
    elif kind == "cld":
        nodes = [N(slug, 0, labels[0], 520, 130, 240, 75), N(slug, 1, labels[1], 900, 320, 240, 75, "teal"), N(slug, 2, labels[2], 520, 500, 240, 75, "amber"), N(slug, 3, labels[3], 140, 320, 240, 75, "violet")]
        edges = [E("n0", "n1", "flow", "+"), E("n1", "n2", "flow", "+"), E("n2", "n3", "flow", "+"), E("n3", "n0", "flow", "−")]
        annotations = [{"x": 565, "y": 350, "text": "B 调节回路", "fontSize": 22, "color": "#b42318"}, {"x": 510, "y": 380, "text": "极性与反馈方向必须可读"}]
    elif kind == "sfd":
        nodes = [N(slug, 0, labels[0], 450, 275, 340, 120, "blue", "stock"), N(slug, 1, labels[1], 75, 290, 180, 80, "amber", "gate"), N(slug, 2, labels[2], 930, 275, 250, 100, "violet"), N(slug, 3, labels[3], 500, 490, 240, 75, "teal")]
        edges = [E("n1", "n0", "flow", "能量流"), E("n0", "n2", "flow", "消耗"), E("n3", "n1", "dependency", "影响速率")]
    elif kind == "dodaf":
        nodes = [N(slug, 0, "视点选择", 55, 145, 190, 75, "gray")]
        matrices = [{"id": "dodaf-viewpoints", "x": 300, "y": 150, "cellWidth": 210, "cellHeight": 85, "columns": ["结构", "行为", "映射"], "rows": labels, "cells": [{"row": 0, "column": 0, "label": "AV-1", "color": "violet", "sourceId": "Example.dodaf.av1"}, {"row": 1, "column": 1, "label": "OV-1", "color": "teal", "sourceId": "Example.dodaf.ov1"}, {"row": 2, "column": 2, "label": "SV-1", "color": "blue", "sourceId": "Example.dodaf.sv1"}, {"row": 3, "column": 0, "label": "PV-1", "color": "amber", "sourceId": "Example.dodaf.pv1"}]}]
    elif kind == "ov1":
        nodes, edges, groups = CONTEXT(slug, labels, True)
    elif kind == "sv1":
        nodes, edges = FLOW(slug, labels, "part", ["I-02", "I-03", "I-04"])
        annotations = [{"x": 70, "y": 560, "text": "SV-1：系统资源与接口，而非项目流程"}]
    elif kind == "cv2":
        nodes, edges = TREE(slug, labels)
    elif kind == "arcadia":
        names = labels[:3] + ["PAB 物理架构", "EPBS 实现分解"]
        nodes = [N(slug, i, label, 70 + i * 245, 285, 220, 105, COLORS[i]) for i, label in enumerate(names)]
        edges = CHAIN(5, "dependency", ["分析", "分配", "细化", "实现"])
    elif kind in {"wbs", "pbs", "class-hierarchy", "profile"}:
        relation = "generalization" if kind == "class-hierarchy" else "composition"
        nodes, edges = TREE(slug, labels, relation, "package" if kind in {"wbs", "pbs", "profile"} else "class")
    elif kind == "gantt":
        nodes, timeline = TIMELINE(slug, labels)
        timelines = [timeline]
    elif kind == "pert":
        nodes = [N(slug, i, label, 45 + i * 305, 280, 240, 110, COLORS[i], "block", "ES / EF · 工期") for i, label in enumerate(labels)]
        edges = CHAIN(4, "flow", ["关键路径", "关键路径", "关键路径"])
        for edge in edges:
            edge["color"] = "red"
        annotations = [{"x": 65, "y": 540, "text": "红色 = 关键路径 · 节点内显示最早开始 / 完成与工期"}]
    elif kind == "risk-matrix":
        nodes, matrix = MATRIX(slug, labels, kind)
        matrices = [matrix]
    elif kind == "burndown":
        nodes, chart = CHART(slug, labels, False)
        charts = [chart]
    elif kind == "class":
        nodes = [N(slug, 0, labels[0], 90, 150, 260, 120, "blue", "class", "attributes\nmethods"), N(slug, 1, labels[1], 480, 150, 300, 120, "teal", "class", "timestamp\nvalues"), N(slug, 2, labels[2], 90, 420, 260, 110, "violet", "class", "state\ntransitions"), N(slug, 3, labels[3], 850, 420, 280, 110, "gray", "class", "receive()")]
        edges = [E("n2", "n0", "generalization", "uses"), E("n0", "n1", "composition", "produces"), E("n1", "n3", "dependency", "sent to")]
    elif kind == "object":
        nodes = [N(slug, i, label, 80 + i * 305, 285, 250, 100, COLORS[i], "object", "instance snapshot") for i, label in enumerate(labels)]
        edges = CHAIN(4, "association", ["samples", "owns", "receives"])
    elif kind == "component":
        nodes = [N(slug, i, label, 60 + i * 305, 280, 240, 105, COLORS[i], "component") for i, label in enumerate(labels)]
        edges = CHAIN(4, "dependency", ["provided", "required", "consumed"])
    elif kind == "composite-structure":
        nodes, edges, groups = CONTEXT(slug, labels)
        for node in nodes[1:3]:
            node["kind"] = "part"
    elif kind == "deployment":
        groups = [{"id": "device", "label": labels[1], "kind": "boundary", "x": 120, "y": 160, "w": 460, "h": 360, "color": "blue"}, {"id": "ground", "label": labels[3], "kind": "boundary", "x": 720, "y": 160, "w": 430, "h": 360, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 200, 280, 280, 100, "amber", "artifact"), N(slug, 1, labels[1], 150, 205, 170, 70, "blue", "node3d"), N(slug, 2, labels[2], 790, 280, 280, 100, "violet", "artifact"), N(slug, 3, labels[3], 850, 205, 170, 70, "teal", "node3d")]
        edges = [E("n0", "n2", "flow", "deploys / runs")]
    elif kind == "communication":
        nodes = [N(slug, 0, labels[0], 120, 180, 220, 90, "teal", "object"), N(slug, 1, labels[1], 500, 150, 220, 90, "blue", "object"), N(slug, 2, labels[2], 860, 220, 220, 90, "violet", "object"), N(slug, 3, labels[3], 500, 450, 220, 90, "gray", "object")]
        edges = [E("n1", "n0", "message", "1: read"), E("n0", "n1", "return", "2: data"), E("n1", "n2", "message", "3: frame"), E("n2", "n3", "message", "4: downlink")]
    elif kind == "interaction-overview":
        groups = [{"id": "normal", "label": labels[1], "kind": "boundary", "x": 390, "y": 170, "w": 260, "h": 150, "color": "teal"}, {"id": "exception", "label": labels[2], "kind": "boundary", "x": 700, "y": 390, "w": 260, "h": 150, "color": "red"}]
        nodes = [N(slug, 0, labels[0], 70, 260, 220, 85), N(slug, 1, labels[1], 420, 205, 200, 75, "teal"), N(slug, 2, labels[2], 730, 425, 200, 75, "red"), N(slug, 3, labels[3], 1000, 260, 200, 85, "violet"), N(slug, 4, "链路正常？", 530, 360, 150, 85, "amber", "decision")]
        edges = [E("n0", "n1"), E("n1", "n4"), E("n4", "n2", "flow", "否"), E("n4", "n3", "flow", "是"), E("n2", "n3")]
    elif kind == "timing":
        nodes, timeline = TIMELINE(slug, labels)
        timelines = [timeline]
        annotations = [{"x": 320, "y": 565, "text": "0 ms          100 ms          200 ms          300 ms          500 ms"}]
    elif kind == "event-storming":
        kinds = ["sticky", "sticky", "sticky", "sticky"]
        nodes = [N(slug, i, label, 45 + i * 305, 280, 245, 110, ["blue", "amber", "teal", "violet"][i], kinds[i], "command / event / policy") for i, label in enumerate(labels)]
        edges = CHAIN(4, "flow", ["触发", "产生", "通知"])
    elif kind == "impact-map":
        nodes, edges = FLOW(slug, labels, "block", ["Why", "Who", "How"])
    elif kind == "module-dependency":
        nodes, edges = FLOW(slug, labels, "package", ["imports", "uses", "registers"])
    elif kind == "eta":
        nodes = [N(slug, 0, labels[0], 480, 130, 300, 80, "amber"), N(slug, 1, labels[1], 480, 270, 300, 85, "violet", "decision"), N(slug, 2, labels[2], 190, 450, 270, 85, "red"), N(slug, 3, labels[3], 820, 450, 270, 85, "teal")]
        edges = [E("n0", "n1"), E("n1", "n2", "flow", "是"), E("n1", "n3", "flow", "否")]
    elif kind == "kanban":
        groups = [{"id": f"lane{i}", "label": label, "kind": "boundary", "x": 45 + i * 305, "y": 140, "w": 270, "h": 440, "color": COLORS[i]} for i, label in enumerate(labels)]
        nodes = [N(slug, 0, "任务卡 A", 80, 220, 200, 70, "blue", "sticky"), N(slug, 1, "任务卡 B", 385, 300, 200, 70, "teal", "sticky"), N(slug, 2, "任务卡 C", 690, 210, 200, 70, "amber", "sticky"), N(slug, 3, "任务卡 D", 995, 400, 200, 70, "violet", "sticky")]
        annotations = [{"x": 370, "y": 545, "text": "WIP ≤ 2", "color": "#b42318", "fontSize": 18}]
    elif kind == "bpmn":
        groups = [{"id": "pool", "label": "CS-1 任务池", "kind": "boundary", "x": 45, "y": 145, "w": 1190, "h": 430, "color": "blue"}]
        nodes = [N(slug, 0, "开始", 80, 290, 45, 45, "teal", "initial"), N(slug, 1, labels[1], 230, 275, 230, 85, "teal", "action"), N(slug, 2, labels[2], 550, 270, 160, 95, "amber", "decision"), N(slug, 3, labels[3], 840, 275, 240, 85, "violet", "action"), N(slug, 4, "结束", 1140, 290, 45, 45, "red", "final")]
        edges = CHAIN(5, "flow", [None, None, "链路可用", None])
    elif kind == "archimate":
        names = ["业务层", "应用层", "技术层"]
        groups = [{"id": f"layer{i}", "label": name, "kind": "boundary", "x": 100, "y": 130 + i * 165, "w": 1080, "h": 135, "color": COLORS[i]} for i, name in enumerate(names)]
        nodes = [N(slug, 0, labels[0], 430, 160, 420, 70, "amber"), N(slug, 1, labels[1], 430, 325, 420, 70, "teal"), N(slug, 2, f"{labels[2]} + {labels[3]}", 430, 490, 420, 70, "blue", "node3d")]
        edges = [E("n0", "n1", "dependency", "realizes"), E("n1", "n2", "dependency", "hosted by")]
    elif kind == "cicd":
        nodes, edges, matrix = DELIVERY(slug, labels)
        annotations = [{"x": 70, "y": 520, "text": "质量关口：tests / signature / approval"}]
    elif kind == "deployment-topology":
        groups = [{"id": "rf", "label": labels[1], "kind": "boundary", "x": 330, "y": 160, "w": 580, "h": 360, "color": "violet"}, {"id": "ground-zone", "label": "地面网络区", "kind": "boundary", "x": 950, "y": 160, "w": 260, "h": 360, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 70, 280, 210, 100, "blue", "node3d"), N(slug, 1, labels[1], 480, 190, 250, 70, "violet", "node3d"), N(slug, 2, labels[2], 465, 355, 260, 100, "teal", "node3d"), N(slug, 3, labels[3], 965, 280, 220, 100, "gray", "node3d")]
        edges = CHAIN(4, "flow", ["RF", "Ethernet", "HTTPS"])
    elif kind == "flame-graph":
        nodes = [N(slug, 0, labels[0], 150, 450, 900, 70, "blue", "flame", "100% total"), N(slug, 1, labels[1], 250, 350, 700, 70, "teal", "flame", "70% layout"), N(slug, 2, labels[2], 350, 250, 500, 70, "amber", "flame", "45% routing"), N(slug, 3, labels[3], 450, 150, 300, 70, "violet", "flame", "25% text")]
    elif kind == "call-graph":
        nodes, edges = FLOW(slug, labels, "component", ["calls", "builds", "renders"])
    elif kind == "story-map":
        groups = [{"id": "release1", "label": "Release 1 · 最小任务", "kind": "boundary", "x": 70, "y": 260, "w": 1140, "h": 135, "color": "teal"}, {"id": "release2", "label": "Release 2 · 完整分析", "kind": "boundary", "x": 70, "y": 425, "w": 1140, "h": 135, "color": "violet"}]
        nodes = [N(slug, i, label, 90 + i * 295, 145, 250, 75, COLORS[i], "sticky") for i, label in enumerate(labels)]
        nodes += [N(slug, 4, "故事 A", 110, 295, 190, 65, "teal", "sticky"), N(slug, 5, "故事 B", 405, 295, 190, 65, "teal", "sticky"), N(slug, 6, "故事 C", 405, 460, 190, 65, "violet", "sticky"), N(slug, 7, "故事 D", 995, 460, 190, 65, "violet", "sticky")]
    elif kind == "ddd-context-map":
        groups = [{"id": "mission", "label": labels[0], "kind": "boundary", "x": 80, "y": 160, "w": 480, "h": 360, "color": "blue"}, {"id": "telemetry", "label": labels[1], "kind": "boundary", "x": 720, "y": 160, "w": 480, "h": 360, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 190, 280, 260, 90), N(slug, 1, labels[1], 830, 280, 260, 90, "teal"), N(slug, 2, labels[2], 480, 430, 320, 75, "violet"), N(slug, 3, labels[3], 830, 190, 260, 65, "gray")]
        edges = [E("n0", "n1", "dependency", "ACL / 发布订阅"), E("n2", "n1", "dependency", "读取")]
    elif kind == "dmn":
        nodes, matrix = MATRIX(slug, labels, kind)
        matrices = [matrix]
    elif kind == "er":
        nodes = [N(slug, 0, labels[0], 70, 275, 230, 95), N(slug, 1, labels[1], 525, 275, 230, 95, "teal"), N(slug, 2, labels[2], 890, 275, 230, 95, "violet"), N(slug, 3, "owns / records", 340, 290, 150, 80, "amber", "decision"), N(slug, 4, "timestamp / values", 490, 130, 280, 75, "gray", "usecase")]
        edges = [E("n0", "n3", "association", "1"), E("n3", "n1", "association", "N"), E("n1", "n2", "association", "1 : N"), E("n4", "n1", "dependency", "attributes")]
    elif kind == "c4-context":
        nodes, edges, groups = CONTEXT(slug, labels, True)
    elif kind == "c4-container":
        groups = [{"id": "system", "label": "CS-1 软件系统", "kind": "boundary", "x": 70, "y": 145, "w": 1140, "h": 420, "color": "blue"}]
        nodes = [N(slug, i, label, 95 + i * 295, 280, 250, 105, COLORS[i], "component", "deployable container") for i, label in enumerate(labels)]
        edges = CHAIN(4, "flow", ["UART", "433 MHz", "SQL / files"])
    elif kind == "delivery":
        nodes, edges, matrix = DELIVERY(slug, labels)
        matrices = [matrix]
        annotations = [{"x": 70, "y": 435, "text": "交付映射：版本、存放位置、运行目标"}]
    elif kind == "sysml-v2":
        nodes, edges = TREE(slug, labels, "dependency")
    elif kind == "context":
        nodes, edges, groups = CONTEXT(slug, labels, True)
    elif kind == "use-case":
        nodes, edges, groups = CONTEXT(slug, labels, True)
    elif kind == "package":
        nodes, edges = TREE(slug, labels, "dependency", "package")
    elif kind in {"activity", "state-machine", "sequence"}:
        nodes, edges = FLOW(slug, labels)
    else:
        nodes, edges = FLOW(slug, labels)
    return nodes, edges, groups, matrices, charts, timelines, annotations


def build_layout(entry):
    nodes, edges, groups, matrices, charts, timelines, annotations = layout(entry)
    return {
        "schema": "diagram-view/v1", "type": entry["type"],
        "intent": {"question": QUESTIONS[entry["type"]]}, "sources": [{"kind": "semantic", "example": entry["slug"]}],
        "selection": {"layout": entry["type"], "nodes": nodes, "edges": edges, "groups": groups, "matrices": matrices, "charts": charts, "timelines": timelines, "qfd": QFD_MODEL if entry["type"] == "qfd" else None, "gantt": GANTT_MODEL if entry["type"] == "gantt" else None, "faultTree": FTA_MODEL if entry["type"] == "fta" else None, "annotations": annotations},
        "presentation": {"title": f"CanSat CS-1｜{entry['title']}", "subtitle": "dgraph · engineering diagram", "theme": "dgraph"},
        "outputs": {"directory": "/absolute/output", "formats": ["viewspec", "dsl", "svg", "report"]},
    }
