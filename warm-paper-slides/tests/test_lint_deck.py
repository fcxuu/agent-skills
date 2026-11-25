import pathlib
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import lint_deck  # noqa: E402


class TestLintDeck(unittest.TestCase):
    def test_starter_tex_passes_static(self):
        starter = SKILL_DIR / "assets" / "starter.tex"
        res = lint_deck.lint_deck(starter, no_build=True)
        self.assertEqual(res["status"], "PASS", res)
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["frames"], 8)

    def test_missing_image_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = pathlib.Path(tmp) / "deck.tex"
            tex.write_text(
                "\\documentclass{beamer}\n"
                "\\usetheme{warmpaper}\n"
                "\\decksections{Intro}\n"
                "\\begin{document}\n"
                "\\section{Intro}\n"
                "\\begin{frame}\n"
                "  \\bititle{Test}{测试}\n"
                "  \\safeimg[height=.5\\textheight]{does_not_exist.png}{cap}\n"
                "\\end{frame}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            res = lint_deck.lint_deck(tex, no_build=True)
            self.assertEqual(res["status"], "FAIL")
            self.assertTrue(any("not found: does_not_exist.png" in e for e in res["errors"]))

    def test_section_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = pathlib.Path(tmp) / "deck.tex"
            tex.write_text(
                "\\documentclass{beamer}\n"
                "\\usetheme{warmpaper}\n"
                "\\decksections{Intro,Method}\n"
                "\\begin{document}\n"
                "\\section{Intro}\n"
                "\\begin{frame}\n"
                "  \\bititle{Test}{测试}\n"
                "\\end{frame}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            res = lint_deck.lint_deck(tex, no_build=True)
            self.assertEqual(res["status"], "FAIL")
            self.assertTrue(any("decksections" in e for e in res["errors"]))

    def test_long_subtitle_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = pathlib.Path(tmp) / "deck.tex"
            tex.write_text(
                "\\documentclass{beamer}\n"
                "\\usetheme{warmpaper}\n"
                "\\decksections{Intro}\n"
                "\\begin{document}\n"
                "\\section{Intro}\n"
                "\\begin{frame}\n"
                "  \\bititle{Test}{这是一个明显超过十二个字的中文副标题}\n"
                "\\end{frame}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            res = lint_deck.lint_deck(tex, no_build=True)
            self.assertEqual(res["status"], "PASS")
            self.assertTrue(any("subtitle" in w.lower() for w in res["warnings"]))

    def test_parse_page_specs(self):
        self.assertEqual(lint_deck.parse_page_specs(["3", "5,3,7"]), [3, 5, 7])


if __name__ == "__main__":
    unittest.main()
