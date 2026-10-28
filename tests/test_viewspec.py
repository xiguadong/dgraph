import copy
import tempfile
import unittest
from pathlib import Path

from dgraph.catalog import CATALOG
from dgraph.viewspec import DgraphError, validate_spec
from examples._shared.scaffold import semantic_spec


NINE = {
    "block-definition", "internal-block", "requirements", "parametric",
    "use-case", "activity", "sequence", "state-machine", "package",
}


def valid_spec(output):
    return {
        "schema": "diagram-view/v1",
        "type": "block-definition",
        "intent": {"question": "What makes up CS-1?"},
        "sources": [],
        "selection": {
            "nodes": [
                {"id": "system", "label": "CS-1", "kind": "block", "x": 80, "y": 80, "w": 180, "h": 70, "sourceId": "sys-1"},
                {"id": "power", "label": "Power", "kind": "block", "x": 80, "y": 260, "w": 180, "h": 70, "sourceId": "part-1"},
            ],
            "edges": [{"source": "system", "target": "power", "kind": "composition", "label": "1"}],
        },
        "presentation": {"title": "CS-1 block definition", "theme": "dgraph"},
        "outputs": {"directory": output, "formats": ["svg", "viewspec", "dsl", "report"]},
    }


class CatalogTests(unittest.TestCase):
    def test_all_atlas_and_delivery_types_are_renderable(self):
        renderable = {item["type"] for item in CATALOG if item["status"] == "renderable"}
        self.assertEqual(61, len(renderable))
        self.assertTrue(NINE.issubset(renderable))
        self.assertFalse(any(item["status"] == "catalog-only" for item in CATALOG))

    def test_delivery_is_renderable(self):
        delivery = next(item for item in CATALOG if item["type"] == "delivery")
        self.assertEqual("renderable", delivery["status"])


class ValidationTests(unittest.TestCase):
    def test_valid_spec_is_normalized_without_mutating_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = valid_spec(tmp)
            before = copy.deepcopy(original)
            normalized = validate_spec(original)
            self.assertEqual(original, before)
            self.assertEqual(1280, normalized["presentation"]["width"])
            self.assertEqual(720, normalized["presentation"]["height"])

    def test_dangling_edge_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = valid_spec(tmp)
            spec["selection"]["edges"][0]["target"] = "missing"
            with self.assertRaisesRegex(DgraphError, "dangling"):
                validate_spec(spec)

    def test_output_directory_is_required(self):
        spec = valid_spec("unused")
        spec["outputs"]["directory"] = ""
        with self.assertRaisesRegex(DgraphError, "output"):
            validate_spec(spec)

    def test_unknown_type_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = valid_spec(tmp)
            spec["type"] = "not-a-diagram"
            with self.assertRaisesRegex(DgraphError, "not renderable"):
                validate_spec(spec)

    def test_dedicated_models_do_not_require_generic_placeholders(self):
        for kind in ("risk-matrix", "dmn", "timing", "tradespace", "pert"):
            with self.subTest(kind=kind):
                spec = semantic_spec(kind)
                spec["selection"]["nodes"] = []
                spec["selection"]["edges"] = []
                self.assertEqual([], validate_spec(spec)["selection"]["nodes"])

    def test_qfd_weights_and_gantt_dependencies_are_checked(self):
        qfd = copy.deepcopy(semantic_spec("qfd"))
        qfd["selection"]["qfd"]["engineering"][0]["weight"] += 1
        with self.assertRaisesRegex(DgraphError, "weight"):
            validate_spec(qfd)
        gantt = copy.deepcopy(semantic_spec("gantt"))
        gantt["selection"]["gantt"]["tasks"][1]["start"] = 1
        with self.assertRaisesRegex(DgraphError, "predecessor"):
            validate_spec(gantt)

    def test_domain_references_and_intervals_are_checked(self):
        changes = (
            ("risk-matrix", lambda model: model["risks"][0].update(probability=6)),
            ("dmn", lambda model: model["rules"][0].update(conditions=["only one"])),
            ("timing", lambda model: model["lifelines"][0]["segments"][1].__setitem__("from", 90)),
            ("tradespace", lambda model: model["paretoIds"].remove(model["paretoIds"][0])),
            ("pert", lambda model: model["tasks"][0].update(dependencies=["G"])),
            ("c4-container", lambda model: model["relations"][0].update(target="missing")),
            ("bpmn", lambda model: model["tasks"][0].update(lane="missing")),
        )
        from dgraph.viewspec import DOMAIN_FIELDS
        for kind, change in changes:
            with self.subTest(kind=kind):
                spec = copy.deepcopy(semantic_spec(kind))
                model = spec["selection"][DOMAIN_FIELDS[kind]]
                change(model)
                with self.assertRaises(DgraphError):
                    validate_spec(spec)

    def test_node_must_fit_canvas(self):
        spec = valid_spec("/absolute/output")
        spec["selection"]["nodes"][0]["x"] = 1270
        with self.assertRaisesRegex(DgraphError, "canvas"):
            validate_spec(spec)


if __name__ == "__main__":
    unittest.main()
