# Commander Skill · 第一版

这是供 Codex 或兼容 Agent Skills 标准的工具继续阅读、调整和试运行的初始版本。技能的完整指令位于 `commander/SKILL.md`。

## 安装到 Codex

1. 解压 `commander-skill.zip`。
2. 将其中的 `commander` 文件夹复制到 Codex 用户技能目录：
   - macOS：`~/.codex/skills/commander/`
   - 若你的 Codex 使用自定义 `CODEX_HOME`，则放入 `$CODEX_HOME/skills/commander/`。
3. 确认最终路径为 `~/.codex/skills/commander/SKILL.md`。
4. 在 Codex 中开启新任务或会话，明确说“使用 commander skill”。如果当前会话尚未发现新技能，重启 Codex 后再试。

若目标文件夹已经存在，先保留或备份已有文件，再决定如何合并；不要直接覆盖你已有的版本。

## 交给 Codex 继续迭代

安装后可在 Codex 新会话中粘贴：

> 请读取我安装的 `commander` skill，并结合我的实际工作流审阅它。先检查技能结构、指令冲突、可执行性、权限边界和不同 Agent 的委派流程；保留有效内容，提出具体改进并直接完成低风险的整理。请明确区分文档审阅、静态检查和实际运行验证；设计少量代表性试用任务，但未经我要求不要声称技能已在 Codex 中验证可运行。最后给出修改清单、验证证据和仍需我决定的事项。

## 版本边界

这是基于用户提供的 ChatGPT 对话内容制作的第一版。它包含技能清单、路由流程、调度提示词、验收和报告格式。当前没有在 Codex 中安装、触发或通过实际任务验证；后续应由用户在自己的 Codex 环境中继续试用和迭代。
