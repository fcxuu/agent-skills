---
name: obsidian-self-study
description: 将一门课程的 PDF、PPT、课本和讲义，经可用的小米 OCR MCP 转成可追溯原始 Markdown，再生成结构清晰、数学准确、配图就近的 Obsidian 自学笔记；支持课程 README 知识索引、期末速览、分级 QA、断点续做，以及 Commander 的多 Agent 任务分配与整合。用于构建或恢复整门课的教学笔记，不用于一对一家教对话。
metadata:
  version: "0.1.0"
---

# Obsidian 自学笔记构建

## 不可违背的约定

- 这是**一次性批量构建**工作流：构建与用户后续阅读分离。不要默认开启实时监控、更新同步、已完成章节重生成或批注合并。
- 用户指定的已有 Obsidian Vault 与课程目录是工作边界。**不要创建额外的 `ObsidianVault/`、`Courses/` 根目录**，不得擅自移动课件、覆盖重要文件或改动 `.obsidian/`。示例：Vault 根目录可以直接是 `/path/to/lectures/`，某课程目录为其下 `认知智能/`；此绝对路径只是通用路径示例，实际运行必须检查后使用。
- 同一课程内的多份 PDF/PPT/讲义，视作一套课程材料，按材料实际顺序组织成一门课。原始 OCR 中间产物**每份源课件对应一个完整 Markdown**；最终教学笔记以小节为主、重要独立知识按需拆分。
- 产物是同一套融合了**精炼课堂笔记风格**与**系统自学教材风格**的笔记，而非两套重复讲义。保留原教材表达和推导深度，重点修复阻碍理解的关键跳步。教师式家教讲解是未来单独模式，不在本 Skill 范围内。
- 核心定义、必要图解、重要假设与关键桥接保持展开；较长证明、例题答案及补充拓展默认折叠。用原生 Obsidian Callout、MathJax 与双链；**原教材已有公式编号保留，新增公式默认不编号**。
- 主动核实事实，不因 OCR 错误、疑似定理或缺失图片而猜测。未经确认的关键内容必须局部隔离，且在 QA 中记录依赖影响。
- 整门课在当前实际执行环境及额度范围内自主推进：**小节保存检查点，章节报告，最后统一交付**。小节失败先记录、跳过独立内容，最终可 `completed_with_issues` 交付。不要假装后台持续运行。

## 0. 预检（正式构建前必做）

**先读 [预检与分工](references/00-preflight.md) 和 [批量执行](references/07-execution.md)。** 判断 Vault/课程目录、材料清单、先前 README/QA、实际文件、工具权限、OCR 能力、可用模型/Agent、额度及依赖。尽量自主确定；只有真正缺少必须输入或涉及高风险覆盖时才问用户。

尤其先判断：
1. **Single-Agent**：无法调用其他 Agent，或协作成本超过收益；自行完成所有步骤。
2. **Commander-Orchestrated**：确有可调用 Worker 且收益明显；Commander 混合分工，优先按课件/章节划分完整任务，必要时集中 OCR、专项数学审查或 QA。指定唯一 README 写入者。
3. **Worker-Agent**：已被分配具体范围；只处理授权文件，提交路径、QA 和索引变更建议，不擅自担任全局协调者。

**不得虚构能够调用的 Agent 或工具；** 若协作接口不可用，应回退单 Agent 或提供明确的人工转发任务契约，不能声称已派发。

## 1. 识别资料与 OCR

按需读 [OCR 规范](references/01-ocr.md)。动态发现实际可用的小米 OCR MCP 工具与支持类型，不写死工具名称或假设某格式必然支持。对每份课件保存一份完整的原始 Markdown 到课程目录 `raw-markdown/`；尽可能保留图表、原页码/幻灯片位置与源文件映射。工具失败如实记录；若某份课件失败，不影响其他独立材料。源 PDF/PPT 是校验依据，OCR Markdown 只是中间层。

## 2. 增量规划与教学重构

按需读 [教学原则](references/02-pedagogy.md)、[Obsidian 排版](references/03-obsidian-style.md)、[知识索引](references/05-knowledge.md)。先读课程 `README.md` 的章节索引与重要关键词速查，再按需读取当前课件 OCR 片段及必要前置笔记片段；**不要反复加载整门课正文**。遵循实际教材顺序；对长小节或值得复用的知识点按需拆页。

每篇正式笔记包含可独立理解的 `## 核心速览` 区域，便于期末复习按标题嵌入。正文的 2A Callout 要突出定义、公式、关键理解和易错点，避免机械地为每条普通句子建立卡片。

## 3. 图像处理

按需读 [图片规范](references/04-images.md)。原图优先；能可靠提取的原始图表尽量归档，正文只精选有助于学习的图。模糊或不足时，在有可靠依据下重绘/补图；关键图与图注、解释放在**对应 Callout 内**。文件本地可用，来源可追溯，禁止杜撰曲线或数据。

## 4. 检查、保存与恢复

按需读 [QA 规范](references/06-quality.md) 及 [批量执行](references/07-execution.md)，使用 [README 模板](templates/README.template.md)、[QA 模板](templates/QA.template.md)、[笔记模板](templates/note.template.md) 与 [复习模板](templates/review.template.md)（按需读取，不要全部展开到上下文）。

- 五种小节状态：`pending` → `processing` → `qa_pending` → `completed`；失败则 `failed`。状态和磁盘文件必须相互核对；不能以文件存在替代 QA 通过。
- 所有笔记做 L1 基础检查；高风险 OCR/数学/关键新增解释做 L2 复核；每章做 L3 综合检查。可使用 `python3 scripts/check_vault.py --vault <VAULT_PATH> --course <COURSE_REL_PATH>` 检查静态路径、链接和结构；它**不能**证明数学正确或 Obsidian 实际渲染无误。
- 有依据的修复尽量局部进行；同一问题默认最多两次**有实质变化**的自动修复。严重且无法确认的内容隔离，先记录到 `QA.md`，再更新 README 状态；受影响依赖不得误标通过。
- 单 Agent 可直接更新课程 README；多 Agent 时**唯一协调写入者**维护 README，Worker 提交独立交付记录/建议；`QA.md` 也由协调者归并，避免并发写冲突。

## 5. 完成交付

课程级状态：`in_progress` / `completed` / `completed_with_issues` / `interrupted`。已尝试所有计划小节且完成章级检查后，即使存在已记录失败也直接交付已完成内容、`README.md`、`QA.md`、本地图像和复习入口；不要为失败项阻滞整书交付。若额度/环境中断且仍有未尝试小节，标 `interrupted`，留下可恢复检查点，不谎报已结束。

最终摘要至少写明：源资料成功/失败数、计划小节数、完成/失败/未处理数、未解决 P0 与依赖影响、复习入口位置、静态检查与 L2/L3 的真实覆盖范围，以及下一步人工/强 Agent 修复线索。**不得写入虚构的成功、验证或工具调用记录。**
