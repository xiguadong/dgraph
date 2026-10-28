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
