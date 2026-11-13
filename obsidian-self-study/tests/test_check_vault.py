"""Regression tests: run with python3 -m unittest discover -s tests -v."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_vault.py"


class VaultCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name)
        self.course = self.vault / "认知智能"
        for folder in ["notes", "review", "raw-markdown", "assets/original", "assets/generated"]:
            (self.course / folder).mkdir(parents=True)
        (self.course / "README.md").write_text("# 课程导航", encoding="utf-8")
        (self.course / "QA.md").write_text("# 质量检查", encoding="utf-8")
        (self.course / "assets/original/source.png").write_bytes(b"fake-png")
        (self.course / "notes/t分布.md").write_text('''---
course: "认知智能"
---
# t 分布
## 核心速览
> [!abstract] 核心
> 若 $Z\\sim N(0,1)$，则
> $$T=Z/\\sqrt{U/\\nu} \\tag{3.7}$$
## 解释
> [!tip] 图文
> ![原图|500](../assets/original/source.png)
> **图 2.1 [原图]**：源课件 P.14。
> [!note]- 数学推导
> 见 [本节核心速览](t分布.md#核心速览)
''', encoding="utf-8")
        (self.course / "review/第三章.md").write_text('![[t分布#核心速览]]\n', encoding="utf-8")

    def write_note(self, content):
        (self.course / "notes/t分布.md").write_text(content, encoding="utf-8")

    def state(self, *, status="completed", output_path="notes/t分布.md", source_ref="Ch01 / 1.1 t 分布"):
        payload = {"schema_version": "0.2.0", "course_status": "in_progress", "sources": {},
                   "sections": [{"id": "ch01-sec01", "status": status, "source_map_ref": source_ref,
                                 "output_path": output_path, "attempts": 1, "qa_ids": [], "updated_at": None}]}
        (self.course / ".build-state.json").write_text(json.dumps(payload), encoding="utf-8")

    def run_check(self, course="认知智能", *, cwd=None):
        r = subprocess.run([sys.executable, str(SCRIPT), "--vault", str(self.vault), "--course", str(course), "--json"],
                           cwd=cwd, capture_output=True, text=True)
        return r, json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}

    def codes(self, result):
        return [i["code"] for i in result["issues"]]

    # T01 + existing compatibility.
    def test_T01_valid_course(self):
        run, payload = self.run_check()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(payload["errors"], 0)
        self.assertEqual(payload["checked_notes_count"], 1)
        self.assertIn("mathematical_correctness", payload["not_checked"])

    def test_T02_missing_core(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text().replace("## 核心速览", "## 小结"))
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("CORE_SECTION", self.codes(data))

    def test_T02_duplicate_core(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + "\n## 核心速览\n重复\n")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("CORE_SECTION", self.codes(data))

    def test_T03_subhead_in_core(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text().replace("## 解释", "### 非法子标题\n## 解释"))
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("CORE_SUBHEADING", self.codes(data))

    def test_T03_math_ids_and_footnote(self):
        note = self.course / "notes/t分布.md"
        text = note.read_text().replace("## 解释", "\\label{abc}\n\\eqref{abc}\n[^note]\n^bad-id\n## 解释")
        self.write_note(text)
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertTrue({"CORE_MATH_LABEL", "CORE_FOOTNOTE", "CORE_BLOCK_ID"}.issubset(set(self.codes(data))))

    def test_T03_core_position(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text().replace("## 核心速览", "## 无关的先行正文\n## 核心速览"))
        run, data = self.run_check()
        self.assertIn("CORE_POSITION", self.codes(data))
        self.assertEqual(run.returncode, 1)

    def test_T04_review_absolute_course_relative(self):
        run, data = self.run_check(str(self.course), cwd="/")
        self.assertEqual(run.returncode, 0, run.stdout)

    def test_T05_missing_review_target(self):
        (self.course / "review/第三章.md").write_text("![[never#核心速览]]\n", encoding="utf-8")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("BROKEN_WIKILINK", self.codes(data))

    def test_T05_missing_review_anchor(self):
        (self.course / "review/第三章.md").write_text("![[t分布#其他标题]]\n", encoding="utf-8")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("HEADING_ANCHOR", self.codes(data))

    def test_T05_review_unique_basename(self):
        (self.course / "review/第三章.md").write_text("![[t分布#核心速览]]\n", encoding="utf-8")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertNotIn("AMBIGUOUS_WIKILINK", self.codes(data))

    def test_T06_valid_mermaid_callout(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + '''\n> [!tip] 流程
> ```mermaid
> flowchart TD
> A[输入] --> B{通过吗？}
>
> B --> C[完成]
> ```
''')
        run, data = self.run_check()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertNotIn("MERMAID_CALLOUT_PREFIX", self.codes(data))

    def test_T07_broken_mermaid_prefix(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + '''\n> [!tip] 流程
> ```mermaid
> A --> B
B --> C
> ```
''')
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("MERMAID_CALLOUT_PREFIX", self.codes(data))

    def test_T07_unclosed_mermaid(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + "\n```mermaid\nflowchart TD\nA --> B\n")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("MERMAID_FENCE", self.codes(data))

    def test_T08_mask_outer_four_fence(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + '''\n````markdown
```mermaid
## 核心速览
\\label{example}
![[不存在]]
```
````
''')
        run, data = self.run_check()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertNotIn("BROKEN_WIKILINK", self.codes(data))

    def test_T08_inline_code_comments(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + '''\nExample `![[不存在]]` and `\\label{dummy}`
%% hidden: ![[不存在]]
## 核心速览
%%
<!-- ![[不存在]]
## 核心速览 -->
''')
        run, data = self.run_check()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertNotIn("BROKEN_WIKILINK", self.codes(data))

    def test_T09_malformed_json(self):
        (self.course / ".build-state.json").write_text("{broken\n", encoding="utf-8")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("STATE_JSON_INVALID", self.codes(data))

    def test_T09_bad_enum(self):
        self.state(status="finished")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("STATE_SECTION_SCHEMA", self.codes(data))

    def test_T10_completed_missing(self):
        self.state(output_path="notes/removed.md")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("STATE_COMPLETED_MISSING", self.codes(data))

    def test_T11_empty_not_initialized(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "空课程").mkdir()
            (root / "空课程/raw-markdown").mkdir()
            (root / "空课程/raw-markdown/source.pdf").write_bytes(b"original")
            run = subprocess.run([sys.executable, str(SCRIPT), "--vault", str(root), "--course", "空课程", "--json"],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout)
            self.assertEqual(json.loads(run.stdout)["course_state"], "not_initialized")
            self.assertEqual(json.loads(run.stdout)["errors"], 0)

    def test_T12_course_path_escape(self):
        run, data = self.run_check("../outside")
        self.assertEqual(run.returncode, 2)
        self.assertIn("禁止越界", run.stderr)

    def test_T12_wikilink_escape(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + "\n[[../../../outside/private.md]]\n")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("PATH_ESCAPES_VAULT", self.codes(data))

    def test_T13_raw_ocr_has_no_core(self):
        (self.course / "raw-markdown/lec01.md").write_text("# 幻灯片 1\n源文本没有速览\n", encoding="utf-8")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertEqual(data["checked_notes_count"], 1)

    def test_original_evidence_warning(self):
        generated = self.course / "assets/generated/redraw.svg"
        generated.write_text("<svg/>", encoding="utf-8")
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text() + "\n> ![[认知智能/assets/generated/redraw.svg]]\n> **图 [忠实重绘]**：根据教材\n")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 0)
        self.assertIn("IMAGE_ORIGINAL_EVIDENCE", self.codes(data))

    def test_source_map_ref_and_duplicate_id(self):
        self.state(source_ref="Ch01 / mismatch")
        mapfile = self.course / "raw-markdown/source-map.md"
        mapfile.write_text("| 逻辑章节 / 小节 | 源课件与定位区间 | 边界状态 | 关联笔记 |\n|---|---|---|---|\n| Ch01 / 1.1 t 分布 | `lec01.pdf` → `raw-markdown/lec01.md` (`P.1-8`) | verified | `notes/t分布.md` |\n", encoding="utf-8")
        (self.course / "raw-markdown/lec01.md").write_text("# Source", encoding="utf-8")
        statepath = self.course / ".build-state.json"
        obj = json.loads(statepath.read_text())
        obj["sections"].append(dict(obj["sections"][0]))
        statepath.write_text(json.dumps(obj), encoding="utf-8")
        run, data = self.run_check()
        self.assertEqual(run.returncode, 1)
        self.assertIn("STATE_SOURCE_MAP_REF", self.codes(data))
        self.assertIn("STATE_DUPLICATE_ID", self.codes(data))

    def test_stable_issue_order_json(self):
        note = self.course / "notes/t分布.md"
        self.write_note(note.read_text().replace("## 核心速览", "## core") + "\n[[不存在]]\n")
        r1, data1 = self.run_check()
        r2, data2 = self.run_check()
        self.assertEqual(r1.stdout, r2.stdout)
        self.assertEqual(data1["issues"], sorted(data1["issues"], key=lambda i: (i["severity"], i["file"], i["line"], i["code"])))

    def test_read_only_digest(self):
        self.state(status="completed")
        import hashlib
        before = {p.relative_to(self.course).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.course.rglob("*") if p.is_file()}
        run, data = self.run_check()
        after = {p.relative_to(self.course).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.course.rglob("*") if p.is_file()}
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertEqual(before, after)


    # V1–V6: one unchanged course tree with three distinct Vault roots.
    def portable_tree(self):
        lectures = self.vault / "lectures"
        outer = lectures / "图数据管理与挖掘"
        course = outer / "课件讲解"
        for d in ["notes/ch05", "assets/original/P05", "review"]:
            (course / d).mkdir(parents=True, exist_ok=True)
        other = lectures / "其他课程/notes"
        other.mkdir(parents=True)
        (other / "other.md").write_text("# 其他课程", encoding="utf-8")
        (course / "README.md").write_text("[当前章节](notes/ch05/ch05-04.md)", encoding="utf-8")
        (course / "QA.md").write_text("# QA", encoding="utf-8")
        (course / "assets/original/P05/fig.png").write_bytes(b"png")
        (course / "notes/ch05/ch05-03-prev.md").write_text(
            "# 前置知识\n## 核心速览\n内容\n## 详细", encoding="utf-8")
        note = course / "notes/ch05/ch05-04.md"
        note.write_text(
            "# 规约剥离\n## 核心速览\n已核验概念\n## 正文\n"
            "> [!tip] 原图\n"
            "> ![原图|550](../../assets/original/P05/fig.png)\n"
            "> **图注 [原图]**：源课件 P.36。\n"
            "[前置知识](ch05-03-prev.md)\n", encoding="utf-8")
        (course / "review/ch05.md").write_text("![[ch05-04#核心速览]]\n", encoding="utf-8")
        return lectures, outer, course, note

    def run_portable(self, vault, course_argument):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--vault", str(vault),
             "--course", str(course_argument), "--json"],
            cwd="/", capture_output=True, text=True)
        return run, json.loads(run.stdout) if run.stdout.strip().startswith("{") else {}

    def test_V1_V2_V3_three_vault_roots(self):
        lectures, outer, course, _ = self.portable_tree()
        for vault, relative in [
            (lectures, "图数据管理与挖掘/课件讲解"),
            (outer, "课件讲解"),
            (course, "."),
        ]:
            with self.subTest(vault=vault):
                run, data = self.run_portable(vault, relative)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertEqual(data["errors"], 0)
                self.assertEqual(data["checked_notes_count"], 2)

    def test_V4_cross_course_escape(self):
        lectures, _, course, note = self.portable_tree()
        note.write_text(note.read_text() + "\n[他课](../../../../其他课程/notes/other.md)")
        run, data = self.run_portable(lectures, "图数据管理与挖掘/课件讲解")
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("PATH_ESCAPES_COURSE", self.codes(data))

    def test_V5_outside_vault_escape(self):
        _, _, course, note = self.portable_tree()
        note.write_text(note.read_text() + "\n![出界图片](../../../outside.png)")
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("PATH_ESCAPES_VAULT", self.codes(data))

    def test_V6_legacy_prefix_fails_with_small_vault(self):
        _, _, course, note = self.portable_tree()
        note.write_text(note.read_text() +
                        "\n![[图数据管理与挖掘/课件讲解/assets/original/P05/fig.png]]")
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("BROKEN_WIKILINK", self.codes(data))

    def test_relative_image_with_urlencoded_spaces(self):
        _, _, course, note = self.portable_tree()
        (course / "assets/original/P05/my fig.png").write_bytes(b"png")
        note.write_text(note.read_text() +
                        "\n![原图|350](../../assets/original/P05/my%20fig.png)\n"
                        "**图注 [原图]**：页 37。")
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_os_absolute_image_forbidden(self):
        _, _, course, note = self.portable_tree()
        note.write_text(note.read_text() + "\n![原图](file:///Users/test/fig.png)")
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 1)
        self.assertIn("OS_ABSOLUTE_PATH_FORBIDDEN", self.codes(data))

    def test_markdown_md_image_is_not_a_review_transclusion(self):
        _, _, course, _ = self.portable_tree()
        (course / "review/ch05.md").write_text(
            "![核心速览](../notes/ch05/ch05-04.md#核心速览)", encoding="utf-8")
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 1)
        self.assertIn("REVIEW_MARKDOWN_NOT_EMBED", self.codes(data))

    def test_ambiguous_review_basename_is_error(self):
        lectures, _, course, _ = self.portable_tree()
        (lectures / "其他课程/notes/ch05-04.md").write_text(
            "# 重名\n## 核心速览\n内容", encoding="utf-8")
        run, data = self.run_portable(lectures, "图数据管理与挖掘/课件讲解")
        self.assertEqual(run.returncode, 1)
        self.assertIn("AMBIGUOUS_WIKILINK", self.codes(data))
        # The same course by itself still resolves unambiguously.
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_review_relative_link_fallback_is_valid(self):
        _, _, course, _ = self.portable_tree()
        (course / "review/ch05.md").write_text(
            "[查看核心速览](../notes/ch05/ch05-04.md#核心速览)", encoding="utf-8")
        run, data = self.run_portable(course, ".")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_course_equal_vault_absolute_flag(self):
        _, _, course, _ = self.portable_tree()
        run, data = self.run_portable(course, course)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_symlink_target_escaping_course(self):
        lectures, _, course, note = self.portable_tree()
        outside = lectures / "private.png"
        outside.write_bytes(b"png")
        link = course / "assets/original/P05/shortcut.png"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlinks unsupported in current filesystem")
        note.write_text(note.read_text() +
                        "\n![原图](../../assets/original/P05/shortcut.png)")
        run, data = self.run_portable(lectures, "图数据管理与挖掘/课件讲解")
        self.assertEqual(run.returncode, 1)
        self.assertIn("PATH_ESCAPES_COURSE", self.codes(data))


if __name__ == "__main__":
    unittest.main()
