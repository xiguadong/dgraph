"""Rich semantic examples used by the dedicated domain renderers."""

QFD_MODEL = {
    "customerNeeds": [
        {"id": "data-integrity", "label": "数据完整", "importance": 5},
        {"id": "recovery", "label": "易回收", "importance": 4},
        {"id": "low-cost", "label": "低成本", "importance": 3},
        {"id": "usability", "label": "易操作", "importance": 2},
    ],
    "engineering": [
        {"id": "sample-rate", "label": "采样率", "unit": "Hz ↑", "target": "≥ 1 Hz", "weight": 50, "rank": 3},
        {"id": "downlink", "label": "下传距离", "unit": "km ↑", "target": "≥ 2 km", "weight": 72, "rank": 1},
        {"id": "mass", "label": "总质量", "unit": "g ↓", "target": "≤ 350 g", "weight": 26, "rank": 5},
        {"id": "cost", "label": "成本", "unit": "元 ↓", "target": "≤ ¥1200", "weight": 31, "rank": 4},
        {"id": "recovery-speed", "label": "回收速度", "unit": "m/s ↓", "target": "≤ 5 m/s", "weight": 57, "rank": 2},
    ],
    "relations": [
        {"need": "data-integrity", "engineering": "sample-rate", "strength": 9},
        {"need": "data-integrity", "engineering": "downlink", "strength": 9},
        {"need": "data-integrity", "engineering": "mass", "strength": 1},
        {"need": "data-integrity", "engineering": "recovery-speed", "strength": 3},
        {"need": "recovery", "engineering": "mass", "strength": 3},
        {"need": "recovery", "engineering": "cost", "strength": 1},
        {"need": "recovery", "engineering": "recovery-speed", "strength": 9},
        {"need": "low-cost", "engineering": "sample-rate", "strength": 1},
        {"need": "low-cost", "engineering": "downlink", "strength": 3},
        {"need": "low-cost", "engineering": "mass", "strength": 3},
        {"need": "low-cost", "engineering": "cost", "strength": 9},
        {"need": "usability", "engineering": "sample-rate", "strength": 1},
        {"need": "usability", "engineering": "downlink", "strength": 9},
        {"need": "usability", "engineering": "recovery-speed", "strength": 3},
    ],
    "roof": [
        {"left": "sample-rate", "right": "downlink", "type": "minus"},
        {"left": "sample-rate", "right": "mass", "type": "minus"},
        {"left": "sample-rate", "right": "cost", "type": "minus"},
        {"left": "downlink", "right": "mass", "type": "minus"},
        {"left": "downlink", "right": "cost", "type": "minus"},
        {"left": "mass", "right": "recovery-speed", "type": "plus"},
    ],
}

GANTT_MODEL = {
    "ticks": ["W1", "W3", "W5", "W7", "W9", "W11"],
    "tasks": [
        {"id": "requirements", "label": "需求与任务分析", "start": 0, "end": 2, "color": "blue", "dependencies": []},
        {"id": "design", "label": "架构 / 详细设计", "start": 2, "end": 5, "color": "blue", "dependencies": ["requirements"]},
        {"id": "manufacture", "label": "采购与制造", "start": 4, "end": 8, "color": "amber", "dependencies": ["design"]},
        {"id": "integration", "label": "子系统集成", "start": 8, "end": 10, "color": "teal", "dependencies": ["manufacture"]},
        {"id": "verification", "label": "试验与验证", "start": 10, "end": 12, "color": "violet", "dependencies": ["integration"]},
    ],
    "milestones": [
        {"id": "pdr", "label": "PDR", "at": 4},
        {"id": "cdr", "label": "CDR", "at": 6},
        {"id": "trr", "label": "TRR", "at": 10},
        {"id": "review", "label": "评审", "at": 12},
    ],
}

