# One rulebook for every agent — AGENTS.md + CLAUDE.md

If you use Codex and Claude Code together, you probably have two rulebooks: `AGENTS.md` and `CLAUDE.md`.
You update one, forget the other, and the two AIs start doing things differently.

## The pattern

Write shared rules **once**, in `AGENTS.md`. Make `CLAUDE.md` point to it.

```text
project/
├── AGENTS.md     ← all shared rules live here (scope, safety, how to test, how to report)
└── CLAUDE.md     ← first line imports AGENTS.md; below it, Claude-only notes
```

`CLAUDE.md`:

```text
@AGENTS.md

## Claude only
- (things only Claude needs to know)
```

`@AGENTS.md` means "import": when Claude reads `CLAUDE.md`, it reads `AGENTS.md` too.

Why this matters: Codex reads `AGENTS.md`. Claude Code reads `CLAUDE.md`, and by default, when a `CLAUDE.md` already exists,
it does not load `AGENTS.md` on its own. Without the import line, rules you wrote in `AGENTS.md` may never reach Claude.

## A starter AGENTS.md

```markdown
# AGENTS.md — shared rules

## Scope
- Work only inside this project folder.

## Safety
- Never print or commit passwords, API keys or .env files.
- Ask a human before: publishing, sending messages, spending money, putting a site live,
  changing account settings, deleting shared data.

## Coding rules
- Before changing anything, say what you understood the task to be and what you are unsure about. If it is unclear, ask.
- Keep each change small: do what was asked, leave unrelated code alone, add nothing extra.
- Agree on the check first (a test, a command, a screenshot). Call it done only after that check passes.

## Reporting
- End with what you did, how you checked it, and what is still open.
```

## What we tested

Two test folders, both with `AGENTS.md` = "Always answer in exactly three bullet points." The only difference was `CLAUDE.md`:

| Folder | CLAUDE.md | `/context` listed AGENTS.md? | Answer to "What is the capital of Malaysia?" |
|---|---|---|---|
| A | `@AGENTS.md` | yes | exactly 3 bullet points |
| B | a plain note, no import | no | two plain paragraphs |

File and shell tools were turned off, so the answer could only reflect rule files loaded at start.
(2026-10-02, Claude Code 2.1.284, headless `claude -p`, one run per folder.)

## Caveat: opening Claude Code from a subfolder

In our test, the import did **not** carry into subfolders:

- Started in the folder that holds both `CLAUDE.md` and `AGENTS.md`: both were loaded.
- Started in a **subfolder** (with no rule files of its own): the parent `CLAUDE.md` was loaded, but the `AGENTS.md` it imports was **not**.
- In a small repro, adding `child/CLAUDE.md` with `@../AGENTS.md`, or a symlink `child/AGENTS.md → ../AGENTS.md`, still did not get it listed.

What to do:

1. Start Claude Code in the folder that holds both files, **or**
2. If you must start in a subfolder, run `/context` first and check that `AGENTS.md` is in the Memory files list. If not, ask Claude to read it at the start of the session.

Not verified: *why* this happens (possibly the approval Claude Code asks for before loading imports from outside the start folder),
interactive sessions after approving the import, and other versions. Tested headless, Claude Code 2.1.284, one run each.

## Check it yourself

Run `/context` in Claude Code. It lists which rule files ("Memory files") this session loaded. If `AGENTS.md` is not there, Claude is not reading it.

## 中文重点

- 共用规则只写在 `AGENTS.md`。`CLAUDE.md` 第一行写 `@AGENTS.md`，下面只放 Claude 专用的。
- 没有这一行，Claude 默认不会载入 `AGENTS.md`。
- 注意：从「子文件夹」打开 Claude Code 时，我们的测试里上层的 `CLAUDE.md` 有载入，它导入的 `AGENTS.md` 却没有。最稳的做法：在放这两个文件的那一层打开；不然先跑 `/context` 检查。
