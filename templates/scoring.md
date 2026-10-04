# Scoring — the fifth role

The scorer does not write and does not review facts. It answers six fixed questions about a draft, each on a 1–5 scale,
so you can compare **before vs. after** and spot weak points (for us: novelty was usually the lowest).

The questions, scales and weights are in `SCORING_RUBRIC.json`. Replace `{reader}` with a description of your own reader.

## The six questions

| Key | Question (short) | Weight |
|---|---|---|
| `hook` | Do the title and first lines make the target reader want to keep reading? | 0.25 |
| `icp_fit` | How relevant and useful is it to the target reader's goal? | 0.25 |
| `voice` | Does it sound like one real person's experience, not a neutral manual? | 0.15 |
| `clarity` | Could a beginner understand the main point and know their first step? | 0.10 |
| `share` | How likely is the reader to save it or pass it on? | 0.15 |
| `novelty` | How new is the main idea to a casual ChatGPT user? | 0.10 |

Weights add up to 1.0, so the total stays on the same 1–5 scale.

## Why probabilities, not a single number

A single number ("4") hides how sure the model is. If your model can give a probability for each answer 1–5,
use the **expected value**:

```
expected = 1·p1 + 2·p2 + 3·p3 + 4·p4 + 5·p5
```

Example: p = [0.05, 0.10, 0.20, 0.40, 0.25]
→ 1·0.05 + 2·0.10 + 3·0.20 + 4·0.40 + 5·0.25 = 0.05 + 0.20 + 0.60 + 1.60 + 1.25 = **3.70**

A model that is torn between 3 and 5 gives a different number from one that is sure it is a 4 — and that difference is useful.

Total score:

```
total = Σ weight[q] · expected[q]
```

Example: hook 4.0, icp_fit 4.0, voice 5.0, clarity 3.5, share 3.5, novelty 3.0
→ 0.25·4.0 + 0.25·4.0 + 0.15·5.0 + 0.10·3.5 + 0.15·3.5 + 0.10·3.0 = **3.93**

## Plug it into any model

You need one function: `ask(instructions, criteria, post) -> probabilities for "1".."5"`.
How you get those probabilities depends on your model:

- **A decision/classifier model that returns probabilities** — use them directly.
- **An LLM API with token log-probabilities** — ask it to answer with one digit, read the log-probs of "1".."5", and normalise.
- **No probabilities available** — ask the same question N times (e.g. 5) and use the share of each answer as p. Or use the single number and accept it is rougher.

Reference code (no keys, no network code — you write `ask` for your own provider):

```python
import json

rubric = json.load(open("templates/SCORING_RUBRIC.json"))

def ask(instructions: str, criteria: dict, post: str) -> dict:
    """Return {"1": p1, ..., "5": p5}. Implement this for your model provider.
    Read API keys from environment variables inside this function; never hard-code them."""
    raise NotImplementedError

def expected(probs: dict) -> float:
    total = sum(probs.values()) or 1.0
    return sum(int(k) * p / total for k, p in probs.items())

def score(post: str) -> dict:
    out = {}
    for key, q in rubric["questions"].items():
        instructions = q["instructions"].replace("{reader}", rubric["reader"])
        out[key] = expected(ask(instructions, q["criteria"], post))
    out["total"] = sum(rubric["weights"][k] * out[k] for k in rubric["weights"])
    return out
```

Score the **title + opening** for a long article (that is what decides whether people read on), and the full text for short posts.

## What we saw

- 16 items (8 articles, 8 LinkedIn posts), scored before and after we rewrote their titles and openings to put the surprising result first: average total went from **3.92 to 4.24**; 15 of 16 went up.
- `novelty` stayed the lowest score on most items. Clear, honest how-to content scores well on clarity and voice but rarely feels new.
- The scoring model we used was noticeably weaker on Chinese text than English. Check yours on your language before trusting it.
- Cost was tiny (well under US$0.01 for all 32 scorings at list price), so it is cheap to run on every draft.

## Limits

- A score is a second opinion, not a verdict. It does not check facts — the reviewer does.
- Do not chase the number. A post written to please the scorer can lose the human voice that made it worth reading.
- Same rubric, same model, same input length — or before/after comparisons mean little.
