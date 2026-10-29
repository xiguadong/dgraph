import json
from pathlib import Path
import tempfile
import unittest

from dgraph.render import inspect_svg
from examples._shared.runner import run_semantic


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "block-definition", "internal-block", "requirements", "parametric",
    "use-case", "activity", "sequence", "state-machine", "package",
}


class NineViewAcceptanceTests(unittest.TestCase):
    def test_public_renderer_generates_exactly_nine_consistent_views(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind in sorted(EXPECTED):
                with self.subTest(view=kind):
                    folder = ROOT / "examples" / kind / "semantic"
                    spec = json.loads((folder / "input.json").read_text())
                    result = run_semantic(folder, Path(tmp) / kind)
                    self.assertTrue(result["ok"])
                    svg = Path(result["artifacts"]["svg"])
                    self.assertGreater(svg.stat().st_size, 1000)
                    self.assertTrue(inspect_svg(svg)["ok"])
                    self.assertIn("CanSat", spec["presentation"]["title"])
                    for node in spec["selection"]["nodes"]:
                        self.assertTrue(node["sourceId"].startswith("CanSat."))


if __name__ == "__main__":
    unittest.main()
