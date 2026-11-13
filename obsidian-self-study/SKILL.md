---
name: obsidian-self-study
description: 将课程 PDF、PPT、教材和讲义整理为 Obsidian 自学笔记，提供清晰的知识讲解、数学推导补全、原图保留、课程知识索引和期末复习入口；支持批量构建、质量验收与断点续做，不用于单次答疑或互动家教。
metadata:
  version: "0.1.0"
---

# Obsidian 自学笔记构建

## 不可违背的约定

- 这是**一次性批量构建**工作流：构建与用户后续阅读分离。不要默认开启实时监控、更新同步、已完成章节重生成或批注合并。
- 用户指定的已有 Obsidian Vault 与课程目录是工作边界。**不要创建额外的 `ObsidianVault/`、`Courses/` 根目录**，不得擅自移动课件、覆盖重要文件或改动 `.obsidian/`。示例：Vault 根目录可以直接是 `/path/to/lectures/`，某课程目录为其下 `认知智能/`；此绝对路径只是通用路径示例，实际运行必须检查后使用。
- 同一课程内的多份 PDF/PPT/讲义，视作一套课程材料，按材料实际顺序组织成一门课。原始摄取产物**每份源课件对应一个完整 Markdown**；最终教学笔记以小节为主、重要独立知识按需拆分。
- 产物是同一套融合了**精炼课堂笔记风格**与**系统自学教材风格**的笔记，而非两套重复讲义。保留原教材表达和推导深度，重点修复阻碍理解的关键跳步。教师式家教讲解是未来单独模式，不在本 Skill 范围内。
- 核心定义、必要图解、重要假设与关键桥接保持展开；较长证明、例题答案及补充拓展默认折叠。用原生 Obsidian Callout、MathJax 与双链；**原教材已有公式编号保留，新增公式默认不编号**。
- 主动核实事实，不因 OCR 错误、疑似定理或缺失图片而猜测。未经确认的关键内容必须局部隔离，且在 QA 中记录依赖影响。
- 整门课在当前实际执行环境及额度范围内自主推进：**小节保存检查点，章节报告，最后统一交付**。小节失败先记录、跳过独立内容，最终可 `completed_with_issues` 交付。不要假装后台持续运行。

## 路径契约（跨客户端通用）

- **`SKILL_DIR`** 是当前 `SKILL.md` 所在的**真实 Skill 安装目录**。优先从宿主提供的 `SKILL.md` 路径取其父目录；若宿主只提供文本，先查当前项目已知的标准安装目录（如 `.agents/skills/obsidian-self-study/`），再查用户级目录（如 `~/.agents/skills/obsidian-self-study/`）；必要时按宿主实际支持的 Skill 目录定位。每个候选必须核验实际 `SKILL.md`；有多个匹配且无法确定本次加载来源时，不得任意猜测。**绝不把 `pwd` 直接当成 `SKILL_DIR`。**
- **Skill 内部只读资产**：`SKILL.md`、`references/`、`templates/`、`scripts/` 的路径以 `SKILL_DIR` 为基准；不得向 Skill 安装目录写入课程笔记、原始 Markdown、QA 或临时日志。
- **用户课程数据**：`VAULT_DIR` 为已确认的 Obsidian Vault 根目录，`COURSE_DIR` 为其中既有课程目录；`.build-state.json`、`README.md`、`QA.md`、`raw-markdown/`、`notes/`、`assets/`、`review/` 均属于 `COURSE_DIR`。两套命名空间不得混用，不擅自搬移源资料或修改 `.obsidian/`。
- **按需读取故障**：需加载内部文件时先核对路径和实际存在性，不通过中文别名猜测替代文件；当前阶段必需文件缺失则暂停其依赖操作并记录受阻位置，未触发的条件文件不阻碍其他独立工作。不得宣称读过无法读取的规范。

## 模块加载门禁（跨平台通用）

