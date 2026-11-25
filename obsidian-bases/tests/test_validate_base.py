import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import validate_base  # noqa: E402


class TestValidateBase(unittest.TestCase):
    def test_valid_base_passes(self):
        sample = (
            "filters:\n"
            "  and:\n"
            "    - 'file.hasTag(\"review\")'\n"
            "formulas:\n"
            "  age_days: '(now() - file.ctime).days.round(0)'\n"
            "properties:\n"
            "  note.status:\n"
            "    displayName: Status\n"
            "views:\n"
            "  - type: table\n"
            "    name: Review Queue\n"
        )
        res = validate_base.validate_text(sample)
        self.assertEqual(res["status"], "PASS", res)
        self.assertEqual(res["errors"], 0)
        self.assertEqual(res["warnings"], 0)

    def test_missing_note_prefix_and_duration_warns(self):
        sample = (
            "formulas:\n"
            "  bad_age: '(now() - file.ctime).round(0)'\n"
            "properties:\n"
            "  status:\n"
            "    displayName: Status\n"
            "views:\n"
            "  - type: table\n"
            "    name: Main\n"
        )
        res = validate_base.validate_text(sample)
        codes = {i["code"] for i in res["issues"]}
        self.assertIn("PROPERTY_MISSING_PREFIX", codes)
        self.assertIn("DURATION_NO_UNIT", codes)

    def test_unknown_top_key_and_tabs_fail(self):
        sample = "unknown_key: 1\nviews:\n\t- type: table\n"
        res = validate_base.validate_text(sample)
        self.assertEqual(res["status"], "FAIL")
        codes = {i["code"] for i in res["issues"]}
        self.assertIn("YAML_TAB_INDENT", codes)


if __name__ == "__main__":
    unittest.main()
