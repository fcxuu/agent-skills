import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "check_verification.py"


class TestContractCrossCheck(unittest.TestCase):
    def test_contract_missing_ac_detected_and_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract = pathlib.Path(tmp) / "contract.md"
            contract.write_text(
                "# Contract\n## Acceptance criteria\n"
                "- [ ] AC-1 | Empty list exports header.\n"
                "- [ ] AC-2 | Non-empty list preserves column order.\n",
                encoding="utf-8",
            )
            report = pathlib.Path(tmp) / "report.md"
            report.write_text(
                "# Verification Report\n\n"
                "## Result\n- Overall: pass\n- Summary: Checked AC-1.\n\n"
                "## Acceptance mapping\n- AC-1: E1\n\n"
                "## Evidence\n- ID: E1\n  Status: pass\n  Check: Empty header\n"
                "  Command: pytest -k empty\n  Observed: id,name\n  Scope: unit\n\n"
                "## Changed files\n- export.py — add header\n\n"
                "## Remaining risks\n- none\n",
                encoding="utf-8",
            )
            r = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--strict", "--json", "--contract", str(contract), str(report)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 1)
            payload = json.loads(r.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertTrue(any("AC-2" in e for e in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