FTA_MODEL = {
    "top": {"id": "TE-1", "label": "遥测中断"},
    "gates": [{"id": "g1", "type": "or"}],
    "events": [
        {"id": "battery", "label": "电池耗尽", "note": "低温容量下降"},
        {"id": "antenna", "label": "天线断裂", "note": "开伞冲击 / 弯折"},
        {"id": "deadlock", "label": "软件死锁", "note": "看门狗未复位"},
        {"id": "ground-lock", "label": "地面站失锁", "note": "遮挡 / 干扰"},
    ],
}

C4_CONTAINER_MODEL = {
    "boundary": {"id": "ground-station", "label": "地面站软件"},
    "actors": [
        {"id": "operator", "label": "操作员", "note": "发射 / 回收", "x": 80, "y": 190},
        {"id": "scientist", "label": "科学用户", "note": "查看 / 导出", "x": 80, "y": 430},
    ],
    "containers": [
        {"id": "web-ui", "label": "Web UI", "note": "操作与查看界面", "x": 390, "y": 180},
        {"id": "mission-service", "label": "任务服务", "note": "任务计划 / 指令", "x": 720, "y": 180},
        {"id": "timeseries-db", "label": "时序数据库", "note": "帧表 + 索引", "x": 390, "y": 390},
        {"id": "telemetry-service", "label": "遥测服务", "note": "接收 / 解码 / 路由", "x": 720, "y": 390},
        {"id": "receiver", "label": "接收机", "note": "433 MHz → USB", "x": 1010, "y": 390, "external": True},
    ],
    "relations": [
        {"source": "operator", "target": "web-ui", "label": "操作"},
        {"source": "scientist", "target": "web-ui", "label": "查看数据"},
        {"source": "web-ui", "target": "mission-service", "label": "REST"},
        {"source": "web-ui", "target": "timeseries-db", "label": "查询"},
        {"source": "mission-service", "target": "timeseries-db", "label": "写入"},
        {"source": "mission-service", "target": "telemetry-service", "label": "计划下发"},
        {"source": "receiver", "target": "telemetry-service", "label": "串口"},
    ],
}

UML_CLASS_MODEL = {
    "classes": [
        {"id": "GroundStation", "x": 70, "y": 150, "attributes": ["stationId: String", "mode: Mode"], "operations": ["startSession()"]},
        {"id": "Mission", "x": 700, "y": 150, "attributes": ["id: String", "startTime: Time"], "operations": ["archive()"]},
        {"id": "Sensor", "x": 70, "y": 410, "attributes": ["kind: SensorType", "rateHz: int"], "operations": ["sample()"]},
        {"id": "TelemetryFrame", "x": 700, "y": 410, "attributes": ["ts: Time", "t, p, rh: float"], "operations": ["crcOk(): bool"]},
    ],
    "relations": [
        {"id": "manages", "kind": "association", "source": "GroundStation", "target": "Mission", "sourceMultiplicity": "1", "targetMultiplicity": "1", "points": [[350, 235], [700, 235]]},
        {"id": "records", "kind": "association", "source": "Mission", "target": "TelemetryFrame", "sourceMultiplicity": "1", "targetMultiplicity": "0..*", "points": [[840, 335], [840, 410]]},
        {"id": "produces", "kind": "association", "source": "Sensor", "target": "TelemetryFrame", "sourceMultiplicity": "1", "targetMultiplicity": "0..*", "points": [[350, 495], [700, 495]]},
    ],
}

