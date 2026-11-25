#!/usr/bin/env python3
"""Validate agent coding handoff and independent review documents."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\[填写[^\]]*\]|\b(?:TODO|TBD|REPLACE_ME)\b", re.IGNORECASE)
HANDOFF_HEADINGS = (
    "Task", "Goal and contract", "Changes", "Evidence",
    "Open issues and risks", "Next action", "Review",
)
NO_CHECK = {"", "none", "n/a", "not run", "not_run", "blocked", "pending", "not_verified", "无", "未运行", "未验证"}
REVIEW_HEADINGS = (
    "Task", "Verdict", "Criteria", "Findings", "Checks actually run",
    "Residual risk and handoff",
)
CONTRACT_AC_RE = re.compile(r"^[ \t]*-[ \t]+\[[ xX]\][ \t]+([\w.#/-]+)[ \t]*\|[ \t]*(\S[^\n]*?)[ \t]*$", re.MULTILINE)


def _sections(text: str, required: tuple[str, ...]) -> tuple[dict[str, str], list[str]]:
    """Parse level-two sections, ignoring fenced code examples."""
    sections: dict[str, list[str]] = {}
    errors: list[str] = []
    current = None
    fence = None
    visible = []
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) and not marker.group(2).strip():
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        visible.append(line)
        heading = re.fullmatch(r" {0,3}##[ \t]+(.+?)[ \t]*", line)
        if heading:
            current = heading.group(1)
            if current in sections:
                errors.append(f"duplicate heading: ## {current}")
            else:
                sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    for heading in required:
        if heading not in sections:
            errors.append(f"missing required heading: ## {heading}")
    if PLACEHOLDER_RE.search("\n".join(visible)):
        errors.append("document contains an unfilled placeholder")
    return {name: "\n".join(lines) for name, lines in sections.items()}, errors


def _extract_contract_ac_ids(contract_text: str) -> list[str]:
    sections, _ = _sections(contract_text, ())
    return [cid for cid, _ in CONTRACT_AC_RE.findall(sections.get("Acceptance criteria", ""))]


def _fields(section: str, name: str) -> list[str]:
    pattern = re.compile(rf"^[ \t]*-[ \t]+{re.escape(name)}:[ \t]*(.*?)[ \t]*$")
    return [match.group(1) for line in section.splitlines() if (match := pattern.fullmatch(line))]


def _one(sections: dict[str, str], section: str, name: str, errors: list[str]) -> str:
    values = _fields(sections.get(section, ""), name)
    if len(values) != 1 or not values[0].strip():
        errors.append(f"{section} needs exactly one non-empty {name} field")
        return ""
    return values[0].strip()


def _validate_handoff(text: str, contract_ac_ids: list[str] | None = None) -> list[str]:
    sections, errors = _sections(text, HANDOFF_HEADINGS)
    required = {
        "Task": ("Repository/root", "Base revision", "Current revision/diff"),
        "Goal and contract": ("Contract path",),
        "Changes": ("Files changed",),
        "Evidence": ("Verification report", "Commands actually run"),
        "Next action": ("Owner", "Action"),
    }
    for section, names in required.items():
        for name in names:
            _one(sections, section, name, errors)
    status = _one(sections, "Task", "Status", errors)
    result = _one(sections, "Evidence", "Result", errors)
    review = _one(sections, "Review", "Review status", errors)
    if status not in {"ready", "blocked", "complete"}:
        errors.append("handoff Status must be ready, blocked, or complete")
    if result not in {"pass", "fail", "partial", "not_verified"}:
        errors.append("handoff Result must be pass, fail, partial, or not_verified")
    if review not in {"pending", "pass", "fail", "not_verified"}:
        errors.append("Review status must be pending, pass, fail, or not_verified")
    if review == "pass":
        reviewers = _fields(sections.get("Review", ""), "Reviewer")
        if reviewers and (len(reviewers) != 1 or reviewers[0].casefold() in NO_CHECK):
            errors.append("passing review cannot name a pending or missing reviewer")
    if status == "complete":
        if result != "pass" or review != "pass":
            errors.append("complete handoff requires Result: pass and Review status: pass")
        for section, field in (("Goal and contract", "Remaining AC IDs"),
                               ("Next action", "Acceptance criteria remaining")):
            values = _fields(sections.get(section, ""), field)
            if len(values) > 1:
                errors.append(f"duplicate {field} field")
            if any(value.casefold() not in {"none", "n/a", "无", "无剩余", "不适用"} for value in values):
                errors.append(f"complete handoff cannot list remaining AC in {field}")

    if contract_ac_ids is not None:
        if not contract_ac_ids:
            errors.append("contract contains no parseable acceptance criteria IDs")
        else:
            valid_set = set(contract_ac_ids)
            for section, field in (("Goal and contract", "Remaining AC IDs"),
                                   ("Next action", "Acceptance criteria remaining")):
                for value in _fields(sections.get(section, ""), field):
                    if value.casefold() in {"none", "n/a", "无", "无剩余", "不适用"}:
                        continue
                    tokens = [t.strip() for t in re.split(r"[,，\s]+", value) if t.strip()]
                    unknown = [t for t in tokens if t not in valid_set]
                    if unknown:
                        errors.append(f"{field} references AC ID(s) not in contract: " + ", ".join(unknown))
    return errors


def _validate_review(text: str, contract_ac_ids: list[str] | None = None) -> list[str]:
    sections, errors = _sections(text, REVIEW_HEADINGS)
    for name in ("Reviewed revision/diff", "Reviewer"):
        _one(sections, "Task", name, errors)
    verdict = _one(sections, "Verdict", "Status", errors)
    if verdict not in {"pass", "fail", "not_verified"}:
        errors.append("review Status must be pass, fail, or not_verified")

    criteria = []
    for line in sections.get("Criteria", "").splitlines():
        if not re.match(r"^[ \t]*[-*+][ \t]+", line):
            continue
        match = re.fullmatch(r"[ \t]*-[ \t]+([\w.#/-]+):[ \t]*(pass|fail|not_verified)[ \t]*[—-][ \t]*(.*?)[ \t]*", line)
        if not match or not match.group(3).strip():
            errors.append("every AC-n criterion must have a valid status and evidence")
            continue
        criteria.append(match.groups())
    if not criteria:
        errors.append("review needs at least one AC-n criterion with status and evidence")
    ids = [item[0] for item in criteria]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("duplicate review criterion ID(s): " + ", ".join(duplicates))
    for criterion_id, status, evidence in criteria:
        if status == "pass" and evidence.strip().casefold() in NO_CHECK:
            errors.append(f"{criterion_id} cannot be pass without evidence")
    if verdict == "pass" and any(status != "pass" for _, status, _ in criteria):
        errors.append("pass review cannot contain failed or unverified criteria")

    if contract_ac_ids is not None:
        if not contract_ac_ids:
            errors.append("contract contains no parseable acceptance criteria IDs")
        else:
            reviewed_set = set(ids)
            missing = [cid for cid in contract_ac_ids if cid not in reviewed_set]
            extra = sorted(reviewed_set - set(contract_ac_ids))
            if missing:
                errors.append("contract AC ID(s) missing from review Criteria: " + ", ".join(missing))
            if extra:
                errors.append("review Criteria references AC ID(s) not in contract: " + ", ".join(extra))

    severities = _fields(sections.get("Findings", ""), "Severity")
    if not severities or any(value not in {"none", "blocker", "major", "minor"} for value in severities):
        errors.append("Findings Severity must be none, blocker, major, or minor")
    if verdict == "pass" and any(value in {"blocker", "major"} for value in severities):
        errors.append("pass review cannot contain unresolved blocker/major findings")
    checks = sections.get("Checks actually run", "").strip()
    if not checks:
        errors.append("Checks actually run cannot be empty; use 'none' when appropriate")
    check_items = [line.strip().lstrip("-* ").strip().casefold() for line in checks.splitlines()]
    if verdict == "pass" and not any(item not in NO_CHECK for item in check_items):
        errors.append("pass review requires at least one actual check")
    return errors


def validate(path: str | Path, kind: str, contract_path: str | Path | None = None) -> list[str]:
    """Return human-readable validation errors, or an empty list when valid."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]
    except UnicodeError as exc:
        return [f"{path} is not valid UTF-8: {exc}"]

    contract_ids: list[str] | None = None
    if contract_path is not None:
        cp = Path(contract_path)
        try:
            contract_ids = _extract_contract_ac_ids(cp.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError) as exc:
            return [f"cannot read contract {cp}: {exc}"]
    return _validate_text(text, kind, contract_ac_ids=contract_ids)


