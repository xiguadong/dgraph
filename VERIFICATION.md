# Verification

## Checkpoint 1 — Catalog and ViewSpec

Command: `PYTHONPATH=dgraph python3 -m unittest discover -s dgraph/tests -p 'test_viewspec.py' -v`

Result: 6 tests passed. The initial run failed with `ModuleNotFoundError: dgraph.catalog` before implementation.

## Checkpoint 2 — SVG renderer and artifacts

Command: `PYTHONPATH=dgraph python3 -m unittest discover -s dgraph/tests -p 'test_render.py' -v`

Result: 5 tests passed. The initial run failed with `ModuleNotFoundError: dgraph.render` before implementation.

## Checkpoint 3 — Pinned SysML compiler

Command: `PYTHONPATH=dgraph python3 -m unittest discover -s dgraph/tests -p 'test_sysml.py' -v`

Result: 3 integration tests passed against the real compiler: valid multi-file export, invalid-source diagnostics, and immutable input/snapshots. The initial run failed with `ModuleNotFoundError: dgraph.sysml`.

Compiler SHA-256: `674fce28512a772d1886ff2397f5f02dda66265299c67c01f5cc36eaf00207f6`.

## Checkpoint 4 — MCP stdio

Command: `PYTHONPATH=dgraph python3 -m unittest discover -s dgraph/tests -p 'test_mcp.py' -v`

Result: 2 protocol tests passed for initialize/discovery/resources/render and structured unknown-tool errors. The initial run failed because `dgraph.__main__` did not exist.

## Checkpoint 5 — Nine-view acceptance set

Command: `PYTHONPATH=dgraph python3 dgraph/examples/generate_nine.py`

Result: all nine views were generated through public `render_diagram`. `examples/cansat/model.sysml` passed parse/check/export with 259 elements in the native semantic export.

## Final verification — 2026-10-27

Command: `PYTHONPATH=dgraph python3 -m unittest discover -s dgraph/tests -v`

Result: **19 tests passed**. Additional regression tests caught and verified fixes for edge-label occlusion, association arrows, and Mermaid manifest hashes before the final run.

Visual review: all nine SVGs were rasterized with headless Chrome at 1280×720 and inspected. The contact sheet and dense IBD, requirements, sequence, state-machine, activity, package, parametric, use-case, and BDD figures were reviewed. Edge-label layering and two crowded label positions were corrected and regenerated. Final images are under `output/cansat/previews/`; `output/cansat/contact-sheet.png` is the nine-view overview.

Scope limit: automated inspection proves SVG parsing, canvas text bounds, and source identity. It does not prove arbitrary-input layout quality, complete SysML view inference, or engineering correctness. This was the v0.1.0 nine-view scope; the expanded scope follows.

## Atlas expansion verification — 2026-10-27, v0.2.0

Coverage: 61 renderable types, all 65 lesson_2 figure mappings, 56 additional lesson figures plus Delivery View. Five UML figures reuse the existing activity, sequence, state-machine, use-case, and package adapters.

Command: `PYTHONPATH=. python3 -m unittest discover -s tests -v`

Result: **28 tests passed**, including real MCP stdio calls, pinned SysML compilation, all 61 catalog renderers, matrix/line/scatter/timeline primitives, all 57 expanded figures, and regression tests for edge-label placement and flame/delivery structure.

Command: `PYTHONPATH=. python3 examples/verify_atlas.py`

Result: verified **57 expanded figures, 231 hashed artifacts, and all previews**. `output/atlas/index.html` is the browser index and `output/atlas/contact-sheet.png` is the overview.

Visual review: all 57 SVGs were rasterized at 1280×720. N², QFD, Gantt, burndown, IDEF0, Delivery, flame, Tradespace, and Kanban representatives were inspected at full size. Default edge-label placement was moved to the edge midpoint; Delivery labels were moved above nodes; Tradespace became a scatter plot; flame became stacked frames; Kanban became a horizontal workflow. The final Delivery layout was re-rendered and inspected.

Scope limit: these examples demonstrate each renderer, not automatic diagram selection or arbitrary-size automatic layout. Real projects still require concern-driven ViewSpec selection, model-fact checks, content reduction, and final visual review.

## Example-router migration — 2026-10-27

Layout: 61 canonical `examples/{type}/semantic/` examples and 10 explicit `examples/{type}/sysml/` examples. Every semantic example has the seven approved README sections, natural-language input, `input.json`, thin `draw.py`, and local output. SysML examples additionally have `model.sysml` and a two-step analysis/render guide.

Migration check: `PYTHONPATH=. python3 cache/check_migration.py` verified SVG identity for **61 canonical figures** before legacy deletion. The old top-level `output/`, `examples/cansat/`, `examples/sysml/`, and four legacy generator/verifier scripts were then removed. Shared source data remains under `examples/_shared/`.

Command: `PYTHONPATH=. python3 examples/draw_all.py`

Result: generated **61 semantic + 10 SysML examples** through the public APIs.

Command: `PYTHONPATH=. python3 examples/verify_examples.py`

Result: verified **292 hashed artifacts** and all required example files; legacy `output/` is absent.

Command: `PYTHONPATH=. python3 cache/verify_readme_json.py`

Result: all **4 README JSON blocks** parse; the pure-semantic spec and the full JSON-RPC `render_diagram` spec both pass `validate_spec`.

Command: `PYTHONPATH=. python3 -m unittest discover -s tests -v`

Result: **33 tests passed**, including every-type README routing, complete example layout, exact SysML scope, deleted legacy sections, all previous renderer/compiler/MCP tests, and legacy-output removal.

Root README now ends with the 61-row, four-column diagram routing table. Per-example questions and prompts are in Chinese; non-applicable SysML cells are `—` rather than fabricated references.
