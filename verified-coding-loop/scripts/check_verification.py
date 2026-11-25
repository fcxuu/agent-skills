#!/usr/bin/env python3
"""Check consistency of a Markdown verification report.

No command in the report is executed. A structurally valid report is not proof
that its observations are accurate or that its coverage is sufficient.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = ("Result", "Evidence", "Changed files", "Remaining risks")
OVERALL_STATES = {"pass", "fail", "partial", "not_verified"}
EVIDENCE_STATES = {"pass", "fail", "not_run", "blocked"}
PLACEHOLDER_RE = re.compile(r"\[填写[^\]]*\]|\b(?:TODO|TBD|REPLACE_ME)\b", re.IGNORECASE)
EMPTY_EVIDENCE = {"", "none", "n/a", "na", "not run", "not_run", "blocked", "unknown"}
CONTRACT_AC_RE = re.compile(r"^[ \t]*-[ \t]+\[[ xX]\][ \t]+([\w.#/-]+)[ \t]*\|[ \t]*(\S[^\n]*?)[ \t]*$", re.MULTILINE)


def _without_fenced_code(text: str) -> str:
    """Ignore Markdown fenced examples when interpreting report structure."""
    result = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is None and match:
            fence = match.group(1)
            result.append("\n")
        elif fence is not None:
            if re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", line):
                fence = None
            result.append("\n")
        else:
            result.append(line)
    return "".join(result)


def _field_count(text: str, name: str) -> int:
    return len(re.findall(rf"^[ \t]*(?:-[ \t]+)?{re.escape(name)}:[ \t]*.*$", text, re.MULTILINE))


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    next_heading = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end]


def _field(text: str, name: str) -> str | None:
    match = re.search(
        rf"^[ \t]*(?:-[ \t]+)?{re.escape(name)}:[ \t]*(.*?)[ \t]*$",
        text,
        re.MULTILINE,
    )
    return match.group(1) if match else None


def _evidence_blocks(section: str) -> list[tuple[str, str]]:
    lines = section.splitlines()
    starts = [
        index for index, line in enumerate(lines)
        if re.match(r"^\s*-\s+ID:\s*\S+\s*$", line)
    ]
    blocks = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end])
        evidence_id = re.match(r"^\s*-\s+ID:\s*(\S+)\s*$", lines[start]).group(1)
        blocks.append((evidence_id, block))
    return blocks


def _extract_contract_ac_ids(contract_text: str) -> list[str]:
    cleaned = _without_fenced_code(contract_text)
    ac_section = _section(cleaned, "Acceptance criteria")
    return [cid for cid, _ in CONTRACT_AC_RE.findall(ac_section)]


def validate(path: str | Path, contract_path: str | Path | None = None) -> list[str]:
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

    return _validate_text(text, contract_ac_ids=contract_ids)


def _validate_text(text: str, contract_ac_ids: list[str] | None = None) -> list[str]:
    text = _without_fenced_code(text)
    errors: list[str] = []
    for heading in REQUIRED_HEADINGS:
        count = len(re.findall(rf"^##[ \t]+{re.escape(heading)}[ \t]*$", text, re.MULTILINE))
        if count == 0:
            errors.append(f"missing required heading: ## {heading}")
        elif count > 1:
            errors.append(f"duplicate heading: ## {heading}")
    if PLACEHOLDER_RE.search(text):
        errors.append("report contains an unfilled placeholder")

    result = _section(text, "Result")
    if _field_count(result, "Overall") > 1:
        errors.append("Result has duplicate Overall fields")
    overall = _field(result, "Overall")
    if overall not in OVERALL_STATES:
        errors.append("Overall must be pass, fail, partial, or not_verified")

    evidence_section = _section(text, "Evidence")
    for line in evidence_section.splitlines():
        if re.match(r"^[ \t]*(?:-[ \t]+)?ID[ \t]*:", line) and not re.fullmatch(
            r"[ \t]*-[ \t]+ID:[ \t]*[^\s,]+[ \t]*", line
        ):
            errors.append(f"malformed evidence ID entry: {line.strip()}")
    evidence = _evidence_blocks(evidence_section)
    if not evidence:
        errors.append("at least one evidence block with an ID is required")
    ids = [evidence_id for evidence_id, _ in evidence]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("duplicate evidence ID(s): " + ", ".join(duplicates))

    mapped_ac_ids: set[str] = set()
    mapping_count = len(re.findall(r"^##[ \t]+Acceptance mapping[ \t]*$", text, re.MULTILINE))
    if mapping_count > 1:
        errors.append("duplicate heading: ## Acceptance mapping")
    if mapping_count:
        mapping = _section(text, "Acceptance mapping")
        lines = [line.strip() for line in mapping.splitlines() if line.strip()]
        if not lines:
            errors.append("Acceptance mapping needs at least one entry")
        for line in lines:
            match = re.fullmatch(r"-[ \t]+([\w.#/-]+):[ \t]*([^\s,]+(?:[ \t]*,[ \t]*[^\s,]+)*)[ \t]*", line)
            if not match:
                errors.append(f"malformed Acceptance mapping entry: {line}")
                continue
            item, references = match.groups()
            if item in mapped_ac_ids:
                errors.append(f"duplicate Acceptance mapping entry: {item}")
            mapped_ac_ids.add(item)
            refs = [ref.strip() for ref in references.split(",")]
            if len(refs) != len(set(refs)):
                errors.append(f"{item} has duplicate evidence references")
            for ref in refs:
                if ref not in ids:
                    errors.append(f"{item} references unknown evidence ID: {ref}")

    if contract_ac_ids is not None:
        if not contract_ac_ids:
            errors.append("contract contains no parseable acceptance criteria IDs")
        else:
            missing_acs = [cid for cid in contract_ac_ids if cid not in mapped_ac_ids]
            extra_acs = sorted(mapped_ac_ids - set(contract_ac_ids))
            if missing_acs:
                errors.append("contract AC ID(s) missing from Acceptance mapping: " + ", ".join(missing_acs))
            if extra_acs:
                errors.append("Acceptance mapping references AC ID(s) not in contract: " + ", ".join(extra_acs))

    statuses: list[str] = []
    for evidence_id, block in evidence:
        fields = {
            name: _field(block, name)
            for name in ("Status", "Check", "Command", "Observed", "Scope")
        }
        for name, value in fields.items():
            if _field_count(block, name) > 1:
                errors.append(f"{evidence_id} has duplicate {name} fields")
            if value is None or not value.strip():
                errors.append(f"{evidence_id} needs a non-empty {name} field")
        status = fields["Status"]
        if status not in EVIDENCE_STATES:
            errors.append(f"{evidence_id} has invalid Status: {status!r}")
        else:
            statuses.append(status)
        if status == "pass":
            for name in ("Command", "Observed"):
                value = (fields[name] or "").strip().lower()
                if value in EMPTY_EVIDENCE:
                    errors.append(f"{evidence_id} cannot be pass without actual {name}")

    if statuses and len(statuses) == len(evidence):
        if "fail" in statuses:
            if overall != "fail":
                errors.append("failed evidence requires overall fail")
        elif not any(status == "pass" for status in statuses):
            if overall != "not_verified":
                errors.append("no actual results requires overall not_verified")
        elif any(status in {"not_run", "blocked"} for status in statuses):
            if overall != "partial":
                errors.append("passed and unrun evidence requires overall partial")
        elif overall not in {"pass", "partial"}:
            errors.append("all passed evidence requires overall pass or explained partial")
        elif overall == "partial":
            summary = (_field(result, "Summary") or "").strip()
            if not summary or summary.lower() in EMPTY_EVIDENCE:
                errors.append("overall partial with all passed evidence requires a Summary explaining the uncovered scope")
    elif overall == "pass":
        errors.append("overall pass requires valid evidence")

    changed_files = _section(text, "Changed files")
    if not re.search(r"^\s*-\s+\S+", changed_files, re.MULTILINE):
        errors.append("Changed files needs at least one file entry")
    risks = _section(text, "Remaining risks").strip()
    if not risks:
        errors.append("Remaining risks cannot be empty; use 'none' when appropriate")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 when document suggestions are found")
    parser.add_argument("--contract", help="optional coding-task-contract Markdown file to cross-check AC coverage")
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

    contract_ids: list[str] | None = None
    if args.contract:
        try:
            contract_ids = _extract_contract_ac_ids(Path(args.contract).read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError) as exc:
            if args.json:
                print(json.dumps({"path": args.path, "status": "error", "errors": [f"cannot read contract {args.contract}: {exc}"]}, ensure_ascii=False, indent=2))
            else:
                print(f"ERROR: cannot read contract {args.contract}: {exc}", file=sys.stderr)
            return 2

    errors = _validate_text(text, contract_ac_ids=contract_ids)
    if args.json:
        status = "ok" if not errors else ("error" if args.strict else "suggestions")
        print(json.dumps({"path": args.path, "contract": args.contract, "status": status, "strict": args.strict, "errors": errors}, ensure_ascii=False, indent=2))
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
