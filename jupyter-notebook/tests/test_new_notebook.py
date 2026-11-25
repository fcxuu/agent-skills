import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "new_notebook.py"


class TestNewNotebook(unittest.TestCase):
    def test_chinese_title_written_unescaped_utf8_with_cell_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "中文示例.ipynb"
            r = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--kind", "tutorial", "--title", "中文示例教程", "--out", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            raw = out.read_text(encoding="utf-8")
            self.assertIn("中文示例教程", raw)
            self.assertNotIn("\\u4e2d\\u6587", raw)
            self.assertIn('"id":', raw)

    def test_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "exp.ipynb"
            r1 = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--kind", "experiment", "--title", "Run 1", "--out", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r1.returncode, 0, r1.stderr)
            r2 = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--kind", "experiment", "--title", "Run 2", "--out", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(r2.returncode, 0)
            r3 = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--kind", "experiment", "--title", "Run 2", "--out", str(out), "--force"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r3.returncode, 0, r3.stderr)


if __name__ == "__main__":
    unittest.main()
