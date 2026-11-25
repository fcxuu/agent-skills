#!/usr/bin/env python3
"""Repository-wide audit script for all Agent Skills in this workspace (stdlib only).

Checks every top-level skill directory for:
- Valid SKILL.md YAML frontmatter (`name` matches directory name, non-empty `description`)
- SKILL.md size <= 8192 bytes (context-mode friendly single read)
- Valid relative Markdown links inside SKILL.md
- World-readable permissions (0644/0755)
- Runs all discovered unittest suites (`python3 -B -m unittest discover -s tests`)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", ".github", "scripts", "__pycache__"}


def audit_repo() -> dict:
    skills = sorted(
        d for d in ROOT.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name not in IGNORED_DIRS
    )
    errors: list[str] = []
    warnings: list[str] = []
    skill_reports: list[dict] = []

    for sk in skills:
        skill_md = sk / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{sk.name}: missing SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        size_b = len(text.encode("utf-8"))
        if size_b > 8192:
            warnings.append(f"{sk.name}/SKILL.md exceeds 8 KB ({size_b} B)")

        fm: dict[str, str] = {}
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                for line in text[4:end].splitlines():
                    if ":" in line and not line.startswith(" "):
                        k, v = line.split(":", 1)
                        fm[k.strip()] = v.strip()
        sname = fm.get("name", "")
        if sname != sk.name:
            errors.append(f"{sk.name}: frontmatter name {sname!r} != directory name {sk.name!r}")
        if not fm.get("description"):
            errors.append(f"{sk.name}: missing frontmatter description")

        # Check relative markdown links (skip URLs, anchors, and code spans)
        cleaned = re.sub(r"`[^`\n]+`", "", text)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", cleaned):
            if target.startswith(("http://", "https://", "#")):
                continue
            resolved = (sk / target).resolve()
            if not resolved.exists():
                errors.append(f"{sk.name}/SKILL.md: broken link {target!r}")

        # Permission check
        bad_perms = []
        for dp, dn, fn in os.walk(sk):
            dn[:] = [d for d in dn if not d.startswith(".") and d != "__pycache__"]
            for f in fn:
                if f.startswith(".") or f.endswith(".pyc"):
                    continue
                fp = Path(dp) / f
                mode = stat.S_IMODE(fp.stat().st_mode)
                if (mode & 0o044) != 0o044:
                    bad_perms.append(f"{fp.relative_to(ROOT)} ({oct(mode)})")
        if bad_perms:
            errors.append(f"{sk.name}: restrictive file permissions: {', '.join(bad_perms[:5])}")

        # Run unit tests if present
        test_dir = sk / "tests"
        tests_status = "none"
        if test_dir.is_dir():
            r = subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
                cwd=sk,
                capture_output=True,
                text=True,
            )
            if r.returncode == 0:
                m = re.search(r"Ran (\d+) tests?", r.stderr + r.stdout)
                tests_status = f"pass ({m.group(1) if m else '?'})"
            else:
                tests_status = "fail"
                errors.append(f"{sk.name}: unit tests failed:\n{(r.stderr or r.stdout).strip()}")

        skill_reports.append({
            "skill": sk.name,
            "skill_md_bytes": size_b,
            "tests": tests_status,
        })

    return {
        "status": "PASS" if not errors else "FAIL",
        "skills_count": len(skill_reports),
        "skills": skill_reports,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit all skills and run all unit tests in the repository.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    res = audit_repo()
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for s in res["skills"]:
            print(f"  {s['skill']:28s} SKILL.md={s['skill_md_bytes']:5d}B  tests={s['tests']}")
        for w in res["warnings"]:
            print("WARN:", w)
        for e in res["errors"]:
            print("FAIL:", e)
        print(f"\nRESULT: {res['status']} ({res['skills_count']} skills, {len(res['errors'])} errors, {len(res['warnings'])} warnings)")
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
