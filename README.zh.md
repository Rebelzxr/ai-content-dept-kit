# ai-content-dept-kit｜AI 内容部门工具包

**一个人，用 5 个 AI 角色，跑一个小小的内容部门。这里是我们真正在用的模板、提示词和工具。**

[English README](README.md)

我们在 DAINER.AI 一边做、一边公开分享：教大家把 AI 当同事用，自己搭 AI 助手（agent），再用一个主 AI 指挥好几个 AI。
这个工具包，是我们内容流程里可以重复用的部分。我们边学边分享。

它不是一个 App。它是一个文件夹：几份文字模板，加两个小脚本。有用的拿去用，没用的跳过。

---

## 5 个角色

| # | 角色 | 做什么 | 我们用的 |
|---|---|---|---|
| 1 | **主 AI** | 指挥其他 AI、管计划、负责发布——**一定要人批准后才发** | Claude Code |
| 2 | **写手** | 写长文，也写各平台的版本 | Claude Code，加一份写好的风格规则 |
| 3 | **制作** | 真的跑测试、截图、做图和投影片 | Codex（含它的做图工具）+ `tools/` 里的脚本 |
| 4 | **审稿** | **新开的、只读的** AI，拿证据逐行检查 | 每一轮新开一个 Codex |
| 5 | **打分** | 用 6 个固定问题给稿子打 1–5 分 | 一个评分模型 |

人没有被取代。方向你定，要发出去的东西你批准，值不值得说也由你决定。

## 7 个步骤

1. **找题目**：先找读者真正想问的问题。用 `templates/STRUCTURE_PROMPT.md` 学别人好帖子的结构，不抄句子。
2. **写稿**：给写手三行任务单（`templates/TASK_BRIEF_3LINE.md`）：做完的样子／什么时候先问我／遇到这些就停。
3. **测试＋截图**：制作的 AI 真的跑一遍，把原始输出存进 `evidence/` 文件夹。截图用这些真实文字做（`tools/gui_frames.py`）。
4. **独立审稿**：新开的审稿 AI 拿证据检查稿子（`templates/REVIEWER_PROMPT.md`），回答 PASS（通过）或 REVISE（退回），附上可以直接替换的句子。改好，再复查。
5. **按平台打包**：一篇通过的长文，变成各平台的原生版本：X 长文＋封面、IG / LinkedIn 轮播图、LinkedIn 贴文、Threads。每个都符合平台的限制。
6. **人批准＋排程上传**：你批准最后的版本，主 AI 才排程或发布。没有东西会自己发出去。
7. **每周检讨**：比较改稿前后的分数（`templates/SCORING_RUBRIC.json` + `templates/scoring.md`），记下什么有效，写一份交接单（`templates/HANDOFF.md`）给下周。

## 里面有什么

```text
ai-content-dept-kit/
├── README.md / README.zh.md
├── LICENSE                      MIT 授权
├── templates/
│   ├── HANDOFF.md               交接单：5 个标题（中英）
│   ├── TASK_BRIEF_3LINE.md      三行任务单
│   ├── REVIEWER_PROMPT.md       新开、只读的审稿提示词：初审＋复查
│   ├── SAFETY_SETTINGS.json     最小的 Claude Code 权限设置（禁止 rm）
│   ├── SAFETY_SETTINGS.md       它做什么、我们测了什么、局限
│   ├── AGENTS_SHARED.md         一份 AGENTS.md 给所有 AI 用＋子文件夹的坑
│   ├── STRUCTURE_PROMPT.md      拆结构、不抄句子
│   ├── SCORING_RUBRIC.json      6 个问题、分数说明、权重
│   └── scoring.md               期望值算法＋怎么接任何模型
├── tools/
│   ├── gui_frames.py            轮播图（1080×1350）＋ PDF
│   ├── article_cover.py         X 长文封面（1500×600）＋代码图
│   ├── test_security.py         输入、路径、临时文件的安全测试
│   └── README.md
├── art/                         DAINER.AI 用 AI 做的 RISO 风格图（封面、小插图、设备）
└── examples/
    ├── slides.sample.json       示范用的投影片设定
    └── output/                  这份示范真的跑出来的结果
```

