# 用户故事地图｜活动与发布（`story-map`）

## 图种与用途

本图回答：**用户活动、任务和发布如何组织故事？**

适用于需要把这一问题讲清楚的评审、设计或维护场景。不要把它当作通用装饰图；问题改变时，应重新选择图种或视图。

## 示例图

![用户故事地图｜活动与发布示例](output/diagram.svg)

## 自然语言输入示例

不使用 SysML，只根据以下语义画一张用户故事地图｜活动与发布，回答“用户活动、任务和发布如何组织故事？”

图上的对象：
- n0：准备任务（来源 Example.x-storymap.n0）。
- n1：执行探空（来源 Example.x-storymap.n1）。
- n2：接收数据（来源 Example.x-storymap.n2）。
- n3：回收分析（来源 Example.x-storymap.n3）。
- n4：配置站点（来源 Example.x-storymap.n4）。
- n5：看实时遥测（来源 Example.x-storymap.n5）。
- n6：导入存储帧（来源 Example.x-storymap.n6）。
- n7：画曲线（来源 Example.x-storymap.n7）。
- n8：多站点模板（来源 Example.x-storymap.n8）。
- n9：异常告警（来源 Example.x-storymap.n9）。
- n10：异常帧回放（来源 Example.x-storymap.n10）。
- n11：导出报告（来源 Example.x-storymap.n11）。

保持来源标识，缺少依据的关系不要补充。

## 输入文件与语义说明

`input.json` 是纯语义 ViewSpec，本例不需要 `.sysml`。

- `intent.question`：本图回答的问题；
- `selection.nodes`：图上的对象，保留 `sourceId` 来源标识；
- `selection.edges`：有依据的关系；
- `selection.matrices/charts/timelines`：该图种需要时使用的专用原语；
- `x/y/w/h`：当前版本的布局约束；
- `outputs.directory`：由 `draw.py` 自动改为本目录的 `output/`。

示例语义标签：准备任务、执行探空、接收数据、回收分析、配置站点、看实时遥测、导入存储帧、画曲线、多站点模板、异常告警、异常帧回放、导出报告。完整输入见 `input.json`。

## 如何运行

从 dgraph 根目录执行：

```bash
PYTHONPATH=. python3 examples/story-map/semantic/draw.py
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

1. 修改节点 `label` 和稳定 `sourceId`，换成自己的对象；
2. 增加对象时同步补充有依据的关系，不编造事实；
3. 调整对应图元或布局约束后重新运行，不直接编辑 `output/diagram.svg`。

## 当前边界与常见问题

**没有 SysML 可以吗？** 可以，`semantic/` 示例就是纯语义输入。

**必须写 Mermaid 吗？** 不需要。Mermaid 只是部分图种的可选导出，SVG 与 YAML DSL 才是完整产物。

**这是任意规模的自动布局吗？** 不是。本例验证图种渲染；复杂项目仍需减少元素并做最终视觉复核。
