# Agent Skills · 学习、写作与协作

这里收集我与 AI Agent 共同编写、持续修改的 skills，涵盖复杂任务协作、Obsidian 课程笔记和学术幻灯片制作。

每个 skill 都包含可直接阅读的 `SKILL.md`，部分还提供参考规范、模板、脚本和示例。你可以先阅读指令，选择适合自己工作流的部分，再复制到所用 Agent 的技能目录中试用。

## 选择一个 skill

| Skill | 适合做什么 | 阅读入口 | 下载 |
| --- | --- | --- | --- |
| **Commander** | 拆解复杂任务、判断是否需要其他 Agent、组织交接、独立验收与整合成果 | [使用说明](../commander-skill/README.md) · [完整指令](../commander-skill/commander/SKILL.md) | [ZIP](../commander-skill.zip) |
| **Obsidian Self-Study** | 从课程课件与教材构建自学笔记，保留来源，组织公式、图片、复习索引与质量记录 | [使用说明](../obsidian-self-study/README.md) · [完整指令](../obsidian-self-study/SKILL.md) | [v0.1 ZIP](../obsidian-self-study-v0.1.zip) |
| **Warm Paper Slides** | 用 LaTeX Beamer 制作暖纸底、陶土色强调的中英双语学术汇报 | [完整指令](../暖纸风学术幻灯片制作_Beamer/SKILL.md) · [PDF 样张](../暖纸风学术幻灯片制作_Beamer/assets/starter.pdf) | [ZIP](../暖纸风学术幻灯片制作_Beamer.zip) |

### Commander：把任务推进到可验收的结果

适合涉及多份材料、多步操作或多个执行者的任务。它强调明确工作边界、按实际能力选择执行方式、检查交付物，再由主 Agent 完成整合。实际委派需要运行环境提供相应工具。

示例任务：

> 使用 commander skill，梳理这个项目的目标和现有文件，完成必要修改，并用实际检查结果说明交付是否满足要求。

### Obsidian Self-Study：把课件变成可复习的自学笔记

适合批量处理一门课程的材料。工作流包括原始 Markdown 归档、教学笔记重构、图文整理、知识索引、分级 QA 和断点恢复。文档摄取优先复用有效的已有产物，再按文件形态与质量选择实际可用的解析、OCR 或原生读取能力；多 Agent 协作按需启用。笔记检查脚本仅依赖 Python 标准库。

示例任务：

> 使用 obsidian-self-study skill，为我已有的 Obsidian Vault 中的一门课程构建自学笔记。先核对材料、工具和已有笔记，再按章节推进并记录质量检查结果。

### Warm Paper Slides：克制、清晰的学术幻灯片

提供 Beamer 主题、七种页面母版、排版规范和检查脚本。适合论文研讨、课程展示和组会汇报，产出 `.tex` 与 PDF。编译需要 XeLaTeX；生成缩略拼版图还需要 Poppler 和 Pillow。字体等具体要求见 [排错说明](../暖纸风学术幻灯片制作_Beamer/references/troubleshooting.md)。

![Warm Paper 七种页面母版预览](../暖纸风学术幻灯片制作_Beamer/assets/starter_sheet.png)

## 如何使用

1. 阅读对应的 `SKILL.md`，确认用途、依赖和执行边界。
2. 下载 ZIP 或克隆仓库，将所需 skill 文件夹复制到你使用的 Agent 支持的技能目录中。
3. 保留文件夹内部结构，让 `references/`、`assets/`、`scripts/` 等配套文件与指令一起安装。
4. 按客户端要求重新加载技能，并在任务中明确提及 skill 名称。

三个安装单元分别是：

```text
commander-skill/commander/       → commander/
obsidian-self-study/            → obsidian-self-study/
暖纸风学术幻灯片制作_Beamer/     → warm-paper-slides/
```

安装目录和加载方式以所用客户端为准；覆盖已有版本前先备份并比较差异。更新仓库后，也需要自行更新已安装的副本。

## 当前状态

这些 skills 是持续迭代的工作材料。Commander 说明中保留了初版验证边界；Obsidian Self-Study 的 v0.2 改进已陆续合入，当前源码版本号仍为 `0.1.0`，下载包沿用 `v0.1` 名称并按最新源码更新；尚未完成真实文档摄取到 Obsidian 阅读视图的端到端测试。Warm Paper 提供源码、样张与检查工具，具体汇报仍需编译并逐页检查。

脚本检查只能覆盖部分问题，实际工具能力、内容准确性和最终阅读效果仍需在任务中核验。仓库中的依赖和示例不代表任何外部服务或模型免费可用。

源码是维护依据。ZIP 是打包时的快照，修改源码后应重新打包再分享。

## 交流与维护

欢迎通过 Issues 提交使用反馈，也欢迎通过 Pull Request 改进指令、模板、检查脚本和示例。反馈时请附上使用环境、复现步骤、预期行为与实际结果，并去除凭据和私人材料。

本地工作区的目录与维护约定见 [工作区 README](../README.md)。
