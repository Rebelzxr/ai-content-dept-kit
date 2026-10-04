# Reviewer prompt — 独立审稿提示词

The reviewer is the most useful role in this kit. In our first batch, the reviewer sent back **every** first draft.

Three rules make it work:

1. **Fresh.** Start a new session (or a different model) that did not write the draft. The writer cannot see its own blind spots.
2. **Read-only.** The reviewer may read everything but write only its own review file. It never "fixes" the draft itself.
3. **Exact inputs.** Give it the exact draft, the evidence (test logs, screenshots, source files) and the written standard. Not a summary.

There are two prompts: a first **audit**, then a short **recheck** after the writer fixes things.

---

## 1. Audit prompt (first review)

```text
JOB: <PIECE-ID>-AUDIT-<DATE>. You are a fresh, independent reviewer. You did not write this.
Read-only, except for one file you write: ./<piece>/AUDIT.md

DRAFT (review exactly these files):
- ./<piece>/<article or post files>
- every rendered image in ./<piece>/slides/  (look at each one)

EVIDENCE (the only source of truth for facts):
- ./<piece>/evidence/  (test logs, receipts, raw outputs, screenshots)

STANDARD:
- ./<your style guide or writing rules file>
- ./<an approved earlier piece and its review, to show the bar>

CHECK:
- Every factual sentence and every screenshot line against the evidence.
  Screenshots show only what really ran or the real file. Trims are marked. No "$" prompt before a command that was not run.
- No claim goes beyond what the evidence shows.
- Each version fits its platform (length limits, links allowed or not, tone).
- The language reads naturally to a human.
- No private data: no account or sheet IDs, no handoff-file contents, no other people's posts or handles, no client details, no keys.
- Images are readable on a phone: no overflow, no tiny text.
- Author's standing rules: <e.g. keep strong openings; put limits and caveats in the body, not the hook>.

RETURN (in <language>, under 450 words):
For each item: OK, or NEEDS FIX + the exact replacement text.
Then one line: VERDICT: PASS | REVISE
Then one line: STATUS: <what you checked and against which files>
```

## 2. Recheck prompt (after fixes)

```text
JOB: <PIECE-ID>-RECHECK-<DATE>. You are a fresh, independent reviewer. Read-only, except ./<piece>/RECHECK.md

Recheck the revised ./<piece>/ files against:
- the earlier review ./<piece>/AUDIT.md
- the writer's fix list ./<piece>/FIXES.md
- the same evidence and standard as before.

Author decisions to accept: <e.g. strong openings kept; factual fixes applied, some in simpler words — accept if equivalent>.
Only flag: a remaining factual error, a screenshot that implies something that did not run, private data,
overflow or unreadable text, or a platform limit broken.

RETURN (in <language>, under 200 words): remaining issues with exact replacement (or "none"),
VERDICT: PASS | REVISE, one STATUS line.
```

---

## 中文说明

- **要新开**：审稿的 AI 不能是写稿的那一个。新开一个对话，或换一个模型。
- **只读**：它可以读所有东西，但只能写自己的审稿文件，不准自己动手改稿。
- **给原件**：给它原稿、证据（测试记录、截图、原始输出）和写好的标准。不要给摘要。
- **逐条回**：每一项写「OK」或「需改 + 一模一样的替换文字」。
- **最后一行**：`VERDICT: PASS`（通过）或 `VERDICT: REVISE`（退回）。
- 退回后，写稿的 AI 照着改，写一份 FIXES.md，再开一个新的审稿 AI 做「复查」（上面第 2 段）。复查只找剩下的错，不重新挑风格。

## Tips

- Keep the reviewer's word limit. Long reviews hide the important line.
- "Exact replacement" matters. "Make this clearer" creates another round. A ready-to-paste sentence does not.
- The recheck should not reopen style choices the author already made. Otherwise the loop never ends.
