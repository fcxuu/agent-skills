# 七种页面母版

每种母版在 `assets/starter.tex` 里都有一页完整样张。写新页面时复制对应样张的结构，只替换内容。

## 选择母版

按顺序问自己：

1. 是第一页吗？→ **A 封面**
2. 这页只有一句话吗（章节转场、核心论点）？→ **G 陈述页**
3. 有图吗？
   - 图的宽高比 > 2.5 → **C 上图下卡**
   - 主要是实验结果（表格、柱状图、曲线）→ **E 数据页**
   - 其他图 → **B 左图右文**
4. 没有图：内容有先后顺序吗？
   - 有（步骤、流水线、推导链）→ **D 卡片流**
   - 没有（并列原因、对比、定义组）→ **F 并列卡**

全篇的节奏：连续 3 页以上用同一种母版时，考虑中间插一页 G 或换一种排法，避免观众疲劳。

## A 封面

```latex
\title{English Paper Title}
\subtitle{中文标题 \muted{——}\ 课程名\dotsep 论文研讨汇报}
\coverkicker{PAPER SEMINAR}           % 全大写小标签，陶土色
\covermeta{汇报小组：…\metasep 小组成员：A\dotsep B\metasep 汇报日期：…}
\coverref{Author A\dotsep Author B (2025), \textit{Venue}\par\muted{DOI: …}}
...
\begin{frame}[plain]\titlepage\end{frame}
```

- 标题过长时（超过两行）手动用 `\\` 在语义断点换行。
- 论文出处放在 `\coverref` 的左竖线框里，人名之间用 `\dotsep`，不要用中文顿号。

## B 左图右文

```latex
\begin{columns}[T,onlytextwidth]
  \column{.54\textwidth}
    \safeimg[width=\linewidth,height=.62\textheight]{fig.pdf}{图注。来源：…}
  \column{.42\textwidth}
    \begin{callout}{对象}…\end{callout}
    \begin{warmcard}{结论}\eqline{…}\end{warmcard}
\end{columns}
\vfill
\begin{fignote}批注…\end{fignote}
```

- 图栏 .50–.58，文栏 .38–.46，两者之和 .96–.97。
- 图偏方或偏竖时缩小图栏到 .45–.50，把空间给文字。
- 右栏 2–4 张卡片，第一张通常是 `callout`（定义或背景），后面是 `warmcard`。
- 高度：图 `height=.55–.65\textheight`；有 fignote 时取下限。

## C 上图下卡

```latex
\safeimg[width=.92\linewidth,height=.30\textheight]{wide.png}{图注。来源：…}
\begin{columns}[T,onlytextwidth]
  \column{.485\textwidth}\begin{callout}[\linewidth][1.3cm]{读图要点}…\end{callout}
  \column{.485\textwidth}\begin{warmcard}[\linewidth][1.3cm]{对应公式}…\end{warmcard}
\end{columns}
```

- 宽图高度 .26–.34\textheight。
- 下方两张卡**必须给同一个固定高度**，否则高低不齐。
- 下方也可以是三栏（每栏 .32），对应图中三个部分。

## D 卡片流

```latex
\begin{columns}[T,onlytextwidth]
  \column{.3\textwidth}\begin{warmcard}[\linewidth][2.3cm]{\stepnum{1}\ Step}…\end{warmcard}
  \column{.035\textwidth}\gaparrow
  \column{.3\textwidth}\begin{warmcard}[\linewidth][2.3cm]{\stepnum{2}\ Step}…\end{warmcard}
  \column{.035\textwidth}\gaparrow
  \column{.3\textwidth}\begin{warmcard}[\linewidth][2.3cm]{\stepnum{3}\ Step}…\end{warmcard}
\end{columns}
\contrastbar{旧方法}{…}{新方法}{…}     % 可选：一条对比结论
```

- 列宽：三步 `.3 / .035`，四步 `.22 / .03`，两步 `.46 / .04`。
- 所有步骤卡等高；`\gaparrow[高度]` 的默认值 1.2cm 大约对准 2.3cm 卡的中线，卡更高时调大。
- 步骤超过 4 个就拆成两行或两页，不要把卡片挤窄。
- 纵向流程（上下排列）用 `\downarrowc` 连接卡片。

## E 数据页

```latex
\begin{columns}[T,onlytextwidth]
  \column{.5\textwidth}
    {\densesize\warmrule
    \begin{tabular}{@{}lrrH@{}}\toprule … \midrule … \bottomrule\end{tabular}\par}
    \figsrc{表注…}
    \begin{takeaway}最大加速 \speedup{33.6$\times$}…\end{takeaway}
  \column{.46\textwidth}
    \safeimg[width=\linewidth,height=.6\textheight]{result.png}{来源：…}
\end{columns}
```

- 表格用 booktabs 三线，`\warmrule` 把线染成暖灰。
- 要突出的列用 `H` 列类型（陶土淡底 + 陶土粗体），每表最多一列。
- 数字右对齐，单位写在表头或表注里，不要每格都写。
- 只有图没有表时：图放左 .58，右侧放 1–2 张解读卡加 takeaway。

## F 并列卡

```latex
\begin{columns}[T,onlytextwidth]
  \column{.32\textwidth}\begin{warmcard}[\linewidth][2.6cm]{Title\\\muted{中文}}…\end{warmcard}
  \column{.32\textwidth}…
  \column{.32\textwidth}…
\end{columns}
\begin{takeaway}一句话收束。\end{takeaway}
```

- 2 卡 `.485`，3 卡 `.32`，4 卡 `.235`（4 卡时正文用 `\densesize`）。
- 卡片标题可以写成"英文\\\muted{中文}"两行。
- 卡片之间不放箭头；有箭头就是 D。

## G 陈述页

```latex
\begin{frame}
  \statementpage{一句话讲清核心想法：\key{关键词}。}[出处或限定条件（可选）]
\end{frame}
```

- 一句话控制在 40 个汉字以内，至多一个 `\key`。
- 不加 `\bititle`，底栏照常显示。
- 用在章节开头，或者全篇最重要的结论之前。

## 尺寸速查

| 项目 | 值 |
|---|---|
| 页面 | 16:9，160mm × 90mm，10pt 基础字号 |
| 左右边距 | 0.9cm |
| 可用高度（标题下到底栏上） | 约 `\textheight`；图高不超过 .65\textheight |
| 卡片内边距 / 间距 | 6pt / 5pt |
| 列宽之和 | .96–.97\textwidth（`onlytextwidth`） |