- **Baseline（启动/恢复/交付）**：本 `SKILL.md` 的安全和教学底线始终有效；仅在启动、断点恢复、最终交付或规则丢失时读取任务预检（`references/00-preflight.md`）与批量执行/恢复（`references/07-execution.md`），逐节生成时不机械重读。
- **Stage-Specific（进入对应阶段时）**：摄取读文档摄取规范（`references/01-ingestion.md`）；笔记撰写读教学规范（`references/02-pedagogy.md`）与 Obsidian 排版规范（`references/03-obsidian-style.md`）；索引/复习读知识索引规范（`references/05-knowledge.md`）；L1/L2/L3 验收读 QA 规范（`references/06-quality.md`）。普通正文写作期间不额外加载其他阶段完整规范。
- **Conditional（条件触发）**：图像处理读图片规范（`references/04-images.md`）；符合 A2 角色/收益门槛时读多 Agent 协作规范（`references/08-multi-agent.md`）；笔记模板（`templates/note.template.md`）、README 模板（`templates/README.template.md`）、QA 模板（`templates/QA.template.md`）、复习模板（`templates/review.template.md`）仅在首次创建对应产物或核对字段骨架时分别读取，不全量加载。
- **复用与重锚定**：同会话同阶段已读且仍可靠可用的规范直接复用。发生上下文压缩/摘要，或长程跨章后无法确认先前规范仍在有效上下文时，先重新读取**当前阶段核心规范**再生成，禁止依赖模糊记忆猜测格式。不得以节省 Token 为由削减数学严谨性、来源追溯、公式/图表校验或 QA。
- **数据侧切片**：完整 `raw-markdown/` 只存于磁盘；每次按目标小节标题或可靠页码/行号读取相关片段与少量前置知识，不一次注入大份课件原文。大量工具输出只取必要的路径、区间与证据。

## 0. 预检（正式构建前必做）

任务启动/恢复时按 Baseline 读取任务预检（`references/00-preflight.md`）与批量执行/恢复（`references/07-execution.md`），检查 Vault/课程目录、文件清单、README/QA、实际文件、文档摄取能力、权限、额度、依赖与当前阶段；尽量自主判断，只有缺少真正必要的输入或涉及高风险覆盖时才询问。

**执行模式分流（默认单 Agent）：** 预检先识别可信指令中的局部 Worker 任务或显式 Commander/多 Agent 要求；二者均按需读取多 Agent 协作规范（`references/08-multi-agent.md`）。否则，只有**真实可委派工具 + 本次课程明确的并行收益**同时成立才将自己视为 Commander 候选并读取该模块；工具存在本身不触发。未满足条件直接独立构建。Commander 仍须评估后自行决定是否委派，绝不虚构分工结果。

## 1. 识别资料与文档摄取

进入摄取阶段时读文档摄取规范（`references/01-ingestion.md`）（若已可靠加载则复用）。先核验并复用已存在的完整 `raw-markdown/`；否则动态发现当前可用的专业文档解析/OCR MCP、本地 CLI/脚本或宿主原生多模态能力，按照**源文件形态、解析质量、资源成本**选择方法，不绑定任何指定 OCR 服务。对新工具或较复杂的大文件优先进行 1–2 页探针；每份课件保存一份完整原始 Markdown 到课程目录 `raw-markdown/`，保留来源、页码/幻灯片与图表位置。在宣布摄取完成前，执行**页/幻灯片覆盖、空页/密度异常、数学公式/编码抽检**；非空文件与工具成功码都不等于成功摄取。失败局部隔离，详细解析过程及异常记录到 QA；源文件仍为第一手核验依据。

## 2. 增量课程大纲映射与教学重构

摄取后、正式生成小节笔记前，依照知识索引与课程映射规范（`references/05-knowledge.md`）增量维护课程内 `raw-markdown/source-map.md`：将**逻辑知识小节**映射到一份或多份课件的可信页码/标题/可用行号区间，支持同文件非连续片段。发现课件结尾知识明显未完结时先探测相邻下一份课件的目录或开头页；未能闭合标 `unverified` 并仅暂停受影响小节，继续其他独立内容。已确定的范围供 B1 精准切片读取；此映射不管理五态任务状态，不预建全书目录。

