import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
STATE_TOOL = SKILL_DIR / "scripts" / "state_tool.py"
CHECK_VAULT = SKILL_DIR / "scripts" / "check_vault.py"


def run_cli(script: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(script), *args],
        capture_output=True,
        text=True,
    )


class TestStateTool(unittest.TestCase):
    def test_full_lifecycle_passes_check_vault(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = pathlib.Path(tmp)
            course = vault / "course-a"
            (course / "slides").mkdir(parents=True)
            (course / "raw-markdown").mkdir(parents=True)
            (course / "notes").mkdir(parents=True)

            (course / "slides" / "lec01.pdf").write_bytes(b"%PDF-1.4 dummy")
            (course / "raw-markdown" / "lec01.md").write_text("# Lec 01\ncontent\n", encoding="utf-8")
            (course / "raw-markdown" / "source-map.md").write_text(
                "| 逻辑章节 / 小节 | 源课件与定位区间 | 边界状态 | 关联教学笔记 |\n"
                "|---|---|---|---|\n"
                "| Ch01 / 1.1 Intro | `slides/lec01.pdf` → `raw-markdown/lec01.md` (`P.1-5`) | `verified` | `notes/01-01-intro.md` |\n",
                encoding="utf-8",
            )

            # 1. init & register source
            self.assertEqual(run_cli(STATE_TOOL, "init", "--course", str(course)).returncode, 0)
            r = run_cli(
                STATE_TOOL,
                "register-source",
                "--course", str(course),
                "--raw", "raw-markdown/lec01.md",
                "--source", "slides/lec01.pdf",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            meta = json.loads(r.stdout)
            self.assertEqual(len(meta["sha256"]), 64)

            # 2. create pending -> processing -> write note -> qa_pending -> completed
            r = run_cli(
                STATE_TOOL, "upsert-section", "--course", str(course),
                "--id", "ch01-sec01",
                "--source-map-ref", "Ch01 / 1.1 Intro",
                "--output", "notes/01-01-intro.md",
            )
            self.assertEqual(r.returncode, 0, r.stderr)

            r = run_cli(
                STATE_TOOL, "upsert-section", "--course", str(course),
                "--id", "ch01-sec01", "--status", "processing", "--bump-attempts",
            )
            self.assertEqual(r.returncode, 0, r.stderr)

            # Cannot mark qa_pending before file exists on disk
            r_fail = run_cli(
                STATE_TOOL, "upsert-section", "--course", str(course),
                "--id", "ch01-sec01", "--status", "qa_pending",
            )
            self.assertNotEqual(r_fail.returncode, 0)

            # Write valid teaching note
            (course / "notes" / "01-01-intro.md").write_text(
                "# 1.1 Intro\n\n## 核心速览\n\n> [!abstract] 核心\n> 基本定义。\n\n## 正文\n\n细节。\n",
                encoding="utf-8",
            )
            self.assertEqual(
                run_cli(STATE_TOOL, "upsert-section", "--course", str(course), "--id", "ch01-sec01", "--status", "qa_pending").returncode,
                0,
            )
            self.assertEqual(
                run_cli(STATE_TOOL, "upsert-section", "--course", str(course), "--id", "ch01-sec01", "--status", "completed").returncode,
                0,
            )
            self.assertEqual(
                run_cli(STATE_TOOL, "set-course-status", "--course", str(course), "--status", "completed").returncode,
                0,
            )

            # Cross-validate directly with check_vault.py!
            cv = run_cli(CHECK_VAULT, "--vault", str(vault), "--course", str(course), "--json")
            self.assertEqual(cv.returncode, 0, cv.stdout + cv.stderr)
            report = json.loads(cv.stdout)
            self.assertEqual(report["course_state"], "completed")
            self.assertEqual([i for i in report["issues"] if i["severity"] == "error"], [])

            # Protected completed guard: cannot auto-revert to processing or pending
            r_block = run_cli(
                STATE_TOOL, "upsert-section", "--course", str(course),
                "--id", "ch01-sec01", "--status", "processing",
            )
            self.assertNotEqual(r_block.returncode, 0)

            # P0 demotion requires --p0-demote + --qa-id
            r_p0 = run_cli(
                STATE_TOOL, "upsert-section", "--course", str(course),
                "--id", "ch01-sec01", "--status", "failed", "--p0-demote", "--qa-id", "QA-001",
            )
            self.assertEqual(r_p0.returncode, 0, r_p0.stderr)
            rec = json.loads(r_p0.stdout)
            self.assertEqual(rec["status"], "failed")
            self.assertIn("QA-001", rec["qa_ids"])

            # Controlled revision unlocks failed -> processing
            r_rev = run_cli(
                STATE_TOOL, "upsert-section", "--course", str(course),
                "--id", "ch01-sec01", "--status", "processing", "--controlled-revision", "--bump-attempts",
            )
            self.assertEqual(r_rev.returncode, 0, r_rev.stderr)
            self.assertEqual(json.loads(r_rev.stdout)["attempts"], 2)

            # Summary JSON output
            r_sum = run_cli(STATE_TOOL, "summary", "--course", str(course), "--json")
            self.assertEqual(r_sum.returncode, 0, r_sum.stderr)
            summary = json.loads(r_sum.stdout)
            self.assertEqual(summary["sections_total"], 1)
            self.assertEqual(summary["counts"]["processing"], 1)


if __name__ == "__main__":
    unittest.main()
