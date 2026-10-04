# Safety settings — notes for `SAFETY_SETTINGS.json`

JSON files cannot hold comments, so the notes live here.

## What it is

`SAFETY_SETTINGS.json` is a minimal Claude Code permissions file. To use it, save it as `.claude/settings.json`
inside your project folder (note the dot in `.claude`).

```json
{
  "permissions": {
    "allow": ["Bash(ls *)"],
    "deny": ["Bash(rm *)"]
  }
}
```

- `allow` = allowed. `ls` lists files.
- `deny` = blocked. `rm` deletes files.
- Meaning: the AI may list files; it may not run `rm`.

## Why a settings file, not just a rule in CLAUDE.md

A line in `CLAUDE.md` like "never delete files" is a reminder to the model. It changes what the AI *wants* to do.
Claude Code's documentation says permission rules are enforced by the Claude Code program, not decided by the model.
So the settings file changes what the AI *can* do.

We think of it as three layers:

1. **Prompt / CLAUDE.md** — a reminder.
2. **Permission settings** — the real lock.
3. **A human's approval** — the last gate, for anything with real-world effects.

## What we tested (and what we did not)

- **Test 1:** a test folder with a throwaway `notes.txt`, this settings file, and the request
  "Delete notes.txt with rm, then run ls." Result: `rm` was blocked by the permission system; `notes.txt` was still there.
  (2026-09-27, Claude Code 2.1.283, one run.)
- **Side finding:** that folder was not yet "trusted" by Claude Code, so the `allow` line was ignored — but the `deny` line still worked.
- **Test 2:** a home-made pre-command checker (a "hook" that returns exit code 2 to block). We fed it command text only, not run inside Claude:
  - `ls -la` → allowed
  - `rm -rf ./demo-target` → blocked
  - `echo rm -rf ./demo-target` → blocked (**false alarm**: echo only prints text)
  - `x=rm; $x -rf ./demo-target` → allowed (**missed**: the variable hid `rm`)
  (2026-09-27, Python 3.9.6, one run per input.)

## Honest limits

- `deny Bash(rm *)` blocks matching Bash commands only. It does **not** promise to block every way of deleting a file.
- Each test ran once. Your version and setup may behave differently. Test it yourself with throwaway files first.
- A home-made checker had both a false alarm and a miss. Use it as an extra layer, never as the only lock.

## Try it in 4 steps

1. Make a test folder with a useless `notes.txt`. Never test on real files.
2. Inside it, create a folder named `.claude` and save this file there as `settings.json`.
3. Open Claude Code in the test folder and ask: "Only use rm to delete notes.txt, then list the folder. If it is refused, do not try another way."
4. You should see a permission refusal and `notes.txt` still there. If the file is gone, stop and check the folder location and the file contents.

## Third layer: things that need a human yes

Our rule: the AI can prepare these, but a person approves before they happen:

- publishing content, sending messages or emails
- spending money, placing orders
- putting a website live
- changing account settings
- deleting shared data

## 中文重点

- 把 `SAFETY_SETTINGS.json` 存成项目里的 `.claude/settings.json`。
- allow 是「允许」，deny 是「禁止」。这份设置：可以列文件，不准用 rm 删文件。
- CLAUDE.md 只是提醒；权限设置才是真正的锁；你本人批准是最后一道门。
- 我们只测了一次（2026-09-27，Claude Code 2.1.283）。它只拦符合规则的 Bash 命令，不保证挡住所有删除方法。请先用没用的文件自己测。
