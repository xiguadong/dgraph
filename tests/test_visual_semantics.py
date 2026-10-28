import tempfile
import unittest
from pathlib import Path

from dgraph.render import render_diagram
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec


class VisualSemanticTests(unittest.TestCase):
    def test_every_atlas_figure_has_its_own_layout_and_no_external_identity(self):
        self.assertGreaterEqual(len({entry["type"] for entry in ATLAS_ENTRIES}), 52)
        with tempfile.TemporaryDirectory() as tmp:
            for entry in ATLAS_ENTRIES:
                with self.subTest(type=entry["type"]):
                    svg = Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()
                    self.assertIn(f'data-layout="{entry["type"]}"', svg)
                    self.assertIn("Example.", svg)
                    self.assertNotIn("lesson", svg.lower())

    def test_representative_figures_use_domain_specific_primitives(self):
        expectations = {
            "opm": 'data-kind="usecase"',
            "dfd": 'data-kind="datastore"',
            "fta": 'data-fta-gate="or"',
            "cld": "B 调节回路",
            "sfd": 'data-kind="stock"',
            "class": 'data-uml-class="Sensor"',
            "object": 'data-kind="object"',
            "component": 'data-kind="component"',
            "deployment": 'data-kind="node3d"',
            "bpmn": 'data-kind="initial"',
            "kanban": "WIP",
            "story-map": "Release 1",
            "er": 'data-kind="decision"',
            "c4": 'data-group-id="context"',
            "delivery": "交付映射",
        }
        with tempfile.TemporaryDirectory() as tmp:
            for kind, marker in expectations.items():
                entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
                svg = Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()
                self.assertIn(marker, svg, kind)


if __name__ == "__main__":
    unittest.main()
