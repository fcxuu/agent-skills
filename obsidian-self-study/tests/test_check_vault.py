"""Run with: python3 -m unittest discover -s tests -v (from skill root)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_vault.py"


class VaultCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.course = self.root / "认知智能"
        for d in ["notes", "review", "assets/original"]:
            (self.course / d).mkdir(parents=True)
        (self.course / "README.md").write_text("# Index", encoding="utf-8")
        (self.course / "QA.md").write_text("# QA", encoding="utf-8")
        (self.course / "assets/original/source.png").write_bytes(b"placeholder")
        (self.course / "notes/t分布.md").write_text('''# t分布
## 核心速览
> [!abstract] 核心
> $$T=Z/\\sqrt{U/\\nu}$$
## 解释
> [!tip] 图文
> ![[认知智能/assets/original/source.png|500]]
> [!note]- 数学推导
> 见 [[认知智能/notes/t分布#核心速览]]
''', encoding="utf-8")
        (self.course / "review/第三章.md").write_text('![[认知智能/notes/t分布#核心速览]]\n', encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self):
        return subprocess.run([sys.executable, str(SCRIPT), "--vault", str(self.root), "--course", "认知智能", "--json"],
                              capture_output=True, text=True)

    def test_valid_course(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"errors": 0', result.stdout)

    def test_missing_image(self):
        (self.course / "assets/original/source.png").unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("BROKEN_WIKILINK", result.stdout)

    def test_missing_core_heading(self):
        note = self.course / "notes/t分布.md"
        note.write_text(note.read_text(encoding="utf-8").replace("## 核心速览", "## 小结"), encoding="utf-8")
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("CORE_SECTION", result.stdout)


if __name__ == "__main__":
    unittest.main()
