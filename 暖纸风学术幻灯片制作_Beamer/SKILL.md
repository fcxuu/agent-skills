---
name: warm-paper-slides
description: |
  用 LaTeX Beamer 制作 "Warm Paper" 风格（暖纸底、陶土单强调色、扁平细边卡片）的中英双语学术汇报。
  负责审美、格式和排版：配色与字号令牌、7 种页面母版、图文配比、卡片层级、公式与表格排版、编译与目检。
  Use when 用户要做论文研讨 / 期中期末汇报 / 课程展示 / 组会 slides，或说"做 PPT""排版课件""把讲稿转成 beamer"
  并希望得到干净、克制、可直接编译的 xelatex 源码。不处理 pptx 文件。
---

# Warm Paper Slides

目标：每一页看起来像排版良好的学术杂志内页。安静的纸色背景，一个强调色，信息按层级排开，没有装饰。

主题文件已经替你实现了所有视觉细节。你的工作是**选对母版、控制每页信息量、用对组件**，然后编译并看图检查。

## 文件

| 路径 | 用途 |
|---|---|
| `assets/beamerthemewarmpaper.sty` | 主题：字体、配色、标题栏、底栏、卡片、插图、表格宏 |
| `assets/starter.tex` | 7 种母版各一页的样张，新 deck 从这里复制开始 |
| `assets/starter.pdf` | 样张效果，动手前先看 |
| `assets/placeholders/` | 三种比例的占位图，图还没到位时用 |
| `scripts/lint_deck.py` | 规则检查 + 两遍编译 + 生成缩略拼版图 |
| `references/design-principles.md` | 审美原则与禁止事项（为什么这样做） |
| `references/layouts.md` | 7 种母版的选择规则、尺寸与写法 |
| `references/components.md` | 每个组件的用法与限额 |
| `references/troubleshooting.md` | 编译与排版常见问题 |

## 工作流程

1. **读材料，分页。** 每页只讲一个论点。先写一张页面清单：页号、英文标题、中文副标题、母版字母（A–G）、要放的图。超过 16:9 一页能装下的内容就拆页，不要缩字号硬塞。
2. **建项目。** 把 `assets/beamerthemewarmpaper.sty` 复制到 deck 所在目录（或用 `TEXINPUTS` 指向它），以 `starter.tex` 为骨架。用 `\decksections{...}` 写 3–5 个章节名，与正文的 `\section{}` 顺序一致。
3. **按母版写页面。** 每页从 `references/layouts.md` 里挑一种母版照抄结构，再填内容。不要发明新的版式；七种母版能覆盖学术汇报的绝大部分页面。
4. **检查。** 运行 `python3 scripts/lint_deck.py deck.tex`。它会做规则检查、编译两遍、输出 `deck_sheet.png`。FAIL 必须全部修掉。
5. **看图。** 打开拼版图逐页看（需要时用 `pdftoppm -r 110 -f N -l N` 放大单页）。按下面的目检清单过一遍，有问题回到第 3 步。

## 七种母版

| 字母 | 名称 | 什么时候用 |
|---|---|---|
| A | 封面 | 第 1 页，`\titlepage` + `[plain]` |
| B | 左图右文 | 一张接近方形或宽高比 1.2–2.5 的图 + 2–4 张解读卡片 |
| C | 上图下卡 | 宽高比 > 2.5 的宽图通栏放顶部，下面 2 张卡 |
| D | 卡片流 | 有先后顺序的 2–4 步流程，卡片之间放箭头 |
| E | 数据页 | 表格或实验图 + 一个 takeaway 结论 |
| F | 并列卡 | 2–4 个并列概念 / 动机 / 对比，不加箭头 |
| G | 陈述页 | 章节转场或一句核心论点，整页只有一句话 |

详细尺寸和写法见 `references/layouts.md`。
## 硬性规则

这些规则是视觉效果的基础，`lint_deck.py` 会检查大部分：

- **一个强调色。** 只用主题里的六个颜色令牌（`BgPaper` `InkMain` `InkMuted` `AccentTerra` `CardSand` `BorderWarm`）和派生的 `TerraTint`。不写 `red` `blue` 这类颜色名。
- **每页强调不超过 4 处**（`\key` + `\speedup`），**takeaway 至多 1 个**。强调多了就等于没有强调。
- **标题统一用 `\bititle{English Title}{中文副标题}`。** 英文用 Title Case，中文副标题不超过 12 个字。
- **字号只用令牌**：`\bodysize`（卡片正文，默认）、`\densesize`（公式密集或 4 卡以上）、`\notesize`（底部批注）、`\capsize`（图注）。不用 `\tiny` `\scriptsize` `\Large`。
- **插图只用 `\safeimg[width=..,height=..]{路径}{图注与来源}`**，宽高都要给，图注写清来源（论文 Figure 编号或原文件名）。
- **公式在卡片里用 `\eqline{...}`**，超宽会自动等比缩小。不用 `\[ \]` 和 `equation`。
- **不用 beamer 自带的 block、阴影、圆角、渐变、图标、emoji。**
- **页面底部的口径说明、勘误、免责声明放进 `fignote`**，不要混在正文卡片里。

## 目检清单

看拼版图时逐页确认：

1. 内容没有贴到底栏，底部至少留出一行空白。
2. 同一行的卡片顶端对齐、高度一致（并列卡用固定高度参数）。
3. 图片没有被拉伸，图注和图左缘对齐。
4. 全页一眼能看出最重要的一句话在哪（通常是 takeaway 或一个 `\key`）。
5. 页面左右两栏的视觉重量大致平衡；一栏空、一栏满时调整列宽或换母版。
6. 没有孤零零一个字落在下一行（标题、卡片标题尤其注意）。
7. 底栏当前章节高亮正确，页码连续。

## 换风格时

允许改的只有两处：`\setaccent{HEX}` 换强调色（选饱和度中等、在 `FAF8F5` 上对比度 ≥ 4.5:1 的颜色，例如深蓝 `2F5D8A`、墨绿 `3F6B4E`），以及在非 macOS 系统上换字体（见 `references/troubleshooting.md`）。其他令牌不要动，它们是一起调过的。
