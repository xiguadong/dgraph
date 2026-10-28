# 风险矩阵｜概率与影响（`risk-matrix`）

## 图种与用途

本图回答：**概率与影响如何共同决定风险优先级？**

适用于需要把这一问题讲清楚的评审、设计或维护场景。不要把它当作通用装饰图；问题改变时，应重新选择图种或视图。

## 示例图

![风险矩阵｜概率与影响示例](output/diagram.svg)

## 自然语言输入示例

不使用 SysML，只根据以下语义画一张风险矩阵｜概率与影响，回答“概率与影响如何共同决定风险优先级？”

以 `selection.riskMatrix` 为图的语义模型：
- probability：极低、低、中、高、极高。
- consequence：可忽略、轻微、中等、严重、灾难。
- risks：R-01（电池低温）（probability=4；consequence=3）。
- risks：R-02（链路失锁）（probability=3；consequence=4）。
- risks：R-03（进度压缩）（probability=4；consequence=4）。
- risks：R-04（开伞失效）（probability=2；consequence=5）。
- risks：R-05（质量超限）（probability=3；consequence=3）。

保持来源标识，缺少依据的关系不要补充。

## 输入文件与语义说明

`input.json` 是纯语义 ViewSpec，本例不需要 `.sysml`。

- `intent.question`：本图回答的问题；
- `selection.riskMatrix`：本图权威语义，包含领域对象、数值与关系；
- `selection.nodes/edges`：仅供通用图使用，不能替代上述专用模型；
- `selection.matrices/charts/timelines`：该图种需要时使用的专用原语；
- `x/y/w/h`：当前版本的布局约束；
- `outputs.directory`：由 `draw.py` 自动改为本目录的 `output/`。

示例语义标签：电池低温、链路失锁、进度压缩、开伞失效、质量超限。完整输入见 `input.json`。

## 如何运行

从 dgraph 根目录执行：

```bash
PYTHONPATH=. python3 examples/risk-matrix/semantic/draw.py
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

1. 修改 `selection.riskMatrix` 中的对象、数值与关系，保持内部 ID 引用一致；
2. 增加对象时同步补充有依据的关系，不编造事实；
3. 调整对应图元或布局约束后重新运行，不直接编辑 `output/diagram.svg`。

## 当前边界与常见问题

**没有 SysML 可以吗？** 可以，`semantic/` 示例就是纯语义输入。

**必须写 Mermaid 吗？** 不需要。Mermaid 只是部分图种的可选导出，SVG 与 YAML DSL 才是完整产物。

**这是任意规模的自动布局吗？** 不是。本例验证图种渲染；复杂项目仍需减少元素并做最终视觉复核。
