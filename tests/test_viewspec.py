import copy
import tempfile
import unittest
from pathlib import Path

from dgraph.catalog import CATALOG
from dgraph.viewspec import DgraphError, validate_spec


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


if __name__ == "__main__":
    unittest.main()