## 快速开始

**1. 把规则放进你的项目**

```bash
cp templates/SAFETY_SETTINGS.json 你的项目/.claude/settings.json   # 先建好 .claude 文件夹
```

再把规则整理成一份：规则写在 `AGENTS.md`，`CLAUDE.md` 第一行写 `@AGENTS.md`。看 `templates/AGENTS_SHARED.md`。

**2. 用三行字交代一篇稿**：`templates/TASK_BRIEF_3LINE.md`。

**3. 新开一个 AI 来审**：把填好的 `templates/REVIEWER_PROMPT.md` 贴进一个**没写过这篇稿**的新对话。

**4. 跑示范投影片**

```bash
pip install pillow numpy
python3 tools/gui_frames.py examples/slides.sample.json examples/output
python3 tools/article_cover.py G02 examples/output "小标" "标题第一行" "标题第二行" "系列名" templates/SAFETY_SETTINGS.json
```

需要 Google Chrome。不是 Mac？设定 `CHROME_PATH`。详细看 `tools/README.md`。
中文投影片：设定文件里不要写 `"lang": "en"`，就会用中文字体。

**5. 批准、排程、每周检讨**：用你自己的排程工具；用 `templates/scoring.md` 打分；用 `templates/HANDOFF.md` 交接。

## 我们学到的

- **每一篇初稿都被退回。** 我们第一批 8 组社媒稿，新开的审稿 AI 8 组都回 REVISE。改一轮之后，8 组复查全部通过。写的人看不到自己的错，第二双眼睛不能省。
- **提示词里的规则只是提醒，不是锁。** 在 `CLAUDE.md` 写「不要删文件」，只影响 AI 想做什么。`.claude/settings.json` 里一行 `deny`，在我们的测试里真的挡住了 `rm`。（Claude Code 2.1.283，跑一次。）
- **自己写的安全检查器，4 个输入里有 1 次误拦、1 次漏检。** 只能当多一层，不能当唯一的锁。
- **`CLAUDE.md` 没导入 `AGENTS.md` 之前，Claude 不读它。** 从子文件夹打开时，导入也没生效。用 `/context` 检查。（Claude Code 2.1.284，各跑一次。）
- **把意外结果放到开头，分数就上升。** 打分显示，最让人停下来的结果都埋在开头后面。我们改写了 16 篇的标题和开头，平均分从 3.92 升到 4.24，16 篇里有 15 篇上升。「新鲜感」一直是最弱的一项。
- **截图一定要来自真的执行。** 审稿 AI 会拿原始输出逐行对截图。前面有 `$` 的指令，就是真的跑过。

## 丑话说在前

- 这是**一个人的设置、一个月、一批稿**的经验。你的结果会不一样。
- 每个测试只跑**一次**，而且是特定版本（Claude Code 2.1.283 / 2.1.284、Python 3.9.6、macOS）。请在你的版本再测一次。
- `deny` 规则只拦符合规则的 Bash 命令，不保证挡住所有删除方法。
- 我们用的评分模型，中文比英文弱。分数只是第二意见，不是查证事实。
- 这个工具包**不会**帮你发文或排程。排程工具你自己接，每一篇都要人批准。
- 两个脚本需要 Chrome，字体要上网下载。只在 macOS 测过。
- 审稿要花时间。每篇至少预留一次 REVISE。

## 授权

MIT（看 `LICENSE`）。Copyright (c) 2026 DAINER.AI。
模板、脚本和里面的图都可以用、可以改、可以分享，商业用途也可以。保留授权声明就好。

## 一起学

我们边做边分享测过的东西。觉得有用，就转给正在搭自己 AI 团队的朋友。

- X：[@Dainer_Jun](https://x.com/Dainer_Jun)
- 网站：[dainer-ai.biz](https://dainer-ai.biz)
