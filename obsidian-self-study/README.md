# Obsidian Self-Study Skill · v0.1

一套面向**课程课件/教材批量构建**的 Agent Skill 草案：把原课件经实际可用的小米 OCR MCP 转为每份课件一份 Markdown，再构建面向 Obsidian 的自学讲义、关键图文、章节复习入口和增量知识索引。包含单 Agent 和 Commander 多 Agent 混合分工约定。

## 安装

将整个 `obsidian-self-study/` 文件夹复制到所用 Agent 客户端**支持加载 Agent Skills 的目录**。例如部分兼容客户端使用 `~/.agents/skills/obsidian-self-study/`，也可能需要项目级 `.agents/skills/`；具体以所用客户端版本及实际配置为准。不要修改现有桌面端的登录、模型、Skills 或 `.obsidian` 配置。主入口为 `SKILL.md`，子规范在 `references/`；模板在 `templates/`。

## 如何下达任务

示例（路径只是通用示例，实际运行先检查）：

> 请使用 Obsidian Self-Study Skill 处理 `/path/to/lectures/认知智能/` 中属于这门课的课件。`lectures/` 本身就是现有 Obsidian Vault。先做预检，动态发现小米 OCR MCP；把同一课程课件合并视为课程材料，生成原始 Markdown、2A Callout 教学笔记、README 索引、QA 和复习入口。自主按章节推进、出现失败小节记录并跳过。若你是 Commander，先判断本次是否值得委派可调用的 Agent，合理混合分工；不要虚构调用成功。

## 文件结构

- `SKILL.md` — 主执行规则，按需指向模块。
- `references/00-preflight.md` — 执行模式、Commander 规划、任务契约。
- `references/01-ocr.md` — 工具能力发现和源材料保真。
- `references/02-pedagogy.md` — 精炼课堂笔记 + 系统自学教材风格。
- `references/03-obsidian-style.md` — 2A Callout、公式、折叠和复习。
- `references/04-images.md` — 原图归档与必要重绘。
- `references/05-knowledge.md` — README、双链、跨课程知识、复习入口。
- `references/06-quality.md` — 分级 QA、局部修复、依赖风险。
- `references/07-execution.md` — 五态断点、批量保存、交付。
- `templates/` — README、QA、教学笔记和复习入口的**模板**（不是要无条件照抄的成品）。
- `scripts/check_vault.py` — 无第三方依赖的只读静态检查，可用来做 L1 的一部分。

## 静态检查

```bash
python3 scripts/check_vault.py --vault "/实际/Vault/路径" --course "实际课程文件夹"
python3 scripts/check_vault.py --vault "/实际/Vault/路径" --course "实际课程文件夹" --json
```

检查现存的笔记、图片资源、部分 Obsidian 双链和复习入口；不检查 OCR 数学真伪、教材覆盖的深层语义或实际 Obsidian 渲染。不要把脚本输出理解为课程已通过全部 QA。

## v0.1 已知边界

- 尚未在用户的真实小米 OCR MCP、Mac 文件系统和 Obsidian 阅读视图中进行端到端测试。
- 不提供后台任务调度器，不代替实际可调用的多 Agent 平台；Commander 逻辑是角色和工作约定。
- 不包含家教/互动授课模式；不建立教材更新监听或学习期间笔记同步。
- Agent Skills 语法参考 <https://agentskills.io/specification>；Obsidian 原生 Callout 与嵌入语法见 <https://obsidian.md/help/callouts>、<https://obsidian.md/help/embeds>。
