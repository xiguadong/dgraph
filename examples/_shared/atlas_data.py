"""Independent engineering-diagram catalog and representative CanSat ViewSpecs."""

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
    E("pm-pbs", "pbs", "PBS｜产品分解", ["CS-1 探空仪", "结构与回收", "电源", "飞控"], "hierarchy"),
    E("pm-gantt", "gantt", "Gantt｜任务、工期与里程碑", ["需求分析", "架构设计", "采购制造", "集成验证"], "timeline"),
    E("pm-pert", "pert", "PERT｜依赖与关键路径", ["需求基线", "架构设计", "详细设计", "设计评审"]),
    E("pm-risk", "risk-matrix", "风险矩阵｜概率与影响", ["链路中断", "质量超支", "供电不足", "降落过快"], "matrix"),
    E("pm-burndown", "burndown", "燃尽图｜剩余工作趋势", ["计划剩余", "实际剩余", "迭代结束", "剩余小时"], "chart"),
    E("uml-class", "class", "UML｜类图", ["Sensor", "TelemetryFrame", "Mission", "GroundStation"], "hierarchy"),
    E("uml-object", "object", "UML｜对象图", ["imu1 : Sensor", "frame42 : Frame", "flight7 : Mission", "gs1 : GroundStation"]),
    E("uml-component", "component", "UML｜组件与接口", ["采样组件", "遥测组件", "存储组件", "地面接收组件"]),
    E("uml-composite", "composite-structure", "UML｜组合结构图", ["CS-1", "传感器部件", "飞控部件", "通信部件"], "context"),
    E("uml-deployment", "deployment", "UML｜部署图", ["固件交付物", "CS-1 MCU", "遥测包", "地面站节点"], "delivery"),
    E("uml-profile", "profile", "UML｜剖面与构造型", ["Class", "Property", "«sensor»", "«telemetry»"], "hierarchy"),
    E("uml-communication", "communication", "UML｜通信图", ["传感器", "飞控", "电台", "地面站"]),
    E("uml-iov", "interaction-overview", "UML｜交互概览图", ["启动交互", "采样序列", "异常序列", "回放序列"]),
    E("uml-timing", "timing", "UML｜时序图与时间约束", ["采样脉冲", "打包窗口", "发送窗口", "接收处理"], "timeline"),
    E("x-eventstorm", "event-storming", "事件风暴｜业务事件链", ["发射命令", "已进入下降", "遥测已生成", "地面已接收"]),
    E("x-impactmap", "impact-map", "影响地图｜目标到交付", ["获得可靠探空数据", "科学用户", "提高数据完整性", "本地存储与下传"], "hierarchy"),
    E("x-moduledep", "module-dependency", "模块依赖｜代码结构", ["gs.ui", "gs.core", "gs.io", "依赖方向"]),
    E("x-classhier", "class-hierarchy", "类层次｜继承结构", ["Frame", "TelemetryFrame", "HousekeepingFrame", "SensorReading"], "hierarchy"),
    E("x-eta", "eta", "ETA｜事件树分析", ["电池电压下降", "保护生效？", "降采样", "任务可继续"], "hierarchy"),
    E("x-kanban", "kanban", "看板｜工作流与在制品", ["待办", "进行中", "待评审", "已完成"]),
    E("x-bpmn", "bpmn", "BPMN｜业务流程", ["帧到达", "接收与解码", "质控合格？", "入库或标记异常"]),
    E("x-archimate", "archimate", "ArchiMate｜业务—应用—技术", ["探空业务服务", "遥测应用服务", "飞控软件", "嵌入式节点"], "layers"),
    E("x-cicd", "cicd", "CI/CD｜构建、关口与发布", ["源码提交", "构建与测试", "制品发布", "部署验证"], "delivery"),
    E("x-topology", "deployment-topology", "部署拓扑｜节点与网络", ["CS-1 设备", "433 MHz 链路", "地面网关", "分析工作站"], "delivery"),
    E("x-flame", "flame-graph", "火焰图｜栈帧耗时", ["decode_loop", "decode_frame", "crc16", "parse_fields"], "flame"),
    E("x-callgraph", "call-graph", "调用图｜函数关系", ["main", "radio_read", "decode_frame", "store_batch"]),
    E("x-storymap", "story-map", "用户故事地图｜活动与发布", ["准备任务", "执行探空", "接收数据", "回收分析"]),
    E("x-ddd", "ddd-context-map", "DDD｜限界上下文映射", ["任务上下文", "遥测上下文", "通信上下文", "分析上下文"], "context"),
    E("x-dmn", "dmn", "DMN｜决策规则表", ["电压", "链路质量", "采样策略", "发送策略"], "matrix"),
    E("x-er", "er", "ER｜实体与关系", ["Mission", "TelemetryFrame", "SensorReading", "GroundStation"]),
    E("x-c4-context", "c4-context", "C4 Context｜系统上下文", ["操作员", "地面站软件", "CS-1 探空仪", "科学用户"], "context"),
    E("x-c4-container", "c4-container", "C4 Container｜可部署容器", ["Web UI", "任务服务", "遥测服务", "时序数据库"], "delivery"),
    E("uml-usecase-shared", "use-case", "UML｜用例图（共享渲染器）", ["操作员", "自检与发射", "科学用户", "接收与回放"], "context"),
    E("uml-activity-shared", "activity", "UML｜活动图（共享渲染器）", ["开始", "采集数据", "电压正常？", "下传或安全模式"]),
    E("uml-state-shared", "state-machine", "UML｜状态机图（共享渲染器）", ["待机", "待发射", "下降", "安全模式"]),
    E("uml-sequence-shared", "sequence", "UML｜序列图（共享渲染器）", ["传感器", "飞控", "电台", "地面站"]),
    E("uml-package-shared", "package", "UML｜包图（共享渲染器）", ["Common", "Requirements", "Architecture", "Verification"], "hierarchy"),
    E("delivery", "delivery", "Delivery View｜源码到运行交付链", ["源码仓库", "构建与测试", "版本化交付物", "制品库／Release", "部署与运行"], "delivery"),
]

from examples._shared.layouts import build_layout


def build_spec(entry, output_dir):
    spec = build_layout(entry)
    spec["outputs"]["directory"] = output_dir
    return spec
