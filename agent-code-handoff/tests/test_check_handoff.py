import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_handoff", ROOT / "scripts" / "check_handoff.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID_HANDOFF = """# Agent Coding Handoff

## Task
- Task ID: AH-001
- Repository/root: /work/project
- Base revision: abc123
- Current revision/diff: working tree diff
- Status: ready

## Goal and contract
- Contract path: /work/TASK_CONTRACT.md
- Goal summary: Add validation while preserving valid requests.
- Remaining AC IDs: AC-2

## Changes
- Files changed: src/validation.py, tests/test_validation.py
- Interfaces/behavior: Invalid input returns the documented error.
- Decisions: Keep the public response schema unchanged.
- Existing user changes preserved: none
- Out of scope preserved: no dependency changes

## Evidence
- Verification report: /work/VERIFICATION.md
- Commands actually run: python3 -m pytest tests/test_validation.py -q
- Result: partial
- Not run/blocked: API regression is pending.

## Open issues and risks
- API regression still needs an independent run.

## Next action
- Owner: receiving agent
- Action: Run the API regression and review the diff.
- Acceptance criteria remaining: AC-2

## Review
- Reviewer: pending
- Review status: pending
- Findings: pending
"""


VALID_REVIEW = """# Independent Coding Review

## Task
- Task ID: AH-001
- Reviewed revision/diff: working tree diff
- Reviewer: independent agent

## Verdict
- Status: pass
- Summary: The listed criteria have direct evidence.

## Criteria
- AC-1: pass — Focused validation test passed with the documented error.
- AC-2: pass — API regression passed with 8 tests.

## Findings
- Severity: none
- Finding: none
- File/line: none
- Evidence: Focused and adjacent checks were inspected.
- Required correction: none

## Checks actually run
- python3 -m pytest tests/test_validation.py tests/test_api.py -q — 11 passed.

## Residual risk and handoff
- No additional runtime environments were checked.
"""


