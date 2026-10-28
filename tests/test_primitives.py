import tempfile
import unittest
from pathlib import Path

from dgraph.render import render_diagram
from test_render import spec


class DrawingPrimitiveTests(unittest.TestCase):
    def test_matrix_cells_are_rendered_with_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp, "wbs")
            value["selection"]["matrices"] = [{
                "id": "interfaces", "x": 300, "y": 160, "cellWidth": 100, "cellHeight": 60,
                "columns": ["Power", "FCU"], "rows": ["Power", "FCU"],
                "cells": [{"row": 0, "column": 1, "label": "I-01", "color": "amber"}],
            }]
            svg = Path(render_diagram(value)["artifacts"]["svg"]).read_text()
            self.assertIn('data-matrix-cell="0:1"', svg)
            self.assertIn("I-01", svg)

    def test_line_chart_series_uses_normalized_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp, "burndown")
            value["selection"]["charts"] = [{
                "id": "work", "kind": "line", "x": 180, "y": 150, "w": 800, "h": 380,
                "xLabel": "Day", "yLabel": "Hours",
                "series": [{"id": "actual", "label": "Actual", "color": "teal", "points": [[0, 100], [50, 55], [100, 10]]}],
            }]
            svg = Path(render_diagram(value)["artifacts"]["svg"]).read_text()
            self.assertIn('data-chart-series="actual"', svg)
            self.assertIn("Actual", svg)

    def test_scatter_chart_has_points_without_connecting_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp, "burndown")
            value["selection"]["charts"] = [{"id": "trade", "kind": "scatter", "x": 180, "y": 150, "w": 800, "h": 380, "series": [{"id": "options", "label": "Options", "points": [[20, 70], [80, 40]]}]}]
            svg = Path(render_diagram(value)["artifacts"]["svg"]).read_text()
            series = svg.split('data-chart-series="options"', 1)[1].split("</g>", 1)[0]
            self.assertIn("<circle", series)
            self.assertNotIn("<path", series)

    def test_timeline_rows_and_markers_are_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = spec(tmp, "wbs")
            value["selection"]["timelines"] = [{
                "id": "schedule", "x": 220, "y": 160, "w": 850, "rowHeight": 70,
                "rows": [{"id": "design", "label": "Design", "start": 0, "end": 45, "color": "blue"}],
                "markers": [{"position": 45, "label": "PDR"}],
            }]
            svg = Path(render_diagram(value)["artifacts"]["svg"]).read_text()
            self.assertIn('data-timeline-bar="design"', svg)
            self.assertIn("PDR", svg)


if __name__ == "__main__":
    unittest.main()
