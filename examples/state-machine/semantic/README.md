# 状态机图（`state-machine`）

## 图种与用途

本图回答：**系统有哪些状态，事件或守卫如何触发迁移？**

适用于需要把这一问题讲清楚的评审、设计或维护场景。不要把它当作通用装饰图；问题改变时，应重新选择图种或视图。

## 示例图

![状态机图示例](output/diagram.svg)

## 自然语言输入示例

不使用 SysML，只根据以下语义画一张状态机图，回答“系统有哪些状态，事件或守卫如何触发迁移？”

图上的对象：
- standby：待机 Standby（来源 CanSat.Standby）。
- armed：待发射 Armed（来源 CanSat.Armed）。
- ascent：上升 Ascent（来源 CanSat.Ascent）。
- descent：下降 Descent（来源 CanSat.Descent）。
- landed：着陆 Landed（来源 CanSat.Landed）。
- replay：回放 Replay（来源 CanSat.Replay）。
- safe：安全模式 Safe（来源 CanSat.Safe）。
- selftest：自检 Self-test（来源 CanSat.SelfTestState）。
有依据的关系：
- standby → selftest：transition 启动。
- selftest → armed：transition 自检通过。
- armed → ascent：transition 发射。
- ascent → descent：transition 开伞。
- descent → landed：transition 触地。
- landed → replay：transition 回收连接。
- standby → safe：transition 。
- armed → safe：transition 。
- ascent → safe：transition 。
- descent → safe：transition 。
- landed → safe：transition 。
- replay → safe：transition 。
- selftest → safe：transition 。

保持来源标识，缺少依据的关系不要补充。

## 输入文件与语义说明

`input.json` 是纯语义 ViewSpec，本例不需要 `.sysml`。

- `intent.question`：本图回答的问题；
- `selection.nodes`：图上的对象，保留 `sourceId` 来源标识；
- `selection.edges`：有依据的关系；
- `selection.matrices/charts/timelines`：该图种需要时使用的专用原语；
- `x/y/w/h`：当前版本的布局约束；
- `outputs.directory`：由 `draw.py` 自动改为本目录的 `output/`。

示例语义标签：待机 Standby、待发射 Armed、上升 Ascent、下降 Descent、着陆 Landed、回放 Replay、安全模式 Safe、自检 Self-test。完整输入见 `input.json`。

## 如何运行

从 dgraph 根目录执行：

```bash
PYTHONPATH=. python3 examples/state-machine/semantic/draw.py
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
