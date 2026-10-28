import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from dgraph.render import render_diagram
from dgraph.viewspec import DgraphError, validate_spec
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec


class SoftwareSemanticTests(unittest.TestCase):
    def render(self, kind, tmp):
        entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
        return Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()

    def test_c4_container_has_actors_boundary_containers_and_protocols(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("c4-container", tmp)
            self.assertIn('data-c4-boundary="ground-station"', svg)
            self.assertIn('data-c4-actor="operator"', svg)
            self.assertIn('data-c4-actor="scientist"', svg)
            for container in ("Web UI", "任务服务", "时序数据库", "遥测服务"):
                self.assertIn(container, svg)
            for protocol in ("REST", "查询", "写入", "串口"):
                self.assertIn(protocol, svg)

    def test_uml_class_has_three_compartments_and_multiplicity(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("class", tmp)
            for class_name in ("GroundStation", "Mission", "Sensor", "TelemetryFrame"):
                self.assertIn(f'data-uml-class="{class_name}"', svg)
            for member in ("stationId: String", "rateHz: int", "startSession()", "crcOk(): bool"):
                self.assertIn(member, svg)
            self.assertIn('data-uml-relation="produces"', svg)
            self.assertIn("0..*", svg)
            root = ET.fromstring(svg)
            relations = [element for element in root.iter() if "data-uml-relation" in element.attrib]
            self.assertEqual(3, len(relations))
            for relation in relations:
                self.assertEqual("association", relation.attrib["data-uml-kind"])
                self.assertNotIn("marker-end", relation.attrib)

    def test_sequence_has_lifelines_activations_and_ordered_messages(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("sequence", tmp)
            self.assertEqual(4, svg.count("data-sequence-lifeline"))
            self.assertGreaterEqual(svg.count("data-sequence-activation"), 3)
            for message in ("1 读取采样", "2 温压湿 / IMU / GPS", "3 打包 TelemetryFrame", "4 UART 遥测帧", "5 433 MHz 下行"):
                self.assertIn(message, svg)
            self.assertIn('data-sequence-return="true"', svg)

    def test_software_domains_reject_missing_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind, field in (("c4-container", "c4Container"), ("class", "umlClass"), ("sequence", "sequenceModel")):
                entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
                spec = build_spec(entry, tmp)
                del spec["selection"][field]
                with self.subTest(type=kind):
                    with self.assertRaisesRegex(DgraphError, field):
                        validate_spec(spec)


if __name__ == "__main__":
    unittest.main()
