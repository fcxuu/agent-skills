#!/usr/bin/env python3
"""Read-only L1 static checks for an Obsidian course folder.

No third-party dependencies. Deliberately does not claim semantic, OCR, or visual QA.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

WIKI = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]|!\[\[([^\]\n]+)\]\]")
IMAGE_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", re.M)
CALLOUT = re.compile(r"^\s*>\s*\[!(\w+)\]([+-]?)\s*(.*)$", re.M | re.I)
EXCLUDE_DIRS = {".obsidian", ".git", "node_modules", "raw-markdown", "handoffs", "assets"}
IMAGE_TYPES = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def redact_code(src: str) -> str:
    """Mask fenced code so sample links don't become false positives."""
    out = []
    inside = False
    fencechar = ""
    fencesize = 0
    for line in src.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if not inside:
                inside, fencechar, fencesize = True, marker[0], len(marker)
            elif marker[0] == fencechar and len(marker) >= fencesize:
                inside = False
            out.append("\n")
        else:
            out.append("\n" if inside else line)
    return "".join(out)


def heading_targets(text: str) -> set[str]:
    return {re.sub(r"\s+", " ", s.strip(" #")) for _, s in HEADING.findall(text)}


def files_under_vault(vault: Path) -> dict[str, list[Path]]:
    names: dict[str, list[Path]] = defaultdict(list)
    for p in vault.rglob("*"):
        if not p.is_file() or any(part in EXCLUDE_DIRS for part in p.relative_to(vault).parts[:-1]):
            continue
        names[p.name.casefold()].append(p)
        if p.suffix.lower() == ".md":
            names[p.stem.casefold()].append(p)
    return names


def resolve_wiki(vault: Path, source: Path, target: str, name_index: dict[str, list[Path]]):
    """Return (resolved_path, possible_ambiguity, exists)."""
    target = unquote(target.strip())
    if not target:  # e.g. [[#heading]] - same page
        return source, False, True
    if target.startswith("./") or target.startswith("../"):
        base = (source.parent / target).resolve()
        candidates = [base, Path(str(base) + ".md")]
    elif "/" in target:
        base = (vault / target).resolve()
        candidates = [base, Path(str(base) + ".md")]
    else:
        matches = name_index.get(target.casefold(), [])
        if not matches and Path(target).suffix.lower() == ".md":
            matches = name_index.get(Path(target).name.casefold(), [])
        matches = list(dict.fromkeys(matches))
        return (matches[0] if matches else None, len(matches) > 1, bool(matches))
    for p in candidates:
        if p.is_file() and p.is_relative_to(vault):
            return p, False, True
    return None, False, False


