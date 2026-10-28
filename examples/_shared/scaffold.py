"""Generate canonical per-type example folders, inputs, and human/agent guides."""

import json
from pathlib import Path

from dgraph.catalog import CATALOG
from dgraph.viewspec import DOMAIN_FIELDS
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
SYSML_TYPES = {"block-definition", "internal-block", "requirements", "parametric", "use-case", "activity", "sequence", "state-machine", "package", "sysml-v2"}
NINE = SYSML_TYPES - {"sysml-v2"}
ENTRY_BY_TYPE = {}
for _entry in ATLAS_ENTRIES:
    ENTRY_BY_TYPE.setdefault(_entry["type"], _entry)

TITLES = {
    "block-definition": "块定义图 BDD", "internal-block": "内部块图 IBD", "requirements": "需求图",
    "parametric": "参数图", "use-case": "用例图", "activity": "活动图",
    "sequence": "序列图", "state-machine": "状态机图", "package": "包图",
}
QUESTIONS = {entry["type"]: entry["question"] for entry in CATALOG}
QUESTION_ZH = {
    "block-definition": "系统由哪些类型、部件和组合关系构成？",
    "internal-block": "内部部件、端口与接口如何连接？",
    "requirements": "需求如何派生、由谁满足，并由什么验证？",
    "parametric": "哪些约束和参数绑定决定工程性能？",
    "use-case": "哪些参与者在系统边界上使用哪些能力？",
    "activity": "动作、判断和控制流如何推进？",
    "sequence": "生命线之间按什么顺序交换消息？",
    "state-machine": "系统有哪些状态，事件或守卫如何触发迁移？",
    "package": "模型如何分包，依赖方向是什么？",
    "sysml-v2": "如何从关注点形成视点，再选择模型内容形成视图？",
    "opm": "对象与过程如何共同表达概念模型？",
    "c4": "如何用 C4 的缩放层级讲清软件架构？",
    "context": "系统边界在哪里，哪些外部实体与系统交互？",
    "ffbd": "功能如何串联、并行和迭代？",
    "n2": "系统元素之间有哪些接口，矩阵如何揭示耦合？",
    "idef0": "功能的输入、输出、控制和机制分别是什么？",
    "dfd": "数据如何在处理、存储和外部实体之间流动？",
    "qfd": "客户需求如何映射为工程特性？",
    "tradespace": "哪些方案位于目标空间的 Pareto 前沿？",
    "fta": "哪些基础失效会组合成顶事件？",
    "cld": "变量之间有哪些增强和调节反馈回路？",
    "sfd": "系统中的存量、流量和速率如何相互作用？",
    "dodaf": "不同视点如何共同描述体系架构？",
    "ov1": "任务背景、参与者和运行概念是什么？",
    "sv1": "系统之间有哪些资源接口？",
    "cv2": "能力如何分解和关联？",
    "arcadia": "如何从运行分析逐层走到物理实现？",
    "wbs": "项目工作如何分解为可管理活动？",
    "pbs": "产品如何分解为物理组成部分？",
    "gantt": "任务何时开始和结束，依赖与里程碑在哪里？",
    "pert": "哪些依赖和路径决定项目工期？",
    "risk-matrix": "概率与影响如何共同决定风险优先级？",
    "burndown": "剩余工作如何随迭代变化？",
    "class": "类、特征和关系如何描述软件类型？",
    "object": "某一时刻有哪些对象实例和链接？",
    "component": "组件如何通过提供和需要的接口协作？",
    "composite-structure": "类内部的部件和连接器如何组织？",
    "deployment": "交付物和软件实例部署到哪些节点？",
    "profile": "构造型如何扩展 UML 元模型？",
    "communication": "对象之间有哪些交互关系，不强调时间轴时如何表达？",
    "interaction-overview": "多个交互片段如何编排？",
    "timing": "状态和消息如何满足时间约束？",
    "event-storming": "事件、命令、聚合和策略如何形成业务叙事？",
    "impact-map": "目标如何连接到参与者、影响和交付物？",
    "module-dependency": "代码模块之间有哪些依赖？",
    "class-hierarchy": "类之间如何继承和特化？",
    "eta": "初始事件之后可能出现哪些后果路径？",
    "kanban": "工作如何流过各阶段，在制品如何受控？",
    "bpmn": "参与者、任务、网关和事件如何形成业务流程？",
    "archimate": "业务、应用和技术层如何关联？",
    "cicd": "代码如何经过检查、制品、关口和部署？",
    "deployment-topology": "网络、节点、服务和链路如何组成运行拓扑？",
    "flame-graph": "哪些调用栈帧占据主要执行时间？",
    "call-graph": "函数之间如何调用？",
    "story-map": "用户活动、任务和发布如何组织故事？",
    "ddd-context-map": "限界上下文及其关系如何交互？",
    "dmn": "哪些输入和规则共同决定输出？",
    "er": "实体、属性和基数如何描述数据？",
    "c4-context": "系统周围有哪些人员和外部软件系统？",
    "c4-container": "系统由哪些可部署容器组成？",
    "delivery": "源码如何构建成交付物，存储、部署并进入运行与维护？",
}


