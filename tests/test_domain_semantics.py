import tempfile
import unittest
from pathlib import Path

from dgraph.render import render_diagram
from dgraph.viewspec import DgraphError, validate_spec
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec


class DomainSemanticTests(unittest.TestCase):
    def render(self, kind, tmp):
        entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
        return Path(render_diagram(build_spec(entry, tmp))["artifacts"]["svg"]).read_text()

    def test_qfd_has_roof_relationships_targets_weights_and_ranks(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("qfd", tmp)
            self.assertIn('data-qfd-roof="engineering-correlation"', svg)
            self.assertIn('data-qfd-relation="data-integrity:sample-rate"', svg)
            self.assertIn("≥ 1 Hz", svg)
            self.assertIn("权重", svg)
            self.assertIn("排序", svg)

    def test_gantt_has_time_ticks_dependencies_and_milestones(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("gantt", tmp)
            for tick in ("W1", "W3", "W5", "W7", "W9", "W11"):
                self.assertIn(tick, svg)
            self.assertIn('data-gantt-dependency="design:manufacture"', svg)
            self.assertIn('data-gantt-milestone="pdr"', svg)
            self.assertIn('data-gantt-milestone="cdr"', svg)

    def test_fta_has_one_or_gate_and_four_basic_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = self.render("fta", tmp)
            self.assertIn('data-fta-gate="or"', svg)
            self.assertEqual(4, svg.count("data-fta-basic-event"))
            self.assertNotIn('data-fta-gate="and"', svg)
            for event in ("电池耗尽", "天线断裂", "软件死锁", "地面站失锁"):
                self.assertIn(event, svg)

    def test_domain_specs_reject_missing_required_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind, field in (("qfd", "qfd"), ("gantt", "gantt"), ("fta", "faultTree")):
                entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
                spec = build_spec(entry, tmp)
                del spec["selection"][field]
                with self.subTest(type=kind):
                    with self.assertRaisesRegex(DgraphError, field):
                        validate_spec(spec)


if __name__ == "__main__":
    unittest.main()
