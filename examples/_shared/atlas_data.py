"""Lesson_2 remaining-figure catalog and representative CanSat ViewSpecs."""

from dgraph.catalog import CATALOG


def E(slug, kind, title, labels, template="flow"):
    return {"slug": slug, "type": kind, "title": title, "labels": labels, "template": template}


ATLAS_ENTRIES = [
    E("sysml-v2", "sysml-v2", "SysML v2｜View 与 Viewpoint", ["Concern 关注点", "Viewpoint 视点", "View 视图", "Rendering 渲染"], "hierarchy"),
    E("opm", "opm", "OPM｜对象—过程对偶", ["TelemetryFrame 对象", "采集过程", "飞控对象", "下传过程"]),
    E("c4-language", "c4", "C4 Model｜四个缩放层级", ["Context 系统上下文", "Container 容器", "Component 组件", "Code 代码"], "layers"),
    E("se-context", "context", "经典 SE｜系统上下文图", ["发射操作员", "CS-1 探空仪", "地面站", "科学用户"], "context"),
    E("se-ffbd", "ffbd", "FFBD｜功能流与分支", ["自检", "采集数据", "打包遥测", "下传数据"]),
    E("se-n2", "n2", "N²／DSM｜接口矩阵", ["结构", "电源", "飞控", "通信"], "matrix"),
    E("se-idef0", "idef0", "IDEF0｜功能、输入、控制与机制", ["任务数据", "采集大气数据", "采样规范", "传感器与飞控"], "icom"),
    E("se-dfd", "dfd", "DFD｜数据流与存储", ["传感器", "采样处理", "数据存储", "地面站"]),
    E("se-qfd", "qfd", "QFD 质量屋｜需求到工程特性", ["数据完整", "续航充足", "质量受限", "链路可靠"], "matrix"),
    E("se-tradespace", "tradespace", "Tradespace／Pareto｜方案权衡", ["LiPo 850", "Li-ion 18650", "LiFePO4", "Pareto 前沿"], "chart"),
    E("se-fta", "fta", "FTA｜故障树分析", ["遥测中断", "供电失效", "电台失效", "天线故障"], "hierarchy"),
    E("se-cld", "cld", "CLD｜因果反馈回路", ["采样率", "数据价值", "功耗", "供电时间"]),
    E("se-sfd", "sfd", "SFD｜存量与流量", ["电池能量", "放电速率", "剩余任务时间", "采样负载"]),
    E("fw-dodaf", "dodaf", "DoDAF／UAF｜视点全景", ["AV 全视点", "OV 运行视点", "SV 系统视点", "PV 项目视点"], "layers"),
    E("fw-ov1", "ov1", "DoDAF OV-1｜高级运行概念", ["发射操作员", "CS-1 任务", "地面站", "科学用户"], "context"),
    E("fw-sv1", "sv1", "DoDAF SV-1｜系统接口描述", ["传感器", "飞控", "通信", "地面站"]),
    E("fw-cv2", "cv2", "DoDAF CV-2｜能力分类", ["探空任务能力", "环境感知", "数据传输", "回收回放"], "hierarchy"),
    E("fw-arcadia", "arcadia", "ARCADIA｜五层工程分析", ["OAB 运行分析", "SAB 系统分析", "LAB 逻辑架构", "PAB／EPBS 物理实现"], "layers"),
    E("pm-wbs", "wbs", "WBS｜工作分解", ["CS-1 项目", "需求与设计", "制造与集成", "试验与交付"], "hierarchy"),
    E("pm-pbs", "pbs", "PBS｜产品分解", ["CS-1 产品", "结构回收", "航电系统", "地面设备"], "hierarchy"),
    E("pm-gantt", "gantt", "Gantt｜任务、工期与里程碑", ["需求分析", "架构设计", "采购制造", "集成验证"], "timeline"),
    E("pm-pert", "pert", "PERT｜依赖与关键路径", ["需求基线", "架构设计", "详细设计", "设计评审"]),
    E("pm-risk", "risk-matrix", "风险矩阵｜概率与影响", ["链路中断", "质量超支", "供电不足", "降落过快"], "matrix"),
    E("pm-burndown", "burndown", "燃尽图｜剩余工作趋势", ["计划剩余", "实际剩余", "迭代结束", "剩余小时"], "chart"),
    E("uml-class", "class", "UML｜类图", ["Sensor", "TelemetryFrame", "Mission", "GroundStation"], "hierarchy"),
    E("uml-object", "object", "UML｜对象图", ["imu1 : Sensor", "frame42 : Frame", "flight7 : Mission", "gs1 : GroundStation"]),
    E("uml-component", "component", "UML｜组件与接口", ["采样组件", "遥测组件", "存储组件", "地面接收组件"]),
    E("uml-composite", "composite-structure", "UML｜组合结构图", ["CS-1", "传感器部件", "飞控部件", "通信部件"], "context"),
    E("uml-deployment", "deployment", "UML｜部署图", ["固件交付物", "CS-1 MCU", "遥测包", "地面站节点"], "delivery"),
    E("uml-profile", "profile", "UML｜剖面与构造型", ["UML Class", "«block»", "«requirement»", "«verification»"], "hierarchy"),
    E("uml-communication", "communication", "UML｜通信图", ["传感器", "飞控", "电台", "地面站"]),
    E("uml-iov", "interaction-overview", "UML｜交互概览图", ["启动交互", "采样序列", "异常序列", "回放序列"]),
    E("uml-timing", "timing", "UML｜时序图与时间约束", ["采样脉冲", "打包窗口", "发送窗口", "接收确认"], "timeline"),
    E("x-eventstorm", "event-storming", "事件风暴｜业务事件链", ["发射命令", "已进入下降", "遥测已生成", "地面已接收"]),
    E("x-impactmap", "impact-map", "影响地图｜目标到交付", ["获得可靠探空数据", "科学用户", "提高数据完整性", "本地存储与下传"], "hierarchy"),
    E("x-moduledep", "module-dependency", "模块依赖｜代码结构", ["model", "compiler", "renderer", "server"]),
    E("x-classhier", "class-hierarchy", "类层次｜继承结构", ["Diagram", "GraphDiagram", "MatrixDiagram", "TimelineDiagram"], "hierarchy"),
    E("x-eta", "eta", "ETA｜事件树分析", ["电池电压下降", "保护生效？", "降采样", "任务可继续"], "hierarchy"),
    E("x-kanban", "kanban", "看板｜工作流与在制品", ["待办", "进行中", "待评审", "已完成"]),
    E("x-bpmn", "bpmn", "BPMN｜业务流程", ["开始任务", "采集与打包", "链路可用？", "发送或存储"]),
    E("x-archimate", "archimate", "ArchiMate｜业务—应用—技术", ["探空业务服务", "遥测应用服务", "飞控软件", "嵌入式节点"], "layers"),
    E("x-cicd", "cicd", "CI/CD｜构建、关口与发布", ["源码提交", "构建与测试", "制品发布", "部署验证"], "delivery"),
    E("x-topology", "deployment-topology", "部署拓扑｜节点与网络", ["CS-1 设备", "433 MHz 链路", "地面网关", "分析工作站"], "delivery"),
    E("x-flame", "flame-graph", "火焰图｜栈帧耗时", ["render", "layout", "route_edges", "measure_text"], "flame"),
    E("x-callgraph", "call-graph", "调用图｜函数关系", ["render_diagram", "validate_spec", "to_ir", "render_svg"]),
    E("x-storymap", "story-map", "用户故事地图｜活动与发布", ["准备任务", "执行探空", "接收数据", "回收分析"]),
    E("x-ddd", "ddd-context-map", "DDD｜限界上下文映射", ["任务上下文", "遥测上下文", "通信上下文", "分析上下文"], "context"),
    E("x-dmn", "dmn", "DMN｜决策规则表", ["电压", "链路质量", "采样策略", "发送策略"], "matrix"),
    E("x-er", "er", "ER｜实体与关系", ["Mission", "TelemetryFrame", "SensorReading", "GroundStation"]),
    E("x-c4-context", "c4-context", "C4 Context｜系统上下文", ["操作员", "CS-1 软件", "地面站软件", "科学用户"], "context"),
    E("x-c4-container", "c4-container", "C4 Container｜可部署容器", ["飞控固件", "遥测服务", "地面 API", "数据存储"], "delivery"),
    E("uml-usecase-shared", "use-case", "UML｜用例图（共享渲染器）", ["操作员", "自检与发射", "科学用户", "接收与回放"], "context"),
    E("uml-activity-shared", "activity", "UML｜活动图（共享渲染器）", ["开始", "采集数据", "电压正常？", "下传或安全模式"]),
    E("uml-state-shared", "state-machine", "UML｜状态机图（共享渲染器）", ["待机", "待发射", "下降", "安全模式"]),
    E("uml-sequence-shared", "sequence", "UML｜序列图（共享渲染器）", ["传感器", "飞控", "电台", "地面站"]),
    E("uml-package-shared", "package", "UML｜包图（共享渲染器）", ["Common", "Requirements", "Architecture", "Verification"], "hierarchy"),
    E("delivery", "delivery", "Delivery View｜源码到运行交付链", ["源码仓库", "构建与测试", "版本化交付物", "制品库／Release", "部署与运行"], "delivery"),
]

