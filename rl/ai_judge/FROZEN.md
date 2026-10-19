# The frozen judge prompt and settings (tag `judge-prompt-frozen-1`, Oct 19, 2026)

Nothing in this list may change until the exam is scored. `tests/test_frozen.py` fails if the prompt texts, the code that lays a prompt out, or the
settings change; a deliberate change needs a new freeze (new fingerprint in `FROZEN.json`, a new tag, and a note here). Records written under these
settings carry `"frozen": true` and the hash of the exact prompt sent (`prompt_sha256`).

| Setting | Value |
|---|---|
| Model | `claude-sonnet-5-5` (one fixed id) |
| Prompt | version `v1`: `SYSTEM` + `ANSWER_FORMAT` in `judge.py`, `COMPACT_LEGEND` for long lists |
| Plan order shown | `shuffle-id`: a fixed shuffle per position (seed = crc32 of the position id); the same on every call for that position |
| Long lists | more than 80 plans: the one-line "compact" form |
| Output cap | 8,000 tokens (the model reasons first; the answer is about 40 tokens) |
| Temperature | not set (the API default) |
| Plan list | world seed 1, at most 2,000 plans (the lister's own `--max-plans`), as tested |
| Answer | exactly `PLAN: <number>` and `REASON: <one short line>` |
| Voting | none: one call per decision |
| Fingerprint | `FROZEN.json` (`python3 judge.py fingerprint` reproduces it) |

Prices in the cost records are still the **assumed** table in `judge.py` (3 / 15 dollars per million input / output tokens); the coordinator checks the console.

## What the freeze rests on (old positions only; the exam was not opened)

All figures are at the assumed prices. Files are in `runs/`; `analyze_bias.py`, `compare_runs.py` and `vote_stability.py` reproduce the numbers.

1. **Position bias** (`runs/bias1_diag14.jsonl`, 84 calls, the 14 diagnostic positions, prompt v1): the same prompt asked twice gave the same listed plan on
   26 of 28 position pairs (93%); another order gave the same plan on 141 of 182 (77%). The choice does not gravitate to a place in the list: the first-shown
   plan was chosen 0 of 28 times in forward order. The disagreements are mostly between nearly equal plans: ending with the Stadium flip or with End the turn,
   one extra Pokémon placed on the Bench, a different Bench target for the Energy.
2. **The same on 30 positions** (the 14 plus 16 more from stage A, `runs/shape1_v1_*`, `runs/shape2_*`): three orders (forward, reverse, one fixed shuffle) gave
   the same plan in 18 of 30 positions (60%), mean pairwise agreement 71%. The same prompt again: 23 of 30 (77%); forward against reverse: 19 of 30 (63%).
3. **Voting over three orders was tried and not adopted:** one majority of three orders against another: 22 of 30 positions (73%), no better than one call
   asked again (77%), at three times the cost. The residual disagreement is the near-equal plans above, which the exam's acceptable-move rule has to absorb,
   not something an order trick fixes.
4. **Prompt v2 was tried and not adopted** (rules facts stated, plans grouped by how they end, the reason must name the rejected alternative; 90 calls on the 30
   positions): order stability fell to 40% of positions (pairwise 56%), agreement with the recorded plan 20% against 16% (not significant), 12% more cost per
   call ($0.045 against $0.040). Grouping by type did not reduce the position effect. v2 stays in `judge.py` as `--prompt v2`, unused.
5. **Compact against full form on four large lists** (225 to 479 plans, `runs/big4_compact_vs_full.jsonl`, 16 calls): the compact form needs 16,000 to 40,000
   input tokens ($0.07 to $0.14 a call) against 63,000 to 144,000 ($0.21 to $0.45) for the full form. The choices differ between forms and between orders alike:
   two of the four positions gave four different plans in four calls, one split by order (plan 2 in forward order, plan 56 in reverse, in both forms) and one
   mostly agreed. A list of hundreds of near-equal plans is noisy in either form; the compact form shows no loss and costs about a third. The threshold stays at 80 plans.
6. **Reasons:** the one-line reasons in the v1 runs are specific and checkable (they cite the card text, the unseen deck, the damage race); no change made.
7. **The frozen configuration itself** (`runs/frozen_check_diag14.jsonl`, 14 calls, $0.49): every call answered and parsed; the same listed plan as the
   recorded one in 5 of 14 positions (a development check on positions the prompt was shaped on: not evidence).
8. **Spend for the position-bias and shaping work:** 300 calls, 3.43 million input and 0.33 million output tokens, **$15.17**, against the $20 allowed; the
   earlier five smoke calls ($0.32) are not in it.

## How to read the exam results given this

- A single judge call is a random variable: on the old positions it repeats its own plan 77% of the time and agrees with another order 63-77% of the time.
  Score it against the exam's **acceptable-move sets**, not only the one recorded move, and run it twice (`--repeat 2`) to report its consistency.
- Report the judge's choice by listed plan number; two plans that differ only by a free optional step are different plans to the lister.

---
# Superseding freeze `judge-prompt-frozen-2` (Oct 19, recovery copy of the Sonnet worker, after Astra's checkpoint-2 findings)

`judge-prompt-frozen-1` (commit 3faaf691) is kept untouched. The prompt text is unchanged; these repairs make the identity exact. Old/synthetic fixtures only; no API calls.

1. **Complete action identity.** Any action without a short pg_pos name is labelled with its name plus all its arguments (`DiscardToolFromPokemon#{"in_play_idx":1,"player":1,"tool_idx":0}`), so Field Blower's different targets are different labels, are shown with their target ("Discard the Tool Heavy Helmet from the opponent's Pichu (Bench 1)") and replay tells them apart. A recorded bare name (`DiscardToolFromPokemon`) still matches every target (replay then returns all candidate keys). Tested on a synthetic position (`MINI-BLOWER`).
2. **Every generation input is pinned and checked.** World seed, plan cap, node cap and step cap are explicit in `FROZEN`, passed on every lister call, echoed by the lister, and a record is `frozen: true` only if they all match. A **capped list is not every legal choice**: live judge calls refuse it (`--allow-capped` exists for experiments and never gives `frozen: true`). In the 92 stage A positions none is capped.
3. **Baseline runners fail loudly.** Lister and replay check exit codes, problem lines, duplicate or missing ids/tags; the pg_pos runner requires exactly one free-play row per requested seed. Nothing is compared on surviving rows.
4. **Exact identity** is in `FROZEN.json`: fingerprint, settings, sha256 of `judge.py`, `plans/src/main.rs`, `plans/Cargo.lock` and of the built lister binary.

## Analysis contract (for the exam)
- **One predefined call per position** (frozen settings, repeat 0) is the primary result. Repeats (`--repeat`) only measure consistency and are reported as a separate sensitivity estimate; never pick the better run, never pool repeats to enlarge the sample.
- Uncertainty is game-clustered (positions from one game are one cluster).
- **Limitation, stated plainly:** on the 30 old positions the same prompt repeated its plan in 23 of 30 and a reordered prompt in 19 of 30. My earlier phrase that the disagreements are "between nearly equal plans" is **not demonstrated**: of the 17 positions where v1 choices differed, 6 differed in kind (attack versus draw/coin versus end turn); the rest differed within a kind. Some of that is real instability of the judge, not only near-ties.
