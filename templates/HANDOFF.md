# HANDOFF — 交接单

Use this when one AI session ends and another one (or a person) picks up the work.
Keep it short. Write facts, file names and commands, not feelings.
Copy the block below, fill it in, save it next to the work (for example `HANDOFF.md` in the project folder).

当一个 AI 对话结束、换另一个 AI（或换人）接手时用。
写短一点。写事实、文件名和指令，不写感觉。
复制下面这一段，填好，放在工作文件夹里（例如项目里的 `HANDOFF.md`）。

---

```markdown
# 交接单 / Handoff — <任务名 task name> — <日期 date>

## 做到哪里 / Where we are
- 已经完成、已经验证的事。每一条写上证据：文件路径、跑过的指令、结果。
- Done and checked. Each line names its proof: file path, command that ran, result.

## 还没做 / Not done yet
- 还没开始或做到一半的事。做到一半的，写清楚停在哪一步。
- Not started or half done. For half-done work, say exactly where it stopped.

## 下一步 / Next step
- 只写一个最先要做的动作，要具体到可以直接开工。
- One first action, specific enough to start right away.

## 已经否决，不要再提 / Already rejected — do not suggest again
- 试过或讨论过、已经决定不用的做法，加一句原因。
- Ideas already tried or discussed and turned down, with one line on why.

## 要老板决定 / Needs the owner's decision
- 只有老板能决定的事：花钱、发布、对外发信息、改账号、删共享资料、价格。
- 每一条写：选项 A / 选项 B / 你的建议。
- Only things the owner decides: spending, publishing, messaging people, account changes,
  deleting shared data, pricing. For each: option A / option B / your recommendation.
```

---

Tips / 小提醒

- "Done" means checked. If you did not check it, it goes under 还没做 / Not done yet.
- 「做完」等于「验证过」。没验证的，放进「还没做」。
- The rejected list saves the most time. Without it, the next AI suggests the same dead ends again.
- 「已经否决」那一栏最省时间。没有它，下一个 AI 会再提一次同样的死路。
- Never paste passwords, API keys or private customer data into a handoff.
- 交接单里绝对不要贴密码、API key 或客户的私人资料。