SEQUENCE_MODEL = {
    "participants": [
        {"id": "sensors", "label": "传感器", "x": 150},
        {"id": "fcu", "label": "飞控", "x": 450},
        {"id": "radio", "label": "电台", "x": 750},
        {"id": "ground", "label": "地面站", "x": 1050},
    ],
    "messages": [
        {"source": "fcu", "target": "sensors", "label": "1 读取采样", "kind": "sync", "activate": True},
        {"source": "sensors", "target": "fcu", "label": "2 温压湿 / IMU / GPS", "kind": "return"},
        {"source": "fcu", "target": "fcu", "label": "3 打包 TelemetryFrame", "kind": "sync", "activate": True},
        {"source": "fcu", "target": "radio", "label": "4 UART 遥测帧", "kind": "sync", "activate": True},
        {"source": "radio", "target": "ground", "label": "5 433 MHz 下行", "kind": "sync"},
        {"source": "ground", "target": "fcu", "label": "6 接收确认（下一场景）", "kind": "return"},
    ],
}

N2_MODEL = {
    "elements": [
        {"id": "structure", "label": "结构"},
        {"id": "power", "label": "电源"},
        {"id": "fcu", "label": "飞控"},
        {"id": "sensors", "label": "传感器"},
        {"id": "comms", "label": "通信"},
        {"id": "ground", "label": "地面站", "external": True},
    ],
    "links": [
        {"from": "structure", "to": "power", "kind": "mechanical", "label": "机"},
        {"from": "structure", "to": "fcu", "kind": "mechanical", "label": "机"},
        {"from": "structure", "to": "sensors", "kind": "mechanical", "label": "机"},
        {"from": "structure", "to": "comms", "kind": "mechanical", "label": "机"},
        {"from": "power", "to": "structure", "kind": "thermal", "label": "热"},
        {"from": "power", "to": "fcu", "kind": "electrical", "label": "电 I-01", "strong": True},
        {"from": "power", "to": "sensors", "kind": "electrical", "label": "电"},
        {"from": "power", "to": "comms", "kind": "electrical", "label": "电"},
        {"from": "fcu", "to": "power", "kind": "data", "label": "数"},
        {"from": "fcu", "to": "sensors", "kind": "data", "label": "数"},
        {"from": "fcu", "to": "comms", "kind": "data", "label": "数 I-03", "strong": True},
        {"from": "sensors", "to": "structure", "kind": "mechanical", "label": "机"},
        {"from": "sensors", "to": "fcu", "kind": "data", "label": "数 I-02", "strong": True},
        {"from": "comms", "to": "structure", "kind": "mechanical", "label": "机"},
        {"from": "comms", "to": "fcu", "kind": "data", "label": "数"},
        {"from": "comms", "to": "ground", "kind": "rf", "label": "射 I-04", "strong": True},
    ],
}

DFD_MODEL = {
    "entities": [
        {"id": "sensors", "label": "传感器", "x": 55, "y": 255},
        {"id": "ground", "label": "地面站", "x": 1010, "y": 255},
        {"id": "operator", "label": "回收人员", "x": 1010, "y": 455},
    ],
    "processes": [
        {"id": "sampling", "label": "采样与打包", "x": 355, "y": 255},
        {"id": "routing", "label": "遥测路由", "x": 665, "y": 255},
    ],
    "stores": [
        {"id": "telemetry-log", "label": "遥测数据存储", "x": 520, "y": 455},
    ],
    "flows": [
        {"source": "sensors", "target": "sampling", "label": "原始采样"},
        {"source": "sampling", "target": "routing", "label": "遥测帧"},
        {"source": "routing", "target": "ground", "label": "433 MHz 下行"},
        {"source": "sampling", "target": "telemetry-log", "label": "同步写入"},
        {"source": "operator", "target": "telemetry-log", "label": "回收后回放"},
    ],
}

