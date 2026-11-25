# Skill 共同创建与维护

这里是我们共同编写、阅读和修改 skill 的工作区，也供其他 agent 学习和复制。默认每个新 skill 在本目录下新建独立文件夹，再在其中开始制作。

本目录存放技能的维护版本。下面九个已在本机通过共享目录链接到这里，修改入口后各客户端可重新发现。其他技能的安装方式见本页维护说明。

## 九个本地 Skill 怎么触发

在 DSH、Codex 或 Pi 中直接说明**想做的动作和对应的文件、项目或产物**，也可以说「请使用 `技能名` 做……」。提到 Python、论文、Git、Obsidian 等主题的闲聊和概念问答，默认按普通对话处理。

| Skill | 适合触发的请求 | 普通聊天中跳过的例子 |
| --- | --- | --- |
| [acquire-codebase-knowledge](acquire-codebase-knowledge/SKILL.md) | 「给这个仓库写一份新人导读，标出入口、模块关系和测试位置。」可只交一页。 | 「Python 模块是什么？」或只解释一行代码 |
| [webapp-testing](webapp-testing/SKILL.md) | 「打开这个本地网页，实际点一次导出，检查下载或控制台错误。」 | 「浏览器为什么会缓存？」 |
| [mcp-builder](mcp-builder/SKILL.md) | 「把这个本地索引封装成 MCP 服务端，提供搜索工具并联调。」 | 「MCP 是什么？」或仅使用已有 MCP 工具 |
| [gh-fix-ci](gh-fix-ci/SKILL.md) | 「查这个 GitHub PR 失败的 Actions 作业，找出第一处相关错误。」要求修复时再改代码。 | 「CI 和 CD 有什么区别？」 |
| [citation-management](citation-management/SKILL.md) | 「把这组 DOI 整理成 BibTeX，核对元数据并标出疑似重复项。」 | 「这篇论文主要讲什么？」 |
| [scientific-visualization](scientific-visualization/SKILL.md) | 「用这份实验 CSV 画论文对比图，显示误差并导出。」也适合审查已有科研图。 | 「误差条怎么理解？」 |
| [obsidian-bases](obsidian-bases/SKILL.md) | 「用已有笔记属性建一个待复习的 .base 筛选视图。」 | 「Obsidian 的反向链接怎么理解？」 |
| [json-canvas](json-canvas/SKILL.md) | 「把这几篇笔记做成 Obsidian .canvas，用连线表示它们的关系。」 | 「解释一下这几个概念之间的关系。」 |
| [jupyter-notebook](jupyter-notebook/SKILL.md) | 「把这个实验脚本整理成能从头运行的教学 .ipynb。」 | 「Python 列表怎么排序？」 |

**本机如何加载。** `~/.agents/skills/<技能名>` 链接到本目录对应的文件夹。三个客户端共用一份入口和资源。Codex 可以用 `$技能名` 点名，Pi 可用 `/skill:技能名`（已打开的会话可执行 `/reload`），DSH 可直接说「使用 json-canvas 生成……」。如旧对话仍显示旧目录，可开新会话。其他机器只需复制选中的整个技能目录，保留相对目录结构。

**上下文开销。** 保留明确任务的自动匹配。技能目录有短名称和描述，仍会有少量目录开销。全部 15 个技能入口（`SKILL.md`）统一为英文、且控制在 8 KB 以内，包含关键护栏、脚本路由与 `$SKILL_DIR` 路径契约；上游完整原文保留为同目录 `UPSTREAM.md`，参考资料和脚本按任务取用。可在根目录运行 `python3 -B scripts/audit_skills.py` 一键校验全部技能结构并执行全量单元测试。

**运行环境。** 网页测试、MCP、引文、科研绘图和 Notebook 各有本机隔离 Python，位置为 `~/.local/share/agent-skill-runtimes/<技能名>/bin/python`。调用只需选对应解释器，无需切换系统 Python。网页测试使用本机 Chrome。MCP 本地联调用 stdio，上游调用模型的评估脚本可能产生费用。引文的在线查证需要网络。GitHub Actions 排查使用已授权的 `gh`。Bases 和 Canvas 文件可直接写，视觉效果可在 Obsidian 中检查。

**本地改动和更新。** 每个目录保留上游入口与许可证，下面是本次引入时的固定版本。Notebook 脚手架从调用方的项目选择默认输出位置，保留中文文件名，两个模板均补齐了 cell ID。更新上游时先比较差异，保留本地入口及这些适配。移动桌面工作区后，需要让共享目录的链接指向新位置。

