#!/usr/bin/env python3
"""Validate the structure of a coding task contract.

This checks documentation consistency only; it does not assess requirement quality
or execute any acceptance criterion.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "Goal and context",
    "Scope",
    "Acceptance criteria",
    "Verification plan",
    "Change and recovery boundaries",
    "Handoff",
)
AC_RE = re.compile(r"^[ \t]*-[ \t]+\[[ xX]\][ \t]+([\w.#/-]+)[ \t]*\|[ \t]*(\S[^\n]*?)[ \t]*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\[填写[^\]]*\]|\b(?:TODO|TBD|REPLACE_ME)\b", re.IGNORECASE)


def _strip_fences(text: str) -> str:
    lines = text.splitlines()
    visible: list[str] = []
    fence: tuple[str, int] | None = None
    for line in lines:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1] and not marker.group(2).strip():
                fence = None
            visible.append("")
        elif marker:
            fence = (marker.group(1)[0], len(marker.group(1)))
            visible.append("")
        else:
            visible.append(line)
    return "\n".join(visible)


def extract_ac_ids(text: str) -> list[str]:
    """Extract ordered acceptance criterion IDs from a contract Markdown string."""
    cleaned = _strip_fences(text)
    sections = re.split(r"(?m)^##\s+(.+?)\s*$", cleaned)
    section_map: dict[str, str] = {}
    for i in range(1, len(sections), 2):
        heading = sections[i]
        section_map[heading] = section_map.get(heading, "") + "\n" + sections[i + 1]
    return [cid for cid, _ in AC_RE.findall(section_map.get("Acceptance criteria", ""))]


def validate(path: str | Path) -> list[str]:
    """Return human-readable validation errors, or an empty list when valid."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]
    except UnicodeError as exc:
        return [f"{path} is not valid UTF-8: {exc}"]

    return _validate_text(text)


def _validate_text(text: str) -> list[str]:
    errors: list[str] = []
    text = _strip_fences(text)
    sections = re.split(r"(?m)^##\s+(.+?)\s*$", text)
    section_map: dict[str, str] = {}
    for i in range(1, len(sections), 2):
        heading = sections[i]
        section_map[heading] = section_map.get(heading, "") + "\n" + sections[i + 1]
    for heading in REQUIRED_HEADINGS:
        if heading not in section_map:
            errors.append(f"missing required heading: ## {heading}")
    for heading in ("In scope", "Out of scope"):
        if not re.search(rf"^###\s+{re.escape(heading)}\s*$", section_map.get("Scope", ""), re.MULTILINE):
            errors.append(f"missing required heading: ### {heading}")

    placeholder_lines = [
        str(number)
        for number, line in enumerate(text.splitlines(), start=1)
        if PLACEHOLDER_RE.search(line)
    ]
    if placeholder_lines:
        errors.append("unfilled placeholder(s) on line(s): " + ", ".join(placeholder_lines))

    criteria_text = section_map.get("Acceptance criteria", "")
    criteria = AC_RE.findall(criteria_text)
    for line in criteria_text.splitlines():
        if re.match(r"^\s*[-*+]\s+", line) and not AC_RE.fullmatch(line):
            errors.append(f"malformed acceptance criterion: {line.strip()}")
    if not criteria:
        errors.append("at least one checklist item matching '- [ ] AC-1 | ...' is required")
    ids = [criterion_id for criterion_id, _ in criteria]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("duplicate acceptance criterion ID(s): " + ", ".join(duplicates))

    for field in ("Baseline", "Checks"):
        if not re.search(rf"^[ \t]*-[ \t]+{field}:[ \t]*\S+", section_map.get("Verification plan", ""), re.MULTILINE):
            errors.append(f"verification plan needs a non-empty {field} field")

    statuses = re.findall(r"^[ \t]*-[ \t]+Status:[ \t]*([^\n]*)$", text, re.MULTILINE)
    if any(status.strip() not in {"draft", "active", "blocked", "done"} for status in statuses):
        errors.append("Status must be draft, active, blocked, or done")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 when document suggestions are found")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON output")
    parser.add_argument("path", help="UTF-8 Markdown document to check")
    args = parser.parse_args()
    try:
        text = Path(args.path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        if args.json:
            print(json.dumps({"path": args.path, "status": "error", "errors": [f"cannot read {args.path} as UTF-8: {exc}"]}, ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: cannot read {args.path} as UTF-8: {exc}", file=sys.stderr)
        return 2
    errors = _validate_text(text)
    ac_ids = extract_ac_ids(text)
    if args.json:
        status = "ok" if not errors else ("error" if args.strict else "suggestions")
        print(json.dumps({"path": args.path, "status": status, "strict": args.strict, "ac_ids": ac_ids, "errors": errors}, ensure_ascii=False, indent=2))
        return 1 if (errors and args.strict) else 0
    if errors:
        if not args.strict:
            print("Optional template notes. You can deliver the current work with open items.", file=sys.stderr)
        for error in errors:
            print(f"{'ERROR' if args.strict else 'SUGGESTION'}: {error}", file=sys.stderr)
        return 1 if args.strict else 0
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
