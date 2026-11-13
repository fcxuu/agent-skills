#!/usr/bin/env python3
"""Read-only, standard-library L1 structural checks for an Obsidian course.

This is not OCR, mathematics, image-fidelity, L2/L3, or runtime-render QA.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

WIKI = re.compile(r"!?\[\[([^\]\n]+)\]\]")
IMAGE_MD = re.compile(r"!\[([^\]\n]*)\]\((<[^>\n]+>|[^)\n]+)\)")
LINK_MD = re.compile(r"(?<!!)\[([^\]\n]+)\]\((<[^>\n]+>|[^)\n]+)\)")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$", re.M)
CALLOUT = re.compile(r"^\s*>\s*\[!(\w+)\]([+-]?)\s*(.*)$", re.I)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")
SOURCE_LABEL = re.compile(r"\[(?:原图|忠实重绘|教学示意)\]")
EXCLUDE_DIRS = {".obsidian", ".git", "node_modules", "raw-markdown", "handoffs"}
IMAGE_TYPES = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
STATES = {"pending", "processing", "qa_pending", "completed", "failed"}
COURSE_STATES = {"in_progress", "completed", "completed_with_issues", "interrupted"}
NOT_CHECKED = ["mathematical_correctness", "ocr_fidelity", "visual_chart_accuracy", "obsidian_runtime_rendering", "qa_l2_l3_evidence"]


def quote_parts(line: str) -> tuple[int, str]:
    """Return blockquote depth and unquoted remainder; ignore indentation <= 3."""
    rest, depth = line, 0
    while True:
        m = re.match(r"^ {0,3}>[ ]?", rest)
        if not m:
            return depth, rest
        depth += 1
        rest = rest[m.end():]


def mask_inline_code(line: str) -> str:
    """Blank *paired* backtick runs; leave unmatched delimiters visible."""
    spans, i = list(line), 0
    while i < len(line):
        if line[i] != "`":
            i += 1
            continue
        j = i
        while j < len(line) and line[j] == "`":
            j += 1
        length = j - i
        end = re.search(r"(?<!`)`{" + str(length) + r"}(?!`)", line[j:])
        if end is None:
            i = j
            continue
        finish = j + end.end()
        spans[i:finish] = " " * (finish - i)
        i = finish
    return "".join(spans)


def mask_comments(line: str, state: dict[str, bool]) -> str:
    """Mask HTML and Obsidian %%...%% comments, including multiline spans."""
    out, i = [], 0
    while i < len(line):
        if state["html"] or state["obsidian"]:
            marker = "-->" if state["html"] else "%%"
            at = line.find(marker, i)
            if at == -1:
                out.append(" " * (len(line) - i))
                break
            out.append(" " * (at + len(marker) - i))
            i = at + len(marker)
            state["html" if marker == "-->" else "obsidian"] = False
        elif line.startswith("<!--", i):
            state["html"] = True
            out.append(" " * 4)
            i += 4
        elif line.startswith("%%", i):
            state["obsidian"] = True
            out.append(" " * 2)
            i += 2
        else:
            out.append(line[i])
            i += 1
    return "".join(out)


def scan_markdown(source: str) -> tuple[list[str], list[tuple[int, str, int, str]]]:
    """Return same-line-number visible text and (line, error code, quote depth, detail).

    A light lexical scanner: fenced code (variable length and quote depth), YAML,
    inline code, HTML/Obsidian comments. Mermaid's callout prefix is checked
    before masking the fenced content. It is deliberately not a Markdown parser.
    """
    lines = source.splitlines()
    visible = [""] * len(lines)
    issues: list[tuple[int, str, int, str]] = []
    front = bool(lines and lines[0].lstrip("\ufeff").strip() == "---")
    fence = None
    comments = {"html": False, "obsidian": False}
    for index, original in enumerate(lines):
        n = index + 1
        if front:
            if index and original.strip() in {"---", "..."}:
                front = False
            continue
        depth, rest = quote_parts(original)
        if fence is not None:
            if fence["mermaid"] and fence["depth"] and depth < fence["depth"]:
                issues.append((n, "MERMAID_CALLOUT_PREFIX", depth, "Callout 内 Mermaid 行或空行缺少 > 前缀"))
            marker = FENCE.match(rest)
            if (marker and depth == fence["depth"] and marker.group(1)[0] == fence["char"]
                    and len(marker.group(1)) >= fence["length"] and not marker.group(2).strip()):
                fence = None
            continue
        no_comment = mask_comments(rest, comments)
        marker = FENCE.match(no_comment)
        if marker:
            info = marker.group(2).strip().casefold()
            fence = {"char": marker.group(1)[0], "length": len(marker.group(1)), "depth": depth,
                     "mermaid": info.startswith("mermaid"), "line": n}
            continue
        visible[index] = mask_inline_code(no_comment)
    if front:
        issues.append((len(lines) or 1, "FRONTMATTER_UNCLOSED", 0, "YAML Frontmatter 未闭合"))
    if fence is not None:
        code = "MERMAID_FENCE" if fence["mermaid"] else "CODE_FENCE_UNCLOSED"
        issues.append((fence["line"], code, fence["depth"], "代码围栏缺少同引用层级的闭合标记"))
    if comments["html"] or comments["obsidian"]:
        issues.append((len(lines) or 1, "COMMENT_UNCLOSED", 0, "注释区域未闭合，请核对正文隔离边界"))
    return visible, issues


def heading_targets(lines: list[str]) -> set[str]:
    return {re.sub(r"\s+", " ", s.strip(" #")) for line in lines for _, s in HEADING.findall(line)}


def name_index(vault: Path) -> dict[str, list[Path]]:
    names: dict[str, list[Path]] = defaultdict(list)
    for p in sorted(vault.rglob("*"), key=lambda p: p.as_posix()):
        if not p.is_file() or p.suffix == ".bak":
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(vault).parts[:-1]):
            continue
        real = p.resolve()
        if not real.is_relative_to(vault):
            continue
        names[p.name.casefold()].append(real)
        if p.suffix.casefold() == ".md":
            names[p.stem.casefold()].append(real)
    return names


def resolve_wiki(vault: Path, source: Path, target: str, names: dict[str, list[Path]]) -> tuple[Path | None, bool, str]:
    """Return (resolved, ambiguous, status: ok/missing/escape)."""
    target = unquote(target.strip())
    if not target:
        return source, False, "ok"
    if target.startswith(("./", "../")):
        base = (source.parent / target).resolve()
    elif "/" in target or target.startswith("/"):
        base = (vault / target).resolve() if not Path(target).is_absolute() else Path(target).resolve()
    else:
        matches = list(dict.fromkeys(names.get(target.casefold(), [])))
        return (matches[0] if matches else None, len(matches) > 1, "ok" if matches else "missing")
    if not base.is_relative_to(vault):
        return None, False, "escape"
    candidates = [base, Path(str(base) + ".md")]
    for p in candidates:
        if p.is_file() and p.resolve().is_relative_to(vault):
            return p.resolve(), False, "ok"
    return None, False, "missing"


def local_md_target(vault: Path, course: Path, source: Path, raw: str) -> tuple[Path | None, str, str]:
    """Resolve Markdown URL from *source file*, never from Vault cwd.

    Returns (resolved, status, anchor). Resolve symlinks before checking both
    containment boundaries. A legitimate ../../assets path is allowed.
    """
    value = raw.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]
    else:
        # Optional Markdown title follows whitespace; filenames with spaces
        # should be URL-encoded or wrapped in angle brackets.
        value = re.split(r'\s+(?=["\'])', value, maxsplit=1)[0]
    value = unquote(value)
    pathpart, _, anchor = value.partition("#")
    if (not pathpart or pathpart.startswith(("/", "~", "\\")) or
            re.match(r"^[a-zA-Z]:[\\/]", pathpart) or
            pathpart.lower().startswith("file:")):
        return None, "absolute", anchor
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", pathpart):
        return None, "external", anchor
    if "?" in pathpart:
        # Query strings are not safe local filesystem references.
        return None, "invalid", anchor
    dest = (source.parent / pathpart).resolve()
    if not dest.is_relative_to(vault):
        return None, "escape_vault", anchor
    if not dest.is_relative_to(course):
        return None, "escape_course", anchor
    if not dest.is_file():
        return dest, "missing", anchor
    return dest, "ok", anchor


def image_evidence(lines: list[str], line_no: int, file: Path, emit) -> None:
    """L1 checks for a local figure's neighboring provenance caption."""
    nearby = "\n".join(lines[line_no:min(len(lines), line_no + 6)])
    labels = SOURCE_LABEL.findall(nearby)
    if not labels:
        emit("warning", "IMAGE_PROVENANCE", file, line_no,
             "图片附近缺少 [原图]/[忠实重绘]/[教学示意] 图注")
    if ("[忠实重绘]" in labels and "assets/original/" not in nearby and
            "原图无法" not in nearby and "不可提取" not in nearby):
        emit("warning", "IMAGE_ORIGINAL_EVIDENCE", file, line_no,
             "忠实重绘未标明原图对照路径或不可提取说明")


