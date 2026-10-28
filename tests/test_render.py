import hashlib
import tempfile
import unittest
from pathlib import Path

from dgraph.catalog import CATALOG
from dgraph.render import inspect_svg, render_diagram
from examples._shared.domain_examples import BPMN_MODEL, C4_CONTAINER_MODEL, DFD_MODEL, FTA_MODEL, GANTT_MODEL, N2_MODEL, QFD_MODEL, SEQUENCE_MODEL, UML_CLASS_MODEL


def spec(output, kind="block-definition", label="CS-1 <System>"):
    return {
        "schema": "diagram-view/v1", "type": kind,
        "intent": {"question": "What is shown?"}, "sources": [],
        "selection": {
            "nodes": [{"id": "a", "label": label, "kind": "block", "x": 100, "y": 140, "w": 220, "h": 80, "sourceId": "native-a"}],
            "edges": [], "groups": [], "annotations": [],
            "qfd": QFD_MODEL if kind == "qfd" else None,
            "gantt": GANTT_MODEL if kind == "gantt" else None,
            "faultTree": FTA_MODEL if kind == "fta" else None,
            "c4Container": C4_CONTAINER_MODEL if kind == "c4-container" else None,
            "umlClass": UML_CLASS_MODEL if kind == "class" else None,
            "sequenceModel": SEQUENCE_MODEL if kind == "sequence" else None,
            "n2Model": N2_MODEL if kind == "n2" else None,
            "dfdModel": DFD_MODEL if kind == "dfd" else None,
            "bpmnModel": BPMN_MODEL if kind == "bpmn" else None,
        },
        "presentation": {"title": "A & B", "subtitle": kind},
        "outputs": {"directory": output, "formats": ["viewspec", "dsl", "svg", "report"]},
    }


class RenderTests(unittest.TestCase):
    def test_renderer_escapes_xml_and_retains_source_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = render_diagram(spec(tmp))
            svg = Path(result["artifacts"]["svg"]).read_text()
            self.assertIn("CS-1 &lt;System&gt;", svg)
            self.assertIn("A &amp; B", svg)
            self.assertIn('data-source-id="native-a"', svg)

    def test_every_renderable_catalog_type_produces_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            for entry in CATALOG:
                if entry["status"] != "renderable":
                    continue
                with self.subTest(type=entry["type"]):
                    target = Path(tmp) / entry["type"]
                    result = render_diagram(spec(str(target), entry["type"]))
                    self.assertTrue(result["ok"])
                    self.assertIn("<svg", Path(result["artifacts"]["svg"]).read_text())

    def test_repeated_render_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = render_diagram(spec(tmp))
            digest = hashlib.sha256(Path(first["artifacts"]["svg"]).read_bytes()).hexdigest()
            second = render_diagram(spec(tmp))
            self.assertEqual(digest, hashlib.sha256(Path(second["artifacts"]["svg"]).read_bytes()).hexdigest())
            self.assertEqual(digest, second["manifest"]["files"]["diagram.svg"])

    def test_required_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = render_diagram(spec(tmp))
            for name in ("view.yaml", "diagram.dsl.yaml", "diagram.svg", "report.json", "manifest.json"):
                self.assertTrue((Path(tmp) / name).is_file(), name)

    def test_inspector_rejects_out_of_canvas_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"><text x="1400" y="20">bad</text></svg>')
            report = inspect_svg(path)
            self.assertFalse(report["ok"])
            self.assertTrue(any(issue["code"] == "out-of-canvas" for issue in report["issues"]))

    def test_edge_labels_are_above_nodes_and_associations_have_no_arrow(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp, "use-case")
            value["selection"]["nodes"].append({"id": "b", "label": "Goal", "kind": "usecase", "x": 500, "y": 140, "w": 220, "h": 80, "sourceId": "native-b"})
            value["selection"]["edges"].append({"source": "a", "target": "b", "kind": "association", "label": "RELATION_LABEL"})
            svg = Path(render_diagram(value)["artifacts"]["svg"]).read_text()
            self.assertGreater(svg.index("RELATION_LABEL"), svg.index('data-node-id="b"'))
            self.assertIn('stroke-dasharray="None" marker-end="none"', svg)

    def test_default_edge_label_is_on_the_edge_not_the_target(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp)
            value["selection"]["nodes"].append({"id": "b", "label": "Target", "kind": "block", "x": 500, "y": 140, "w": 220, "h": 80, "sourceId": "native-b"})
            value["selection"]["edges"].append({"source": "a", "target": "b", "kind": "association", "label": "MIDPOINT"})
            svg_path = Path(render_diagram(value)["artifacts"]["svg"])
            root = ET.parse(svg_path).getroot()
            label = next(element for element in root.iter("{http://www.w3.org/2000/svg}text") if element.text == "MIDPOINT")
            self.assertLess(float(label.attrib["x"]), 500)

    def test_mermaid_artifact_is_included_in_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = render_diagram(spec(tmp, "activity"))
            manifest = __import__("json").loads(Path(result["artifacts"]["manifest"]).read_text())
            self.assertIn("diagram.mmd", manifest["files"])
            self.assertEqual(hashlib.sha256(Path(result["artifacts"]["mmd"]).read_bytes()).hexdigest(), manifest["files"]["diagram.mmd"])


if __name__ == "__main__":
    unittest.main()
