# 常见问题

## 编译

| 现象 | 原因 | 处理 |
|---|---|---|
| `File 'beamerthemewarmpaper.sty' not found` | 主题文件不在 deck 目录 | 复制过去，或 `TEXINPUTS=/path/to/assets//: xelatex deck.tex` |
| `The font "PingFang SC" cannot be found` | 不是 macOS | 在 `\usetheme` 前写 `\newcommand{\warmcjkfont}{Noto Sans CJK SC}` 和 `\newcommand{\warmlatinfont}{Noto Sans CJK SC}`；Windows 可用 `Microsoft YaHei`。若新字体没有 Regular/Semibold 子字体名，需要改 `\warm@latinfeatures` |
| `Missing character` | 字体缺字（常见于 emoji、特殊符号） | 删掉 emoji；数学符号放进 `$…$` |
| 底栏总页数显示 `??` 或不对 | 只编译了一遍 | 编译两遍；`lint_deck.py` 会自动两遍 |
| 下划线报错 `Missing $ inserted` | 文件名里的 `_` | 用 `\file{…}` |
| `\safeimg` 报 `File not found` | 路径相对编译目录 | 检查 `\graphicspath`，或写相对 deck.tex 的路径 |

## 排版

| 现象 | 处理 |
|---|---|
| `Overfull \hbox` | 某行太宽。公式改用 `\eqline`（自动缩小）；长英文词加 `\allowbreak`；表格列宽改 `p{}` |
| 内容压到底栏 | 编译不一定报错，看图才能发现。先删字或拆页；其次降一档字号（`\densesize`）；最后才压图高 |
| 并排卡片高低不齐 | 给每张卡同一个固定高度：`\begin{warmcard}[\linewidth][2.4cm]{…}` |
| 固定高度的卡片里文字溢出 | 加大固定高度，或减少内容 |
| 箭头没对准卡片中线 | 调 `\gaparrow[高度]`，大约取卡片高度的一半 |
| 图注比图宽很多 | 图太窄时图注最窄 60% 栏宽，这是设计行为；嫌宽就加大图 |
| 中文标点挤在一起 | 人名或元信息之间用 `\dotsep`，不要连用中文顿号和空格 |
| 标题末尾一个字单独换行 | 缩短副标题，或在英文标题里手动 `\\` |
| 列总宽超出页面 | 列宽之和不超过 .97\textwidth，并使用 `columns[T,onlytextwidth]` |

## 看图

```bash
pdftoppm -r 110 -f 5 -l 5 -png deck.pdf /tmp/p   # 放大看第 5 页
```

拼版图分辨率低，只用来看整体节奏和明显溢出。对齐、字距这类细节要放大单页看。
