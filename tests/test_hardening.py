import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dgraph.artifacts import inspect_svg, publish_items
from dgraph.errors import DgraphError
from dgraph.render import render_diagram
from dgraph.schema import viewspec_schema
from dgraph.viewspec import validate_spec
from examples._shared.atlas_data import ATLAS_ENTRIES, build_spec
from test_render import spec


def atlas_spec(kind, output):
    entry = next(item for item in ATLAS_ENTRIES if item["type"] == kind)
    return build_spec(entry, output)


class StrictViewSpecTests(unittest.TestCase):
    def test_non_finite_and_negative_geometry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for field, value in (("x", float("nan")), ("y", float("inf")), ("x", -1), ("w", 0)):
                value_spec = spec(tmp)
                value_spec["selection"]["nodes"][0][field] = value
                with self.subTest(field=field, value=value):
                    with self.assertRaises(DgraphError) as caught:
                        validate_spec(value_spec)
                    self.assertIn(caught.exception.code, {"invalid-node", "invalid-geometry"})

    def test_duplicate_node_and_source_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp)
            value["selection"]["nodes"].append(copy.deepcopy(value["selection"]["nodes"][0]))
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("duplicate-node-id", caught.exception.code)
            value = spec(tmp)
            value["selection"]["nodes"].append(
                {"id": "b", "label": "B", "kind": "block", "x": 500, "y": 140, "w": 100, "h": 60, "sourceId": "native-a"}
            )
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("duplicate-source-id", caught.exception.code)

    def test_unknown_fields_and_formats_are_rejected_with_field_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp)
            value["selection"]["nodes"][0]["colour"] = "red"
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("unknown-field", caught.exception.code)
            self.assertEqual("selection.nodes[0]", caught.exception.field)
            value = spec(tmp)
            value["outputs"]["formats"] = ["svg", "pdf"]
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("unsupported-format", caught.exception.code)
            self.assertEqual("outputs.formats", caught.exception.field)

    def test_resource_limits_are_enforced_before_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp)
            template = value["selection"]["nodes"][0]
            value["selection"]["nodes"] = [
                {**template, "id": f"n{index}", "sourceId": f"s{index}"}
                for index in range(501)
            ]
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("input-limit", caught.exception.code)

    def test_sources_must_be_bounded_json_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp)
            value["sources"] = [{"kind": "model", "payload": {1, 2, 3}}]
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("invalid-source", caught.exception.code)

    def test_authority_is_validated_and_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp)
            value["selection"]["nodes"][0]["authority"] = "fact"
            result = render_diagram(value)
            self.assertEqual(1, result["report"]["provenance"]["declared"]["fact"])
            self.assertEqual(0, result["report"]["provenance"]["undeclaredNodes"])
            value["selection"]["nodes"][0]["authority"] = "guess"
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("invalid-node", caught.exception.code)

    def test_output_must_stay_inside_configured_root_and_not_target_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            allowed = Path(tmp) / "allowed"
            other = Path(tmp) / "other"
            allowed.mkdir()
            other.mkdir()
            value = spec(str(other))
            with patch.dict(os.environ, {"DGRAPH_OUTPUT_ROOT": str(allowed)}):
                with self.assertRaises(DgraphError) as caught:
                    validate_spec(value)
            self.assertEqual("invalid-output", caught.exception.code)
            value = spec("/")
            with self.assertRaises(DgraphError) as caught:
                validate_spec(value)
            self.assertEqual("invalid-output", caught.exception.code)

    def test_public_schema_matches_runtime_version_and_domain_requirement(self):
        schema = viewspec_schema("gantt")
        self.assertEqual("diagram-view/v1", schema["x-schemaVersion"])
        self.assertFalse(schema["additionalProperties"])
        self.assertIn("gantt", schema["properties"]["selection"]["required"])
        json.dumps(schema)