BPMN_MODEL = {
    "pool": "CS-1 任务池",
    "events": [
        {"id": "start", "label": "开始", "kind": "start", "x": 90, "y": 310},
        {"id": "end", "label": "结束", "kind": "end", "x": 1180, "y": 310},
    ],
    "tasks": [
        {"id": "sample", "label": "采集与打包", "x": 220, "y": 270},
        {"id": "send", "label": "发送遥测", "x": 780, "y": 190},
        {"id": "store", "label": "写入本地存储", "x": 780, "y": 420},
    ],
    "gateways": [
        {"id": "link-ok", "label": "链路可用？", "x": 530, "y": 270},
        {"id": "join", "label": "汇合", "x": 1010, "y": 270},
    ],
    "flows": [
        {"source": "start", "target": "sample"},
        {"source": "sample", "target": "link-ok"},
        {"source": "link-ok", "target": "send", "label": "是"},
        {"source": "link-ok", "target": "store", "label": "否", "branch": "unavailable"},
        {"source": "send", "target": "join"},
        {"source": "store", "target": "join"},
        {"source": "join", "target": "end"},
    ],
}

# All numbers below are teaching examples, not measured mission data.
RISK_MATRIX_MODEL = {
    "probability": ["极低", "低", "中", "高", "极高"],
    "consequence": ["可忽略", "轻微", "中等", "严重", "灾难"],
    "risks": [
        {"id": "R-01", "label": "电池低温", "probability": 4, "consequence": 3},
        {"id": "R-02", "label": "链路失锁", "probability": 3, "consequence": 4},
        {"id": "R-03", "label": "进度压缩", "probability": 4, "consequence": 4},
        {"id": "R-04", "label": "开伞失效", "probability": 2, "consequence": 5},
        {"id": "R-05", "label": "质量超限", "probability": 3, "consequence": 3},
    ],
}
DMN_MODEL = {
    "title": "发射许可 Go / No-Go", "hitPolicy": "F",
    "inputs": [{"id": "wind", "label": "风速", "unit": "m/s"}, {"id": "voltage", "label": "电池电压", "unit": "V"}, {"id": "selftest", "label": "自检", "unit": "通过 / 失败"}, {"id": "margin", "label": "链路裕度", "unit": "dB"}],
    "output": {"label": "发射决策"},
    "rules": [
        {"id": "1", "conditions": ["> 8", "—", "—", "—"], "result": "No-Go"},
        {"id": "2", "conditions": ["—", "< 6.4", "—", "—"], "result": "No-Go"},
        {"id": "3", "conditions": ["—", "—", "失败", "—"], "result": "No-Go"},
        {"id": "4", "conditions": ["—", "[6.4, 7.0)", "—", "—"], "result": "Hold"},
        {"id": "5", "conditions": ["—", "—", "—", "< 6"], "result": "Hold"},
        {"id": "6", "conditions": ["≤ 8", "≥ 7.0", "通过", "≥ 6"], "result": "Go"},
    ],
}
TIMING_MODEL = {
    "durationMs": 2000, "ticks": [0, 500, 1000, 1500, 2000],
    "lifelines": [
        {"id": "sensor", "label": "传感器", "segments": [{"from": 0, "to": 80, "state": "采样"}, {"from": 80, "to": 1000, "state": "等待"}, {"from": 1000, "to": 1080, "state": "采样"}, {"from": 1080, "to": 2000, "state": "等待"}]},
        {"id": "ground", "label": "地面站", "segments": [{"from": 0, "to": 130, "state": "等待"}, {"from": 130, "to": 230, "state": "处理"}, {"from": 230, "to": 1130, "state": "等待"}, {"from": 1130, "to": 1230, "state": "处理"}, {"from": 1230, "to": 2000, "state": "等待"}]},
        {"id": "radio", "label": "电台", "segments": [{"from": 0, "to": 80, "state": "空闲"}, {"from": 80, "to": 130, "state": "发送"}, {"from": 130, "to": 1080, "state": "空闲"}, {"from": 1080, "to": 1130, "state": "发送"}, {"from": 1130, "to": 2000, "state": "空闲"}]},
    ],
    "constraints": [{"label": "采样周期 T = 1000 ms", "from": 0, "to": 1000}, {"label": "发送 ≤ 50 ms", "from": 80, "to": 130}, {"label": "处理 ≤ 100 ms", "from": 130, "to": 230}],
}
TRADESPACE_MODEL = {
    "x": {"label": "电池质量（g）", "min": 0, "max": 180}, "y": {"label": "可用能量（Wh）", "min": 0, "max": 25},
    "thresholds": {"maxX": 120, "minY": 10},
    "alternatives": [
        {"id": "lipo450", "label": "LiPo 2S 450", "x": 28, "y": 3.3, "cost": 55},
        {"id": "lipo850", "label": "LiPo 2S 850", "x": 48, "y": 6.3, "cost": 85, "labelDx": -112, "labelDy": -16},
        {"id": "lifepo", "label": "LiFePO4 2S 700", "x": 52, "y": 4.5, "cost": 110},
        {"id": "lipo1000", "label": "LiPo 2S 1000", "x": 56, "y": 7.4, "cost": 95, "labelDx": 12, "labelDy": -4},
        {"id": "lipo3s", "label": "LiPo 3S 850", "x": 66, "y": 9.4, "cost": 110, "labelDx": 12, "labelDy": -12},
        {"id": "liion18650", "label": "Li-ion 2S 18650", "x": 94, "y": 15.8, "cost": 120},
        {"id": "liion21700", "label": "Li-ion 2S 21700", "x": 140, "y": 21.6, "cost": 180},
        {"id": "nimh", "label": "NiMH 2S", "x": 110, "y": 7.2, "cost": 70},
    ],
    "paretoIds": ["lipo450", "lipo850", "lipo1000", "lipo3s", "liion18650", "liion21700"],
}
PERT_MODEL = {"tasks": [
    {"id": "A", "label": "需求分析", "duration": 2, "dependencies": [], "x": 50, "y": 230},
    {"id": "B", "label": "架构设计", "duration": 2, "dependencies": ["A"], "x": 215, "y": 230},
    {"id": "C", "label": "详细设计", "duration": 2, "dependencies": ["B"], "x": 380, "y": 230},
    {"id": "D", "label": "采购制造", "duration": 4, "dependencies": ["C"], "x": 545, "y": 230},
    {"id": "E", "label": "系统集成", "duration": 2, "dependencies": ["D", "H"], "x": 710, "y": 230},
    {"id": "F", "label": "系统试验", "duration": 3, "dependencies": ["E"], "x": 875, "y": 230},
    {"id": "G", "label": "评审冻结", "duration": 1, "dependencies": ["F"], "x": 1040, "y": 230},
    {"id": "H", "label": "地面站软件", "duration": 3, "dependencies": ["B"], "x": 465, "y": 420},
]}

