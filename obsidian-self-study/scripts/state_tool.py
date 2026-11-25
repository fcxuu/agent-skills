#!/usr/bin/env python3
"""Atomic CLI manager for obsidian-self-study .build-state.json (stdlib only).

Matches the exact schema validated by scripts/check_vault.py, computes real SHA-256
source fingerprints, enforces 5-state transitions and protected-completed guards,
and commits atomically via .build-state.json.tmp + os.replace().
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

STATES = ("pending", "processing", "qa_pending", "completed", "failed")
COURSE_STATES = ("in_progress", "completed", "completed_with_issues", "interrupted")

# Automatic transitions permitted without special flags
AUTO_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"pending", "processing"},
    "processing": {"processing", "qa_pending", "failed"},
    "qa_pending": {"qa_pending", "completed", "processing", "failed"},
    "completed": {"completed"},  # protected snapshot; requires --p0-demote or --controlled-revision
    "failed": {"failed"},        # requires --controlled-revision to resume
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def course_rel_path(course: Path, raw: str) -> tuple[str, Path]:
    p = Path(raw)
    resolved = (p if p.is_absolute() else (course / p)).resolve()
    course_res = course.resolve()
    if not resolved.is_relative_to(course_res):
        raise ValueError(f"Path escapes course directory: {raw}")
    rel = resolved.relative_to(course_res).as_posix()
    return rel, resolved


def compute_sha256(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
            total += len(chunk)
    return h.hexdigest(), total


def load_state(course: Path) -> dict:
    state_path = course / ".build-state.json"
    if not state_path.is_file():
        raise FileNotFoundError(f"Missing state file: {state_path} (run `init` first)")
    data = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid .build-state.json: root must be a JSON object")
    return data


def save_state_atomic(course: Path, state: dict) -> Path:
    state_path = course / ".build-state.json"
    tmp_path = course / ".build-state.json.tmp"
    payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    tmp_path.write_text(payload, encoding="utf-8")
    os.replace(tmp_path, state_path)
    # Verify readable JSON after commit
    json.loads(state_path.read_text(encoding="utf-8"))
    return state_path


def cmd_init(args: argparse.Namespace) -> int:
    course = Path(args.course).resolve()
    if not course.is_dir():
        print(f"ERROR: course directory not found: {course}", file=sys.stderr)
        return 2
    state_path = course / ".build-state.json"
    if state_path.exists() and not args.force:
        print(f"ERROR: {state_path} already exists (pass --force to overwrite)", file=sys.stderr)
        return 1
    state = {
        "schema_version": args.schema_version,
        "course_status": "in_progress",
        "sources": {},
        "sections": [],
    }
    save_state_atomic(course, state)
    print(f"Initialized {state_path}")
    return 0


def cmd_register_source(args: argparse.Namespace) -> int:
    course = Path(args.course).resolve()
    state = load_state(course)
    raw_rel, raw_abs = course_rel_path(course, args.raw)
    if not raw_rel.startswith("raw-markdown/") or not raw_rel.endswith(".md"):
        print(f"ERROR: --raw must be inside raw-markdown/ and end with .md: {raw_rel}", file=sys.stderr)
        return 2
    src_rel, src_abs = course_rel_path(course, args.source)
    if not raw_abs.is_file():
        print(f"ERROR: raw markdown file does not exist: {raw_abs}", file=sys.stderr)
        return 1
    if not src_abs.is_file():
        print(f"ERROR: source file does not exist: {src_abs}", file=sys.stderr)
        return 1

    sha256, size_bytes = compute_sha256(raw_abs)
    state.setdefault("sources", {})[raw_rel] = {
        "source_file": src_rel,
        "sha256": sha256,
        "size_bytes": size_bytes,
    }
    save_state_atomic(course, state)
    print(json.dumps({"raw": raw_rel, "source_file": src_rel, "sha256": sha256, "size_bytes": size_bytes}, ensure_ascii=False))
    return 0


def cmd_upsert_section(args: argparse.Namespace) -> int:
    course = Path(args.course).resolve()
    state = load_state(course)
    sections: list[dict] = state.setdefault("sections", [])
    existing = next((s for s in sections if isinstance(s, dict) and s.get("id") == args.id), None)

    if existing is None:
        if not args.source_map_ref or not args.output:
            print("ERROR: creating a new section requires --source-map-ref and --output", file=sys.stderr)
            return 2
        out_rel, out_abs = course_rel_path(course, args.output)
        if not out_rel.lower().endswith(".md"):
            print(f"ERROR: --output must end with .md: {out_rel}", file=sys.stderr)
            return 2
        target_status = args.status or "pending"
        if target_status == "completed" and (not out_abs.is_file() or out_abs.stat().st_size == 0):
            print(f"ERROR: cannot mark completed; output file missing or empty: {out_rel}", file=sys.stderr)
            return 1
        record = {
            "id": args.id,
            "status": target_status,
            "source_map_ref": args.source_map_ref,
            "output_path": out_rel,
            "attempts": 1 if args.bump_attempts else 0,
            "qa_ids": list(dict.fromkeys(args.qa_id or [])),
            "updated_at": utc_now(),
        }
        sections.append(record)
        save_state_atomic(course, state)
        print(json.dumps(record, ensure_ascii=False))
        return 0

    cur_status = existing.get("status", "pending")
    new_status = args.status or cur_status

    if new_status != cur_status:
        allowed = AUTO_TRANSITIONS.get(cur_status, set())
        if cur_status == "completed":
            if new_status == "failed" and args.p0_demote:
                if not args.qa_id and not existing.get("qa_ids"):
                    print("ERROR: --p0-demote requires at least one --qa-id", file=sys.stderr)
                    return 1
            elif new_status == "processing" and args.controlled_revision:
                pass
            else:
                print(
                    f"ERROR: protected completed section '{args.id}' cannot transition to '{new_status}' "
                    "(use --p0-demote with --qa-id for failed, or --controlled-revision for authorized edit)",
                    file=sys.stderr,
                )
                return 1
        elif cur_status == "failed":
            if new_status == "processing" and args.controlled_revision:
                pass
            else:
                print(
                    f"ERROR: failed section '{args.id}' cannot auto-transition to '{new_status}' "
                    "(pass --controlled-revision after explicit user approval)",
                    file=sys.stderr,
                )
                return 1
        elif new_status not in allowed:
            print(f"ERROR: illegal transition for '{args.id}': {cur_status} -> {new_status}", file=sys.stderr)
            return 1

    if args.source_map_ref:
        existing["source_map_ref"] = args.source_map_ref
    if args.output:
        out_rel, _ = course_rel_path(course, args.output)
        if not out_rel.lower().endswith(".md"):
            print(f"ERROR: --output must end with .md: {out_rel}", file=sys.stderr)
            return 2
        existing["output_path"] = out_rel

    _, out_abs = course_rel_path(course, existing["output_path"])
    if new_status in ("qa_pending", "completed") and (not out_abs.is_file() or out_abs.stat().st_size == 0):
        print(f"ERROR: cannot set '{new_status}'; output file missing or empty: {existing['output_path']}", file=sys.stderr)
        return 1

    existing["status"] = new_status
    if args.bump_attempts:
        existing["attempts"] = int(existing.get("attempts", 0)) + 1
    if args.qa_id:
        merged = list(existing.get("qa_ids", []))
        for qid in args.qa_id:
            if qid not in merged:
                merged.append(qid)
        existing["qa_ids"] = merged
    existing["updated_at"] = utc_now()

    save_state_atomic(course, state)
    print(json.dumps(existing, ensure_ascii=False))
    return 0


def cmd_set_course_status(args: argparse.Namespace) -> int:
    course = Path(args.course).resolve()
    state = load_state(course)
    state["course_status"] = args.status
    save_state_atomic(course, state)
    print(json.dumps({"course_status": args.status}, ensure_ascii=False))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    course = Path(args.course).resolve()
    state = load_state(course)
    sections = state.get("sections", [])
    counts = {s: 0 for s in STATES}
    next_pending: list[str] = []
    failed_ids: list[str] = []
    for sec in sections:
        st = sec.get("status")
        if st in counts:
            counts[st] += 1
        if st == "pending":
            next_pending.append(sec.get("id", ""))
        elif st == "failed":
            failed_ids.append(sec.get("id", ""))
    out = {
        "schema_version": state.get("schema_version"),
        "course_status": state.get("course_status"),
        "sources_count": len(state.get("sources", {})),
        "sections_total": len(sections),
        "counts": counts,
        "next_pending": next_pending[:5],
        "failed_sections": failed_ids,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(
            f"course_status={out['course_status']} sources={out['sources_count']} "
            f"sections={out['sections_total']} counts={counts}"
        )
        if next_pending:
            print("next_pending:", ", ".join(next_pending[:5]))
        if failed_ids:
            print("failed:", ", ".join(failed_ids))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Atomic manager for obsidian-self-study .build-state.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize a fresh .build-state.json")
    p_init.add_argument("--course", required=True, help="Course directory path")
    p_init.add_argument("--schema-version", default="0.2.0")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing .build-state.json")
    p_init.set_defaults(func=cmd_init)

    p_src = sub.add_parser("register-source", help="Register/update a raw-markdown source with real SHA-256")
    p_src.add_argument("--course", required=True)
    p_src.add_argument("--raw", required=True, help="Course-relative raw-markdown/*.md path")
    p_src.add_argument("--source", required=True, help="Course-relative original source file path")
    p_src.set_defaults(func=cmd_register_source)

    p_sec = sub.add_parser("upsert-section", help="Create or update a section with 5-state transition guards")
    p_sec.add_argument("--course", required=True)
    p_sec.add_argument("--id", required=True, help="Stable section ID (e.g. ch01-sec01)")
    p_sec.add_argument("--source-map-ref", help="Logical section key in raw-markdown/source-map.md")
    p_sec.add_argument("--output", help="Course-relative output note .md path")
    p_sec.add_argument("--status", choices=STATES)
    p_sec.add_argument("--qa-id", action="append", help="QA ID to associate (repeatable)")
    p_sec.add_argument("--bump-attempts", action="store_true", help="Increment attempts by 1")
    p_sec.add_argument("--p0-demote", action="store_true", help="Allow completed -> failed on verified new P0")
    p_sec.add_argument("--controlled-revision", action="store_true", help="Allow completed/failed -> processing after explicit user approval")
    p_sec.set_defaults(func=cmd_upsert_section)

    p_cs = sub.add_parser("set-course-status", help="Update top-level course_status")
    p_cs.add_argument("--course", required=True)
    p_cs.add_argument("--status", required=True, choices=COURSE_STATES)
    p_cs.set_defaults(func=cmd_set_course_status)

    p_sum = sub.add_parser("summary", help="Show concise course build status summary")
    p_sum.add_argument("--course", required=True)
    p_sum.add_argument("--json", action="store_true")
    p_sum.set_defaults(func=cmd_summary)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