def question_for(kind):
    return QUESTION_ZH[kind]


def title_for(kind):
    if kind in TITLES:
        return TITLES[kind]
    return ENTRY_BY_TYPE.get(kind, {"title": kind}).get("title", kind)


def family_for(kind):
    if kind in SYSML_TYPES:
        return "SysML 与模型视图"
    if kind in {"opm", "c4", "context", "ffbd", "n2", "idef0", "dfd", "qfd", "tradespace", "fta", "cld", "sfd"}:
        return "OPM 与经典系统工程"
    if kind in {"dodaf", "ov1", "sv1", "cv2", "arcadia"}:
        return "体系架构框架"
    if kind in {"wbs", "pbs", "gantt", "pert", "risk-matrix", "burndown"}:
        return "项目管理"
    if kind in {"class", "object", "component", "composite-structure", "deployment", "profile", "communication", "interaction-overview", "timing"}:
        return "UML 补充图"
    if kind == "delivery":
        return "交付与维护"
    return "软件、数据与运行"


def semantic_spec(kind):
    if kind in NINE:
        return json.loads((EXAMPLES / "_shared/cansat" / f"{kind}.yaml").read_text(encoding="utf-8"))
    entry = ENTRY_BY_TYPE[kind]
    return build_spec(entry, "/absolute/output")


def _labels(spec):
    field = DOMAIN_FIELDS.get(spec["type"])
    if field:
        model = spec["selection"].get(field) or {}
        for name in ("customerNeeds", "tasks", "events", "containers", "classes", "participants", "elements", "processes", "risks", "inputs", "lifelines", "alternatives"):
            if model.get(name):
                return [item.get("label", item.get("id", "")) for item in model[name]]
    return [node["label"].replace("\n", " ") for node in spec["selection"].get("nodes", [])]


def _facts(kind, spec):
    field = DOMAIN_FIELDS.get(kind)
    selection = spec["selection"]
    if field:
        model = selection[field]
        lines = [f"以 `selection.{field}` 为图的语义模型："]
        for name, value in model.items():
            if isinstance(value, list):
                if value and isinstance(value[0], dict):
                    for item in value:
                        identity = f"{item['id']}（{item['label']}）" if item.get("id") and item.get("label") else item.get("label", item.get("id", f"{item.get('source', '')} → {item.get('target', '')}"))
                        detail = "；".join(f"{key}={json.dumps(child, ensure_ascii=False)}" for key, child in item.items() if key not in {"id", "label"})
                        lines.append(f"- {name}：{identity}" + (f"（{detail}）" if detail else "") + "。")
                else:
                    lines.append(f"- {name}：{'、'.join(map(str, value))}。")
            elif isinstance(value, dict):
                detail = "；".join(f"{key}={json.dumps(child, ensure_ascii=False)}" for key, child in value.items())
                lines.append(f"- {name}：{detail}。")
            else:
                lines.append(f"- {name}：{value}。")
        return "\n".join(lines)
    lines = ["图上的对象："]
    for node in selection.get("nodes", []):
        label = node["label"].replace("\n", " ") or node.get("kind", "图元")
        lines.append(f"- {node['id']}：{label}（来源 {node['sourceId']}）。")
    if selection.get("edges"):
        lines.append("有依据的关系：")
        for edge in selection["edges"]:
            lines.append(f"- {edge['source']} → {edge['target']}：{edge.get('kind', '')} {edge.get('label', '')}。")
    return "\n".join(lines)


def _prompt(kind, spec):
    return f"不使用 SysML，只根据以下语义画一张{title_for(kind)}，回答“{question_for(kind)}”\n\n{_facts(kind, spec)}\n\n保持来源标识，缺少依据的关系不要补充。"


