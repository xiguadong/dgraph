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
        {"id": "mass", "label": "总质量", "unit": "g ↓", "target": "≤ 350 g", "weight": 25, "rank": 5},
        {"id": "cost", "label": "成本", "unit": "元 ↓", "target": "≤ ¥1200", "weight": 31, "rank": 4},
        {"id": "recovery-speed", "label": "回收速度", "unit": "m/s ↓", "target": "≤ 5 m/s", "weight": 54, "rank": 2},
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
        {"id": "manages", "source": "GroundStation", "target": "Mission", "sourceMultiplicity": "1", "targetMultiplicity": "1", "points": [[350, 235], [700, 235]]},
        {"id": "records", "source": "Mission", "target": "TelemetryFrame", "sourceMultiplicity": "1", "targetMultiplicity": "0..*", "points": [[840, 300], [840, 410]]},
        {"id": "produces", "source": "Sensor", "target": "TelemetryFrame", "sourceMultiplicity": "1", "targetMultiplicity": "0..*", "points": [[350, 495], [700, 495]]},
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
