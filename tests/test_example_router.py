from pathlib import Path
import unittest

from dgraph.catalog import CATALOG


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
SYSML_TYPES = {"block-definition", "internal-block", "requirements", "parametric", "use-case", "activity", "sequence", "state-machine", "package", "sysml-v2"}
README_SECTIONS = ["图种与用途", "示例图", "自然语言输入示例", "输入文件", "如何运行", "输出文件", "如何改成自己的图", "当前边界与常见问题"]


class ExampleLayoutTests(unittest.TestCase):
    def test_every_type_has_a_complete_semantic_example(self):
        self.assertEqual(61, len(CATALOG))
        for entry in CATALOG:
            with self.subTest(type=entry["type"]):
                folder = EXAMPLES / entry["type"] / "semantic"
                for name in ("README.md", "draw.py", "input.json", "output/diagram.svg", "output/view.yaml", "output/report.json", "output/manifest.json"):
                    self.assertTrue((folder / name).is_file(), folder / name)
                readme = (folder / "README.md").read_text()
                for section in README_SECTIONS:
                    self.assertIn(section, readme)

    def test_sysml_examples_are_explicitly_scoped(self):
        actual = {path.parent.parent.name for path in EXAMPLES.glob("*/sysml/draw.py")}
        self.assertEqual(SYSML_TYPES, actual)
        for kind in SYSML_TYPES:
            folder = EXAMPLES / kind / "sysml"
            for name in ("README.md", "draw.py", "input.json", "model.sysml", "output/diagram.svg", "output/sysml-analysis/report.json"):
                self.assertTrue((folder / name).is_file(), folder / name)

    def test_no_legacy_output_root_or_generators_remain(self):
        root = EXAMPLES.parent
        self.assertFalse((root / "output").exists())
        for name in ("generate_nine.py", "generate_atlas.py", "verify_atlas.py", "verify_delivery.py"):
            self.assertFalse((EXAMPLES / name).exists())


if __name__ == "__main__":
    unittest.main()
