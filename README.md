# Skill 共同创建与维护

这里是我们共同编写、阅读和修改 skill 的工作区，也供其他 agent 学习和复制。默认每个新 skill 在本目录下新建独立文件夹，再在其中开始制作。

**本目录不是各 agent 的默认 skill 安装目录。** 在这里修改的内容不会自动同步到已安装的 skill；需要使用时，按照目标 agent 的安装方式复制或安装，并确认目标路径和已有版本。具体任务另有指定时，以当次要求为准。

## 目录树

```text
skill存储与编写/
├── README.md                  # 工作区说明和维护约定
├── .gitignore                 # 不纳入版本管理的本地文件
├── .github/
│   └── README.md              # GitHub 展示首页：用途、入口与使用方式
├── commander-skill/           # Commander skill 的工作材料
│   ├── README.md              # 该 skill 的说明与安装指引
│   └── commander/
│       └── SKILL.md           # skill 指令
├── commander-skill.zip        # Commander 的打包快照
├── obsidian-self-study/       # Obsidian 课程自学笔记构建
│   ├── README.md              # 使用说明
│   ├── SKILL.md               # skill 指令
│   ├── references/            # 预检、OCR、教学、排版和质量检查等规范
│   ├── scripts/               # Vault 检查脚本
│   ├── templates/             # 笔记、索引与 QA 模板
│   └── tests/                 # 检查脚本的测试
├── obsidian-self-study-v0.1.zip  # Obsidian 自学笔记的打包快照
├── 暖纸风学术幻灯片制作_Beamer/  # Warm Paper Beamer 幻灯片制作
│   ├── SKILL.md               # skill 指令
│   ├── assets/                # 主题、样张和占位图片
│   ├── references/            # 设计、版式、组件及排错说明
│   └── scripts/               # 幻灯片检查脚本
└── 暖纸风学术幻灯片制作_Beamer.zip  # Warm Paper 的打包快照
```

目录树反映当前结构；新增、移动或删除项目时，请一并更新。压缩包是某个时间点的快照，修改源文件后不会自动更新；分享前应检查内容并按需重新打包。

## 创建和维护

1. 在本目录下为新 skill 建立一个名称清晰的独立文件夹，放入 `SKILL.md` 和所需的说明、参考资料或脚本。具体结构按该 skill 的需要决定。
2. 修改时保留原有意图，检查引用的路径和配套文件；有实际运行要求时，记录检查和试用结果，区分已验证与尚未验证的内容。
3. 在本 README 的目录树中登记新项目；项目复杂时，在项目内部另写 README，说明用途、安装方法和验证情况。
4. 需要让 agent 使用时，参照该 agent 的约定安装到其正常的 skill 目录；更新工作区不等于更新安装副本。覆盖已有安装版本前先检查差异并保留需要的内容。
5. 分享压缩包前检查其版本与源文件是否一致，避免把旧快照当作最新版本。

## Git 维护

本目录使用本地 Git 仓库记录文件变更，不会自动上传或同步到远程。常用命令（在本目录运行）：

```bash
git status                 # 查看变更
git diff                   # 查看已跟踪文件的具体修改
git add <文件或目录>        # 选择要记录的内容
git diff --cached          # 检查准备提交的内容
git commit -m "描述本次修改"  # 创建一条本地历史记录
git log --oneline --graph  # 查看提交历史树
```

提交前检查新增文件及差异，避免将密码、令牌或私人材料纳入仓库。Git 不会自动识别压缩包内部的逐行变化；如需追踪修改，请保留可读的源文件。
