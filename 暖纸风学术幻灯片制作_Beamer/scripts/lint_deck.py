#!/usr/bin/env python3
"""Warm Paper 版式检查：规则静态检查 + xelatex 两遍编译 + 渲染缩略图拼版。

用法：
  python3 lint_deck.py deck.tex              # 全部检查，生成 deck_sheet.png
  python3 lint_deck.py deck.tex --no-build   # 只做静态检查
退出码 0 = 通过。拼版图需要 pdftoppm（poppler）与 Pillow，缺失时跳过并提示。
"""
import argparse, pathlib, re, shutil, subprocess, sys, tempfile

errors, warns = [], []

def strip_comments(s):
    return re.sub(r'(?<!\\)%.*', '', s)

def frames_of(body):
    return re.findall(r'\\begin\{frame\}(.*?)\\end\{frame\}', body, flags=re.S)

def check_frame(i, f):
    tag = f'[p{i:02d}]'
    plain = f.lstrip().startswith('[plain]')
    if not plain and r'\bititle{' not in f and r'\statementpage{' not in f:
        errors.append(f'{tag} 缺少 \\bititle{{English}}{{中文}}（陈述页用 \\statementpage）')
    if f.count(r'\begin{takeaway}') > 1:
        errors.append(f'{tag} takeaway 超过 1 个')
    n = f.count(r'\key{') + f.count(r'\speedup{')
    if n > 4:
        errors.append(f'{tag} 强调（\\key + \\speedup）用了 {n} 次，上限 4')
    if r'\includegraphics' in f:
        errors.append(f'{tag} 帧内直接使用了 \\includegraphics，改用 \\safeimg')
    for opt, p in re.findall(r'\\safeimg(\[[^\]]*\])?\{([^}]*)\}', f):
        if 'height=' not in opt:
            errors.append(f'{tag} \\safeimg{{{p}}} 没有给 height=，图可能撑出页面')
    for pat, why in [(r'\\\[', '用 \\eqline{...} 代替 \\[ \\]'),
                     (r'\\begin\{(block|alertblock|exampleblock)\}', '用 warmcard / callout 代替 block'),
                     (r'\\(textcolor|color)\{(red|blue|green|orange|yellow|purple)', '只用主题色令牌'),
                     (r'\\(tiny|scriptsize)\b', '用 \\densesize / \\notesize / \\capsize 字号令牌'),
                     (r'\\(Large|LARGE|huge|Huge)\b', '正文不放大字号；需要大字用 \\statementpage'),
                     (r'\\textbf\{[^}]*\\textbf', '粗体嵌套')]:
        if re.search(pat, f):
            errors.append(f'{tag} {why}')
    cards = len(re.findall(r'\\begin\{(warmcard|callout|papercard)\}', f))
    if cards > 6:
        warns.append(f'{tag} 卡片 {cards} 张，超过 6 张通常说明该拆页')
    text = re.sub(r'\\[A-Za-z]+|[{}\[\]$]', '', f)
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    if cjk > 260:
        warns.append(f'{tag} 约 {cjk} 个汉字，超过 260 字建议拆页或改用 \\densesize')

def build(tex):
    if not shutil.which('xelatex'):
        errors.append('[deck] 未找到 xelatex'); return False
    for _ in range(2):
        r = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', tex.name],
                           cwd=tex.parent, capture_output=True, text=True, errors='replace')
    log = tex.with_suffix('.log').read_text(encoding='utf-8', errors='replace')
    if r.returncode:
        errors.append('[deck] 编译失败：' + ' | '.join(re.findall(r'^! .*', log, flags=re.M)[:3]))
        return False
    for line in re.findall(r'^Overfull .*|^LaTeX Font Warning.*|^Missing character.*', log, flags=re.M):
        errors.append('[log] ' + line.strip())
    for line in re.findall(r'^Underfull \\vbox.*', log, flags=re.M):
        warns.append('[log] ' + line.strip())
    return True

def sheet(pdf, cols=3):
    try:
        from PIL import Image
    except ImportError:
        warns.append('[sheet] 未安装 Pillow，跳过拼版'); return
    if not shutil.which('pdftoppm'):
        warns.append('[sheet] 未找到 pdftoppm，跳过拼版'); return
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '60', '-png', str(pdf), f'{d}/p'], check=True)
        ims = [Image.open(p) for p in sorted(pathlib.Path(d).glob('p-*.png'))]
        w, h = ims[0].size
        rows = -(-len(ims) // cols)
        out = Image.new('RGB', (cols * (w + 8) + 8, rows * (h + 8) + 8), (110, 110, 110))
        for k, im in enumerate(ims):
            out.paste(im, (8 + (k % cols) * (w + 8), 8 + (k // cols) * (h + 8)))
        dst = pdf.with_name(pdf.stem + '_sheet.png')
        out.save(dst)
        print(f'拼版图：{dst}（{len(ims)} 页）—— 打开逐页目检')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tex')
    ap.add_argument('--no-build', action='store_true')
    a = ap.parse_args()
    tex = pathlib.Path(a.tex).resolve()
    src = tex.read_text(encoding='utf-8')
    if r'\usetheme{warmpaper}' not in src:
        warns.append('[deck] 没有 \\usetheme{warmpaper}；若使用内联导言区，确认与主题文件一致')
    body = strip_comments(src[src.index(r'\begin{document}'):])
    for i, f in enumerate(frames_of(body), 1):
        check_frame(i, f)
    if not a.no_build and build(tex):
        sheet(tex.with_suffix('.pdf'))
    for w in warns:
        print('WARN', w)
    for e in errors:
        print('FAIL', e)
    print('PASS' if not errors else f'FAIL：{len(errors)} 项')
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
