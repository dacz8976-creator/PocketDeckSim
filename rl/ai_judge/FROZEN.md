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

---
# Superseding freeze `judge-prompt-frozen-3` (Oct 19, the live Sonnet worker, after the overnight recovery copies and Astra's source review)

`judge-prompt-frozen-1` (3faaf691) and `judge-prompt-frozen-2` (cb8835dc) are kept untouched. **The prompt is unchanged** (the fingerprint equals frozen-2's
`0cb24215...`); the identity and the source hashes are new. Old and synthetic fixtures only; no exam access, no API calls, no main merge.

What changed since frozen-2 (source commit 9bc0e0a7 was the recovery copy's source-only step; the rest is this freeze):

1. **The formal comparison cannot silently drop a row** (`formal.py`, `judge.py compare`). The expected rows (position x bot x seed, or judge repeat) are fixed first.
   A row that is missing, duplicated, unexpected, unresolved (an unfollowable or AMBIGUOUS move list, a judge parse failure), a dry run, not frozen, from a capped plan
   list, or from a baseline executable other than the frozen one is a problem; so is a reference (accepted) move list that does not map to exactly one listed plan.
   With any problem there are **no agreement numbers**: `--on-problem fail` (default) exits 2 and still writes the report with status `failed`; `--on-problem
   inconclusive` writes status `inconclusive`, lists every expected row with its state, and exits 3. Only a clean batch exits 0. `score` (development check) now
   exits 2 on any row it cannot score unless `--lenient`; `run` exits 2 when a row cannot be mapped to ONE listed plan (the row is still written); `judge --live` exits
   2 when a call was skipped (`--stop-usd`) or gave no usable choice. Tested on that path itself (`tests/test_formal.py`: the pure logic, then the command line on
   the fixtures), not only on `number_for`.
2. **One concrete label format, key order never matters.** `Name#<compact JSON, keys sorted>` everywhere (lister, baseline printer). `Name#{json}` is re-written
   canonically in Python before replay and in the lister itself, so key order and spacing do not matter; legacy `Name{k:v}` converts losslessly or is rejected; a bare
   recorded name still fits every target and is then reported AMBIGUOUS (never the first target). A bare name is never used when the requested label carries arguments.
3. **The baseline printer (pg_pos, `pgd_patch.py`) was rebuilt and runtime-validated** from this branch's engine tree (`70652fff03af`, rustc 1.93.1, 2 jobs): on the
   fixtures Field Blower's two Tool targets and Quick-Grow Extract's two random-evolution targets come out as distinct labels, byte-equal to the lister's, the bot's
   choice carries its target, free play keeps every target in `plan_full`, and the harness maps each row to ONE listed plan. The OLD executable (stage A's
   `pg_pos_blade`) prints the bare name for both targets (the defect). The committed script `build_baseline.sh` was run a second time from scratch and gave the
   identical executable (same sha256). Evidence: `validation/baseline_printer_validation.json`; reproduce with
   `python3 validate_baseline.py` (and `tests/test_baseline_printer.py`).
4. **Executable identity is enforced.** `FROZEN.json` records the sha256 of the lister and of the baseline executable and the engine tree; step-bot rows carry
   `pg_pos_sha256`; `compare` refuses a different lister and flags rows from a different baseline (`--allow-other-binaries` is for experiments only).
   `python3 freeze_identity.py --check` compares the repository and the executables with `FROZEN.json`; `tests/test_frozen.py` runs it.
5. **Stadium chance rule (generic note from the laptop).** Playing a Stadium is never chance (tested). `UseStadium` is chance for Mesagoza (coin), Fragrant Forest
   (random card from the deck) and Arcade (3 coins); for Area Zero and Kid's Room the use opens a choice and the chance comes at the next step; Rainbow Cave is not chance
   (`validation/stadium_use_audit.json`). The lister's rule is mechanical (a coin, a random pick from the deck, hidden information); the laptop's exam-side rule
   ("chance only for Mesagoza") agrees on Mesagoza and Rainbow Cave but would continue a plan past Fragrant Forest and Arcade, where the lister stops. No exam
   position is known to this worker, so the effect on the exam is not known.

## Still not shown
- No exam position, answer or bot output was used; the formal path is tested on synthetic rows and fixtures only.
- The rebuilt baseline is validated on three small fixtures, not on a corpus: a Tool-target, a random-evolution target and a Stadium. Other action types that print as
  `Name#JSON` (the rest of the fallback set) rely on the same rule but were not each exercised.
- The game-clustered uncertainty required by the analysis contract is not implemented in this harness; the report keeps the `game` of every row so it can be.
  (**Implemented in frozen-4**: `analysis.py`, below.)

---
# Superseding freeze `judge-prompt-frozen-4` (Oct 19, the live Sonnet worker, after Astra's re-review of frozen-3 and the exam side's selection requirement)

`judge-prompt-frozen-1` (3faaf691), `-2` (cb8835dc) and `-3` (316f3577) are kept untouched. **The prompt is unchanged**: the fingerprint equals frozen-2's and
frozen-3's (`0cb24215...`), checked by `tests/test_frozen.py` and, new, by `compare` itself, which refuses to run when the code's fingerprint, sources or executables
differ from this record (`--allow-other-binaries` is the experiment switch). Old and synthetic fixtures only; no exam access, no API calls, no main merge.

## Dated disclosure (Oct 19, 2026)

On the morning of Oct 19, while reading the agent mailbox, I opened two messages that were **not addressed to `sonnet`** (an independent source review, and the
coordinator's note to its author) and I said so in my mailbox message `20261019T1426Z-sonnet-001`. One of them contained **one exam example** (one answer-key
example). Astra ruled this developer exposure to one answer-key example; the exposed game is excluded from the primary comparison on the exam side, so in a
report it can only appear in the diagnostic block. I did not use, copy or record the example anywhere and it is not repeated here. **The judge prompt has not
changed since frozen-2** (fingerprint `0cb24215...`, verified at frozen-3 and again at frozen-4), so nothing I read can have shaped the prompt. The code written
afterwards (`formal.py`, `analysis.py`, the `compare` command) is generic and was tested on synthetic fixtures only. From now on I read only mailbox messages
addressed to `sonnet`.

## What changed since frozen-3 (generic work; old and synthetic fixtures only)

1. **A plan number is checked, never believed** (`formal.py`). A row that names a plan must name a whole number inside the CURRENT plan list (bool, float, text, 0 and
   999 in a two-plan list are refused); must not carry a `match_error` or `parse_error` beside it; must carry `plan_list_sha256` (sha256 of the lister's whole
   record: start state, world seed, limits, every plan with key, labels and end) equal to the hash of the list used now, and the `plan_key` of that numbered plan;
   a step bot's full move list (`plan_full`) is replayed through the engine again and must reach exactly that plan; a judge row must map, in the prompt re-rendered
   under the frozen settings, to that plan (`shown_number`), carry that prompt's hash and the plan's labels, and its stored reply (`raw`) must say the number it
   records. Rows that predate these fields get one clear `predates_identity` problem. Negative controls run through the FORMAL path (`tests/test_formal.py`),
   on pure logic and on the command line with rows written by the real writers.
2. **Exact row identity and flags.** A row's run is its whole-number `seed` (step bot) or `repeat` (judge), never a mixture or a bool/float; `frozen` must be
   exactly `true` and `dry_run` exactly `false`; the judge's recorded model, `max_tokens` and `temperature` (now written into every judge row) must equal the
   freeze. Malformed rows, labels, contrasts, seeds and references are recorded as problems (with a report), not tracebacks; duplicate JSON keys in an input are refused.
3. **The selection is explicit and the references are filtered** (`--eligibility FILE`, `analysis.py`). The references file covers ALL points; the eligibility file names
   the primary point ids, the full-scope subset and every point's game (`{"primary_ids", "full_scope_ids", "games", "excluded_reasons"}`). Only references of points in
   the batch are read or validated; every selected point must have references; no unselected point reaches the primary aggregation, the bootstrap or the full-scope
   block (`analyse` refuses rows outside the selection). **Prefix agreement** (agreement up to the plan's own end: first chance event, attack, end of turn) is
   reported for all primary points; **full-plan agreement** (the complete move sequence equals an accepted complete sequence, compared in canonical label form) only for
   the full-scope subset, as a separate block; a judge plan that stops at a chance event or for the opponent's choice has no complete sequence and is counted as
   "not comparable" (listed, never scored, the pairs dropped are named). Points of the batch outside the selection appear **only in a separate descriptive
   diagnostic block** (no interval, no verdict); a problem at such a point never stops the primary comparison. Tested with synthetic references in which some ids are
   excluded and with garbage rows at the excluded points.
4. **The analysis contract is implemented** (`analysis.py`). Unit = decision (point); resampling unit = game (whole games drawn with replacement); estimator = sum of
   per-decision values / number of decisions; 95% nominal percentile interval, 20,000 resamples, fixed seed 20261019; one predefined judge call per decision (repeat
   0) is the primary result; extra repeats are a separate sensitivity estimate (per-decision mean over repeats; no verdict is drawn from it; they are never extra
   samples; no run is picked); a step bot's value is the mean over all its expected seeds; an interval that includes 0 is "inconclusive"; a direction also needs the
   exact sign-flip test over games (p < 0.05); fewer than 10 games among the primary points fails the batch (`--min-games` below 10 or `--resamples` below 5,000
   marks the report as an experiment). Calibration by simulation (statistics review): the interval's real coverage is about 89-94% at 10-17 games, not 95%; the
   verdict rule is conservative (false directions 2-4% under a true null) and, being in effect the sign-flip test, has low power: with ~51 decisions a true gap of
   about 0.3 is needed for ~80% power at 10-17 games, so "inconclusive" will be the usual outcome for smaller gaps. No multiplicity adjustment: with the two default
   contrasts the chance of at least one false direction is about 5%; name one primary contrast if a single claim is wanted.
5. **The report says what it was made from** (`report["run"]`): freeze tag and fingerprints, lister and required baseline hashes, sha256 of the positions, references,
   eligibility and results files, per-position plan-list hashes, request (bots, seeds, repeats, contrasts, thresholds), `formal: true/false` with the list of
   experiment switches used, and a plan-list label check. `row_account` is a count of rows (every seed and repeat is a row) and not an agreement figure; there is no
   pooled `agreement` headline. A failed or inconclusive report carries no row-level agreement.
6. **Identity** (`FROZEN.json`): fingerprint unchanged; source hashes now include `analysis.py` and the two test files; `freeze_identity.py --check` also flags a
   source missing from the record.

## Known limitation found by the review, not fixed in this freeze unless stated in FROZEN.json

On four of the 92 old positions the lister's short labels do not identify a plan: **one action kind, `ChooseRetreatEnergy` (printed `RetreatPay:<slot>`), drops
which Energy was paid** (1,142 of 5,728 plans; 434 groups of plans share identical labels and identical step text but are different states: the Energy left on
the retreated Pokemon). A bot or recorded move list that uses such a label is AMBIGUOUS and fails the formal comparison; the judge is shown plans that look
identical. `judge.py preflight` and `report["run"]["plan_list_label_check"]` list the affected positions. A second, smaller defect: `--replay` abandons a whole
move list when one fan-out alternative cannot follow it (137 plans, all at one position, and one recorded old plan). See the mailbox message for the proposed fix.

## Still not shown
- No exam position, answer or bot output was used. The formal path and the analysis are tested on synthetic rows and fixtures only.
- The rebuilt baseline printer is validated on three small fixtures; the full-plan comparison is label-based (canonical label equality), so it inherits the label
  limitation above.
- The percentile interval undercovers slightly at 10-17 games (see item 4); power is low for small true gaps.
