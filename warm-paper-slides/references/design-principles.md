# Aesthetic Principles

Warm Paper is modeled on well-typeset academic journals and magazine spreads rather than commercial pitch decks. Each rule below includes its rationale so you can make consistent judgment calls when an edge case arises.

## 1. Restrained Palette

- `BgPaper #FAF8F5` — warm off-white paper tone; avoids harsh pure-white projection glare.
- `InkMain #18181B` — near-black primary text; gentler contrast for prolonged reading.
- `InkMuted #71717A` — secondary metadata (subtitles, captions, footnotes, older baselines). Hierarchy relies on tonal value rather than jarring font-size jumps.
- `AccentTerra #C85A32` — the **sole** accent color, reserved for the title divider `｜`, card left bars, bullets, step badges, `\key`, table highlight column, and active footer section. Limit to 1–4 focal spots per slide.
- `CardSand #F0ECE1` & `BorderWarm #D6D1C7` — subtle card fill and 1pt thin border. Low contrast against paper is deliberate: cards group content without shouting for attention.

Never add a second accent color. For "old vs. new" or "bad vs. good" contrast, pair `InkMuted` (old/baseline) with `AccentTerra` (new/result) instead of red vs. green.

## 2. Flat Surfaces and Hairlines

All containers are flat color blocks with either a 1pt border (`warmcard`, `papercard`) or a 2.6pt left vertical bar (`callout`, `takeaway`). No shadows, rounded corners, gradients, or 3D effects—academic content is already dense and decorative chrome competes with it.

Left-bar containers (`callout`, `takeaway`) signal definitions, framing, or conclusions, feeling lighter than full-bordered `warmcard` blocks.

## 3. Minimal, Stable Type Scale

Only 7 font sizes exist in the theme: frame title `15pt`, subtitle `12.5pt`, card title `9.5pt`, body `9pt`, dense body `8pt`, footnote `7pt`, caption `6.5pt`. Line leading for CJK is ~1.4× font size (wider than LaTeX's default 1.2×) to prevent dense Chinese strokes from crowding.

Never drop body text below `7pt` to force content onto a slide—split the slide instead.

## 4. Bilingual Headers

Format: `English Title ｜ 中文副标题` via `\bititle{English Title}{中文副标题}`. English carries the formal Title Case heading in bold; the Chinese subtitle uses muted regular weight for rapid scanning, separated by a terracotta `｜` and a 0.4pt warm rule below.

## 5. One Claim per Slide

Every slide answers a single question. Litmus test: can you state in one sentence what the audience should remember from this slide? That sentence is usually your `takeaway`.

Density reference ceilings: ~260 Chinese characters, ≤ 6 cards, 1 primary figure, ≤ 1 `takeaway`.

## 6. Figures Lead

On figure slides, the figure takes 50–60% width (Layout B) or full width (Layout C). Captions use `6.5pt` muted gray stating both what the figure shows and its exact source. Never crop or stretch original paper figures; call out regions in adjacent text cards rather than drawing red circles over the image.

## 7. Alignment and Whitespace

- Left/right margins are `0.9cm`; all blocks share one left alignment edge.
- Card vertical gap is `5pt`; column gutter comes from the remaining width in `columns[T,onlytextwidth]` (sum of column widths `0.96–0.97\textwidth`).
- Side-by-side cards must share an identical fixed height (`[height]` second optional argument). Uneven bottoms are the fastest way to make a slide look sloppy.
- Push bottom `fignote` above the footer with `\vfill`.

## Prohibited Patterns

| Do Not Use | Reason | Use Instead |
|---|---|---|
| Default Beamer themes, `block`, `alertblock` | Rounded gradients clash with flat paper style | `warmcard` / `callout` |
| Named colors (`red`, `green`, `blue`, etc.) | Breaks single-accent restraint | `\key` / `\muted` |
| > 4 highlights per slide | Visual noise destroys hierarchy | Keep only the top 1–4 terms |
| Bolding entire sentences | Negates emphasis | Bold keywords only |
| Emoji, clipart, decorative icons | Unprofessional in academic talks; missing glyphs | Plain text or `\stepnum` |
| Incremental `\pause` animations | Bloats exported PDFs with duplicate slides | One static state per slide |
| Center-aligned prose paragraphs | Harder to scan | Left-aligned (center only equations & Layout G) |
| Shrinking figures tiny to fit more text | Unreadable plots | Split into two slides |