# The next task may start only after each listed predecessor finishes.
GANTT_MODEL["tasks"][2]["dependencies"] = ["requirements"]  # procurement overlaps design
# The RF link is downlink-only in the teaching scenario; no ACK is specified.
SEQUENCE_MODEL["messages"] = SEQUENCE_MODEL["messages"][:-1]
# Telemetry service persists frames. A recovery person asks a process to replay,
# rather than reading a DFD data store directly.
C4_CONTAINER_MODEL["relations"] = [r for r in C4_CONTAINER_MODEL["relations"] if not (r["source"] == "mission-service" and r["target"] == "timeseries-db")]
C4_CONTAINER_MODEL["relations"].append({"source": "telemetry-service", "target": "timeseries-db", "label": "写入遥测"})
DFD_MODEL["entities"][-1]["id"] = "scientist"
DFD_MODEL["entities"][-1]["label"] = "科学用户"
DFD_MODEL["processes"].append({"id": "replay", "label": "回放数据", "x": 760, "y": 455})
DFD_MODEL["flows"] = [flow for flow in DFD_MODEL["flows"] if flow["source"] != "operator"]
DFD_MODEL["flows"] += [{"source": "telemetry-log", "target": "replay", "label": "存储帧"}, {"source": "replay", "target": "scientist", "label": "回放数据"}]