进入笔记撰写阶段时读教学规范（`references/02-pedagogy.md`）与 Obsidian 排版规范（`references/03-obsidian-style.md`）；仅在增量映射、知识索引或复习入口操作时读知识索引规范（`references/05-knowledge.md`）。先从课程 `README.md` 的章节索引与关键词速查定位，只读取当前小节源 Markdown 的相关片段及必要前置笔记的 `## 核心速览`/关键定义；**不要反复加载整门课正文**。遵循可信知识逻辑顺序；跨课件同一主题去重整合、选定主符号并用 `[符号对照]` 标明异构记号及来源，无法核验的实质冲突隔离记入 QA；对长小节或值得复用的知识点按需拆页。按小节信息密度适配重构深度：忠实原文整理无需逐句标签，实质新增推导/直觉/拓展分别标注 `[推导补全]`、`[直觉桥接]`、`[拓展补充]`；未经核验的关键论证局部隔离，不进入 `## 核心速览`。

每篇正式笔记包含可独立理解的 `## 核心速览` 区域，便于期末复习按标题嵌入。正文的 2A Callout 要突出定义、公式、关键理解和易错点，避免机械地为每条普通句子建立卡片。

## 3. 图像处理

仅在确实需要原图提取、补图、重绘或复杂图文处理时读图片规范（`references/04-images.md`）。原图优先；能可靠提取的原始图表尽量归档，正文只精选有助于学习的图。模糊或不足时，在有可靠依据下重绘/补图；关键图与图注、解释放在**对应 Callout 内**。文件本地可用，来源可追溯，禁止杜撰曲线或数据。

## 4. 检查、保存与恢复

进入 L1/L2/L3 验收阶段时读 QA 规范（`references/06-quality.md`）；恢复或交付时按需复核批量执行/恢复规范（`references/07-execution.md`）。四份 `templates/` 模板仅在创建对应产物或核对结构时读取单个文件，不要求每节重读。

- 小节五态（`pending` / `processing` / `qa_pending` / `completed` / `failed`）由课程根目录 `.build-state.json` 持久化；`README.md` 仅为学生导航及检查点进度投影，`QA.md` 为证据台账，C1 的 `source-map.md` 只管源边界。按**实际文件与 QA 证据 > JSON > README**恢复；`completed` 必须存在非空笔记且通过必要 QA，自动恢复时默认只读。
- 所有笔记做 L1 基础检查；高风险 OCR/数学/关键新增解释做 L2 复核；每章做 L3 综合检查。可在预检确认实际 Skill 根目录后使用 `python3 "$SKILL_DIR/scripts/check_vault.py" --vault "$VAULT_DIR" --course "$COURSE_DIR" --json` 执行**只读 L1 静态检查**；`--course` 同时支持 Vault 内的相对或绝对路径。脚本报告的 `not_checked` 包括数学、OCR、图表真实性、L2/L3 与实际 Obsidian 渲染，退出码 0 **不等于整门课程 QA 通过**。
- 有依据的修复尽量局部进行；已通过 QA 的 `completed` 笔记在恢复期间默认只读；同一问题默认最多两次**有实质变化**的自动修复。严重且无法确认的内容先写 `QA.md` 记录，再安全写入 `.build-state.json` 的失败状态，`README.md` 在检查点同步；受影响依赖不得误标通过。
- 默认由当前构建 Agent 更新课程 `.build-state.json`、README/QA 和来源映射；多 Agent 时依照多 Agent 协作规范（`references/08-multi-agent.md`）由唯一协调者写入全部共享文件。

## 5. 完成交付

课程级状态：`in_progress` / `completed` / `completed_with_issues` / `interrupted`。已尝试所有计划小节且完成章级检查后，即使存在已记录失败也直接交付已完成内容、`README.md`、`QA.md`、本地图像和复习入口；不要为失败项阻滞整书交付。若额度/环境中断且仍有未尝试小节，标 `interrupted`，写入真实的 `.build-state.json` 检查点并同步必要 README 摘要，不谎报已结束。

最终摘要至少写明：源资料摄取成功/失败数及覆盖异常、计划小节数、完成/失败/未处理数、未解决 P0 与依赖影响、复习入口位置、静态检查与 L2/L3 的真实覆盖范围，以及下一步人工/强 Agent 修复线索。**不得写入虚构的成功、验证或工具调用记录。**
