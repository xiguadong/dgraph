"""Build the root human/agent diagram-type routing README."""

from dgraph.catalog import CATALOG
from examples._shared.scaffold import ROOT, SYSML_TYPES, family_for, question_for, title_for


SEMANTIC_SPEC = '''{
  "schema": "diagram-view/v1",
  "type": "context",
  "intent": {"question": "系统边界在哪里？"},
  "sources": [],
  "selection": {
    "nodes": [
      {"id": "system", "label": "CS-1", "kind": "block", "x": 500, "y": 250, "w": 260, "h": 100, "sourceId": "demo.system"},
      {"id": "user", "label": "科学用户", "kind": "actor", "x": 100, "y": 250, "w": 100, "h": 100, "sourceId": "demo.user"}
    ],
    "edges": [
      {"source": "user", "target": "system", "kind": "association"}
    ]
  },
  "presentation": {"title": "CS-1 系统上下文"},
  "outputs": {"directory": "/absolute/output", "formats": ["viewspec", "dsl", "svg", "report"]}
}'''


def build_readme():
    sections = [f"""# dgraph

`dgraph` 是一个无内置模型的本地工程绘图 MCP。Kimi、Codex 或其他 MCP 客户端负责理解自然语言；dgraph 负责确定性的 ViewSpec 校验、SysML v2 编译、SVG 渲染和产物检查。

**没有 SysML 也可以直接绘图。**你可以只提供节点、关系、矩阵、图表或时间轴等语义输入。

## 快速开始

要求 Python 3.10+；随包 SysML 编译器适用于 Apple Silicon macOS。无需第三方 Python 包。

```bash
PYTHONPATH=/Users/xigua/life/SE/dgraph python3 -m dgraph
```

MCP 客户端配置示例（字段名以具体客户端为准）：

```json
{{
  "mcpServers": {{
    "dgraph": {{
      "command": "python3",
      "args": ["-m", "dgraph"],
      "env": {{"PYTHONPATH": "/Users/xigua/life/SE/dgraph"}}
    }}
  }}
}}
```

MCP 使用换行分隔的 JSON-RPC 消息。五个工具是：`list_diagram_types`、`analyze_sysml`、`validate_viewspec`、`render_diagram`、`inspect_diagram`。

## 输入方式 A：只有自然语言或结构化语义，没有 SysML

自然语言由客户端模型转换为 ViewSpec；dgraph 本身不内置模型。你也可以绕过模型，直接提交 JSON。

例如，对客户端说：

> 不使用 SysML。CS-1 是系统，科学用户是外部参与者，用户接收 CS-1 的遥测。画系统上下文图，突出系统边界。

对应的完整纯语义输入如下。`sources: []` 是合法值，不要求 `.sysml`，也不要求 Mermaid。

```json
{SEMANTIC_SPEC}
```

- `intent.question` 决定图要回答的问题；
- `selection.nodes/edges` 提供有依据的语义；
- `sourceId` 保留来源标识；
- `x/y/w/h` 是当前版本的布局约束；
- `outputs.directory` 必须是绝对路径。

可直接运行的完整示例：[`examples/context/semantic/`](examples/context/semantic/README.md)。

### 通过 MCP 调用

下面是完整的 JSON-RPC `tools/call` 请求。把 `spec` 换成你的 ViewSpec 即可：

```json
{{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {{
    "name": "render_diagram",
    "arguments": {{
      "spec": {SEMANTIC_SPEC}
    }}
  }}
}}
```

## 输入方式 B：已有 SysML v2 模型

SysML 模型回答“系统里有哪些事实”，当前用户意图回答“这次要说明什么问题”。已有 `view` 只作参考，不自动成为出图指令。

```text
.sysml 文件
  → analyze_sysml：冻结快照、parse、check、语义导出
  → 客户端按当前问题编写 ViewSpec
  → render_diagram：重新选择视图并渲染
```

`analyze_sysml` 输入示例：

```json
{{
  "files": [
    {{"name": "common.sysml", "content": "package Common {{ part def Power; }}"}},
    {{"name": "model.sysml", "content": "package Model {{ import Common::*; part def System {{ part power : Power; }} }}"}}
  ],
  "outputDir": "/absolute/output/sysml-analysis"
}}
```

原文件不会被修改。编译通过只代表实际执行的语法和支持的语义检查通过，不等于视图选择正确或工程验证完成。完整两步示例：[`examples/block-definition/sysml/`](examples/block-definition/sysml/README.md)。

## 支持图类型

每个图种都有独立的 `semantic/` 指南、自然语言参考、`input.json`、`draw.py` 和 `output/`。只有明确列出 SysML 参考的图种提供 `.sysml` 示例；`—` 表示不需要或没有 SysML 参考。

表头为 **视图类型 / 调用方法 / SysML 参考 / 自然语言参考**。调用方法列中的工具均为 `render_diagram`。点击参考链接进入对应目录。
"""]
    family = None
    for entry in CATALOG:
        kind = entry["type"]
        current_family = family_for(kind)
        if current_family != family:
            if family is not None:
                sections.append("")
            sections.append(f"### {current_family}\n")
            sections.append("| 视图类型 | 调用方法 | SysML 参考 | 自然语言参考 |\n| --- | --- | --- | --- |")
            family = current_family
        sysml = f"[SysML 参考](examples/{kind}/sysml/README.md)" if kind in SYSML_TYPES else "—"
        semantic = f"[自然语言参考](examples/{kind}/semantic/README.md)"
        sections.append(f"| {title_for(kind)}<br>`{kind}` | `render_diagram` | {sysml} | {semantic} |")
    return "\n".join(sections) + "\n"


if __name__ == "__main__":
    (ROOT / "README.md").write_text(build_readme(), encoding="utf-8")
    print("README.md regenerated from diagram catalog")
