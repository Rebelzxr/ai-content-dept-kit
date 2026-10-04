# ai-content-dept-kit

**How one person runs a small content department with 5 AI roles — the templates, prompts and tools we actually use.**

[中文版 README](README.zh.md)

We build in public at DAINER.AI: we teach people to use AI as co-workers, build their own agents, and coordinate
several agents through one main agent. This kit is the reusable part of our own content pipeline. We share it while we learn.

It is not an app. It is a folder of plain-text templates and two small scripts. Copy what helps, ignore the rest.

---

## The 5 roles

| # | Role | What it does | What we used |
|---|---|---|---|
| 1 | **Main agent** | Coordinates the others, keeps the plan, and posts — **only after a human approves** | Claude Code |
| 2 | **Writer** | Drafts the article and the platform versions | Claude Code, with a written style guide |
| 3 | **Maker** | Runs the real tests, takes screenshots, makes images and slides | Codex (incl. its image tool) + the scripts in `tools/` |
| 4 | **Reviewer** | A **fresh, read-only** session that checks every line against the evidence | A new Codex session each round |
| 5 | **Scorer** | Rates the draft on 6 fixed questions, 1–5 | A decision/scoring model |

The human (you) does not disappear. You set the direction, approve anything that goes out, and decide what is worth saying.

## The 7 steps

1. **Research** — find the question your reader actually has. Use `templates/STRUCTURE_PROMPT.md` to learn from good posts without copying them.
2. **Write** — give the writer a 3-line brief (`templates/TASK_BRIEF_3LINE.md`): *Done looks like / Check in when / Stop if*.
3. **Test + screenshots** — the maker runs the real thing and saves raw outputs to an `evidence/` folder. Screenshots are built from that real text (`tools/gui_frames.py`).
4. **Independent review** — a fresh reviewer checks the draft against the evidence (`templates/REVIEWER_PROMPT.md`). It answers PASS or REVISE with exact replacement lines. Fix, then recheck.
5. **Package per platform** — one approved article becomes native versions: X Article + cover, Instagram/LinkedIn carousel, LinkedIn post, Threads. Each fits its platform's limits.
6. **Human approval + scheduled upload** — you approve the final pack. Only then does the main agent schedule or post it. Nothing goes out on its own.
7. **Weekly review** — score before vs. after (`templates/SCORING_RUBRIC.json` + `templates/scoring.md`), note what worked, and write a handoff (`templates/HANDOFF.md`) for next week.

## What is inside

```text
ai-content-dept-kit/
├── README.md / README.zh.md
├── LICENSE                      MIT
├── templates/
│   ├── HANDOFF.md               5-heading handoff (Chinese + English)
│   ├── TASK_BRIEF_3LINE.md      Done looks like / Check in when / Stop if
│   ├── REVIEWER_PROMPT.md       fresh read-only reviewer: audit + recheck prompts
│   ├── SAFETY_SETTINGS.json     minimal Claude Code permissions (deny rm)
│   ├── SAFETY_SETTINGS.md       what it does, what we tested, limits
│   ├── AGENTS_SHARED.md         one AGENTS.md for every agent + the subfolder caveat
│   ├── STRUCTURE_PROMPT.md      learn a post's structure without copying it
│   ├── SCORING_RUBRIC.json      6 questions, scales, weights
│   └── scoring.md               expected-value math + how to plug in any model
├── tools/
│   ├── gui_frames.py            carousel slides (1080×1350) + PDF
│   ├── article_cover.py         X Article cover (1500×600) + code card
│   ├── test_security.py         input, path and temp-file safety checks
│   └── README.md
├── art/                         RISO-style AI art made by DAINER.AI (cover, spots, devices)
└── examples/
    ├── slides.sample.json       a sample deck spec
    └── output/                  the real render of that sample
```

## Quick start

**1. Copy the rules into your project**

```bash
cp templates/SAFETY_SETTINGS.json your-project/.claude/settings.json   # create .claude/ first
```

Then set up one shared rulebook: `AGENTS.md` for the rules, and a `CLAUDE.md` whose first line is `@AGENTS.md`.
See `templates/AGENTS_SHARED.md`.

**2. Brief one post in three lines** — `templates/TASK_BRIEF_3LINE.md`.

**3. Review it with a fresh session** — paste `templates/REVIEWER_PROMPT.md` (filled in) into a new chat or a new CLI session that did not write the draft.

**4. Render the sample slides**

```bash
pip install pillow numpy
python3 tools/gui_frames.py examples/slides.sample.json examples/output
python3 tools/article_cover.py G02 examples/output "KICKER" "Title line 1" "Title line 2" "series" templates/SAFETY_SETTINGS.json
```

Needs Google Chrome. Not on macOS? Set `CHROME_PATH`. Details in `tools/README.md`.

**5. Approve, schedule, and review weekly** — use your own scheduler; score with `templates/scoring.md`; hand off with `templates/HANDOFF.md`.

## What we learned

- **The reviewer sent back every first draft.** In our first batch of 8 social packs, the fresh reviewer answered REVISE on all 8. After one round of fixes, all 8 passed the recheck. A writer cannot see its own mistakes; a second pair of eyes is not optional.
- **A rule in a prompt is a reminder, not a lock.** "Never delete files" in `CLAUDE.md` changes what the AI wants to do. One `deny` line in `.claude/settings.json` blocked `rm` in our test. (Claude Code 2.1.283, one run.)
- **A home-made safety checker had one false alarm and one miss** out of four inputs. Use it as an extra layer only.
- **Claude did not read our `AGENTS.md` until `CLAUDE.md` imported it** — and when we started from a subfolder, the import did not load. Check with `/context`. (Claude Code 2.1.284, one run each.)
- **Putting the surprise first moved the scores.** Our scorer showed the surprising results were buried below the opening. After we rewrote titles and openings across 16 pieces, the average score went from 3.92 to 4.24, and 15 of 16 went up. Novelty stayed the weakest question.
- **Screenshots must come from real runs.** The reviewer checks every screenshot line against the raw output. A `$` in front of a command means it really ran.

## Honest limits

- This is **one person's setup, one month, one batch**. Your results will differ.
- Each test ran **once**, on specific versions (Claude Code 2.1.283 / 2.1.284, Python 3.9.6, macOS). Re-test on yours.
- The `deny` rule blocks matching Bash commands only — not every way to delete a file.
- The scoring model we used was weaker on Chinese than on English. A score is a second opinion, not a fact check.
- The kit does **not** post or schedule anything for you. You connect your own scheduler, and a human approves every post.
- The renderers need Chrome and (for fonts) internet access. Only tested on macOS.
- Review rounds cost time. Plan for at least one REVISE per piece.

## License

MIT — see `LICENSE`. Copyright (c) 2026 DAINER.AI.
You may use, change and share the templates, scripts and the included art, including commercially. Keep the license notice.

## Follow along

We share what we test as we build. If this helped, share it with someone who is setting up their own AI team.

- X: [@Dainer_Jun](https://x.com/Dainer_Jun)
- Web: [dainer-ai.biz](https://dainer-ai.biz)