def _validate_text(text: str, kind: str, contract_ac_ids: list[str] | None = None) -> list[str]:
    if kind == "handoff":
        return _validate_handoff(text, contract_ac_ids=contract_ac_ids)
    if kind == "review":
        return _validate_review(text, contract_ac_ids=contract_ac_ids)
    return [f"unknown document kind: {kind}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("handoff", "review"), required=True)
    parser.add_argument("--strict", action="store_true", help="exit 1 when document suggestions are found")
    parser.add_argument("--contract", help="optional coding-task-contract Markdown file to cross-check AC IDs")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON output")
    parser.add_argument("path", help="UTF-8 Markdown document to check")
    args = parser.parse_args()
    try:
        text = Path(args.path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        if args.json:
            print(json.dumps({"path": args.path, "kind": args.kind, "status": "error", "errors": [f"cannot read {args.path} as UTF-8: {exc}"]}, ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: cannot read {args.path} as UTF-8: {exc}", file=sys.stderr)
        return 2

    contract_ids: list[str] | None = None
    if args.contract:
        try:
            contract_ids = _extract_contract_ac_ids(Path(args.contract).read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError) as exc:
            if args.json:
                print(json.dumps({"path": args.path, "kind": args.kind, "status": "error", "errors": [f"cannot read contract {args.contract}: {exc}"]}, ensure_ascii=False, indent=2))
            else:
                print(f"ERROR: cannot read contract {args.contract}: {exc}", file=sys.stderr)
            return 2

    errors = _validate_text(text, args.kind, contract_ac_ids=contract_ids)
    if args.json:
        status = "ok" if not errors else ("error" if args.strict else "suggestions")
        print(json.dumps({"path": args.path, "kind": args.kind, "contract": args.contract, "status": status, "strict": args.strict, "errors": errors}, ensure_ascii=False, indent=2))
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