def _readme(kind, mode, spec):
    title = title_for(kind)
    labels = _labels(spec)
    is_sysml = mode == "sysml"
    field = DOMAIN_FIELDS.get(kind)
    kinds = {source.get("kind") for source in spec.get("sources", [])}
    overlay = is_sysml and kinds == {"semantic"}
    input_description = ("`model.sysml` 先经过编译检查；`input.json` 声明图的来源与视图内容。"
                         if is_sysml else "`input.json` 是纯语义 ViewSpec，本例不需要 `.sysml`。")
    prompt = _prompt(kind, spec) if not is_sysml else (
        f"先编译 `model.sysml`。本图采用课件教学语义，按 `input.json` 的对象、关系和来源绘制{title}；不要把教学补充内容称为已编译模型事实。"
        if overlay else f"读取 `model.sysml`，核对 `sourceId` 所指的真实模型元素，结合“{question_for(kind)}”选择视图并绘制{title}。")
    model_section = """
## 模型与视图的关系

- `model.sysml` 先经过解析和语义检查，原文件只读；
- `input.json` 的 `sources.kind` 标明图的来源；`semantic` 表示课件教学补充语义，不能冒充模型元素；
- 仅当 `sources.kind=sysml` 且 `sourceId` 与编译导出的元素匹配时，才声明该视图直接引用模型事实；
- 不自动继承模型已有的 `view`；
- 先运行 `analyze_sysml`，核对 `view-provenance.json`，再运行 `render_diagram`；编译通过不等于图义或工程验证正确。
""" if is_sysml else ""
    semantic_description = (
        f"- `selection.{field}`：本图权威语义，包含领域对象、数值与关系；\n"
        "- `selection.nodes/edges`：仅供通用图使用，不能替代上述专用模型；"
        if field else
        "- `selection.nodes`：图上的对象，保留 `sourceId` 来源标识；\n"
        "- `selection.edges`：有依据的关系；"
    )
    editing_steps = (
        f"1. 修改 `selection.{field}` 中的对象、数值与关系，保持内部 ID 引用一致；"
        if field else
        "1. 修改节点 `label` 和稳定 `sourceId`，换成自己的对象；"
    )
    return f"""# {title}（`{kind}`）

## 图种与用途

本图回答：**{question_for(kind)}**

适用于需要把这一问题讲清楚的评审、设计或维护场景。不要把它当作通用装饰图；问题改变时，应重新选择图种或视图。

## 示例图

![{title}示例](output/diagram.svg)

## 自然语言输入示例

{prompt}

## 输入文件与语义说明

{input_description}

- `intent.question`：本图回答的问题；
{semantic_description}
- `selection.matrices/charts/timelines`：该图种需要时使用的专用原语；
- `x/y/w/h`：当前版本的布局约束；
- `outputs.directory`：由 `draw.py` 自动改为本目录的 `output/`。

示例语义标签：{'、'.join(labels)}。完整输入见 `input.json`。
{model_section}
## 如何运行

从 dgraph 根目录执行：

```bash
PYTHONPATH=. python3 examples/{kind}/{mode}/draw.py
```

脚本只调用公共 API，不绕过渲染器，也不直接手写 SVG。

## 输出文件

```text
output/
├── diagram.svg        # 最终图
├── view.yaml          # 实际执行的 ViewSpec
├── diagram.dsl.yaml   # 图形语义与布局
├── report.json        # 校验与检查结果
└── manifest.json      # 输入与产物哈希
```

部分图种另有 `diagram.mmd`；SysML 示例另有 `output/sysml-analysis/`。

## 如何改成自己的图

{editing_steps}
2. 增加对象时同步补充有依据的关系，不编造事实；
3. 调整对应图元或布局约束后重新运行，不直接编辑 `output/diagram.svg`。

## 当前边界与常见问题

**没有 SysML 可以吗？** 可以，`semantic/` 示例就是纯语义输入。

**必须写 Mermaid 吗？** 不需要。Mermaid 只是部分图种的可选导出，SVG 与 YAML DSL 才是完整产物。

**这是任意规模的自动布局吗？** 不是。本例验证图种渲染；复杂项目仍需减少元素并做最终视觉复核。
"""


def _runner_source(mode):
    return f"""from pathlib import Path
from examples._shared.runner import run_{mode}

if __name__ == "__main__":
    result = run_{mode}(Path(__file__).resolve().parent)
    if not result.get("ok"):
        raise SystemExit(result)
    print(result["artifacts"]["svg"])
"""


def _write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scaffold_examples():
    for entry in CATALOG:
        kind = entry["type"]
        spec = semantic_spec(kind)
        for mode in (["sysml", "semantic"] if kind in SYSML_TYPES else ["semantic"]):
            folder = EXAMPLES / kind / mode
            folder.mkdir(parents=True, exist_ok=True)
            spec["outputs"]["directory"] = "/absolute/output"
            _write_json(folder / "input.json", spec)
            (folder / "README.md").write_text(_readme(kind, mode, spec), encoding="utf-8")
            (folder / "draw.py").write_text(_runner_source(mode), encoding="utf-8")
            if mode == "sysml":
                source = EXAMPLES / "_shared/cansat/model.sysml" if kind in NINE else EXAMPLES / "_shared/sysml/viewpoint.sysml"
                (folder / "model.sysml").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return len(CATALOG), len(SYSML_TYPES)


def gallery_html():
    cards = []
    for entry in CATALOG:
        kind = entry["type"]
        cards.append(f'<div class="card"><a href="{kind}/semantic/output/diagram.svg"><img loading="lazy" src="{kind}/semantic/output/diagram.svg"><span>{title_for(kind)}</span></a><small>{kind} · <a href="{kind}/semantic/README.md">语义指南</a></small></div>')
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>dgraph 图种路由</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;margin:32px;background:#f5f7fb;color:#15202b}h1{font-size:30px}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.card{background:white;border:1px solid #dbe3ef;border-radius:12px;padding:10px;text-decoration:none;color:#173d73}.card img{width:100%}.card span{display:block;font-weight:700;margin-top:8px}.card small{color:#64748b}@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}</style></head><body><h1>dgraph 图种路由</h1><p>61 个独立语义示例；点击图查看 SVG，点击语义指南查看输入和调用。</p><div class="grid">""" + "".join(cards) + "</div></body></html>"
