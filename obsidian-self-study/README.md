# Obsidian Self-Study Skill · v0.1（v0.2 改进中）

一套面向**课程课件/教材批量构建**的 Agent Skill 草案：通过当前环境已有的文档解析、OCR 或原生读取能力，将每份课件转换为一份可核验的完整 Markdown，再构建面向 Obsidian 的自学讲义、关键图文、章节复习入口和增量知识索引。默认支持单 Agent 完整构建；识别可信 Worker 分工、显式 Commander 要求，或同时具备真实委派能力和任务并行收益时，才按需加载 Commander/Worker 协作规则。

## 安装

将整个 `obsidian-self-study/` 文件夹复制到所用 Agent 客户端**支持加载 Agent Skills 的目录**。例如部分兼容客户端使用 `~/.agents/skills/obsidian-self-study/`，也可能需要项目级 `.agents/skills/`；具体以所用客户端版本及实际配置为准。不要修改现有桌面端的登录、模型、Skills 或 `.obsidian` 配置。主入口为 `SKILL.md`，子规范在 `references/`；模板在 `templates/`。

## 如何下达任务

示例（路径只是通用示例，实际运行先检查）：

> 请使用 Obsidian Self-Study Skill 处理 `/path/to/lectures/认知智能/` 中属于这门课的课件。`lectures/` 本身就是现有 Obsidian Vault。先做预检，核验并复用已有原始 Markdown，否则动态发现实际可用的解析/OCR/原生读取能力，并抽查覆盖页码与关键公式；把同一课程课件合并视为课程材料，生成原始 Markdown、2A Callout 教学笔记、README 索引、QA 和复习入口。自主按章节推进、出现失败小节记录并跳过。若你是 Commander，先判断本次是否值得委派可调用的 Agent，合理混合分工；不要虚构调用成功。

## 文件结构

- `SKILL.md` — 主执行规则，按需指向模块。
- `references/00-preflight.md` — 轻量任务预检和执行身份判断。
- `references/01-ingestion.md` — 工具无关的分级文档摄取、文件形态路由、探针与完整性检查。
- `references/02-pedagogy.md` — 精炼课堂笔记 + 系统自学教材风格。
- `references/03-obsidian-style.md` — 2A Callout、公式、折叠和复习。
- `references/04-images.md` — 原图归档与必要重绘。
- `references/05-knowledge.md` — README、双链、跨课程知识、复习入口。
- `references/06-quality.md` — 分级 QA、局部修复、依赖风险。
- `references/07-execution.md` — 五态断点、批量保存、交付。
- `references/08-multi-agent.md` — **按需加载**：Commander 委派三问（原则上至少两项满足且净收益为正）、Worker 任务契约、共享文件单写入者与决策留痕。
- `templates/` — README、QA、教学笔记和复习入口的**模板**（不是要无条件照抄的成品）。
- `scripts/check_vault.py` — 无第三方依赖的只读静态检查，可用来做 L1 的一部分。

## 静态检查

```bash
# SKILL_DIR 应由客户端提供的 SKILL.md 路径或实际安装目录核验得到
SKILL_DIR="/实际安装路径/obsidian-self-study"
VAULT_DIR="/实际/Vault/路径"
COURSE_DIR="$VAULT_DIR/实际课程文件夹"
python3 "$SKILL_DIR/scripts/check_vault.py" \
  --vault "$VAULT_DIR" --course "$COURSE_DIR" --json

# --course 也可传 Vault 内相对路径，如 --course "认知智能"
python3 -m unittest discover -s "$SKILL_DIR/tests" -v
```

工具为标准库、只读的 L1 静态检查，支持从任意工作目录调用。结果包含稳定排序的 `issues`、`not_checked` 和退出码 `0/1/2`；检查速览结构、图片/双链/复习嵌入、基础状态文件与 Mermaid 语法。**无法证明 OCR/数学真伪、图表真实性或 Obsidian 桌面/移动端渲染正确，也不能替代 L2/L3 QA**。

## 改进记录

- **A1：已合并至 `main`。** 文档摄取工具无关化，覆盖校验与异常记录。
- **A2：累计 PR 中的已实施改动。** 主入口轻量角色路由；满足可信角色或实际委派收益时才加载多 Agent 规范，委派前完成准入评估与决策记录。
- **B1：累计 PR 中的已实施改动。** 保留独立规范，采用 Baseline/Stage-Specific/Conditional 三层加载门禁；长任务上下文重锚定、原始 Markdown 与前置笔记切片、最小恢复上下文、已完成内容只读保护。
- **B2：已在本累计 PR 中实施。** Skill 资产使用 `SKILL_DIR`（`SKILL.md` 所在目录）、课程资料使用 `VAULT_DIR` / `COURSE_DIR`，严格区分只读规则与课程输出；首次跨模块引用使用功能名与精确路径双标，不依赖 `pwd`；缺失规范按依赖级别阻断或跳过。
- **C1：累计 PR 中的已实施改动。** 增量维护 `raw-markdown/source-map.md`；支持跨课件/非连续来源区间、右边界探测、`[符号对照]` 与冲突隔离，并保持 README 学习导航简洁。来源边界 `verified/unverified` 不替代任务五态。
- **D1：本累计 PR 中的已实施改动。** 课程根目录 `.build-state.json` 维护五态机器状态、SHA-256 来源指纹与断点；README 为检查点同步的学习导航；磁盘+QA 证据优先仲裁，已完成笔记恢复时只读，单写入协调与 C1 源边界状态互不混淆。
- **E3：已实施。** 只读 Python 标准库检查器升级为轻量词法扫描，支持 E1/D1/E2 的确定性结构验收、JSON 物理证据检查、反误报、路径越界防护、稳定 JSON 与 `not_checked`；临时 Vault 26 项回归测试通过。
- A3 入口规范已满足，留待版本发布时统一检查；其他改进项仍待讨论，未经确认不实施。

## A1 文档摄取改进

- 能力顺序：先复用有效 `raw-markdown/`，再动态发现专业 MCP、本地工具、宿主原生文档读取能力；依据文件形态和质量择优，避免整本教材重复试错。
- 新工具或复杂大文件优先选 1–2 页公式/图表样本验证；摄取完成需检查页覆盖、异常稀疏页及公式/编码；失败按页或文件隔离，不能把非空 Markdown 当作完整成功。
- README 保留简明的来源→覆盖→笔记导航；解析方式、探针、回退及异常证据记录到 QA.md。
- `references/01-ocr.md` 暂保留为迁移兼容入口；新规则以 `references/01-ingestion.md` 为准。

## v0.1 已知边界

- 尚未在真实文档摄取工具、Mac 文件系统和 Obsidian 阅读视图中进行端到端测试。
- 不提供后台任务调度器，不代替实际可调用的多 Agent 平台；默认按单 Agent 执行，多 Agent 模块只在有可信角色要求或实际委派收益时加载。
- 不包含家教/互动授课模式；不建立教材更新监听或学习期间笔记同步。
- Agent Skills 语法参考 <https://agentskills.io/specification>；Obsidian 原生 Callout 与嵌入语法见 <https://obsidian.md/help/callouts>、<https://obsidian.md/help/embeds>。
