import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_contract", ROOT / "scripts" / "check_contract.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID_CONTRACT = """# Coding Task Contract

## Task
- Status: active

## Goal and context
- User goal: Return a useful error for invalid input.

## Scope
### In scope
- Validate the input and preserve valid requests.

### Out of scope
- Redesign the public API.

## Acceptance criteria
- [ ] AC-1 | Given an empty name, when the request is submitted, then return the documented validation error.
- [ ] AC-2 | Given a valid request, when it is submitted, then preserve the existing response.

## Verification plan
- Baseline: Run the existing validation tests before editing.
- Checks: Run the focused validation tests and the API regression tests.
- Negative/edge cases: Empty and malformed input.
- Regression scope: Existing valid requests.

## Change and recovery boundaries
- Allowed paths: src/ and tests/.
- Do not modify: public schemas.
- Rollback/recovery: Revert only the task diff.

## Handoff
- Owner: implementation agent
- Next action: Implement and run the planned checks.
"""


class ContractValidationTests(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.md"
            path.write_text(text, encoding="utf-8")
            return MODULE.validate(path)

    def test_valid_contract(self):
        self.assertEqual(self.check(VALID_CONTRACT), [])

    def test_missing_criteria_and_placeholder_are_rejected(self):
        text = VALID_CONTRACT.replace(
            "- [ ] AC-1 | Given an empty name, when the request is submitted, then return the documented validation error.\n",
            "",
        ).replace(
            "- [ ] AC-2 | Given a valid request, when it is submitted, then preserve the existing response.\n",
            "",
        ).replace("Return a useful error for invalid input.", "[填写]")
        errors = self.check(text)
        self.assertTrue(any("AC-1" in error or "acceptance" in error for error in errors))
        self.assertTrue(any("placeholder" in error for error in errors))

    def test_duplicate_criterion_ids_are_rejected(self):
        text = VALID_CONTRACT.replace("AC-2 |", "AC-1 |")
        errors = self.check(text)
        self.assertTrue(any("duplicate" in error for error in errors))

    def test_fenced_examples_do_not_satisfy_structure(self):
        text = VALID_CONTRACT.replace("## Acceptance criteria", "## Other")
        text += "\n```markdown\n## Acceptance criteria\n- [ ] AC-9 | Example that should not count.\n```\n"
        self.assertTrue(any("Acceptance criteria" in e for e in self.check(text)))

    def test_fields_must_be_in_verification_section(self):
        text = VALID_CONTRACT.replace("- Checks: Run the focused validation tests and the API regression tests.", "- Checks:")
        text += "\n- Checks: A misplaced check.\n"
        self.assertTrue(any("Checks" in e for e in self.check(text)))

    def test_malformed_criterion_is_not_silently_ignored(self):
        text = VALID_CONTRACT.replace("- [ ] AC-2 |", "- AC-2 |")
        self.assertTrue(any("malformed" in e for e in self.check(text)))

    def test_fenced_placeholders_are_ignored(self):
        text = VALID_CONTRACT + "\n```\n[填写] TODO\n```\n"
        self.assertEqual(self.check(text), [])

    def test_scope_subheadings_must_be_in_scope_section(self):
        text = VALID_CONTRACT.replace("### Out of scope", "### Exclusions")
        text += "\n### Out of scope\n- Elsewhere.\n"
        self.assertTrue(any("Out of scope" in e for e in self.check(text)))

    def test_short_chinese_criterion_is_accepted(self):
        text = VALID_CONTRACT.replace(
            "Given an empty name, when the request is submitted, then return the documented validation error.",
            "空值返回 422",
        )
        self.assertEqual(self.check(text), [])

    def test_invalid_status_values_are_rejected(self):
        for status in ("in progress", "active!", "", "done (verified)"):
            with self.subTest(status=status):
                text = VALID_CONTRACT.replace("- Status: active", f"- Status: {status}")
                self.assertTrue(any("Status" in e for e in self.check(text)))

    def test_missing_status_remains_compatible(self):
        self.assertEqual(self.check(VALID_CONTRACT.replace("- Status: active\n", "")), [])

    def test_multiple_statuses_all_checked(self):
        text = VALID_CONTRACT.replace("- Status: active", "- Status: active\n- Status: in progress")
        self.assertTrue(any("Status" in e for e in self.check(text)))

    def test_repeated_acceptance_sections_are_combined(self):
        text = VALID_CONTRACT.replace("## Verification plan", "## Acceptance criteria\n- [ ] AC-3 | 返回 422\n\n## Verification plan")
        self.assertEqual(self.check(text), [])
        text = text.replace("AC-3 |", "AC-1 |")
        self.assertTrue(any("duplicate" in e for e in self.check(text)))

    def test_empty_repeated_section_does_not_hide_criteria(self):
        text = VALID_CONTRACT.replace("## Verification plan", "## Acceptance criteria\n\n## Verification plan")
        self.assertEqual(self.check(text), [])

    def test_original_ticket_ids_and_shipped_example(self):
        contract = VALID_CONTRACT.replace("AC-1 |", "工单/17.A |")
        self.assertEqual(self.check(contract), [])
        self.assertEqual(MODULE.validate(ROOT / "references" / "handoff-example.md"), [])


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_contract.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_advisory_strict_and_valid_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "document.md"
            for kind, valid in [(None, VALID_CONTRACT)]:
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