def lint(vault: Path, course: Path):
    issues = []
    def emit(sev, code, path, message):
        issues.append({"severity": sev, "code": code, "path": str(path.relative_to(vault)) if path.is_relative_to(vault) else str(path), "message": message})

    if not course.is_dir():
        emit("error", "COURSE_MISSING", course, "课程目录不存在")
        return issues, 0, 0

    for required in ("README.md", "QA.md"):
        if not (course / required).is_file():
            emit("warning", "INDEX_MISSING", course / required, f"缺少 {required}，无法完整跟踪任务状态")

    notes_dir = course / "notes"
    review_dir = course / "review"
    notes = sorted(notes_dir.rglob("*.md")) if notes_dir.exists() else []
    review = sorted(review_dir.rglob("*.md")) if review_dir.exists() else []
    if not notes:
        emit("warning", "NO_NOTES", notes_dir, "没有发现已生成的 notes/*.md；可能尚未开始构建")
    if not review:
        emit("warning", "NO_REVIEW", review_dir, "没有发现 review/*.md；检查是否应生成期末复习入口")

    name_index = files_under_vault(vault)
    for file in notes + review:
        try:
            content = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as e:
            emit("error", "UNREADABLE", file, f"无法读取 Markdown: {e}")
            continue
        visible = redact_code(content)
        # Core section must be present in every primary note, but not review pages.
        if file in notes and not re.search(r"^##\s+核心速览\s*$", visible, re.M):
            emit("error", "CORE_SECTION", file, "缺少稳定标题 '## 核心速览'")
        if visible.count("$$") % 2:
            emit("error", "MATH_DELIMITER", file, "块数学定界符 $$ 数量为奇数；检查未闭合公式")
        for typ, sign, title in CALLOUT.findall(visible):
            if typ.lower() in {"note", "example"} and sign != "-" and re.search(r"(证明|推导|参考解答|完整解答|补充知识|拓展)", title):
                emit("warning", "FOLD", file, f"'{title}' 似乎应默认折叠，可检查 [!{typ}]-")
        for match in WIKI.finditer(visible):
            raw = match.group(1) or match.group(2)
            if not raw:
                continue
            is_embed = match.group(0).startswith("!")
            destination = raw.split("|", 1)[0]
            pathpart, sep, anchor = destination.partition("#")
            resolved, ambiguous, exists = resolve_wiki(vault, file, pathpart, name_index)
            if not exists:
                emit("error", "BROKEN_WIKILINK", file, f"目标不存在：{destination}")
                continue
            if ambiguous:
                emit("warning", "AMBIGUOUS_WIKILINK", file, f"有多个同名目标，推荐改用 Vault 相对路径：{destination}")
            if is_embed and resolved and resolved.suffix.lower() in IMAGE_TYPES and not resolved.is_file():
                emit("error", "IMAGE_MISSING", file, f"图片不存在：{destination}")
            if anchor and resolved and resolved.suffix.lower() == ".md" and not anchor.startswith("^"):
                try:
                    headings = heading_targets(redact_code(resolved.read_text(encoding="utf-8")))
                except (OSError, UnicodeError):
                    headings = set()
                if anchor not in headings:
                    emit("warning", "HEADING_ANCHOR", file, f"未找到标题锚点：{destination}（部分 Obsidian 标题规范化可能不同）")
        for image_match in IMAGE_MD.finditer(visible):
            raw = image_match.group(1).strip().split(" ", 1)[0].strip("<>\"'")
            if raw.startswith(("http://", "https://", "data:")):
                continue
            p = (file.parent / unquote(raw).split("#", 1)[0]).resolve()
            if not p.is_file() or not p.is_relative_to(vault):
                emit("error", "BROKEN_MARKDOWN_IMAGE", file, f"图片路径无效：{raw}")
    return issues, len(notes), len(review)


def main():
    parser = argparse.ArgumentParser(description="只读检查 Obsidian 课程笔记的基础链接、图片及 Markdown 结构（非数学或渲染 QA）")
    parser.add_argument("--vault", required=True, help="已经存在的 Obsidian Vault 根目录")
    parser.add_argument("--course", required=True, help="Vault 内课程相对路径，也可指定其中的绝对路径")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        parser.error(f"Vault 不存在：{vault}")
    course_arg = Path(args.course).expanduser()
    course = (course_arg if course_arg.is_absolute() else vault / course_arg).resolve()
    if not course.is_relative_to(vault):
        parser.error("课程路径必须位于指定的 Vault 内；拒绝扫描或修改其他目录")
    issues, notes, review = lint(vault, course)
    errors = sum(i["severity"] == "error" for i in issues)
    warnings = sum(i["severity"] == "warning" for i in issues)
    result = {"vault": str(vault), "course": str(course), "notes_checked": notes, "review_checked": review,
              "errors": errors, "warnings": warnings, "issues": issues,
              "limitation": "只读静态检查，不能验证 OCR/数学内容、源材料覆盖或 Obsidian 实际渲染"}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Obsidian static QA: notes={notes}, reviews={review}, errors={errors}, warnings={warnings}")
        for i in issues:
            print(f"{i['severity'].upper():7} {i['code']:24} {i['path']}: {i['message']}")
        print(result["limitation"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