| 上游版本 | 本地技能 |
| --- | --- |
| [GitHub Awesome Copilot · f10fdb8](https://github.com/github/awesome-copilot/tree/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/acquire-codebase-knowledge) | acquire-codebase-knowledge |
| [Anthropic Skills · e4bb5d9](https://github.com/anthropics/skills/tree/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills) | webapp-testing、mcp-builder |
| [OpenAI Skills · 49f948f](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated) | gh-fix-ci、jupyter-notebook |
| [K-Dense Scientific Agent Skills · ec59a29](https://github.com/K-Dense-AI/scientific-agent-skills/tree/ec59a29a03d5c40f73ab40878df04860bc00e876/skills) | citation-management、scientific-visualization |
| [Obsidian Skills · b110b2f](https://github.com/obsidianmd/obsidian-skills/tree/b110b2f8e9eb1f287892f937050dfd40af862cbb/plugins/obsidian/skills) | obsidian-bases、json-canvas |

## 编码任务怎么选 Skill

| 遇到的情况 | 选哪个 | 用完拿到什么 |
| --- | --- | --- |
| 开工前还说不清哪些行为要改，或者要让另一位开发者按同一标准实现 | [coding-task-contract](coding-task-contract/SKILL.md) | 一份任务约定，写明目标、改动边界、带编号的验收条件和检查方法。已有工单可以直接补全。 |
| 正在修 bug、实现功能或检查改动，需要知道哪些行为已经验证 | [verified-coding-loop](verified-coding-loop/SKILL.md) | 对应验收条件的证据，包括复现输入、实际检查、观察结果，以及仍缺哪些验证。 |
| 准备换 Agent、换设备，或请另一人复核补丁 | [agent-code-handoff](agent-code-handoff/SKILL.md) | 接收方能打开的代码版本或补丁、已知结果、剩余工作和下一步。需要独立验收时，复核者另记自己的观察。 |

例如，工单要求「导出空列表时 CSV 仍有表头，有数据时沿用原列序」。可以把下面任意一句交给对应的 Agent。

- **定需求**：「使用 coding-task-contract，把工单的两种输入写成可观察的验收条件，给出检查方法。先交付契约。」
- **做修改**：「使用 verified-coding-loop 修复导出。用同样的两组输入检查改动前后，把实际 CSV 首行和列序对应到工单的验收编号。」
- **换人复核**：「使用 agent-code-handoff 整理这次修改。接收方只有我转交的附件，请附上能重建改动的文件和原始验收条件，让对方独立核验两份 CSV。」

三个 Skill 各自都能单独使用。若刚好有前一阶段的工单或证据，沿用原编号即可。支持 Skill 的客户端可加载整个目录；普通聊天可直接提供相应的 `SKILL.md` 和任务材料。

**卡住时怎样结束这一轮。** 同一尝试持续给出相同结果，或缺少的条件已经明确，就可以记下卡在哪里、试过什么、已有结果和何时值得再试。能独立做的部分可以继续，其余随本轮结果一起交付。例如「两次都因缺少 Safari 无法启动测试。CSV 首行已核对。拿到目标浏览器后，从下载按钮继续」。

模板、编号、脚本均可按任务选用。三个脚本默认对文档给提示，格式有差异也能结束本轮。退出码 0 表示脚本完成读取和检查，实际验收结论看证据。已有自动化需要沿用原来的格式错误退出码时，可显式加 `--strict`。维护者可在各 Skill 目录运行 `python3 -B -m unittest discover -s tests`，测试与脚本仅用 Python 标准库。

## 目录树

```text
skill存储与编写/
├── README.md                  # 工作区说明和维护约定
├── .gitignore                 # 不纳入版本管理的本地文件
├── .github/
│   └── README.md              # GitHub 展示首页：用途、入口与使用方式
├── scripts/
│   └── audit_skills.py        # 全仓 15 个 Skill 的结构、权限、链接与单元测试总检脚本
├── commander/                   # 通用多 Agent 编排与总控 Skill
│   ├── README.md                # 使用说明与安装指引
│   ├── SKILL.md                 # 主入口指令
│   ├── references/              # 能力路由与验收评估规范
│   └── templates/               # 派发、纠偏与交付报告模板
├── obsidian-self-study/         # Obsidian 课程自学笔记构建
│   ├── README.md                # 使用说明
│   ├── SKILL.md                 # 主入口指令
│   ├── references/              # 预检、文档摄取、教学、排版和质量检查等规范
│   ├── scripts/                 # Vault 静检与状态管理脚本
│   ├── templates/               # 笔记、索引与 QA 模板
│   └── tests/                   # 脚本单元测试
├── warm-paper-slides/           # Warm Paper Beamer 幻灯片制作
│   ├── SKILL.md                 # 主入口指令
│   ├── assets/                  # 主题、样张和占位图片
│   ├── references/              # 设计、版式、组件及排错说明
│   ├── scripts/                 # 幻灯片检查与编译脚本
│   └── tests/                   # 静检单元测试
├── acquire-codebase-knowledge/  # 代码库导读
├── webapp-testing/              # 本地网页交互测试
├── mcp-builder/                 # MCP 服务开发与联调
├── gh-fix-ci/                   # GitHub Actions 故障排查
├── citation-management/         # 引文检索与 BibTeX 整理
├── scientific-visualization/    # 科研图表绘制与审查
├── obsidian-bases/              # Obsidian 数据库视图
├── json-canvas/                 # JSON Canvas 画布
├── jupyter-notebook/            # 实验与教学 Notebook
├── coding-task-contract/       # 编码任务契约与验收标准
│   ├── SKILL.md
│   ├── references/
│   ├── templates/
│   ├── scripts/
│   └── tests/
├── verified-coding-loop/       # 证据驱动实现、调试与验证
│   ├── SKILL.md
│   ├── references/
│   ├── templates/
│   ├── scripts/
│   └── tests/
└── agent-code-handoff/         # 跨 Agent 交接与独立复核
    ├── SKILL.md
    ├── references/
    ├── templates/
    ├── scripts/
    └── tests/
```

目录树反映当前结构；新增、移动或删除项目时，请一并更新。仓库直接维护可读源文件，不再保留 `.zip` 快照包。

## 创建和维护

1. 在本目录下为新 skill 建立一个名称清晰的独立文件夹（目录名与 `SKILL.md` 的 `name` 一致），放入 `SKILL.md` 和所需的说明、参考资料或脚本。具体结构按该 skill 的需要决定。
2. 修改时保留原有意图，检查引用的路径和配套文件；有实际运行要求时，记录检查和试用结果，区分已验证与尚未验证的内容。
3. 在本 README 的目录树中登记新项目；项目复杂时，在项目内部另写 README，说明用途、安装方法和验证情况。
4. 需要让 agent 使用时，参照该 agent 的约定安装或软链到其正常的 skill 目录；共享链接会读取工作区版本，独立复制的安装则需手动更新。覆盖已有安装版本前先检查差异并保留需要的内容。

## 从云端更新本地 Skill（标准流程）

- 本地工作路径：`/Users/fuchenxu/Desktop/skill存储与编写`
- 云端仓库：<https://github.com/fcxuu/agent-skills.git>（远程 `origin`，默认分支 `main`）

以后凡是需要**从云端更新本地 skill**，按下面步骤执行：

1. **拉取更新**（先确认工作区干净，不要用拉取覆盖未提交的改动）：

   ```bash
   cd "/Users/fuchenxu/Desktop/skill存储与编写"
   git status                     # 有未提交改动先提交或 stash
   git pull --ff-only origin main
   git diff --stat HEAD@{1} HEAD  # 查看这次从云端带回了什么
   ```

2. **跑对应 skill 自带的检查/测试**，确认更新后的源码可用：

   ```bash
   cd obsidian-self-study
   python3 -B -m unittest discover -s tests
   ```

3. **提交并推送**（如有本地整理）：

   ```bash
   git add -A
   git diff --cached --stat
   git commit -m "chore: update skills"
   git push origin main
   ```

4. **需要给某个 agent 实际使用时**，把工作区中的 skill 文件夹软链或复制到该 agent 的技能目录；覆盖已有版本前先比对差异并备份。

## Git 维护

本目录使用 Git 记录文件变更，已关联公开仓库 [fcxuu/agent-skills](https://github.com/fcxuu/agent-skills)。本地修改不会自动上传；远程更新也需要主动拉取。常用命令（在本目录运行）：

```bash
git status                 # 查看变更
git diff                   # 查看已跟踪文件的具体修改
git add <文件或目录>        # 选择要记录的内容
git diff --cached          # 检查准备提交的内容
git commit -m "描述本次修改"  # 创建一条本地历史记录
git log --oneline --graph  # 查看提交历史树
```

提交前检查新增文件及差异，避免将密码、令牌或私人材料纳入仓库。Git 不会自动识别压缩包内部的逐行变化；如需追踪修改，请保留可读的源文件。
