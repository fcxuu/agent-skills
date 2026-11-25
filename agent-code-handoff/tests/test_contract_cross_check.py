import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "check_handoff.py"


class TestHandoffContractCrossCheck(unittest.TestCase):
    def test_review_missing_contract_ac_detected_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract = pathlib.Path(tmp) / "contract.md"
            contract.write_text(
                "# Contract\n## Acceptance criteria\n"
                "- [ ] AC-1 | Empty list exports header.\n"
                "- [ ] AC-2 | Non-empty list preserves order.\n",
                encoding="utf-8",
            )
            review = pathlib.Path(tmp) / "review.md"
            review.write_text(
                "# Review\n\n"
                "## Task\n- Task ID: T1\n- Reviewed revision/diff: abc123\n- Reviewer: Agent-B\n\n"
                "## Verdict\n- Status: pass\n- Summary: Checked AC-1.\n\n"
                "## Criteria\n- AC-1: pass — verified header row id,name\n\n"
                "## Findings\n- Severity: none\n\n"
                "## Checks actually run\n- pytest -k empty -> 1 passed\n\n"
                "## Residual risk and handoff\n- none\n",
                encoding="utf-8",
            )
            r = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--kind", "review", "--strict", "--json", "--contract", str(contract), str(review)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 1)
            payload = json.loads(r.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertTrue(any("AC-2" in e for e in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
