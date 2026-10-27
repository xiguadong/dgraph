# dgraph 示例路由

每个图种都有独立 `semantic/` 示例，包含有针对性的 README、自然语言输入、ViewSpec、可运行 `draw.py` 和本地 `output/`。

九类 SysML 图和 `sysml-v2` 另有 `sysml/` 两步参考：`analyze_sysml` 读取模型事实，`render_diagram` 按当前问题重新选择视图。其他图种不需要也不伪造 SysML。

```bash
PYTHONPATH=. python3 examples/draw_all.py
PYTHONPATH=. python3 examples/verify_examples.py
```

从仓库根目录的 README 图种表进入具体示例；`index.html` 可浏览全部语义图。
