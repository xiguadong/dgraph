import unittest

from examples._shared.runner import check_view_provenance


class ViewProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.analysis = {
            "model": {"elements": [
                {"id": "element-1", "qualifiedName": "CanSat::Power"},
                {"id": "element-2", "qualifiedName": "CanSat::Radio"},
            ]}
        }
        self.spec = {
            "sources": [{"kind": "sysml", "model": "CanSat"}],
            "selection": {"nodes": [
                {"id": "power", "sourceId": "CanSat::Power"},
                {"id": "radio", "sourceId": "CanSat::Radio"},
            ]},
        }

    def test_sysml_claims_must_resolve_to_compiled_elements(self):
        self.assertTrue(check_view_provenance(self.spec, self.analysis)["ok"])
        self.spec["selection"]["nodes"][1]["sourceId"] = "CanSat::Invented"
        result = check_view_provenance(self.spec, self.analysis)
        self.assertFalse(result["ok"])
        self.assertIn("CanSat::Invented", result["unresolved"])

    def test_semantic_overlay_is_explicit(self):
        self.spec["sources"] = [{"kind": "semantic", "example": "lesson2-cansat"}]
        self.assertEqual("semantic-overlay", check_view_provenance(self.spec, self.analysis)["mode"])

    def test_mixed_sources_require_per_node_origin(self):
        self.spec["sources"].append({"kind": "semantic", "example": "lesson2-cansat"})
        self.assertFalse(check_view_provenance(self.spec, self.analysis)["ok"])
        self.spec["selection"]["nodes"][0]["sourceKind"] = "sysml"
        self.spec["selection"]["nodes"][1]["sourceKind"] = "semantic"
        self.assertTrue(check_view_provenance(self.spec, self.analysis)["ok"])


if __name__ == "__main__":
    unittest.main()
