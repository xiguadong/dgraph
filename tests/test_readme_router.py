from pathlib import Path
import unittest

from dgraph.catalog import CATALOG


class ReadmeRouterTests(unittest.TestCase):
    def test_readme_contains_every_type_and_calling_contract(self):
        text = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        self.assertIn("视图类型 / 调用方法 / SysML 参考 / 自然语言参考", text)
        self.assertIn('"sources": []', text)
        self.assertIn('"method": "tools/call"', text)
        self.assertIn('"name": "render_diagram"', text)
        for entry in CATALOG:
            with self.subTest(type=entry["type"]):
                self.assertIn(f"`{entry['type']}`", text)
                self.assertIn(f"examples/{entry['type']}/semantic/README.md", text)

    def test_supported_types_starts_with_five_example_images(self):
        text = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        start = text.index("## 支持图类型")
        end = text.index("### SysML 与模型视图")
        gallery = text[start:end]
        expected = ["block-definition", "n2", "gantt", "c4-context", "delivery"]
        for kind in expected:
            self.assertIn(f"![{kind} 示例](examples/{kind}/semantic/output/diagram.svg)", gallery)
        self.assertEqual(5, gallery.count("!["))

    def test_legacy_delivery_sections_are_removed(self):
        text = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        for heading in ("## 九视图交付", "## lesson_2 扩展图鉴", "## 验证", "## 当前边界"):
            self.assertNotIn(heading, text)


if __name__ == "__main__":
    unittest.main()
