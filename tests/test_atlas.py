import tempfile
import unittest
from pathlib import Path

from dgraph.render import inspect_svg, render_diagram
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec


class AtlasTests(unittest.TestCase):
    def test_remaining_56_atlas_figures_and_delivery_render_through_public_tool(self):
        self.assertEqual(57, len(ATLAS_ENTRIES))
        self.assertEqual(57, len({entry["slug"] for entry in ATLAS_ENTRIES}))
        with tempfile.TemporaryDirectory() as tmp:
            for entry in ATLAS_ENTRIES:
                with self.subTest(figure=entry["slug"]):
                    result = render_diagram(build_spec(entry, tmp))
                    self.assertTrue(result["ok"])
                    svg = Path(result["artifacts"]["svg"])
                    self.assertGreater(svg.stat().st_size, 2500)
                    self.assertTrue(inspect_svg(svg)["ok"])
                    self.assertIn("Example.", svg.read_text())

    def test_specialized_figures_use_their_own_primitives(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases = {"n2": "data-matrix-cell", "qfd": "data-qfd", "risk-matrix": "data-matrix", "burndown": "data-chart-series", "tradespace": "data-chart-series", "gantt": "data-gantt-task", "delivery": "publishes"}
            for kind, marker in cases.items():
                entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
                svg = Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()
                self.assertIn(marker, svg)

    def test_delivery_relation_labels_sit_above_the_nodes(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as tmp:
            entry = next(item for item in ATLAS_ENTRIES if item["type"] == "delivery")
            path = Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"])
            root = ET.parse(path).getroot()
            labels = [element for element in root.iter("{http://www.w3.org/2000/svg}text") if element.text == "publishes"]
            self.assertEqual(1, len(labels))
            self.assertLess(float(labels[0].attrib["y"]), 290)

    def test_flame_graph_uses_frames_not_a_gantt_timeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = next(item for item in ATLAS_ENTRIES if item["type"] == "flame-graph")
            svg = Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()
            self.assertNotIn("data-timeline", svg)
            self.assertIn('kind="flame"', svg)


if __name__ == "__main__":
    unittest.main()