_QUESTIONS = {entry["type"]: entry["question"] for entry in CATALOG}


def _node(slug, index, label, x, y, w=240, h=90, color="blue", kind="block"):
    return {"id": f"n{index}", "label": label, "kind": kind, "x": x, "y": y, "w": w, "h": h, "color": color, "sourceId": f"Lesson2.{slug}.n{index}"}


def _edges(count, kind="flow", labels=None):
    result = []
    for index in range(count - 1):
        edge = {"source": f"n{index}", "target": f"n{index+1}", "kind": kind, "color": "teal" if kind == "flow" else "blue"}
        if labels and index < len(labels):
            edge["label"] = labels[index]
        result.append(edge)
    return result


def build_spec(entry, output_dir):
    slug, kind, labels = entry["slug"], entry["type"], entry["labels"]
    template = entry["template"]
    nodes, edges, groups, matrices, charts, timelines = [], [], [], [], [], []
    if template == "hierarchy":
        nodes = [_node(slug, 0, labels[0], 500, 135, 280, 85, "violet")]
        nodes += [_node(slug, i + 1, label, 80 + i * 400, 410, 300, 100, "blue") for i, label in enumerate(labels[1:4])]
        edges = [{"source": "n0", "target": f"n{i}", "kind": "composition", "label": "1"} for i in range(1, 4)]
    elif template == "layers":
        nodes = [_node(slug, i, label, 340, 130 + i * 125, 600, 78, ["blue", "teal", "amber", "violet"][i]) for i, label in enumerate(labels[:4])]
        edges = _edges(4, "dependency")
    elif template == "context":
        groups = [{"id": "boundary", "label": labels[1], "kind": "boundary", "x": 330, "y": 150, "w": 620, "h": 400, "color": "blue"}]
        nodes = [_node(slug, 0, labels[0], 65, 260, 200, 90, "gray"), _node(slug, 1, labels[1], 500, 285, 280, 110, "blue"), _node(slug, 2, labels[2], 1010, 260, 200, 90, "teal"), _node(slug, 3, labels[3], 500, 455, 280, 70, "violet")]
        edges = [{"source": "n0", "target": "n1", "kind": "association"}, {"source": "n1", "target": "n2", "kind": "flow", "label": "interface"}, {"source": "n3", "target": "n1", "kind": "dependency"}]
    elif template == "icom":
        nodes = [_node(slug, 0, labels[0], 55, 290, 230, 90, "gray"), _node(slug, 1, labels[1], 500, 290, 280, 100, "teal"), _node(slug, 2, labels[2], 500, 135, 280, 80, "amber"), _node(slug, 3, labels[3], 500, 480, 280, 80, "blue")]
        edges = [{"source": "n0", "target": "n1", "kind": "flow", "label": "input"}, {"source": "n2", "target": "n1", "kind": "dependency", "label": "control"}, {"source": "n3", "target": "n1", "kind": "association", "label": "mechanism"}]
    elif template == "matrix":
        nodes = [_node(slug, 0, labels[0], 55, 145, 190, 75, "gray")]
        axis = labels[:4] if kind == "n2" else labels[1:4]
        matrices = [{"id": f"{slug}-matrix", "x": 300 if kind == "n2" else 320, "y": 150, "cellWidth": 160 if kind == "n2" else 210, "cellHeight": 75 if kind == "n2" else 85, "columns": axis, "rows": axis, "cells": [{"row": 0, "column": 1, "label": "I-01" if kind == "n2" else labels[0], "color": "amber", "sourceId": f"Lesson2.{slug}.cell01"}, {"row": 1, "column": 2, "label": "I-02" if kind == "n2" else "相关 / 接口", "color": "teal", "sourceId": f"Lesson2.{slug}.cell12"}, {"row": 2, "column": 0, "label": "I-03" if kind == "n2" else "追溯", "color": "violet", "sourceId": f"Lesson2.{slug}.cell20"}]}]
    elif template == "chart":
        nodes = [_node(slug, 0, labels[0], 90, 555, 240, 65, "blue"), _node(slug, 1, labels[1], 950, 555, 240, 65, "teal")]
        is_scatter = kind == "tradespace"
        charts = [{"id": f"{slug}-chart", "kind": "scatter" if is_scatter else "line", "x": 170, "y": 150, "w": 900, "h": 340, "xLabel": labels[2], "yLabel": labels[3], "series": [{"id": "planned", "label": labels[0], "color": "gray", "points": [[20, 80], [50, 60], [85, 35]] if is_scatter else [[0, 100], [50, 50], [100, 0]]}, {"id": "actual", "label": labels[1], "color": "teal", "points": [[15, 30], [45, 55], [70, 75], [90, 88]] if is_scatter else [[0, 95], [35, 65], [70, 30], [100, 12]]}]}]
    elif template == "timeline":
        nodes = [_node(slug, 0, "里程碑 / 验收点", 90, 555, 250, 65, "amber")]
        timelines = [{"id": f"{slug}-timeline", "x": 95, "y": 150, "w": 1060, "rowHeight": 82, "labelWidth": 210, "rows": [{"id": f"row{i}", "label": label, "start": i * 14, "end": min(95, i * 14 + 45), "color": ["blue", "teal", "amber", "violet"][i], "sourceId": f"Lesson2.{slug}.row{i}"} for i, label in enumerate(labels[:4])], "markers": [{"position": 58, "label": "PDR / 评审"}]}]
    elif template == "flame":
        nodes = [_node(slug, 0, labels[0], 150, 450, 900, 70, "blue", "flame"), _node(slug, 1, labels[1], 250, 350, 700, 70, "teal", "flame"), _node(slug, 2, labels[2], 350, 250, 500, 70, "amber", "flame"), _node(slug, 3, labels[3], 450, 150, 300, 70, "violet", "flame")]
        for node, share in zip(nodes, ["100% total", "70% layout", "45% routing", "25% text"]):
            node["compartment"] = share
    else:
        count = len(labels) if template == "delivery" else 4
        xs = [25, 275, 525, 775, 1025] if count == 5 else [45, 350, 655, 960]
        width = 220 if count == 5 else 240
        nodes = [_node(slug, i, labels[i], xs[i], 290, width, 105, ["gray", "blue", "amber", "violet", "teal"][i]) for i in range(count)]
        edge_labels = ["builds", "produces", "publishes", "deploys / runs"] if template == "delivery" else None
        edges = _edges(count, "flow", edge_labels)
        if template == "delivery":
            for index, edge in enumerate(edges):
                label = edge["label"]
                gap_center = (xs[index] + width + xs[index + 1]) / 2
                edge["labelPosition"] = [gap_center - len(label) * 4, 255]
    return {
        "schema": "diagram-view/v1", "type": kind,
        "intent": {"question": _QUESTIONS[kind]}, "sources": [{"kind": "lesson", "figure": slug}],
        "selection": {"nodes": nodes, "edges": edges, "groups": groups, "matrices": matrices, "charts": charts, "timelines": timelines, "annotations": [{"x": 50, "y": 645, "text": f"lesson_2 图鉴扩展 · {entry['title']} · 统一 CanSat／dgraph 教学示例"}]},
        "presentation": {"title": f"CanSat CS-1｜{entry['title']}", "subtitle": "dgraph · lesson_2 diagram atlas", "theme": "lesson"},
        "outputs": {"directory": output_dir, "formats": ["viewspec", "dsl", "svg", "report"]},
    }