# Ground-station quality workflow: the telemetry service receives, checks and
# archives accepted frames; the scientific user analyzes the accepted data.
BPMN_MODEL = {
    "pool": "地面站遥测处理",
    "lanes": [
        {"id": "telemetry", "label": "遥测服务\n接收 · 质控 · 归档", "y": 180, "height": 205},
        {"id": "science", "label": "科学分析\n查看 · 分析", "y": 385, "height": 215},
    ],
    "events": [
        {"id": "start", "label": "帧到达", "kind": "start", "lane": "telemetry", "x": 228, "y": 247},
        {"id": "abnormal-end", "label": "终止", "kind": "end", "lane": "telemetry", "x": 1060, "y": 337},
        {"id": "end", "label": "完成", "kind": "end", "lane": "science", "x": 1150, "y": 477},
    ],
    "tasks": [
        {"id": "receive", "label": "接收并解码帧", "lane": "telemetry", "x": 290, "y": 205},
        {"id": "archive", "label": "入库", "lane": "telemetry", "x": 730, "y": 205},
        {"id": "reject", "label": "标记异常", "lane": "telemetry", "x": 730, "y": 295},
        {"id": "analyze", "label": "查看与分析", "lane": "science", "x": 840, "y": 435},
    ],
    "gateways": [{"id": "quality", "label": "质控合格？", "lane": "telemetry", "x": 520, "y": 205}],
    "flows": [
        {"source": "start", "target": "receive", "points": [[250, 247], [290, 247]]},
        {"source": "receive", "target": "quality", "points": [[500, 247], [520, 247]]},
        {"source": "quality", "target": "archive", "label": "合格", "points": [[650, 247], [730, 247]]},
        {"source": "quality", "target": "reject", "label": "不合格", "branch": "unavailable", "points": [[585, 289], [585, 337], [730, 337]]},
        {"source": "reject", "target": "abnormal-end", "points": [[940, 337], [1038, 337]]},
        {"source": "archive", "target": "analyze", "points": [[940, 247], [985, 247], [985, 410], [945, 410], [945, 435]]},
        {"source": "analyze", "target": "end", "points": [[1050, 477], [1128, 477]]},
    ],
}

# Explicit boundary-to-boundary routes keep arrows out of labels and symbols.
C4_CONTAINER_MODEL["relations"][0]["points"] = [[100, 214], [350, 214], [350, 215], [390, 215]]
C4_CONTAINER_MODEL["relations"][1]["points"] = [[100, 454], [320, 454], [320, 265], [390, 265]]
for relation in C4_CONTAINER_MODEL["relations"]:
    routes = {
        ("web-ui", "mission-service"): [[630, 240], [720, 240]],
        ("web-ui", "timeseries-db"): [[510, 300], [510, 390]],
        ("mission-service", "telemetry-service"): [[840, 300], [840, 390]],
        ("receiver", "telemetry-service"): [[1010, 450], [960, 450]],
        ("telemetry-service", "timeseries-db"): [[720, 450], [630, 450]],
    }
    relation["points"] = routes.get((relation["source"], relation["target"]), relation.get("points", []))
DFD_MODEL["stores"][0]["x"] = 355
DFD_MODEL["processes"][-1]["x"] = 710
for flow in DFD_MODEL["flows"]:
    routes = {
        ("sensors", "sampling"): [[255, 305], [310, 305], [310, 310], [355, 310]],
        ("sampling", "routing"): [[585, 310], [665, 310]],
        ("routing", "ground"): [[895, 310], [1010, 305]],
        ("sampling", "telemetry-log"): [[470, 365], [470, 467]],
        ("telemetry-log", "replay"): [[603, 500], [660, 500], [660, 510], [710, 510]],
        ("replay", "scientist"): [[940, 510], [1010, 505]],
    }
    flow["points"] = routes[(flow["source"], flow["target"])]