class HandoffValidationTests(unittest.TestCase):
    def check(self, text, kind):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / f"{kind}.md"
            path.write_text(text, encoding="utf-8")
            return MODULE.validate(path, kind)

    def test_valid_handoff(self):
        self.assertEqual(self.check(VALID_HANDOFF, "handoff"), [])

    def test_valid_review(self):
        self.assertEqual(self.check(VALID_REVIEW, "review"), [])

    def test_complete_handoff_requires_passing_review(self):
        text = VALID_HANDOFF.replace("Status: ready", "Status: complete")
        errors = self.check(text, "handoff")
        self.assertTrue(any("complete handoff" in error for error in errors))

    def test_pass_review_rejects_unverified_criterion(self):
        text = VALID_REVIEW.replace("AC-2: pass", "AC-2: not_verified")
        errors = self.check(text, "review")
        self.assertTrue(any("pass review" in error for error in errors))

    def test_invalid_criterion_cannot_hide_behind_valid_one(self):
        text = VALID_REVIEW.replace("AC-2: pass", "AC-2: skipped")
        self.assertTrue(any("every AC-n" in error for error in self.check(text, "review")))

    def test_later_major_finding_rejects_pass(self):
        text = VALID_REVIEW.replace("- Finding: none", "- Severity: major\n- Finding: broken API")
        self.assertTrue(any("blocker/major" in error for error in self.check(text, "review")))

    def test_legacy_handoff_does_not_require_transfer_manifest(self):
        self.assertEqual(self.check(VALID_HANDOFF, "handoff"), [])

    def test_fields_must_be_in_their_section_and_not_fenced(self):
        text = VALID_HANDOFF.replace("- Contract path: /work/TASK_CONTRACT.md", "```\n- Contract path: /work/TASK_CONTRACT.md\n```")
        text += "\n## Other\n- Contract path: elsewhere\n"
        self.assertTrue(any("Contract path" in e for e in self.check(text, "handoff")))

    def test_empty_field_does_not_consume_next_line(self):
        text = VALID_HANDOFF.replace("- Owner: receiving agent", "- Owner:")
        self.assertTrue(any("Owner" in e for e in self.check(text, "handoff")))

    def test_duplicate_heading_and_status_are_rejected(self):
        for text in (VALID_REVIEW.replace("- Status: pass", "- Status: pass\n- Status: fail"),
                     VALID_REVIEW + "\n## Verdict\n- Status: fail\n"):
            self.assertTrue(self.check(text, "review"))

    def test_complete_cannot_list_remaining_criteria(self):
        text = (VALID_HANDOFF.replace("Status: ready", "Status: complete")
                .replace("Result: partial", "Result: pass")
                .replace("Review status: pending", "Review status: pass"))
        self.assertTrue(any("remaining AC" in e for e in self.check(text, "handoff")))
        text = text.replace("Reviewer: pending", "Reviewer: receiver").replace("Remaining AC IDs: AC-2", "Remaining AC IDs: none").replace("Acceptance criteria remaining: AC-2", "Acceptance criteria remaining: none")
        self.assertEqual(self.check(text, "handoff"), [])

    def test_malformed_ac_punctuation_and_empty_evidence(self):
        for bad in ("- AC-2： pass — evidence", "- AC-2: pass —", "- AC-2: pass evidence"):
            text = VALID_REVIEW.replace("- AC-2: pass — API regression passed with 8 tests.", bad)
            self.assertTrue(any("every AC-n" in e for e in self.check(text, "review")))

    def test_original_ticket_ids(self):
        review = VALID_REVIEW.replace("AC-2:", "工单/17.A:")
        self.assertEqual(self.check(review, "review"), [])
        review = review.replace("工单/17.A: pass", "工单/17.A: not_verified")
        self.assertTrue(self.check(review, "review"))

    def test_open_fence_with_language_is_not_a_closing_fence(self):
        review = VALID_REVIEW.replace("## Criteria", "```text\n```example\n## Criteria")
        self.assertTrue(self.check(review, "review"))

    def test_pass_needs_an_actual_review_or_check(self):
        handoff = VALID_HANDOFF.replace("Review status: pending", "Review status: pass")
        self.assertTrue(self.check(handoff, "handoff"))
        review = VALID_REVIEW.replace(
            "python3 -m pytest tests/test_validation.py tests/test_api.py -q — 11 passed.",
            "not_run",
        )
        self.assertTrue(self.check(review, "review"))


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_handoff.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_advisory_strict_and_valid_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "document.md"
            for kind, valid in [("handoff", VALID_HANDOFF), ("review", VALID_REVIEW)]:
                args = ["--kind", kind] if kind else []
                with self.subTest(kind=kind):
                    path.write_text("# Incomplete document\n", encoding="utf-8")
                    advisory = self.run_cli(*args, path)
                    self.assertEqual(advisory.returncode, 0, advisory.stderr)
                    self.assertIn("SUGGESTION:", advisory.stderr)
                    self.assertNotIn("OK:", advisory.stdout + advisory.stderr)
                    strict = self.run_cli(*args, "--strict", path)
                    self.assertEqual(strict.returncode, 1, strict.stderr)
                    self.assertIn("ERROR:", strict.stderr)
                    path.write_text(valid, encoding="utf-8")
                    for options in ([], ["--strict"]):
                        result = self.run_cli(*args, *options, path)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn("OK:", result.stdout)

    def test_io_and_usage_errors_are_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.md"
            args = ["--kind", "handoff"]
            for options in ([], ["--strict"]):
                result = self.run_cli(*args, *options, path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("cannot read", result.stderr)
                path.write_bytes(b"\xff\xfe")
                result = self.run_cli(*args, *options, path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("UTF-8", result.stderr)
                path.unlink()
            self.assertNotEqual(self.run_cli().returncode, 0)
            self.assertNotEqual(self.run_cli(*args, "--unknown", path).returncode, 0)


if __name__ == "__main__":
    unittest.main()
