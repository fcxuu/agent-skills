import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_verification", ROOT / "scripts" / "check_verification.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID_REPORT = """# Verification Report

## Task
- Task ID: VC-001
- Revision/diff: working tree diff

## Result
- Overall: pass
- Summary: The targeted behavior and regression check passed.

## Evidence
- ID: E1
  Status: pass
  Check: Empty input returns the documented error.
  Command: python3 -m pytest tests/test_validation.py -q
  Observed: 3 tests passed; the error payload matched the contract.
  Scope: Focused validation behavior.
- ID: E2
  Status: pass
  Check: Existing valid requests remain compatible.
  Command: python3 -m pytest tests/test_api.py -q
  Observed: 8 tests passed.
  Scope: Adjacent API regression.

## Regression and edge cases
- Empty and malformed input covered.

## Changed files
- src/validation.py — Add the required validation.
- tests/test_validation.py — Add regression coverage.

## Remaining risks
- Browser behavior was not part of this change.

## Completion statement
- Only the listed checks are claimed as passed.
"""


class VerificationValidationTests(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "verification.md"
            path.write_text(text, encoding="utf-8")
            return MODULE.validate(path)

    def test_valid_report(self):
        self.assertEqual(self.check(VALID_REPORT), [])

    def test_pass_with_unrun_evidence_is_rejected(self):
        text = VALID_REPORT.replace("  Status: pass\n  Check: Existing valid requests", "  Status: not_run\n  Check: Existing valid requests")
        errors = self.check(text)
        self.assertTrue(any("requires overall partial" in error for error in errors))

    def test_pass_without_observed_evidence_is_rejected(self):
        text = VALID_REPORT.replace("  Observed: 3 tests passed; the error payload matched the contract.", "  Observed: not_run")
        errors = self.check(text)
        self.assertTrue(any("without actual Observed" in error for error in errors))

    def test_partial_report_can_record_unrun_checks(self):
        text = VALID_REPORT.replace("Overall: pass", "Overall: partial", 1).replace(
            "  Status: pass\n  Check: Existing valid requests",
            "  Status: not_run\n  Check: Existing valid requests",
        )
        self.assertEqual(self.check(text), [])

    def test_malformed_id_does_not_hide_unrun_evidence(self):
        for bad_id in ("E 2", "", "E2 extra"):
            text = VALID_REPORT.replace("- ID: E2", f"- ID: {bad_id}").replace(
                "  Status: pass\n  Check: Existing valid requests", "  Status: blocked\n  Check: Existing valid requests")
            self.assertTrue(any("malformed evidence ID" in e for e in self.check(text)))

    def test_status_matrix(self):
        for first, second, accepted in (
            ("fail", "pass", {"fail"}),
            ("not_run", "blocked", {"not_verified"}),
            ("pass", "not_run", {"partial"}),
            ("pass", "pass", {"pass", "partial"}),
        ):
            for overall in ("pass", "fail", "partial", "not_verified"):
                with self.subTest(first=first, second=second, overall=overall):
                    text = VALID_REPORT.replace("Overall: pass", f"Overall: {overall}")
                    text = text.replace("  Status: pass", f"  Status: {first}", 1)
                    pos = text.index("- ID: E2")
                    text = text[:pos] + text[pos:].replace("  Status: pass", f"  Status: {second}", 1)
                    self.assertEqual(not self.check(text), overall in accepted)

    def test_acceptance_mapping_valid_and_legacy(self):
        text = VALID_REPORT.replace("## Evidence", "## Acceptance mapping\n- AC-1: E1, E2\n- TICKET-42: E2\n\n## Evidence")
        self.assertEqual(self.check(text), [])
        self.assertEqual(self.check(VALID_REPORT), [])

    def test_acceptance_mapping_rejects_duplicates_and_dangling(self):
        for mapping, message in (
            ("- AC-1: E1\n- AC-1: E2", "duplicate Acceptance"),
            ("- AC-1: E1, E99", "unknown evidence ID"),
            ("- AC-1: E1, E1", "duplicate evidence references"),
            ("- AC-1: ", "malformed Acceptance"),
        ):
            text = VALID_REPORT.replace("## Evidence", f"## Acceptance mapping\n{mapping}\n\n## Evidence")
            self.assertTrue(any(message in e for e in self.check(text)), self.check(text))

    def test_duplicate_status_cannot_hide_failure(self):
        text = VALID_REPORT.replace("  Status: pass", "  Status: pass\n  Status: fail", 1)
        self.assertTrue(any("duplicate Status" in e for e in self.check(text)))

    def test_duplicate_overall_and_evidence_heading_rejected(self):
        text = VALID_REPORT.replace("- Overall: pass", "- Overall: pass\n- Overall: partial")
        text += "\n## Evidence\n- ID: E3\n  Status: blocked\n"
        errors = self.check(text)
        self.assertTrue(any("duplicate Overall" in e for e in errors))
        self.assertTrue(any("duplicate heading" in e for e in errors))

    def test_fenced_evidence_does_not_count(self):
        start = VALID_REPORT.index("- ID: E1")
        end = VALID_REPORT.index("## Regression")
        text = VALID_REPORT[:start] + "```markdown\n" + VALID_REPORT[start:end] + "```\n\n" + VALID_REPORT[end:]
        self.assertTrue(any("at least one evidence" in e for e in self.check(text)))

    def test_manual_observation_and_old_report_remain_valid(self):
        text = VALID_REPORT.replace("python3 -m pytest tests/test_validation.py -q", "Manual: inspect output in browser")
        self.assertEqual(self.check(text), [])

    def test_code_fence_with_longer_closer(self):
        text = VALID_REPORT + "\n~~~~markdown\n## Evidence\n~~~~~\n"
        self.assertEqual(self.check(text), [])

    def test_non_english_issue_and_evidence_ids(self):
        report = VALID_REPORT.replace("- ID: E1", "- ID: 记录-1")
        report = report.replace("## Evidence", "## Acceptance mapping\n- 工单/17.A: 记录-1\n\n## Evidence")
        self.assertEqual(self.check(report), [])


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_verification.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_advisory_strict_and_valid_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "document.md"
            for kind, valid in [(None, VALID_REPORT)]:
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
            args = []
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
