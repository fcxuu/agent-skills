# 组件手册

所有组件都在 `assets/beamerthemewarmpaper.sty` 里定义。方括号是可选参数。

## 容器

| 组件 | 外观 | 用途 | 限额 |
|---|---|---|---|
| `\begin{warmcard}[宽][固定高]{标题}` | 沙色底 + 1pt 暖灰边框 | 默认内容卡：解读、公式、步骤 | 每页 ≤ 6 张容器 |
| `\begin{callout}[宽][固定高]{标题}` | 沙色底 + 陶土左竖线 | 定义、背景、读图要点 | 同上 |
| `\begin{papercard}[宽][固定高]{标题}` | 纸色底 + 细边框 | 卡片里的次级层，或与 warmcard 区分的辅助信息 | 少用 |
| `\begin{takeaway}[宽]` | 陶土淡底 + 陶土左竖线，无标题 | 本页结论，一到两句话 | 每页 ≤ 1 |
| `\begin{fignote}[宽]` | 上方细线 + 7pt 灰字 | 页底批注：勘误、省略说明、口径、免责声明 | 每页 ≤ 1，前面放 `\vfill` |

- 标题留空 `{}` 时不输出标题行。
- 固定高度只在需要并排等高时给；内容超出固定高度会溢出到下方，编译不报错，必须看图确认。
- 卡片里的正文默认 `\bodysize`。内容多时在卡片开头写 `\densesize`。
- 不要嵌套同类卡片。需要分层时，外层 `warmcard`，内层 `papercard`。

## 公式

| 写法 | 用途 |
|---|---|
| `\eqline{公式}` | 卡片内单独一行的公式，居中，超宽自动缩小 |
| `$…$` | 正文行内公式 |
| `\begin{align*}…\end{align*}` | 多行对齐推导，只在宽卡片里用 |

- 一张卡片里最多 3 条 `\eqline`，再多就拆卡片。
- 公式下面的解释用 `{\densesize …\par}`，一行为限。
- 数学字体是 STIX Two Math，和正文的苹方粗细接近。不要改成 Computer Modern。

## 插图

```latex
\safeimg[width=\linewidth,height=.6\textheight]{路径}{图注。来源：…}
\figsrc{…}   % 图和图注不在同一栏时，单独写图注
```

- `\safeimg` 按 `keepaspectratio` 缩放，宽高谁先到上限就按谁缩。宽高都要写。
- 图注宽度跟随图宽（最窄 60% 栏宽），左对齐。
- 优先用 PDF 矢量图；位图至少 150 dpi（按最终显示尺寸算）。
- 文件名里有下划线时，正文中用 `\file{name_with_underscore.pdf}` 显示。

## 行内强调

| 宏 | 效果 | 用途 |
|---|---|---|
| `\key{…}` | 陶土粗体 | 本页最关键的术语、算子、结论词 |
| `\speedup{…}` | 陶土粗体 11pt | 核心数字（加速比、提升幅度） |
| `\muted{…}` | 灰色 | 补充说明、旧方法、括号内容 |
| `\textbf{…}` | 黑色粗体 | 卡片内的小标签（“输入：”“输出：”） |
| `\textit{…}` | 仿斜体 | 论文名、期刊名 |

`\key` 和 `\speedup` 合计每页不超过 4 处。

## 连接与编号

| 宏 | 用途 |
|---|---|
| `\stepnum{n}` | 陶土实心圆编号，放在卡片标题前 |
| `\gaparrow[高度]` | 放在窄列里的横向箭头，连接左右两张卡 |
| `\downarrowc` | 居中的纵向箭头，连接上下两张卡 |
| `\flowarrow` | 行内长箭头，例如 `A \flowarrow B` |
| `\contrastbar{旧标签}{旧描述}{新标签}{新描述}` | 一条“旧方法 → 新方法”的对比条，旧方法自动弱化成灰色 |
| `\dotsep` | 人名、元信息之间的间隔点 |

## 表格

```latex
{\densesize\warmrule
\begin{tabular}{@{}lrrH@{}}
  \toprule
  \textbf{列 1} & \textbf{列 2} & \textbf{列 3} & \textbf{高亮列}\\
  \midrule
  … \\
  \bottomrule
\end{tabular}\par}
```

- 只用 `\toprule` `\midrule` `\bottomrule`，不加竖线。
- `H` 是高亮列类型，右对齐，每表最多一列。
- 主题已把 `\arraystretch` 设为 1.45；表格行数超过 8 行时局部改为 1.2。
- 列宽需要控制时用 `p{.2\textwidth}`，配合 `>{\raggedright\arraybackslash}`。

## 列表

- `itemize` 的条目符号是陶土小方块，二级是灰色小方块。
- 条目之间加 `\setlength{\itemsep}{4–6pt}`。
- 列表不超过 5 条、两级。更多内容改成并列卡（母版 F）。

## 页面级

| 宏 | 用途 |
|---|---|
| `\bititle{English}{中文}` | 帧标题，每页第一行 |
| `\statementpage{一句话}[小字]` | 陈述页（母版 G） |
| `\decksections{A,B,C}` | 底栏章节列表，与 `\section{}` 顺序一致 |
| `\setaccent{HEX}` | 换强调色（整套只换一次） |
| `\renewcommand{\decktotal}{16}` | 底栏总页数写死（默认自动统计） |
