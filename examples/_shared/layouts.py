"""Diagram-specific semantic layouts with independent dgraph identities."""

from dgraph.catalog import CATALOG
from examples._shared.domain_examples import BPMN_MODEL, C4_CONTAINER_MODEL, DFD_MODEL, FTA_MODEL, GANTT_MODEL, N2_MODEL, QFD_MODEL, SEQUENCE_MODEL, UML_CLASS_MODEL, RISK_MATRIX_MODEL, DMN_MODEL, TIMING_MODEL, TRADESPACE_MODEL, PERT_MODEL


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
        nodes = [N(slug, 0, "执行探空任务", 480, 285, 300, 100, "teal", "usecase"), N(slug, 1, "探空仪\n待机 / 运行", 65, 145, 240, 85), N(slug, 2, "科学数据\n未采集 / 完整", 950, 145, 240, 85), N(slug, 3, "电池能量\n充足 / 耗尽", 65, 470, 240, 85, "amber"), N(slug, 4, "地面站\n空闲 / 接收", 950, 470, 240, 85, "violet"), N(slug, 5, "操作员\n待命 / 监控", 480, 115, 300, 85, "gray", "actor")]
        edges = [E("n1", "n0", "flow", "执行"), E("n0", "n2", "flow", "产生"), E("n3", "n0", "flow", "消耗"), E("n0", "n4", "flow", "影响"), E("n5", "n0", "association", "操作")]
    elif kind == "c4":
        groups = [{"id": "context", "label": labels[0], "kind": "boundary", "x": 80, "y": 130, "w": 1120, "h": 470, "color": "gray"}, {"id": "container", "label": labels[1], "kind": "boundary", "x": 160, "y": 200, "w": 960, "h": 360, "color": "blue"}, {"id": "component", "label": labels[2], "kind": "boundary", "x": 250, "y": 275, "w": 780, "h": 240, "color": "teal"}]
        nodes = [N(slug, 0, labels[3], 480, 355, 320, 90, "violet", "class", "fields + methods")]
        annotations = [{"x": 285, "y": 585, "text": "逐层缩放：系统 → 容器 → 组件 → 代码"}]
    elif kind == "ffbd":
        nodes = [N(slug, 0, "准备 / 自检", 35, 310, 170, 70), N(slug, 1, "释放 / 投放", 235, 310, 170, 70), N(slug, 2, "AND", 440, 230, 12, 245, "gray", "parallel"), N(slug, 3, "采集温压湿 ≥1 Hz", 500, 210, 210, 70, "teal"), N(slug, 4, "采集姿态 / 位置", 500, 320, 210, 70, "teal"), N(slug, 5, "下传遥测 I-04", 500, 430, 210, 70, "teal"), N(slug, 6, "AND", 765, 230, 12, 245, "gray", "parallel"), N(slug, 7, "着陆 / 回收", 820, 310, 170, 70, "violet"), N(slug, 8, "分析 / 回放", 1030, 310, 180, 70, "violet")]
        edges = [E("n0", "n1"), E("n1", "n2")] + [E("n2", f"n{i}") for i in (3, 4, 5)] + [E(f"n{i}", "n6") for i in (3, 4, 5)] + [E("n6", "n7"), E("n7", "n8")]
        for index, y in enumerate((245, 355, 465)):
            edges[2 + index]["points"] = [[452, y], [500, y]]
            edges[5 + index]["points"] = [[710, y], [765, y]]
        edges.append(E("n0", "n0", "flow", "自检不通过：重新准备", "amber", points=[[120, 310], [120, 190], [20, 190], [20, 345], [35, 345]], label_position=[35, 165]))
        annotations = [{"x": 480, "y": 570, "text": "AND 并行支路全部汇合后进入着陆与回收"}]
    elif kind == "n2":
        nodes, matrix = MATRIX(slug, labels, kind)
        matrices = [matrix]
    elif kind == "idef0":
        nodes = [N(slug, 0, labels[0], 45, 290, 220, 90, "gray"), N(slug, 1, labels[1], 500, 290, 280, 100, "teal"), N(slug, 2, labels[2], 500, 135, 280, 80, "amber"), N(slug, 3, labels[3], 500, 480, 280, 80), N(slug, 4, "遥测数据", 1000, 290, 220, 90, "violet")]
        edges = [E("n0", "n1", "flow", "input"), E("n2", "n1", "dependency", "control"), E("n3", "n1", "association", "mechanism"), E("n1", "n4", "flow", "output")]
    elif kind == "dfd":
        pass  # The dedicated model is the single source of diagram semantics.
    elif kind == "qfd":
        nodes, matrix = MATRIX(slug, labels, kind)
    elif kind == "tradespace":
        pass  # Dedicated tradespaceModel renders axes, alternatives and Pareto front.
    elif kind == "fta":
        nodes = [N(slug, 0, labels[0], 500, 125, 280, 75, "red"), N(slug, 1, "OR", 565, 235, 150, 65, "amber", "gate"), N(slug, 2, labels[1], 280, 390, 250, 85, "red"), N(slug, 3, labels[2], 750, 390, 250, 85, "red"), N(slug, 4, "AND", 815, 505, 120, 60, "amber", "gate"), N(slug, 5, labels[3], 770, 590, 210, 55, "gray")]
        edges = [E("n0", "n1", "flow", None, "red"), E("n1", "n2", "flow", None, "red"), E("n1", "n3", "flow", None, "red"), E("n3", "n4", "flow", None, "red"), E("n4", "n5", "flow", None, "red")]
    elif kind == "cld":
        names = ["采样率", "数据量", "功耗", "电池质量", "总质量", "下降速度", "振动", "误码率", "重传", "剩余能量"]
        positions = [(70,150),(300,150),(530,150),(760,150),(990,150),(990,370),(760,370),(530,370),(300,370),(70,370)]
        nodes = [N(slug, i, name, x, y, 170, 65, COLORS[i % 5]) for i, (name, (x, y)) in enumerate(zip(names, positions))]
        edges = [E("n0","n1","flow","+"), E("n1","n2","flow","+"), E("n2","n3","flow","+"), E("n3","n4","flow","+"), E("n4","n5","flow","+"), E("n5","n6","flow","+"), E("n6","n7","flow","+"), E("n7","n8","flow","+"), E("n8","n2","flow","+", points=[[385,370],[385,290],[615,290],[615,215]]), E("n2","n9","flow","−", points=[[615,215],[615,530],[155,530],[155,435]]), E("n9","n0","flow","+", points=[[155,370],[155,215]])]
        annotations = [{"x": 450, "y": 580, "text": "R：重传增加功耗；B：剩余能量降低触发降采样"}]
    elif kind == "sfd":
        nodes = [N(slug, 0, "电池能量 E\nWh · 存量", 325, 280, 270, 100, "blue", "stock"), N(slug, 1, "放电 P_avg ≤ 2.0 W", 760, 295, 70, 70, "amber", "valve"), N(slug, 2, "热耗散", 1040, 295, 170, 70, "gray"), N(slug, 3, "安全模式\n降低采样与功率", 490, 480, 270, 85, "red")]
        edges = [E("n0","n1","flow","能量流"), E("n1","n2","flow"), E("n0","n3","dependency","电压 < 6.4 V"), E("n3","n1","dependency","控制放电功率")]
        annotations = [{"x": 90, "y": 600, "text": "dE/dt = −P_avg；安全模式降低消耗（教学示意）"}]
    elif kind == "dodaf":
        names = [("AV 全视点", "AV-1 概述"), ("CV 能力", "CV-2 能力分类"), ("OV 运行", "OV-1 运行概念"), ("SV 系统", "SV-1 系统接口"), ("SvcV 服务", "SvcV-1 服务描述"), ("DIV 数据", "DIV-1 概念数据模型"), ("StdV 标准", "StdV-1 标准概览"), ("PV 项目", "PV-1 项目关联")]
        nodes = [N(slug, i, f"{view}\n{example}", 80 + (i % 4) * 300, 180 + (i // 4) * 185, 260, 110, COLORS[i % 5]) for i, (view, example) in enumerate(names)]
        annotations = [{"x": 260, "y": 600, "text": "同一架构模型的八类视点：先确定关注问题，再选择视图"}]
    elif kind == "ov1":
        nodes = [N(slug, 0, "发射操作员", 60, 185, 200, 80, "gray", "actor"), N(slug, 1, "CS-1 探空仪", 410, 185, 250, 90), N(slug, 2, "地面站", 820, 185, 230, 90, "teal"), N(slug, 3, "回收人员", 410, 450, 250, 80, "gray", "actor"), N(slug, 4, "科学用户", 820, 450, 230, 80, "violet", "actor")]
        edges = [E("n0","n1","flow","投放"), E("n1","n2","flow","433 MHz 遥测"), E("n1","n3","flow","回收"), E("n3","n4","flow","回放数据"), E("n2","n4","flow","数据产品")]
        annotations = [{"x": 70, "y": 590, "text": "任务阶段：投放 → 下降采集 → 下传 → 回收回放；不展开内部结构"}]
    elif kind == "sv1":
        nodes, edges = FLOW(slug, labels, "part", ["I-02", "I-03", "I-04"])
        annotations = [{"x": 70, "y": 560, "text": "SV-1：系统资源与接口，而非项目流程"}]
    elif kind == "cv2":
        nodes, edges = TREE(slug, labels)
    elif kind == "arcadia":
        names = labels[:3] + ["PAB 物理架构", "EPBS 实现分解"]
        nodes = [N(slug, i, label, 70 + i * 245, 285, 220, 105, COLORS[i]) for i, label in enumerate(names)]
        edges = CHAIN(5, "dependency", ["分析", "分配", "细化", "实现"])
    elif kind == "wbs":
        nodes = [N(slug, 0, "CS-1 研制项目", 500, 120, 280, 75, "violet")]
        branches = [("1.1 需求分析", "1.1.1 任务书", "1.1.2 需求基线"), ("1.2 设计", "1.2.1 架构设计", "1.2.2 详细设计"), ("1.3 采购制造", "1.3.1 器材采购", "1.3.2 结构加工"), ("1.4 集成", "1.4.1 系统集成", "1.4.2 总装联调"), ("1.5 试验评审", "1.5.1 环境试验", "1.5.2 飞行试验")]
        edges = []
        for i, (parent, first, second) in enumerate(branches):
            x = 25 + i * 250
            nodes.extend([N(slug, i+1, parent, x, 290, 220, 70, COLORS[i]), N(slug, i+6, first, x, 420, 220, 60, COLORS[i]), N(slug, i+11, second, x, 515, 220, 60, COLORS[i])])
            edges += [E("n0", f"n{i+1}", "association"), E(f"n{i+1}", f"n{i+6}", "association"), E(f"n{i+1}", f"n{i+11}", "association", points=[[x+215,360],[x+235,360],[x+235,545],[x+220,545]])]
        annotations = [{"x": 350, "y": 635, "text": "叶子工作包可估算、分配和验收；WBS 分解工作而非产品"}]
    elif kind == "class-hierarchy":
        nodes = [N(slug, 0, "«abstract» Frame", 500, 145, 260, 80, "gray", "class"), N(slug, 1, "TelemetryFrame", 200, 360, 240, 90, "blue", "class"), N(slug, 2, "HousekeepingFrame", 510, 360, 240, 90, "teal", "class"), N(slug, 3, "SensorReading", 200, 510, 240, 90, "violet", "class")]
        edges = [E(f"n{i}", "n0", "generalization") for i in (1, 2)] + [E("n1", "n3", "composition", "1..*", label_position=[365, 480])]
        annotations = [{"x": 480, "y": 620, "text": "空心三角指向父类；子类继承 Frame 的共同语义"}]
    elif kind == "pbs":
        nodes = [N(slug, 0, "CS-1 探空仪", 490, 130, 300, 80)]
        for i, name in enumerate(["结构与回收", "电源", "飞控", "传感器", "通信"], 1):
            nodes.append(N(slug, i, name, 40 + (i - 1) * 240, 345, 200, 90, COLORS[(i - 1) % 5]))
        edges = [E("n0", f"n{i}", "composition") for i in range(1, 6)]
        annotations = [{"x": 90, "y": 565, "text": "地面站是外部系统，不属于 CS-1 产品分解"}]
    elif kind == "profile":
        nodes = [N(slug, 0, "«metaclass» Class", 240, 170, 260, 80, "gray", "class"), N(slug, 1, "«metaclass» Property", 780, 170, 260, 80, "gray", "class"), N(slug, 2, "«stereotype» sensor", 240, 385, 260, 80, "violet", "class"), N(slug, 3, "«stereotype» telemetry", 780, 385, 260, 80, "violet", "class")]
        edges = [E("n2", "n0", "extension", "«extension»"), E("n3", "n1", "extension", "«extension»")]
        annotations = [{"x": 380, "y": 570, "text": "构造型扩展元类；可用于标注领域语义"}]
    elif kind == "gantt":
        nodes, timeline = TIMELINE(slug, labels)
        timelines = [timeline]
    elif kind == "pert":
        pass  # Dedicated pertModel computes dependencies and critical path.
    elif kind == "risk-matrix":
        pass
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
        nodes = [N(slug, 0, "gs.ui", 100, 290, 230, 100, "blue", "component"), N(slug, 1, "gs.telemetry", 520, 290, 230, 100, "teal", "component"), N(slug, 2, "gs.storage", 950, 290, 230, 100, "violet", "component"), N(slug, 3, "", 385, 325, 24, 24, "blue", "required-interface"), N(slug, 4, "", 410, 325, 24, 24, "teal", "provided-interface"), N(slug, 5, "", 810, 325, 24, 24, "teal", "required-interface"), N(slug, 6, "", 835, 325, 24, 24, "violet", "provided-interface")]
        edges = [E("n0", "n3", "connection"), E("n4", "n1", "connection"), E("n1", "n5", "connection"), E("n6", "n2", "connection")]
        annotations = [{"x": 230, "y": 570, "text": "ITelemetry                                  IFrameStore · 棒棒糖为提供接口，插座为需要接口"}]
    elif kind == "composite-structure":
        groups = [{"id": "ground", "label": "«component» GroundStation", "kind": "boundary", "x": 100, "y": 130, "w": 1080, "h": 420, "color": "blue"}]
        nodes = [N(slug, 0, "ui : UI", 210, 275, 230, 90, "blue", "part"), N(slug, 1, "mission : MissionManager", 525, 275, 230, 90, "teal", "part"), N(slug, 2, "radio : RadioGateway", 840, 275, 230, 90, "violet", "part"), N(slug, 3, "pUser", 90, 305, 20, 20, "blue", "port"), N(slug, 4, "pRf", 1170, 305, 20, 20, "violet", "port")]
        edges = [E("n3","n0","connection"), E("n0","n1","connection"), E("n1","n2","connection"), E("n2","n4","connection")]
        annotations = [{"x": 300, "y": 600, "text": "part 是运行时实例；port 是可见交互点；connector 连接部件"}]
    elif kind == "deployment":
        groups = [{"id": "device", "label": labels[1], "kind": "boundary", "x": 120, "y": 160, "w": 460, "h": 360, "color": "blue"}, {"id": "ground", "label": labels[3], "kind": "boundary", "x": 720, "y": 160, "w": 430, "h": 360, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 200, 280, 280, 100, "amber", "artifact"), N(slug, 1, labels[1], 150, 205, 170, 70, "blue", "node3d"), N(slug, 2, labels[2], 790, 280, 280, 100, "violet", "artifact"), N(slug, 3, labels[3], 850, 205, 170, 70, "teal", "node3d")]
        edges = [E("n0", "n2", "flow", "deploys / runs")]
    elif kind == "communication":
        nodes = [N(slug, 0, labels[0], 120, 180, 220, 90, "teal", "object"), N(slug, 1, labels[1], 500, 150, 220, 90, "blue", "object"), N(slug, 2, labels[2], 860, 220, 220, 90, "violet", "object"), N(slug, 3, labels[3], 500, 450, 220, 90, "gray", "object")]
        edges = [E("n1", "n0", "message", "1: read"), E("n0", "n1", "return", "2: data"), E("n1", "n2", "message", "3: frame"), E("n2", "n3", "message", "4: downlink")]
    elif kind == "interaction-overview":
        groups = [{"id": "normal", "label": "ref", "kind": "boundary", "x": 250, "y": 170, "w": 270, "h": 130, "color": "teal"}, {"id": "retry", "label": "ref", "kind": "boundary", "x": 760, "y": 370, "w": 220, "h": 120, "color": "amber"}, {"id": "failure", "label": "ref", "kind": "boundary", "x": 1025, "y": 370, "w": 200, "h": 120, "color": "red"}]
        nodes = [N(slug, 0, "帧到达", 45, 215, 170, 65), N(slug, 1, "正常接收帧", 275, 215, 220, 55, "teal"), N(slug, 2, "CRC 合格？", 570, 205, 140, 80, "amber", "decision"), N(slug, 3, "完成", 1030, 215, 170, 65, "teal"), N(slug, 4, "丢包重试", 775, 405, 190, 55, "amber"), N(slug, 5, "失败处理", 1040, 405, 170, 55, "red")]
        edges = [E("n0","n1"), E("n1","n2"), E("n2","n3","flow","是", label_position=[855,190]), E("n2","n4","flow","否", points=[[640,285],[640,435],[775,435]], label_position=[655,320]), E("n4","n5","flow","重试失败", label_position=[965,350])]
        annotations = [{"x": 340, "y": 580, "text": "活动控制流串接交互引用；每个 ref 可展开为序列图"}]
    elif kind == "timing":
        pass
    elif kind == "event-storming":
        roles = ["操作员", "遥测服务", "科学用户"]
        commands = ["创建任务", "接收帧", "生成报告"]
        events = ["任务已创建", "帧已收录", "报告已生成"]
        aggregates = ["Mission 聚合", "TelemetryFrame 聚合", "回收看板 · 读模型"]
        nodes = []
        for i in range(3):
            x = 85 + i * 395
            nodes += [N(slug, i, roles[i], x, 145, 230, 60, "gray", "sticky"), N(slug, i+3, commands[i], x, 245, 230, 65, "blue", "sticky"), N(slug, i+6, events[i], x, 365, 230, 65, "amber", "sticky"), N(slug, i+9, aggregates[i], x, 485, 230, 65, "violet", "sticky")]
        edges = [E(f"n{i}", f"n{i+3}", "flow") for i in range(3)] + [E(f"n{i+3}", f"n{i+6}", "flow") for i in range(3)] + [E(f"n{i+6}", f"n{i+9}", "flow") for i in range(3)] + [E("n6","n7","dependency","时间 →"), E("n7","n8","dependency","时间 →")]
        annotations = [{"x": 420, "y": 620, "text": "角色 → 命令 → 领域事件 → 聚合 / 读模型；横向表示时间"}]
    elif kind == "impact-map":
        nodes, edges = FLOW(slug, labels, "block", ["Why", "Who", "How"])
    elif kind == "module-dependency":
        nodes = [N(slug, 0, "gs.ui\n页面 / 交互", 430, 160, 420, 90, "blue", "package"), N(slug, 1, "gs.core\n领域模型 / 用例服务", 430, 325, 420, 90, "teal", "package"), N(slug, 2, "gs.io\n电台驱动 / 存储适配", 430, 490, 420, 90, "violet", "package")]
        edges = [E("n0", "n1", "dependency", "依赖"), E("n2", "n1", "dependency", "实现接口")]
        annotations = [{"x": 65, "y": 620, "text": "依赖方向指向领域；禁止领域层反向依赖界面或基础设施"}]
    elif kind == "eta":
        nodes = [N(slug, 0, "遥测中断", 40, 290, 180, 75, "amber"), N(slug, 1, "重传成功？", 275, 290, 150, 75, "violet", "decision"), N(slug, 2, "数据可恢复\nP = 0.80", 505, 130, 205, 75, "teal"), N(slug, 3, "降级成功？", 505, 360, 150, 75, "violet", "decision"), N(slug, 4, "任务降级\nP = 0.10", 760, 250, 210, 75, "amber"), N(slug, 5, "回收成功？", 760, 450, 150, 75, "violet", "decision"), N(slug, 6, "数据部分保留\nP = 0.06", 1020, 390, 220, 75, "amber"), N(slug, 7, "任务失败\nP = 0.04", 1020, 520, 220, 75, "red")]
        edges = [E("n0","n1"), E("n1","n2","flow","成功 0.80"), E("n1","n3","flow","失败 0.20"), E("n3","n4","flow","成功 0.50"), E("n3","n5","flow","失败 0.50"), E("n5","n6","flow","成功 0.60"), E("n5","n7","flow","失败 0.40")]
        annotations = [{"x": 60, "y": 625, "text": "各出口概率为沿途分支概率乘积；各后果合计为 1（教学示意）"}]
    elif kind == "kanban":
        groups = [{"id": f"lane{i}", "label": label, "kind": "boundary", "x": 45 + i * 305, "y": 140, "w": 270, "h": 440, "color": COLORS[i]} for i, label in enumerate(labels)]
        nodes = [N(slug, 0, "任务卡 A", 80, 220, 200, 70, "blue", "sticky"), N(slug, 1, "任务卡 B", 385, 300, 200, 70, "teal", "sticky"), N(slug, 2, "任务卡 C", 690, 210, 200, 70, "amber", "sticky"), N(slug, 3, "任务卡 D", 995, 400, 200, 70, "violet", "sticky")]
        annotations = [{"x": 370, "y": 545, "text": "WIP ≤ 2", "color": "#b42318", "fontSize": 18}]
    elif kind == "bpmn":
        pass  # The dedicated model is the single source of diagram semantics.
    elif kind == "archimate":
        names = ["业务层", "应用层", "技术层"]
        groups = [{"id": f"layer{i}", "label": name, "kind": "boundary", "x": 100, "y": 130 + i * 165, "w": 1080, "h": 135, "color": COLORS[i]} for i, name in enumerate(names)]
        nodes = [N(slug, 0, labels[0], 430, 160, 420, 70, "amber"), N(slug, 1, labels[1], 430, 325, 420, 70, "teal"), N(slug, 2, f"{labels[2]} + {labels[3]}", 430, 490, 420, 70, "blue", "node3d")]
        edges = [E("n0", "n1", "dependency", "realizes"), E("n1", "n2", "dependency", "hosted by")]
    elif kind == "cicd":
        names = ["提交\ngit push", "构建\n编译 / 单测", "测试\n覆盖率", "镜像\n版本化制品", "部署\n灰度发布"]
        nodes = [N(slug, i, name, 35 + i * 245, 240, 195, 90, COLORS[i]) for i, name in enumerate(names)]
        nodes += [N(slug, 5, "测试失败\n阻断合并", 525, 435, 195, 80, "red"), N(slug, 6, "部署失败\n回滚上一版", 1015, 435, 195, 80, "red")]
        edges = CHAIN(5, "flow", ["触发", "验证", "通过", "审批"])
        edges += [E("n2","n5","flow","失败", "red"), E("n4","n6","flow","失败", "red")]
        annotations = [{"x": 320, "y": 585, "text": "质量门禁失败阻断合并；部署失败切回上一版，修复后重试"}]
    elif kind == "deployment-topology":
        groups = [{"id": "rf", "label": labels[1], "kind": "boundary", "x": 330, "y": 160, "w": 580, "h": 360, "color": "violet"}, {"id": "ground-zone", "label": "地面网络区", "kind": "boundary", "x": 950, "y": 160, "w": 260, "h": 360, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 70, 280, 210, 100, "blue", "node3d"), N(slug, 1, labels[1], 480, 190, 250, 70, "violet", "node3d"), N(slug, 2, labels[2], 465, 355, 260, 100, "teal", "node3d"), N(slug, 3, labels[3], 965, 280, 220, 100, "gray", "node3d")]
        edges = CHAIN(4, "flow", ["RF", "Ethernet", "HTTPS"])
    elif kind == "flame-graph":
        nodes = [N(slug, 0, "decode_loop 100%", 120, 470, 1040, 65, "blue", "flame"), N(slug, 1, "radio_read 20%", 120, 385, 208, 65, "gray", "flame"), N(slug, 2, "decode_frame 62%", 328, 385, 645, 65, "teal", "flame"), N(slug, 3, "store_batch 18%", 973, 385, 187, 65, "violet", "flame"), N(slug, 4, "crc16 32%", 328, 300, 333, 65, "amber", "flame"), N(slug, 5, "parse_fields 20%", 661, 300, 208, 65, "blue", "flame"), N(slug, 6, "filter 10%", 869, 300, 104, 65, "teal", "flame")]
        annotations = [{"x": 125, "y": 575, "text": "示例采样占比；块宽表示耗时比例，栈由下向上展开"}]
    elif kind == "call-graph":
        nodes = [N(slug, 0, "main()", 500, 150, 220, 70), N(slug, 1, "radio_read()", 100, 310, 230, 70, "gray"), N(slug, 2, "decode_frame()", 510, 310, 230, 70, "teal"), N(slug, 3, "store_batch()", 925, 310, 230, 70, "violet"), N(slug, 4, "crc16()", 350, 500, 230, 70, "amber"), N(slug, 5, "parse_fields()", 700, 500, 230, 70, "blue")]
        edges = [E("n0", "n1", "flow", "×1200"), E("n0", "n2", "flow", "×1200"), E("n0", "n3", "flow", "×50"), E("n2", "n4", "flow", "×1200"), E("n2", "n5", "flow", "×1200")]
        annotations = [{"x": 80, "y": 625, "text": "调用次数为教学示例，并非实测插桩统计"}]
    elif kind == "story-map":
        groups = [{"id": "release1", "label": "Release 1 · 最小任务", "kind": "boundary", "x": 70, "y": 260, "w": 1140, "h": 135, "color": "teal"}, {"id": "release2", "label": "Release 2 · 完整分析", "kind": "boundary", "x": 70, "y": 425, "w": 1140, "h": 135, "color": "violet"}]
        nodes = [N(slug, i, label, 90 + i * 295, 145, 250, 75, COLORS[i], "sticky") for i, label in enumerate(labels)]
        names = ["配置站点", "看实时遥测", "导入存储帧", "画曲线", "多站点模板", "异常告警", "异常帧回放", "导出报告"]
        nodes += [N(slug, i + 4, name, 110 + (i % 4) * 295, 295 if i < 4 else 460, 190, 65, "teal" if i < 4 else "violet", "sticky") for i, name in enumerate(names)]
    elif kind == "ddd-context-map":
        groups = [{"id": "mission", "label": labels[0], "kind": "boundary", "x": 80, "y": 160, "w": 480, "h": 360, "color": "blue"}, {"id": "telemetry", "label": labels[1], "kind": "boundary", "x": 720, "y": 160, "w": 480, "h": 360, "color": "teal"}]
        nodes = [N(slug, 0, labels[0], 190, 280, 260, 90), N(slug, 1, labels[1], 830, 280, 260, 90, "teal"), N(slug, 2, labels[2], 480, 430, 320, 75, "violet"), N(slug, 3, labels[3], 830, 190, 260, 65, "gray")]
        edges = [E("n0", "n1", "dependency", "ACL / 发布订阅"), E("n2", "n1", "dependency", "读取")]
    elif kind == "dmn":
        pass
    elif kind == "er":
        nodes = [N(slug, 0, labels[0], 70, 275, 230, 95), N(slug, 1, labels[1], 525, 275, 230, 95, "teal"), N(slug, 2, labels[2], 890, 275, 230, 95, "violet"), N(slug, 3, "owns / records", 340, 290, 150, 80, "amber", "decision"), N(slug, 4, "timestamp / values", 490, 130, 280, 75, "gray", "usecase")]
        edges = [E("n0", "n3", "association", "1"), E("n3", "n1", "association", "N"), E("n1", "n2", "association", "1 : N"), E("n4", "n1", "dependency", "attributes")]
    elif kind == "c4-context":
        groups = [{"id": "system", "label": "地面站软件系统边界", "kind": "boundary", "x": 385, "y": 160, "w": 500, "h": 350, "color": "blue"}]
        nodes = [N(slug, 0, "操作员", 70, 200, 200, 80, "gray", "actor"), N(slug, 1, "科学用户", 70, 425, 200, 80, "gray", "actor"), N(slug, 2, "地面站软件\n遥测接收 · 数据查看", 485, 280, 300, 100, "blue"), N(slug, 3, "CS-1 探空仪\n外部系统", 1000, 280, 220, 100, "teal")]
        edges = [E("n0","n2","flow","操作 / 监视"), E("n1","n2","flow","查看数据"), E("n3","n2","flow","I-04 · 433 MHz")]
    elif kind == "c4-container":
        pass  # The dedicated model is the single source of diagram semantics.
    elif kind == "delivery":
        nodes, edges, matrix = DELIVERY(slug, labels)
        matrices = [matrix]
        annotations = [{"x": 70, "y": 435, "text": "交付映射：版本、存放位置、运行目标"}]
    elif kind == "sysml-v2":
        nodes, edges = TREE(slug, labels, "dependency")
    elif kind == "context":
        nodes = [N(slug, 0, "CS-1 探空仪\n黑盒系统", 495, 275, 290, 110), N(slug, 1, "发射装置", 70, 150, 200, 75, "gray"), N(slug, 2, "环境", 70, 420, 200, 75, "gray"), N(slug, 3, "地面站", 1010, 150, 200, 75, "teal"), N(slug, 4, "空域管理", 1010, 420, 200, 75, "gray", "actor"), N(slug, 5, "科学用户", 510, 535, 250, 75, "violet", "actor")]
        edges = [E("n1","n0","flow","机械释放"), E("n2","n0","flow","环境扰动"), E("n0","n3","flow","I-04 遥测下行"), E("n4","n0","dependency","空域约束"), E("n0","n5","flow","回收后回放")]
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
        "selection": {"layout": entry["type"], "nodes": nodes, "edges": edges, "groups": groups, "matrices": matrices, "charts": charts, "timelines": timelines, "qfd": QFD_MODEL if entry["type"] == "qfd" else None, "gantt": GANTT_MODEL if entry["type"] == "gantt" else None, "faultTree": FTA_MODEL if entry["type"] == "fta" else None, "c4Container": C4_CONTAINER_MODEL if entry["type"] == "c4-container" else None, "umlClass": UML_CLASS_MODEL if entry["type"] == "class" else None, "sequenceModel": SEQUENCE_MODEL if entry["type"] == "sequence" else None, "n2Model": N2_MODEL if entry["type"] == "n2" else None, "dfdModel": DFD_MODEL if entry["type"] == "dfd" else None, "bpmnModel": BPMN_MODEL if entry["type"] == "bpmn" else None, "riskMatrix": RISK_MATRIX_MODEL if entry["type"] == "risk-matrix" else None, "dmnModel": DMN_MODEL if entry["type"] == "dmn" else None, "timingModel": TIMING_MODEL if entry["type"] == "timing" else None, "tradespaceModel": TRADESPACE_MODEL if entry["type"] == "tradespace" else None, "pertModel": PERT_MODEL if entry["type"] == "pert" else None, "annotations": annotations},
        "presentation": {"title": f"CanSat CS-1｜{entry['title']}", "subtitle": "dgraph · engineering diagram", "theme": "dgraph"},
        "outputs": {"directory": "/absolute/output", "formats": ["viewspec", "dsl", "svg", "report"]},
    }
