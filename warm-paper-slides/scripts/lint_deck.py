#!/usr/bin/env python3
"""Warm Paper Beamer deck linter, 2-pass xelatex builder, and visual sheet renderer.

Usage:
  python3 lint_deck.py deck.tex                    # static lint + 2-pass build + deck_sheet.png
  python3 lint_deck.py deck.tex --no-build         # static checks only
  python3 lint_deck.py deck.tex --page 3,5         # also render 110 dpi zoom PNGs for pages 3 & 5
  python3 lint_deck.py deck.tex --json             # machine-readable JSON output

Exit code 0 = PASS (no FAIL items; WARN allowed).
Auto-injects <SKILL_DIR>/assets// into TEXINPUTS during xelatex compilation.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

IMAGE_EXTS = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps")


def strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", s)


def extract_graphics_paths(preamble: str, base_dir: pathlib.Path) -> list[pathlib.Path]:
    paths = [base_dir]
    for match in re.finditer(r"\\graphicspath\s*\{(.*?)\}\s*(?:\n|$)", preamble, flags=re.S):
        inner = match.group(1)
        for sub in re.findall(r"\{([^{}]+)\}", inner):
            candidate = (base_dir / sub).resolve()
            if candidate not in paths:
                paths.append(candidate)
    return paths


def resolve_image(img_ref: str, search_dirs: list[pathlib.Path]) -> pathlib.Path | None:
    ref = img_ref.strip()
    if not ref:
        return None
    raw_path = pathlib.Path(ref)
    if raw_path.is_absolute():
        for ext in IMAGE_EXTS:
            cand = pathlib.Path(str(raw_path) + ext) if ext and not raw_path.suffix else raw_path
            if cand.is_file():
                return cand
        return None
    for d in search_dirs:
        base = d / ref
        if base.is_file():
            return base
        if not base.suffix:
            for ext in IMAGE_EXTS[1:]:
                cand = d / (ref + ext)
                if cand.is_file():
                    return cand
    return None


def frames_of(body: str) -> list[str]:
    return re.findall(r"\\begin\{frame\}(.*?)\\end\{frame\}", body, flags=re.S)


def extract_deck_sections(preamble: str) -> list[str] | None:
    m = re.search(r"\\decksections\{([^}]*)\}", preamble)
    if not m:
        return None
    items = [item.strip() for item in m.group(1).split(",") if item.strip()]
    return items


def extract_body_sections(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"\\section\*?(?:\[[^\]]*\])?\{([^}]*)\}", body)]


def check_frame(
    i: int,
    f: str,
    search_dirs: list[pathlib.Path],
    errors: list[str],
    warns: list[str],
) -> None:
    tag = f"[p{i:02d}]"
    plain = f.lstrip().startswith("[plain]")
    if not plain and r"\bititle{" not in f and r"\statementpage{" not in f:
        errors.append(f"{tag} Missing \\bititle{{English}}{{中文}} (use \\statementpage for Layout G)")

    for m in re.finditer(r"\\bititle\{([^{}]*)\}\{([^{}]*)\}", f):
        zh_sub = re.sub(r"\s+", "", m.group(2))
        if len(zh_sub) > 12:
            warns.append(f"{tag} Chinese subtitle has {len(zh_sub)} chars (recommended <= 12): {m.group(2)}")

    if f.count(r"\begin{takeaway}") > 1:
        errors.append(f"{tag} More than 1 takeaway on a single slide")
    n = f.count(r"\key{") + f.count(r"\speedup{")
    if n > 4:
        errors.append(f"{tag} Emphasis (\\key + \\speedup) used {n} times (max 4)")
    if r"\includegraphics" in f:
        errors.append(f"{tag} Direct \\includegraphics used; switch to \\safeimg")
    for opt, p in re.findall(r"\\safeimg(\[[^\]]*\])?\{([^}]*)\}", f):
        if "height=" not in opt:
            errors.append(f"{tag} \\safeimg{{{p}}} is missing height=; figure may collide with footer")
        if resolve_image(p, search_dirs) is None:
            errors.append(f"{tag} \\safeimg target image not found: {p}")

    for pat, why in [
        (r"\\\[", r"Use \eqline{...} instead of \[ \]"),
        (r"\\begin\{(block|alertblock|exampleblock)\}", "Use warmcard / callout instead of Beamer block"),
        (r"\\(textcolor|color)\{(red|blue|green|orange|yellow|purple)\b", "Use theme color tokens only"),
        (r"\\(tiny|scriptsize)\b", r"Use \densesize / \notesize / \capsize tokens"),
        (r"\\(Large|LARGE|huge|Huge)\b", r"Do not enlarge body text; use \statementpage for large thesis text"),
        (r"\\textbf\{[^}]*\\textbf", "Nested \\textbf"),
    ]:
        if re.search(pat, f):
            errors.append(f"{tag} {why}")

    cards = len(re.findall(r"\\begin\{(warmcard|callout|papercard)\}", f))
    if cards > 6:
        warns.append(f"{tag} {cards} cards on one slide (> 6 usually warrants splitting)")
    text = re.sub(r"\\[A-Za-z]+|[{}\[\]$]", "", f)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    if cjk > 260:
        warns.append(f"{tag} ~{cjk} CJK chars (> 260; consider splitting or using \\densesize)")


def build(
    tex: pathlib.Path,
    assets_dir: pathlib.Path,
    errors: list[str],
    warns: list[str],
) -> bool:
    if not shutil.which("xelatex"):
        errors.append("[deck] xelatex not found in PATH")
        return False

    env = os.environ.copy()
    if assets_dir.is_dir():
        existing = env.get("TEXINPUTS", "")
        prefix = f"{assets_dir}//:"
        env["TEXINPUTS"] = prefix + (existing if existing else ":")
        if not (tex.parent / "beamerthemewarmpaper.sty").is_file() and tex.parent.resolve() != assets_dir.resolve():
            warns.append(
                "[deck] beamerthemewarmpaper.sty not found beside deck.tex; "
                "using skill assets via TEXINPUTS (copy .sty before sharing standalone)"
            )

    r = None
    for pass_num in (1, 2):
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
            cwd=tex.parent,
            env=env,
            capture_output=True,
            text=True,
            errors="replace",
        )
        if r.returncode != 0:
            break

    log_path = tex.with_suffix(".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    if r is None or r.returncode != 0:
        bangs = re.findall(r"^! .*", log, flags=re.M)[:3]
        detail = " | ".join(bangs) if bangs else f"exit code {r.returncode if r else 'unknown'}"
        errors.append(f"[deck] Compilation failed (pass {pass_num}): {detail}")
        return False

    for line in re.findall(r"^Overfull .*|^LaTeX Font Warning.*|^Missing character.*", log, flags=re.M):
        errors.append("[log] " + line.strip())
    for line in re.findall(r"^Underfull \\vbox.*", log, flags=re.M):
        warns.append("[log] " + line.strip())
    return True


def sheet(pdf: pathlib.Path, warns: list[str], cols: int = 3) -> pathlib.Path | None:
    try:
        from PIL import Image
    except ImportError:
        warns.append("[sheet] Pillow not installed; skipping contact sheet")
        return None
    if not shutil.which("pdftoppm"):
        warns.append("[sheet] pdftoppm not found; skipping contact sheet")
        return None
    if not pdf.is_file():
        warns.append(f"[sheet] PDF not found: {pdf}")
        return None

    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["pdftoppm", "-r", "60", "-png", str(pdf), f"{d}/p"], capture_output=True, text=True)
        if r.returncode != 0:
            warns.append(f"[sheet] pdftoppm failed: {r.stderr.strip()}")
            return None
        pngs = sorted(pathlib.Path(d).glob("p-*.png"))
        if not pngs:
            warns.append("[sheet] pdftoppm produced 0 pages; skipping contact sheet")
            return None
        ims = [Image.open(p) for p in pngs]
        w, h = ims[0].size
        rows = -(-len(ims) // cols)
        out = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 8) + 8), (110, 110, 110))
        for k, im in enumerate(ims):
            out.paste(im, (8 + (k % cols) * (w + 8), 8 + (k // cols) * (h + 8)))
        dst = pdf.with_name(pdf.stem + "_sheet.png")
        out.save(dst)
        return dst


def render_pages(pdf: pathlib.Path, pages: list[int], warns: list[str]) -> list[pathlib.Path]:
    rendered: list[pathlib.Path] = []
    if not pages:
        return rendered
    if not shutil.which("pdftoppm"):
        warns.append("[page] pdftoppm not found; cannot render zoomed pages")
        return rendered
    if not pdf.is_file():
        warns.append(f"[page] PDF not found for zoom rendering: {pdf}")
        return rendered

    for pno in pages:
        with tempfile.TemporaryDirectory() as d:
            prefix = f"{d}/zoom"
            r = subprocess.run(
                ["pdftoppm", "-r", "110", "-f", str(pno), "-l", str(pno), "-png", str(pdf), prefix],
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                warns.append(f"[page] Failed to render page {pno}: {r.stderr.strip()}")
                continue
            outs = sorted(pathlib.Path(d).glob("zoom-*.png"))
            if not outs:
                warns.append(f"[page] Page {pno} out of range (0 images rendered)")
                continue
            dst = pdf.with_name(f"{pdf.stem}_p{pno:02d}.png")
            shutil.copyfile(outs[0], dst)
            rendered.append(dst)
    return rendered


def parse_page_specs(specs: list[str] | None) -> list[int]:
    if not specs:
        return []
    pages: list[int] = []
    for raw in specs:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if not part.isdigit() or int(part) < 1:
                raise argparse.ArgumentTypeError(f"Invalid page number: {part!r}")
            val = int(part)
            if val not in pages:
                pages.append(val)
    return pages


def lint_deck(
    tex_path: pathlib.Path,
    no_build: bool = False,
    pages: list[int] | None = None,
    assets_dir: pathlib.Path | None = None,
) -> dict:
    errors: list[str] = []
    warns: list[str] = []
    tex = tex_path.resolve()
    if assets_dir is None:
        assets_dir = pathlib.Path(__file__).resolve().parents[1] / "assets"

    if not tex.is_file():
        errors.append(f"[deck] File not found: {tex}")
        return {"status": "FAIL", "errors": errors, "warnings": warns, "sheet": None, "zoom_pages": []}

    src = tex.read_text(encoding="utf-8")
    if r"\usetheme{warmpaper}" not in src:
        warns.append("[deck] Missing \\usetheme{warmpaper}; verify inline preamble matches theme")

    cleaned = strip_comments(src)
    doc_marker = r"\begin{document}"
    if doc_marker not in cleaned:
        errors.append("[deck] Missing \\begin{document}")
        return {"status": "FAIL", "errors": errors, "warnings": warns, "sheet": None, "zoom_pages": []}

    split_idx = cleaned.index(doc_marker)
    preamble = cleaned[:split_idx]
    body = cleaned[split_idx:]

    deck_secs = extract_deck_sections(preamble)
    body_secs = extract_body_sections(body)
    if deck_secs is not None and deck_secs != body_secs:
        errors.append(f"[deck] \\decksections {deck_secs} does not match body \\section list {body_secs}")

    search_dirs = extract_graphics_paths(preamble, tex.parent)
    frames = frames_of(body)
    for i, f in enumerate(frames, 1):
        check_frame(i, f, search_dirs, errors, warns)

    sheet_path: pathlib.Path | None = None
    zoom_paths: list[pathlib.Path] = []
    pdf_path = tex.with_suffix(".pdf")
    if not no_build:
        if build(tex, assets_dir, errors, warns):
            sheet_path = sheet(pdf_path, warns)
            zoom_paths = render_pages(pdf_path, pages or [], warns)
    elif pages:
        zoom_paths = render_pages(pdf_path, pages, warns)

    return {
        "status": "PASS" if not errors else "FAIL",
        "frames": len(frames),
        "errors": errors,
        "warnings": warns,
        "sheet": str(sheet_path) if sheet_path else None,
        "zoom_pages": [str(p) for p in zoom_paths],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint, build, and inspect a Warm Paper Beamer deck.")
    ap.add_argument("tex", help="Path to the .tex file")
    ap.add_argument("--no-build", action="store_true", help="Run static checks only (skip xelatex)")
    ap.add_argument(
        "--page",
        action="append",
        help="Render 110 dpi zoom PNG for specific page(s), e.g. --page 3 or --page 3,5",
    )
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = ap.parse_args()

    try:
        pages = parse_page_specs(args.page)
    except argparse.ArgumentTypeError as exc:
        ap.error(str(exc))

    result = lint_deck(pathlib.Path(args.tex), no_build=args.no_build, pages=pages)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["sheet"]:
            print(f"Contact sheet: {result['sheet']} ({result['frames']} slides) -- open to inspect")
        for zp in result["zoom_pages"]:
            print(f"Zoom page: {zp}")
        for w in result["warnings"]:
            print("WARN", w)
        for e in result["errors"]:
            print("FAIL", e)
        print("PASS" if result["status"] == "PASS" else f"FAIL: {len(result['errors'])} item(s)")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
