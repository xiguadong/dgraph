import tempfile
import unittest
from pathlib import Path

from dgraph.render import render_diagram
from dgraph.viewspec import DgraphError, validate_spec
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec


class ProcessSemanticTests(unittest.TestCase):
    def render(self, kind, tmp):
        entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
        return Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()

    def test_n2_has_six_elements_typed_interfaces_and_strong_coupling(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("n2", tmp)
            for element in ("结构", "电源", "飞控", "传感器", "通信", "地面站"):
                self.assertIn(element, svg)
            for interface in ("I-01", "I-02", "I-03", "I-04"):
                self.assertIn(interface, svg)
            self.assertIn("行 = 提供方", svg)
            self.assertIn("列 = 接收方", svg)
            self.assertIn("强耦合", svg)
            self.assertIn('data-n2-external="ground"', svg)

    def test_dfd_has_processes_stores_and_named_flows(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("dfd", tmp)
            self.assertIn('data-dfd-process="sampling"', svg)
            self.assertIn('data-dfd-store="telemetry-log"', svg)
            for flow in ("原始采样", "遥测帧", "433 MHz 下行", "存储帧", "回放数据"):
                self.assertIn(flow, svg)

    def test_bpmn_has_events_gateway_and_two_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("bpmn", tmp)
            self.assertIn('data-bpmn-event="start"', svg)
            self.assertIn('data-bpmn-event="end"', svg)
            self.assertIn('data-bpmn-gateway="quality"', svg)
            self.assertIn("接收并解码帧", svg)
            self.assertIn("入库", svg)
            self.assertIn("标记异常", svg)
            self.assertIn('data-bpmn-branch="unavailable"', svg)

    def test_process_domains_reject_missing_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind, field in (("n2", "n2Model"), ("dfd", "dfdModel"), ("bpmn", "bpmnModel")):
                entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
                spec = build_spec(entry, tmp)
                del spec["selection"][field]
                with self.subTest(type=kind):
                    with self.assertRaisesRegex(DgraphError, field):
                        validate_spec(spec)


if __name__ == "__main__":
    unittest.main()
