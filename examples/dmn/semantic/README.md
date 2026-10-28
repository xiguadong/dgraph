# DMN｜决策规则表（`dmn`）

## 图种与用途

本图回答：**哪些输入和规则共同决定输出？**

适用于需要把这一问题讲清楚的评审、设计或维护场景。不要把它当作通用装饰图；问题改变时，应重新选择图种或视图。

## 示例图

![DMN｜决策规则表示例](output/diagram.svg)

## 自然语言输入示例

不使用 SysML，只根据以下语义画一张DMN｜决策规则表，回答“哪些输入和规则共同决定输出？”

以 `selection.dmnModel` 为图的语义模型：
- title：发射许可 Go / No-Go。
- hitPolicy：F。
- inputs：wind（风速）（unit="m/s"）。
- inputs：voltage（电池电压）（unit="V"）。
- inputs：selftest（自检）（unit="通过 / 失败"）。
- inputs：margin（链路裕度）（unit="dB"）。
- output：label="发射决策"。
- rules：1（conditions=["> 8", "—", "—", "—"]；result="No-Go"）。
- rules：2（conditions=["—", "< 6.4", "—", "—"]；result="No-Go"）。
- rules：3（conditions=["—", "—", "失败", "—"]；result="No-Go"）。
- rules：4（conditions=["—", "[6.4, 7.0)", "—", "—"]；result="Hold"）。
- rules：5（conditions=["—", "—", "—", "< 6"]；result="Hold"）。
- rules：6（conditions=["≤ 8", "≥ 7.0", "通过", "≥ 6"]；result="Go"）。

保持来源标识，缺少依据的关系不要补充。

## 输入文件与语义说明

`input.json` 是纯语义 ViewSpec，本例不需要 `.sysml`。

- `intent.question`：本图回答的问题；
- `selection.dmnModel`：本图权威语义，包含领域对象、数值与关系；
- `selection.nodes/edges`：仅供通用图使用，不能替代上述专用模型；
- `selection.matrices/charts/timelines`：该图种需要时使用的专用原语；
- `x/y/w/h`：当前版本的布局约束；
- `outputs.directory`：由 `draw.py` 自动改为本目录的 `output/`。

示例语义标签：风速、电池电压、自检、链路裕度。完整输入见 `input.json`。

## 如何运行

从 dgraph 根目录执行：

```bash
PYTHONPATH=. python3 examples/dmn/semantic/draw.py
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

1. 修改 `selection.dmnModel` 中的对象、数值与关系，保持内部 ID 引用一致；
2. 增加对象时同步补充有依据的关系，不编造事实；
3. 调整对应图元或布局约束后重新运行，不直接编辑 `output/diagram.svg`。

## 当前边界与常见问题

**没有 SysML 可以吗？** 可以，`semantic/` 示例就是纯语义输入。

**必须写 Mermaid 吗？** 不需要。Mermaid 只是部分图种的可选导出，SVG 与 YAML DSL 才是完整产物。

**这是任意规模的自动布局吗？** 不是。本例验证图种渲染；复杂项目仍需减少元素并做最终视觉复核。