def course_path_from_ref(course: Path, relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    resolved = (course / relative).resolve()
    return resolved if resolved.is_relative_to(course) else None


def source_map_refs(course: Path, emit) -> set[str]:
    mapfile = course / "raw-markdown" / "source-map.md"
    if not mapfile.is_file():
        return set()
    if not mapfile.resolve().is_relative_to(course):
        emit("error", "SOURCE_MAP_ESCAPE", mapfile, 0, "source-map 符号链接越出课程目录")
        return set()
    try:
        rows = mapfile.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        emit("error", "SOURCE_MAP_UNREADABLE", mapfile, 0, f"无法读取来源映射: {exc}")
        return set()
    refs: set[str] = set()
    for line_no, row in enumerate(rows, 1):
        if not row.startswith("|") or row.startswith("|---"):
            continue
        columns = [x.strip() for x in re.split(r"(?<!\\)\|", row.strip("|"))]
        if len(columns) < 4 or columns[0].startswith(("逻辑章节", ":---", "---")):
            continue
        if columns[0] in refs:
            emit("warning", "SOURCE_MAP_DUPLICATE", mapfile, line_no, "来源映射小节键重复")
        refs.add(columns[0])
        for target in re.findall(r"`(raw-markdown/[^`\n]+?\.md)`", row):
            dest = course_path_from_ref(course, target)
            if dest is None or not dest.is_file():
                emit("error", "SOURCE_MAP_TARGET", mapfile, line_no, f"映射中的原始 Markdown 不存在或越界：{target}")
    return refs


def lint_state(course: Path, emit, refs: set[str], has_map: bool) -> str:
    path = course / ".build-state.json"
    if not path.is_file():
        return "unknown"
    if not path.resolve().is_relative_to(course):
        emit("error", "STATE_ESCAPE", path, 0, "状态文件符号链接越出课程目录")
        return "invalid"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        emit("error", "STATE_JSON_INVALID", path, 0, f"状态文件损坏或无法读取: {exc}")
        return "invalid"
    if not isinstance(state, dict) or not isinstance(state.get("schema_version"), str) or state.get("course_status") not in COURSE_STATES or not isinstance(state.get("sources"), dict) or not isinstance(state.get("sections"), list):
        emit("error", "STATE_SCHEMA", path, 0, "顶层 schema_version/course_status/sources/sections 缺失或类型错误")
        return "invalid"
    for raw, meta in sorted(state["sources"].items()):
        loc = course_path_from_ref(course, raw)
        if not raw.startswith("raw-markdown/") or loc is None or not isinstance(meta, dict):
            emit("error", "STATE_SOURCE", path, 0, f"来源路径/结构无效：{raw}")
            continue
        sha = meta.get("sha256")
        size = meta.get("size_bytes")
        if (not isinstance(meta.get("source_file"), str) or course_path_from_ref(course, meta["source_file"]) is None
                or (sha is not None and (not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", sha)))
                or not isinstance(size, int) or isinstance(size, bool) or size < 0):
            emit("error", "STATE_SOURCE", path, 0, f"来源元数据字段无效：{raw}")
    ids: set[str] = set()
    for i, section in enumerate(state["sections"], 1):
        if not isinstance(section, dict):
            emit("error", "STATE_SECTION_SCHEMA", path, 0, "小节必须是对象")
            continue
        sid = section.get("id")
        status = section.get("status")
        attempts = section.get("attempts")
        qa_ids = section.get("qa_ids")
        reference = section.get("source_map_ref")
        if (not isinstance(sid, str) or not sid or status not in STATES
                or not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 0
                or not isinstance(qa_ids, list) or not all(isinstance(x, str) for x in qa_ids)
                or not isinstance(reference, str) or not reference
                or not isinstance(section.get("output_path"), str) or not section["output_path"]):
            emit("error", "STATE_SECTION_SCHEMA", path, 0, f"小节 #{i} 字段缺失、类型或五态值非法")
            continue
        if sid in ids:
            emit("error", "STATE_DUPLICATE_ID", path, 0, f"重复小节 ID: {sid}")
        ids.add(sid)
        dest = course_path_from_ref(course, section["output_path"])
        if dest is None or dest.suffix.lower() != ".md":
            emit("error", "STATE_OUTPUT_PATH", path, 0, f"output_path 无效或越界：{section['output_path']}")
        elif status == "completed" and (not dest.is_file() or dest.stat().st_size == 0):
            emit("error", "STATE_COMPLETED_MISSING", path, 0, f"completed 但磁盘笔记缺失或为空：{section['output_path']}")
        if has_map and reference not in refs:
            emit("error", "STATE_SOURCE_MAP_REF", path, 0, f"source_map_ref 无对应逻辑小节：{reference}")
    return state["course_status"]


def lint(vault: Path, course: Path) -> dict:
    issues: list[dict] = []

    def emit(severity: str, code: str, path: Path, line: int, message: str):
        file = path.relative_to(course).as_posix() if path.is_relative_to(course) else path.as_posix()
        vpath = path.relative_to(vault).as_posix() if path.is_relative_to(vault) else path.as_posix()
        issues.append({"severity": severity, "code": code, "file": file, "line": line,
                       "path": vpath, "message": message})

    notesdir, reviewdir = course / "notes", course / "review"
    notes = sorted(notesdir.rglob("*.md"), key=lambda p: p.as_posix()) if notesdir.is_dir() else []
    review = sorted(reviewdir.rglob("*.md"), key=lambda p: p.as_posix()) if reviewdir.is_dir() else []
    is_new = not (course / ".build-state.json").exists() and not (course / "README.md").exists() and not notes
    if is_new:
        return report(vault, course, [], 0, 0, "not_initialized")
    for required in ("README.md", "QA.md"):
        if not (course / required).is_file():
            emit("warning", "INDEX_MISSING", course / required, 0, f"缺少 {required}，状态/审计可能不完整")
    names = name_index(vault)
    refs = source_map_refs(course, emit)
    course_state = lint_state(course, emit, refs, (course / "raw-markdown/source-map.md").is_file())
    rawdir = course / "raw-markdown"
    if rawdir.is_dir():
        for raw in sorted(rawdir.glob("*.md"), key=lambda p: p.as_posix()):
            if not raw.resolve().is_relative_to(course):
                emit("error", "RAW_ESCAPE", raw, 0, "原始 Markdown 符号链接越出课程目录，拒绝读取")
                continue
            try:
                # Scan in chunks to avoid materializing whole OCR documents.
                with raw.open("r", encoding="utf-8") as handle:
                    while handle.read(65536):
                        pass
            except (OSError, UnicodeError) as exc:
                emit("error", "RAW_UNREADABLE", raw, 0, f"原始 Markdown 无法读取：{exc}")
    for file in notes + review:
        if not file.resolve().is_relative_to(course):
            emit("error", "NOTE_ESCAPE", file, 0, "笔记/复习文件符号链接越出课程目录，拒绝读取")
            continue
        try:
            source = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            emit("error", "UNREADABLE", file, 0, f"无法读取 Markdown：{exc}")
            continue
        lines, lexical = scan_markdown(source)
        for number, code, depth, message in lexical:
            severity = "error" if code in {"MERMAID_FENCE", "MERMAID_CALLOUT_PREFIX", "CODE_FENCE_UNCLOSED"} else "warning"
            emit(severity, code, file, number, message)
        headings = [(i + 1, match.group(1), match.group(2).strip()) for i, line in enumerate(lines) for match in HEADING.finditer(line)]
        if file in notes:
            cores = [(i, level) for i, level, title in headings if level == "##" and title == "核心速览"]
            if len(cores) != 1:
                emit("error", "CORE_SECTION", file, cores[0][0] if cores else 0, f"必须有且仅有一个 '## 核心速览'，实际 {len(cores)} 个")
            else:
                core_at = cores[0][0]
                top = [i for i, level, title in headings if level == "#" and i < core_at]
                prior_h2 = [i for i, level, title in headings if level == "##" and i < core_at]
                if not top or prior_h2:
                    emit("error", "CORE_POSITION", file, core_at, "核心速览须在主标题之后、其他正文二级标题之前")
                end = next((i for i, level, title in headings if level in {"#", "##"} and i > core_at), len(lines) + 1)
                for i, level, title in headings:
                    if core_at < i < end and len(level) >= 3:
                        emit("error", "CORE_SUBHEADING", file, i, "速览区域不能出现 ### 或更深层标题")
                for i in range(core_at, end):
                    text = lines[i - 1]
                    if re.search(r"\\(?:label|eqref)\s*\{", text):
                        emit("error", "CORE_MATH_LABEL", file, i, "速览内禁止动态 MathJax label/eqref")
                    if re.search(r"\[\^[^\]\n]+\]", text):
                        emit("error", "CORE_FOOTNOTE", file, i, "速览内不使用脚注引用")
                    if re.search(r"(?:^|\s)\^[A-Za-z0-9-]+\s*$", text):
                        emit("error", "CORE_BLOCK_ID", file, i, "速览内不使用自定义块 ID")
                    if re.search(r"(?:见下文(?:的)?(?:证明|推导)|如(?:下|上)(?:图|文|一节))", text):
                        emit("warning", "CORE_DEICTIC", file, i, "速览可能有无法独立阅读的上下文指代")
        if "$$" in "\n".join(lines) and sum(x.count("$$") for x in lines) % 2:
            emit("error", "MATH_DELIMITER", file, 0, "块公式 $$ 数量为奇数；请核对未闭合公式")
        for line_no, line in enumerate(lines, 1):
            match = CALLOUT.match(line)
            if match:
                name, fold, title = match.groups()
                if name.lower() in {"note", "example"} and fold != "-" and re.search(r"(证明|推导|参考解答|完整解答|补充知识|拓展)", title):
                    emit("warning", "FOLD", file, line_no, f"'{title}' 可能应默认折叠")
            for match in WIKI.finditer(line):
                raw = match.group(1)
                is_embed = match.group(0).startswith("!")
                destination = raw.split("|", 1)[0]
                pathpart, sep, anchor = destination.partition("#")
                resolved, ambiguous, status = resolve_wiki(vault, file, pathpart, names)
                if status == "escape":
                    emit("error", "LINK_ESCAPE", file, line_no, f"引用越过 Vault 边界：{destination}")
                    continue
                if status != "ok":
                    emit("error", "BROKEN_WIKILINK", file, line_no, f"目标不存在：{destination}")
                    continue
                if ambiguous:
                    emit("warning", "AMBIGUOUS_WIKILINK", file, line_no, f"同名目标不唯一：{destination}")
                if file in review and is_embed and resolved and resolved.suffix == ".md":
                    prefix = pathpart.replace("\\", "/")
                    expected = course.relative_to(vault).as_posix() + "/notes/"
                    if not prefix.startswith(expected) or prefix.endswith(".md") or anchor != "核心速览":
                        emit("error", "REVIEW_EMBED_PATH", file, line_no, f"复习嵌入应使用完整课程路径并指向核心速览：{destination}")
                if sep and resolved and resolved.suffix.casefold() == ".md" and not anchor.startswith("^"):
                    try:
                        targets, _ = scan_markdown(resolved.read_text(encoding="utf-8"))
                        present = anchor in heading_targets(targets)
                    except (OSError, UnicodeError):
                        present = False
                    if not present:
                        sev = "error" if file in review and is_embed else "warning"
                        emit(sev, "HEADING_ANCHOR", file, line_no, f"目标无标题锚点：{destination}")
                if is_embed and resolved and resolved.suffix.casefold() in IMAGE_TYPES and file in notes:
                    nearby = "\n".join(lines[line_no:min(len(lines), line_no + 6)])
                    labels = SOURCE_LABEL.findall(nearby)
                    if not labels:
                        emit("warning", "IMAGE_PROVENANCE", file, line_no, "图片附近缺少 [原图]/[忠实重绘]/[教学示意] 图注")
                    if "[忠实重绘]" in labels and "assets/original/" not in nearby and "原图无法" not in nearby and "不可提取" not in nearby:
                        emit("warning", "IMAGE_ORIGINAL_EVIDENCE", file, line_no, "忠实重绘未标明原图对照路径或不可提取说明")
            for match in IMAGE_MD.finditer(line):
                raw = match.group(1).strip().split(" ", 1)[0].strip("<>\"'")
                if raw.startswith(("https://", "http://", "data:")):
                    continue
                dest = (file.parent / unquote(raw).split("#", 1)[0]).resolve()
                if not dest.is_relative_to(vault):
                    emit("error", "LINK_ESCAPE", file, line_no, f"图片路径越界：{raw}")
                elif not dest.is_file():
                    emit("error", "BROKEN_MARKDOWN_IMAGE", file, line_no, f"图片目标不存在：{raw}")
    return report(vault, course, issues, len(notes), len(review), course_state)


def report(vault: Path, course: Path, issues: list[dict], notes: int, review: int, state: str) -> dict:
    issues.sort(key=lambda i: (i["severity"], i["file"], i["line"], i["code"]))
    errors = sum(x["severity"] == "error" for x in issues)
    warnings = sum(x["severity"] == "warning" for x in issues)
    return {"vault_path": str(vault), "course_path": course.relative_to(vault).as_posix(), "course_state": state,
            "checked_notes_count": notes, "checked_review_count": review, "summary": {"error_count": errors, "warning_count": warnings},
            "issues": issues, "not_checked": NOT_CHECKED,
            "disclaimer": "仅 L1 只读静态检查，不代表数学正确、OCR 保真、图片真实性或 L2/L3/Obsidian 渲染通过。",
            # Backwards-compatible keys for existing callers:
            "vault": str(vault), "course": str(course), "notes_checked": notes, "review_checked": review,
            "errors": errors, "warnings": warnings,
            "limitation": "只读静态检查，不能验证 OCR/数学内容、源材料覆盖或 Obsidian 实际渲染"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Obsidian course read-only L1 static checks (stdlib only)")
    parser.add_argument("--vault", required=True, help="现有 Obsidian Vault 根目录")
    parser.add_argument("--course", required=True, help="Vault 内课程相对路径或其绝对路径")
    parser.add_argument("--json", action="store_true", help="输出确定性 JSON 报告")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        parser.error(f"Vault 不存在或不是目录：{vault}")
    course_arg = Path(args.course).expanduser()
    course = (course_arg if course_arg.is_absolute() else vault / course_arg).resolve()
    if not course.is_relative_to(vault):
        parser.error("课程必须位于 Vault 内（允许课程目录即 Vault 根目录），禁止越界")
    if not course.is_dir():
        parser.error(f"课程目录不存在：{course}")
    result = lint(vault, course)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Obsidian static QA: notes={result['notes_checked']}, reviews={result['review_checked']}, errors={result['errors']}, warnings={result['warnings']}, state={result['course_state']}")
        for issue in result["issues"]:
            print(f"{issue['severity'].upper():7} {issue['code']:26} {issue['file']}:{issue['line']}: {issue['message']}")
        print(result["disclaimer"])
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
