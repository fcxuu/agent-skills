#!/usr/bin/env python3
"""Static validator for Obsidian Bases (.base) YAML files.

Uses PyYAML when installed, falling back to a pure-stdlib structural parser so it works
in zero-dependency environments. Checks YAML syntax, top-level schema keys, view types,
missing `note.` prefixes under `properties:`, and common Duration formula errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_TOP_KEYS = {"filters", "formulas", "properties", "summaries", "views"}
VALID_VIEW_TYPES = {"table", "cards", "list", "map"}
DURATION_MISTAKE_RE = re.compile(
    r"\(\s*(?:now\(\)|today\(\)|file\.[cm]time|date\([^)]*\))\s*-\s*(?:now\(\)|today\(\)|file\.[cm]time|date\([^)]*\)|note\.[A-Za-z0-9_-]+)\s*\)\.(?:round|floor|ceil|abs|toFixed)\s*\("
)
VALID_PROP_PREFIXES = ("note.", "file.", "formula.")


def _parse_yaml(text: str) -> tuple[dict | None, list[dict]]:
    issues: list[dict] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\t+", line):
            issues.append({
                "severity": "error",
                "code": "YAML_TAB_INDENT",
                "line": idx,
                "message": "Tabs are forbidden for YAML indentation; use spaces",
            })

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except Exception as exc:
            line_no = getattr(getattr(exc, "problem_mark", None), "line", 0) + 1
            issues.append({
                "severity": "error",
                "code": "YAML_PARSE_ERROR",
                "line": line_no,
                "message": f"Invalid YAML: {exc}",
            })
            return None, issues
        if not isinstance(data, dict):
            issues.append({
                "severity": "error",
                "code": "ROOT_NOT_MAPPING",
                "line": 1,
                "message": "Top-level .base content must be a YAML mapping",
            })
            return None, issues
        return data, issues

    # Pure-stdlib lightweight fallback parser for top-level keys, properties, and views
    data = _stdlib_fallback_parse(text, issues)
    return data, issues


def _stdlib_fallback_parse(text: str, issues: list[dict]) -> dict:
    data: dict = {}
    section: str | None = None
    views: list[dict] = []
    props: dict[str, dict] = {}
    formulas: dict[str, str] = {}
    current_view: dict | None = None

    for idx, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            m = re.match(r"^([A-Za-z0-9_.-]+)\s*:(.*)$", raw)
            if not m:
                issues.append({
                    "severity": "error",
                    "code": "YAML_TOP_SYNTAX",
                    "line": idx,
                    "message": f"Malformed top-level YAML line: {stripped}",
                })
                section = None
                continue
            section = m.group(1)
            val = m.group(2).strip()
            data[section] = val if val else {}
            current_view = None
            continue

        if section == "properties" and indent == 2:
            m = re.match(r"^\s{2}([\"']?[A-Za-z0-9_.\-/]+[\"']?)\s*:", raw)
            if m:
                key = m.group(1).strip("\"'")
                props[key] = {}
        elif section == "formulas" and indent == 2:
            m = re.match(r"^\s{2}([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
            if m:
                formulas[m.group(1)] = m.group(2).strip()
        elif section == "views":
            m_item = re.match(r"^\s*-\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
            if m_item:
                current_view = {m_item.group(1): m_item.group(2).strip().strip("\"'")}
                views.append(current_view)
            elif current_view is not None:
                m_kv = re.match(r"^\s{4,}([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
                if m_kv and m_kv.group(1) not in current_view:
                    current_view[m_kv.group(1)] = m_kv.group(2).strip().strip("\"'")

    if "properties" in data:
        data["properties"] = props
    if "formulas" in data:
        data["formulas"] = formulas
    if "views" in data:
        data["views"] = views
    return data


def validate_text(text: str) -> dict:
    data, issues = _parse_yaml(text)

    # Scan raw text for Duration formula mistakes regardless of parser mode
    for idx, line in enumerate(text.splitlines(), 1):
        if DURATION_MISTAKE_RE.search(line):
            issues.append({
                "severity": "warning",
                "code": "DURATION_NO_UNIT",
                "line": idx,
                "message": "Date subtraction yields a Duration; access .days/.hours/.minutes before calling .round()/.floor()",
            })

    if data is not None:
        for key in sorted(data.keys()):
            if key not in VALID_TOP_KEYS:
                issues.append({
                    "severity": "error",
                    "code": "UNKNOWN_TOP_KEY",
                    "line": 1,
                    "message": f"Unknown top-level key {key!r} (allowed: {sorted(VALID_TOP_KEYS)})",
                })

        props = data.get("properties")
        if isinstance(props, dict):
            for pkey in sorted(props.keys()):
                if not isinstance(pkey, str) or not pkey.startswith(VALID_PROP_PREFIXES):
                    issues.append({
                        "severity": "warning",
                        "code": "PROPERTY_MISSING_PREFIX",
                        "line": 1,
                        "message": f"Property {pkey!r} under properties: lacks note./file./formula. prefix and may be ignored by Obsidian",
                    })

        views = data.get("views")
        if views is None:
            issues.append({
                "severity": "warning",
                "code": "NO_VIEWS",
                "line": 1,
                "message": "No views: section defined",
            })
        elif not isinstance(views, list) or not views:
            issues.append({
                "severity": "error",
                "code": "INVALID_VIEWS",
                "line": 1,
                "message": "views: must be a non-empty YAML list",
            })
        else:
            for i, view in enumerate(views, 1):
                if not isinstance(view, dict):
                    issues.append({
                        "severity": "error",
                        "code": "VIEW_NOT_MAPPING",
                        "line": 1,
                        "message": f"View #{i} must be a mapping",
                    })
                    continue
                vtype = view.get("type")
                if not vtype:
                    issues.append({
                        "severity": "error",
                        "code": "VIEW_MISSING_TYPE",
                        "line": 1,
                        "message": f"View #{i} is missing required 'type' field",
                    })
                elif vtype not in VALID_VIEW_TYPES:
                    issues.append({
                        "severity": "warning",
                        "code": "VIEW_UNKNOWN_TYPE",
                        "line": 1,
                        "message": f"View #{i} has non-standard type {vtype!r} (built-in: {sorted(VALID_VIEW_TYPES)})",
                    })

    issues.sort(key=lambda x: (x["severity"], x["line"], x["code"]))
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    return {
        "status": "PASS" if errors == 0 else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
        "not_checked": ["obsidian_live_rendering", "vault_frontmatter_existence", "formula_runtime_evaluation"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate an Obsidian Bases (.base) file.")
    ap.add_argument("path", help="Path to the .base file")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    args = ap.parse_args(argv)

    p = Path(args.path)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read {p}: {exc}", file=sys.stderr)
        return 2

    res = validate_text(text)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for item in res["issues"]:
            print(f"{item['severity'].upper()} [L{item['line']}] {item['code']}: {item['message']}")
        print(f"{res['status']} (errors={res['errors']}, warnings={res['warnings']})")
    return 0 if res["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