class DomainInvariantTests(unittest.TestCase):
    def test_qfd_reference_and_gantt_cycle_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            qfd = atlas_spec("qfd", tmp)
            qfd["selection"]["qfd"]["relations"][0]["engineering"] = "missing"
            with self.assertRaises(DgraphError) as caught:
                validate_spec(qfd)
            self.assertEqual("invalid-qfd", caught.exception.code)
            gantt = atlas_spec("gantt", tmp)
            gantt["selection"]["gantt"]["tasks"][0]["dependencies"] = ["verification"]
            with self.assertRaises(DgraphError) as caught:
                validate_spec(gantt)
            self.assertEqual("invalid-gantt", caught.exception.code)

    def test_duplicate_n2_link_and_unknown_dfd_flow_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            n2 = atlas_spec("n2", tmp)
            n2["selection"]["n2Model"]["links"].append(copy.deepcopy(n2["selection"]["n2Model"]["links"][0]))
            with self.assertRaises(DgraphError) as caught:
                validate_spec(n2)
            self.assertEqual("duplicate-relation", caught.exception.code)
            dfd = atlas_spec("dfd", tmp)
            dfd["selection"]["dfdModel"]["flows"][0]["target"] = "missing"
            with self.assertRaises(DgraphError) as caught:
                validate_spec(dfd)
            self.assertEqual("invalid-dfdModel", caught.exception.code)

    def test_disconnected_bpmn_and_overlapping_classes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bpmn = atlas_spec("bpmn", tmp)
            lane_id = bpmn["selection"]["bpmnModel"]["lanes"][0]["id"]
            bpmn["selection"]["bpmnModel"]["tasks"].append({"id": "orphan", "label": "孤立任务", "lane": lane_id, "x": 400, "y": 550})
            with self.assertRaises(DgraphError) as caught:
                validate_spec(bpmn)
            self.assertEqual("disconnected-graph", caught.exception.code)
            uml_class = atlas_spec("class", tmp)
            uml_class["selection"]["umlClass"]["classes"][1]["x"] = 100
            uml_class["selection"]["umlClass"]["classes"][1]["y"] = 160
            with self.assertRaises(DgraphError) as caught:
                validate_spec(uml_class)
            self.assertEqual("invalid-umlClass", caught.exception.code)

    def test_specialized_renderer_preserves_explicit_source_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            uml_class = atlas_spec("class", tmp)
            uml_class["selection"]["umlClass"]["classes"][0]["sourceId"] = "model.GroundStation"
            result = render_diagram(uml_class)
            self.assertIn("model.GroundStation", result["report"]["sourceIds"])
            self.assertIn('data-source-id="model.GroundStation"', Path(result["artifacts"]["svg"]).read_text())


class SVGInspectionTests(unittest.TestCase):
    def test_overlap_duplicate_identity_and_text_overflow_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.svg"
            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
                '<g data-node-id="a" data-source-id="same"><rect x="10" y="10" width="80" height="40"/></g>'
                '<g data-node-id="b" data-source-id="same"><rect x="30" y="20" width="80" height="40"/></g>'
                '<text x="190" y="90" font-size="20">overflow</text>'
                "</svg>",
                encoding="utf-8",
            )
            report = inspect_svg(path)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("node-overlap", codes)
            self.assertIn("out-of-canvas", codes)
            self.assertEqual(2, report["metrics"]["nodeCount"])

    def test_missing_source_identity_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "identity.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="10" y="10">x</text></svg>')
            report = inspect_svg(path)
            self.assertIn("missing-source-identity", {issue["code"] for issue in report["issues"]})

    def test_node_text_overflow_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "overflow.svg"
            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200">'
                '<g data-node-id="a" data-source-id="model.a" data-kind="block">'
                '<rect x="20" y="20" width="80" height="40"/>'
                '<text x="60" y="45" font-size="16">a label that cannot fit</text>'
                "</g></svg>",
                encoding="utf-8",
            )
            report = inspect_svg(path)
            self.assertIn("node-text-overflow", {issue["code"] for issue in report["issues"]})


class ArtifactTransactionTests(unittest.TestCase):
    def test_publish_replaces_only_named_artifacts_and_removes_stale_owned_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            output = root / "output"
            staging.mkdir()
            output.mkdir()
            (staging / "diagram.svg").write_text("new", encoding="utf-8")
            (staging / "report.json").write_text("{}", encoding="utf-8")
            (output / "diagram.svg").write_text("old", encoding="utf-8")
            (output / "diagram.mmd").write_text("stale", encoding="utf-8")
            (output / "user.txt").write_text("keep", encoding="utf-8")
            publish_items(staging, output, ["diagram.svg", "report.json"], remove=["diagram.mmd"])
            self.assertEqual("new", (output / "diagram.svg").read_text())
            self.assertFalse((output / "diagram.mmd").exists())
            self.assertEqual("keep", (output / "user.txt").read_text())

    def test_failed_publish_restores_previous_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            output = root / "output"
            staging.mkdir()
            output.mkdir()
            (output / "diagram.svg").write_text("old svg", encoding="utf-8")
            (output / "report.json").write_text("old report", encoding="utf-8")
            (staging / "diagram.svg").write_text("new svg", encoding="utf-8")
            with self.assertRaises(DgraphError) as caught:
                publish_items(staging, output, ["diagram.svg", "report.json"])
            self.assertEqual("output-commit", caught.exception.code)
            self.assertEqual("old svg", (output / "diagram.svg").read_text())
            self.assertEqual("old report", (output / "report.json").read_text())


if __name__ == "__main__":
    unittest.main()
