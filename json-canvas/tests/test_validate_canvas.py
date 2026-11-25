import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import validate_canvas  # noqa: E402


class TestValidateCanvas(unittest.TestCase):
    def test_valid_canvas_with_group_passes(self):
        board = {
            "nodes": [
                {"id": "g1", "type": "group", "x": 0, "y": 0, "width": 900, "height": 400, "label": "Topic"},
                {"id": "n1", "type": "text", "x": 40, "y": 40, "width": 320, "height": 160, "text": "Concept A"},
                {"id": "n2", "type": "file", "x": 440, "y": 40, "width": 320, "height": 160, "file": "notes/b.md"},
            ],
            "edges": [
                {"id": "e1", "fromNode": "n1", "fromSide": "right", "toNode": "n2", "toSide": "left"},
            ],
        }
        res = validate_canvas.validate_data(board)
        self.assertEqual(res["status"], "PASS", res)
        self.assertEqual(res["warnings"], 0)

    def test_dangling_edge_and_duplicate_id_fail(self):
        board = {
            "nodes": [
                {"id": "n1", "type": "text", "x": 0, "y": 0, "width": 200, "height": 100, "text": "A"},
                {"id": "n1", "type": "link", "x": 300, "y": 0, "width": 200, "height": 100},
            ],
            "edges": [
                {"id": "e1", "fromNode": "n1", "toNode": "missing"},
            ],
        }
        res = validate_canvas.validate_data(board)
        self.assertEqual(res["status"], "FAIL")
        codes = {i["code"] for i in res["issues"]}
        self.assertIn("DUPLICATE_ID", codes)
        self.assertIn("LINK_NODE_MISSING_URL", codes)
        self.assertIn("EDGE_DANGLING_ENDPOINT", codes)

    def test_overlap_warns(self):
        board = {
            "nodes": [
                {"id": "n1", "type": "text", "x": 0, "y": 0, "width": 300, "height": 150, "text": "A"},
                {"id": "n2", "type": "text", "x": 200, "y": 50, "width": 300, "height": 150, "text": "B"},
            ],
            "edges": [],
        }
        res = validate_canvas.validate_data(board)
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(any(i["code"] == "NODE_OVERLAP" for i in res["issues"]))


if __name__ == "__main__":
    unittest.main()
