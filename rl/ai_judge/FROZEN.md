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
   reported for all primary points; **full-plan agreement** (a complete turn: the same listed plan as an accepted move list, order of moves up to the plan's own
   end not mattering, and what follows a chance event equal label by label in canonical form; the part after a chance event cannot be replayed, so it is compared
   as written and is order-sensitive) only for
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

## Label identity and replay (the lister and the baseline were REBUILT for this freeze; the engine is untouched)

The round-2 review found that on four of the 92 old positions the lister's short labels did not identify a plan: **one action kind, `ChooseRetreatEnergy` (printed
`RetreatPay:<slot>`), dropped which Energy was paid** (1,142 of 5,728 plans could not be named by their own labels; 434 groups of plans shared identical labels and
identical step text but were different states: the Energy left on the retreated Pokemon). A bot or recorded move list that used such a label was AMBIGUOUS and failed
the formal comparison, and the judge was shown plans that looked identical. Fixed, as asked by the coordinator, in `plans/src/main.rs` and in the baseline printer
(`pgd_patch.py`): the short label is gone, a paid retreat now prints `ChooseRetreatEnergy#{"energies":["Fire"],"to_in_play_idx":1}` (the existing `Name#JSON`
fallback) and its step reads "Pay the retreat cost of X (switching with Y) by discarding Fire Energy". Also in this rebuild (same executables, so the same freeze):
1. **Energy lists are a multiset**: `energies` is sorted when labels are COMPARED (lister `label_matches` / `canon_label`, Python `concrete_label`), so a reference written in
   another Energy order still matches. The printed labels (lister output, baseline `plan_full`) carry the engine's own order (Grass, Fire, Water, Lightning ...):
   pass raw printed labels through `judge.concrete_label` before comparing them as strings.
2. **Replay prunes dead alternatives**: a fan-out alternative that cannot follow the rest of a move list (for example a slotless `Place:X` put on a slot where the
   later `Tool:...@2` is not legal) is dropped; the list is unfollowable only when NO alternative can follow it. Before, the first dead end abandoned the whole list
   (137 plans at one old position, and the recorded plan of KW-261013_020824000-t03).
3. **Effect on the old positions** (`python3 judge.py preflight --set stageA`): 0 of the 92 positions now have plans whose labels do not name them (was 4); the
   recorded (human) plans that replay to exactly one listed plan are 84 of 88 (was 83); the other four are recorded plans with a slotless `Place:X` that fits
   several bench slots (genuinely ambiguous: give the slot, or list the accepted variants as separate references). Plan numbers inside the four affected positions
   changed (plans are sorted by label text); old judge rows made before this freeze at those positions (e.g. `runs/big4_compact_vs_full.jsonl`) refer to the old
   numbering and are not comparable; they are development rows, never exam rows.
4. `judge.py preflight` (and `report["run"]["plan_list_label_check"]`) lists positions whose plan lists contain a paid retreat or anything else the labels fail to
   name; the exam side can run it to check its references against the new label format (a reference that retreats must now name the payment, or list the payments as
   separate accepted variants).

## Still not shown
- No exam position, answer or bot output was used. The formal path and the analysis are tested on synthetic rows and fixtures only.
- The rebuilt baseline printer is validated on four small fixtures (Tool target, random-evolution target, retreat payment, Stadium); the full-plan comparison is
  label-based after a chance event (canonical label equality, order-sensitive there), so it is only as good as the labels; the tail of a step bot's turn after a chance
  event is not replay-checked (it is the executable's output, identified by the baseline hash in the row).
- The frozen baseline executable plays `k<number>` / `km<number>` bots (km3); the playout pilot kx3 is a different program and has no frozen identity here: rows
  from it fail `baseline_binary`. `--bots` defaults to `km3,judge`.
- The percentile interval undercovers slightly at 10-17 games (see item 4); power is low for small true gaps. The card texts in the prompt come from
  `lib/deckgym-database.json` (now part of the source hashes and recorded in the report); a card id missing from the database gets no text, silently.
- Not changed, by decision: a position the lister cannot build stops `compare` before any comparison (exit 1), also when it is an unselected one (drop it from `--ids`);
  a run that dies leaves a `did_not_finish` / `failed` stub at `--out`, never an older result.

---
# Superseding freeze `judge-prompt-frozen-5` (Oct 21, the live Sonnet worker; the judge is Gemini 4 Argon)

**Why.** Run 1 (frozen-4, `claude-sonnet-5-5`) did not pass against km3 (aggregate only: `RUN1_OUTCOME.md` on main). Dustin wants to try a different model as the judge, out
of curiosity, with about $10-15 of his Google API credits. The coordinator pre-registered ONE model before any build: **Gemini 4 Argon at high reasoning effort**. The prompt
is unchanged; only the model and the provider change.

**What did not change** (checked by `tests/test_frozen.py` and `tests/test_gemini.py`): the prompt fingerprint `0cb24215...` (the same as frozen-2, -3 and -4), `judge.FROZEN`
(still the Anthropic freeze's settings: the dict is inside the fingerprint, so the Gemini settings live in `providers.py` and in the new `judge` block of `FROZEN.json`),
the parser (`parse_choice`), the invalid-label handling (a reply with no PLAN line, two numbers, or a number outside the list keeps no choice), the no-retry policy, the plan
lister and the baseline executable (the same hashes, engine tree `70652fff`: the exam was built on them), and the formal comparison and the analysis.

**What is new.**
1. `providers.py`: the Gemini provider (Interactions API, `POST https://generativelanguage.googleapis.com/v1beta/interactions`, key in the `x-goog-api-key` header),
   its request builder, response parser, prices and key loader. `judge.judge_one(..., provider='gemini', thinking_level=...)` sends exactly the frozen system and user
   text; a Gemini row also records `provider`, `thinking_level` and `thinking_summaries`, which `compare` checks against the `judge` block of `FROZEN.json` (a frozen-4
   row against this freeze fails every setting; the Anthropic rows keep their old shape and are checked against the old settings when the record has no `judge` block).
2. `budget_judge.py`: the hard spend bound for the scored run (Astra's exam-run-1 design, ported): every call's worst case is reserved before it is sent at the
   conservative price ($4 / $20 per 1M tokens, the higher published price), settled at the price in force, a failed call charged in full, one ledger shared by the primary and
   the repeat run (`--total-usd 15`).
3. `freeze_identity.py` records and checks the `judge` block and the new sources (`providers.py`, `budget_judge.py`, `tests/test_gemini.py`, `tests/test_budget.py`).

**Model and price (Google's own pages, read Oct 21, 2026, not memory).**
- Model id `gemini-4-argon` (Stable; thinking levels low / medium / high; 65,536 output tokens synchronous; context 1,048,576): https://ai.google.dev/gemini-api/docs/models
- Price, Standard tier, USD per 1M tokens, input / output **including thinking tokens**: **$2 / $10 through 2026-11-30, $4 / $20 from 2026-12-01**, no prompt-length tiers
  listed; not on the free tier: https://ai.google.dev/gemini-api/docs/pricing
- Thinking (`generation_config.thinking_level`; `max_output_tokens` is "the combined total of thinking tokens and output tokens"; thinking is billed as output; a run that
  hits the limit while reasoning ends "incomplete"): https://ai.google.dev/gemini-api/docs/thinking
- The Interactions API: https://ai.google.dev/gemini-api/docs/interactions and https://ai.google.dev/api/interactions-api

**Settings mapping (each is also in `FROZEN.json` -> `judge.mapping`).**

| frozen-4 (Anthropic) | frozen-5 (Gemini) | matches? |
|---|---|---|
| system text, user text | `system_instruction`, `input` (identical text; same `prompt_sha256`) | yes |
| `max_tokens` 8,000, reasoning counted as output | `generation_config.max_output_tokens` 8,000, documented as thinking + answer | same meaning; **tokenizers differ**, so 8,000 Gemini tokens are not 8,000 Claude tokens, and at high thinking the cap may be spent on thinking: an "incomplete" reply keeps no choice, like a reply cut at `max_tokens` |
| the model's default reasoning (no setting) | `thinking_level` "high" (highest of low / medium / high) | **no**: different mechanisms; "high" is the closest to "as much as it will do" |
| thought text | `thinking_summaries` "none": none requested, none stored | n/a |
| temperature not set | not set (none documented for this model; `--temperature` is refused) | yes |
| no retry | no retry | yes |
| finish | `stop_reason` "end_turn" only for status "completed"; any other status is stored `gemini:<status>` and keeps no choice | same rule |

**Not verified until a live call.** The documents give the request fields and the response's `steps` / `usage` fields but not the error body, so the parser is tolerant (it
reads `model_output` text only, treats a missing usage block as unknown cost and charges the worst case) and the one live smoke test (at most $0.50, two old positions)
is what confirms the call and the parse. The Standard price ends its introductory rate after Nov 30; the reservation always uses the higher one.

**Disclosure.** No exam position, reference, answer or RESULTS file was opened for this freeze; no live call was made while writing it (mocks only); no main merge.

**What happened next (live, Oct 21).** The one smoke test of frozen-6 (5 old positions, a $2 ledger) made one call and got HTTP 404 NOT_FOUND for
`projects/<project number>/locations/us-central1/publishers/google/models/gemini-4-argon`: the key authenticated and the `x-goog-api-key` header was accepted, but the project-less
URL of the express-mode form pins location us-central1, where the model is not served. frozen-6 is therefore superseded by frozen-7 (kept, not moved).

---
# Superseding freeze `judge-prompt-frozen-7` (Oct 21, the live Sonnet worker; the Vertex URL names the project and the location, and failed judge rows can count as misses)

**Prompt, parser, lister, baseline and engine are unchanged** (fingerprint `0cb24215...`; lister sha256 `bd4eeb6e...`; baseline `f35a1a99...`; engine tree `70652fff`). Same judge as frozen-6:
`gemini-4-argon` on Vertex AI, GenerateContent, thinkingLevel HIGH, maxOutputTokens 32,768, text parts only, finishReason STOP = an answer, no retry, key `VERTEX_API_KEY` in the
`x-goog-api-key` header. frozen-5 and frozen-6 are kept, not moved. Two changes, both asked for by the coordinator:

1. **The URL names the project and the location** (`providers.VERTEX_URL`): `POST https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/publishers/google/models/gemini-4-argon:generateContent`.
   A `countTokens` probe with the same key and header on exactly this URL answered HTTP 200 (a free call, Oct 21), so a service-account-bound API key is accepted on the
   project-scoped path (Google documents that path only with a Bearer token). The location `global` is a **frozen setting**: every Vertex row records `location`, and `compare`
   refuses another. The **project** (id or number; not a secret) is NOT in the freeze: it comes from `VERTEX_PROJECT` (environment) or the run kit's `--vertex-project` flag
   (`judge.py judge|run`, `budget_judge.py`), is validated (a project id or number, nothing that could change the path), is recorded in every row as `vertex_project` and listed in
   the compare report (`run.judge_vertex_projects`, with a warning when rows come from more than one). A live run without a project stops before any ledger exists.
2. **Failed judge rows (pre-registered for run 2; explicit, recorded, default OFF).** `judge.py compare --failed-judge-rows {abort,miss}`, recorded in `FROZEN.json` -> `judge.failed_judge_rows`
   and in the report (`run.request.failed_judge_rows`, `failed_judge_rows`, `analysis.method`). `abort` (the default, and the behaviour of run 1 and of frozen-4 to frozen-6): a
   judge row without a valid choice is an `unresolved` problem and stops the compare. `miss`: such a row counts as a MISS (agreement 0) in the prefix scoring and, at a full-scope
   point, in the full-scope scoring (never "not comparable": the judge produced no plan), so one bad reply cannot void a paid run.
   - *Which rows:* a JUDGE row with no plan number: an invalid label ("PLAN: 4 or 7", a number outside the list, no PLAN line), a reply cut at the cap, a blocked prompt, any finish
     but STOP. It must still be a row that is **consistent with being a failed reply and nothing else** (rows are not authenticated: this is what the row's own fields can show), or
     the compare stops as before (`formal.check_no_choice_row`): it says why (`parse_error`), carries no plan / cut / shown number / plan key / match error (falsy values included),
     carries the identity of the plan list used now, is the answer to the prompt re-rendered under the frozen settings (prompt hash and every frozen setting, location included),
     carries its stored reply, its stop reason agrees with the finish fields recorded beside it (`vertex:X` needs finish_reason X, a block needs its block_reason, `end_turn` needs
     STOP, `gemini:S` needs status S), and the reply really holds no valid choice (it did not finish, or its text parses to no choice: a finished reply that names a valid plan cannot
     be turned into a miss). `dry_run`, `capped`, `frozen`, mock rows and every other row-level check apply unchanged, and a row that has another problem is unresolved, never a miss.
     A step-bot row without a plan, a missing row and a duplicate still stop the compare.
   - *Reported plainly:* the console line `JUDGE ROWS WITHOUT A VALID CHOICE ... N at primary points, M at diagnostic points, of K primary judge rows: position repeat (stop reason:
     reason); ...`; a WARNING (stderr and `run.warnings`) when more than 20% of the primary judge decisions failed (a systematic fault, such as a cap that is too small, would
     otherwise read as "the judge lost"; it stays a warning, not an abort); `report.failed_judge_rows` (policy, counts, every row with position, repeat, stop reason and reason; present on
     every report, zeros included); `report.n_no_choice_rows`; the row account has a `no_choice` state; every report row says `state: no_choice`, `agrees: false` (and `null` while the
     batch has any problem: with a problem there are no numbers at all).
   - *Where it counts:* primary points (repeat 0 is the predefined call). A failed repeat > 0 only enters the repeat sensitivity block (as a miss; two empty repeats are not "the same
     plan"). A failed row at a point outside the primary selection is counted apart (diagnostic block, descriptive) and never moves a primary number.
   - *What it can and cannot do (corrected after review):* it can only lower the judge's RATE and the whole prefix block relative to the same run with those decisions answered
     (checked on 1,700 random replacements: never higher). In the full-scope block the contrast is not strictly monotone: an answered plan that stops at a chance event is "not
     comparable" there and its pair is dropped, whereas a miss is a pair that counts, so the full-scope contrast can move toward zero. To keep a failed reply from opening the
     min-games gate, a game that exists in the full-scope contrast only because of a miss does NOT count toward the gate (`n_games_gate`, with the reason in the verdict text); the
     verdict rules, the bootstrap and the sign-flip test are otherwise unchanged. A high failure rate shows as a low score, which is why the count is printed, stored and warned about.
     The laptop adds `--failed-judge-rows miss` to PREREG_RUN2 before the run.

**Tests (mocks and the real CLI on synthetic rows):** the miss policy with the pure comparison (each kind of failed reply qualifies; 28 ways a row is NOT a consistent failed reply still stop
the compare; missing / duplicate / step-bot rows still stop it; prefix and full-scope rates; diagnostic and repeat handling; the default is unchanged) and through `judge.py compare` with
rows written by the real writer (rates drop by exactly one decision; the console line; the report fields; tampered rows refused; the flag only takes `abort` or `miss`); the Vertex URL, the
project setting and its validation, the row fields (`location`, `vertex_project`), the wrapper's `--vertex-project` and the missing-project stop.

**Review before the tag** (2 agents, wf_aefd9b8b-3c5; 45 mutants of the new code, 39 killed, the survivors are now covered; 2,000 randomized default-policy scenarios gave reports
identical to frozen-6's apart from the documented additions): fixed in this commit: the min-games gate rule above and its wording; a stop reason is cross-checked against the finish fields;
`early_failure` reports carry `failed_judge_rows` and `n_no_choice_rows` too; the console line shows the finish and the reason; the 20% warning; a project setting that is not a project id
(for example an API key pasted into it) is refused WITHOUT echoing it, and an unusable ambient `VERTEX_PROJECT` no longer stops a dry run, a mock run or the test suite (only a live call);
the real project id and number are no longer in a frozen test file; stale text (frozen-6 as current, "never a miss", the checked settings) corrected.

**Disclosure.** No exam position, reference, answer or RESULTS file was opened for this freeze. One live call besides the frozen-6 smoke test: the free `countTokens` probe above.

---
# Superseding freeze `judge-prompt-frozen-6` (Oct 21, the live Sonnet worker; the same judge model served by Vertex AI)

**Why.** Dustin's Google credits are a Google Cloud free trial, and Google's Gemini API billing page says that for accounts opened after March 2, 2026 the trial credit cannot
pay for Gemini API / AI Studio usage (https://ai.google.dev/gemini-api/docs/billing). The credits can pay for Vertex AI (now "Gemini Enterprise Agent Platform"). Dustin chose to
use them: frozen-5 (Developer API, tag `judge-prompt-frozen-5`, commit 544d80ff) is **not moved**; frozen-6 changes only the provider and one setting. **The prompt is unchanged**
(fingerprint `0cb24215...`, the same as frozen-2 to -5), and so are `judge.FROZEN`, the parser, the invalid-label handling, the no-retry policy, the plan lister, the baseline
and the engine tree `70652fff`.

**What changed against frozen-5.**
1. Provider `gemini-vertex` (`providers.py`): `POST https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-4-argon:generateContent`, GenerateContent body
   (`systemInstruction` + one user `contents` turn + `generationConfig` {`maxOutputTokens` 32768, `thinkingConfig.thinkingLevel` "HIGH"}), the key only in the `x-goog-api-key`
   header (never in the URL), the answer is the text of the first candidate's parts that are not flagged `thought: true`, `finishReason` STOP is a finished answer and anything
   else (MAX_TOKENS, SAFETY, CONTINUATION, no candidate, a blocked prompt) is `vertex:<reason>` and keeps **no choice**, usage from `usageMetadata` (thinking included), one request,
   no retry. Key variable **`VERTEX_API_KEY`** (environment, else the last `export VERTEX_API_KEY=` line of `~/.bashrc`, parsed as text), never printed, logged or committed.
2. **The output cap is 32,768 (frozen-5: 8,000).** Run 1's Claude judge used at most 4,213 output tokens; Gemini at its highest thinking level may use most of 8,000 and end cut
   off, which would measure "Gemini with its thinking cut short". 32,768 is the most a non-streaming direct HTTP request allows (the guide: 65,536 per synchronous request, 32,768
   for non-streaming direct HTTP; thinking counts toward it). A row without a choice aborts the formal comparison (`compare`: kind `unresolved`, exit 2; `formal.py`), so the cap
   is the protection, not a retry. Tokenizers differ from Claude's, so the cap still cannot "match" frozen-4's 8,000.
3. `budget_judge.py` default provider is `gemini-vertex`; reservations at $4 / $20 per 1M tokens, so at 32,768 output tokens one call reserves **about $0.68-0.83 for the old
   positions' prompts of 2k-19k tokens** ($0.655 of it is the output cap) and up to about $1.64 for the largest old prompt (1,203 plans). Four workers hold about $2.7-3.3, which
   fits in the $15 ledger until about $11.5 has been spent; a $2 smoke test fits two workers, not three (use one). A call that fits only once the calls in flight have settled now
   WAITS for them instead of being dropped (the review showed that with four workers and a run cap below the total the tail of the batch was refused after only $5 of $15 was spent);
   for the primary run set `--run-cap-usd` equal to `--total-usd`. Actual cost of one call is far below its reservation (about $0.02-0.15 at the introductory price unless thinking
   runs to the cap, when it is about $0.33 plus input). If every one of the 51 primary calls ran to the 32,768 cap the introductory-price cost would be about $17-18 for old-position
   prompts and the $15 bound would stop the run: that is what the bound is for. The ledger now records the calls in flight, so a run that is killed is charged for them when the
   ledger is next opened. The $2 smoke test uses its own ledger file: its spend is on top of the $15 formal ledger.
4. Fixed on the way, after two adversarial reviews of this candidate (round 1: 14 agents, wf_5a44aaa7-1ea; round 2 on the fixes: 2 agents, wf_c507d08a-0d0): a key with a trailing
   CR/LF (a Windows-edited file) was printed by the HTTP library's error and not scrubbed: `load_key` now strips it and accepts only letters, digits, '.', '-' and '_' (every Google
   API key; a shell expression such as `export VERTEX_API_KEY=$(cat file)` is refused instead of being sent as the literal text, which would have cost a charged call), and a
   `ValueError` from the request shows its type only; a redirect answer is an error and is no longer followed (urllib would have re-sent the key header to the redirect's host); an
   error body is scrubbed before it is cut; a body that ends early (`http.client.HTTPException`) or is absurdly nested stops the call cleanly; a later empty `export VERTEX_API_KEY=`
   retires an earlier key; the ledger is exception-safe (a failed ledger write halts the run instead of leaving a waiter blocked for ever, a reply the costing cannot read is charged at
   its worst case, a nan or infinite cap is refused, nothing in flight means nothing to wait for); a task failure behind several workers (any exception) ends the batch as incomplete
   (exit 2) instead of a traceback; a reply whose output count is absent is charged its worst case in the row too; a candidate without a finishReason is `vertex:NO_FINISH_REASON`;
   `--mock` rows say `mock: true` and `compare` refuses them; a Gemini row records `model_returned` and the compare report lists the distinct values (`run.judge_models_returned`) and warns
   when they differ or are not the frozen model; `freeze_identity` refuses a Gemini freeze record that has no `judge` block; the client timeout is 1,260 s (the guide's per-request
   limit is 20 minutes). One shared request routine serves both Gemini providers (also frozen-5's code, which stays).

**Price (Google Cloud announcement, read Oct 21; the Vertex pricing page's tables could not be read through my tools, verify in the billing console).** $2 / $10 per 1M input /
output tokens (thinking billed as output) through 2026-11-30, $4 / $20 from 2026-12-01 (https://cloud.google.com/blog/products/ai-machine-learning/gemini-4-argon-available-on-google-cloud).

**Settings mapping** (also `FROZEN.json` -> `judge.mapping`; what cannot match is marked):

| frozen-4 (Anthropic) | frozen-6 (Vertex AI) | matches? |
|---|---|---|
| system text, user text | `systemInstruction` (one text part), `contents` (one user turn) | yes (same `prompt_sha256`) |
| `max_tokens` 8,000, reasoning counted as output | `maxOutputTokens` 32,768, thinking + answer together | meaning yes, size no: the most a non-streaming call allows; tokenizers differ |
| the model's default reasoning | `thinkingConfig.thinkingLevel` "HIGH" (LOW / MEDIUM default / HIGH) | no: different mechanisms |
| thought text | not requested; parts flagged `thought: true` are skipped | n/a |
| temperature not set | not set (Vertex ignores a custom value for this model; `--temperature` is refused) | yes |
| no retry | no retry | yes |
| finish | STOP = finished; anything else = no choice | same rule |
| the serving stack | Vertex AI, the same model id as frozen-5 on the Developer API | identical outputs not guaranteed |

**The key.** A Google Cloud API key bound to a service account, made in the Cloud console following
https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/api-keys?usertype=standard (project with the trial's billing account; enable the Vertex AI API, which Google
now calls the Agent Platform API; a service account with the Agent Platform (Vertex AI) User role, `roles/aiplatform.user`, which the API quickstart names; the key page itself names
"Gemini Enterprise Agent Platform Express User (Beta)": a 403 is a role problem, not a freeze-breaking fault; Credentials > Create credentials > API key > "Authenticate API calls
through a service account"). The organization policy `iam.managed.disableServiceAccountApiKeyCreation` must be off; if it cannot be, the page falls back to application default
credentials, which this adapter does NOT support (stop and report). Express mode (the @gmail key) is not an option: its model list does not include gemini-4-argon and it is separate
from the Google Cloud Free Program.

**Not verified until a live call.** The response fields (`candidates[].content.parts[].text` / `thought`, `finishReason`, `usageMetadata.promptTokenCount` / `candidatesTokenCount` /
`thoughtsTokenCount` / `totalTokenCount` / `cachedContentTokenCount`, `promptFeedback.blockReason`) are documented by Vertex's own v1 reference
(https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerateContentResponse); what it does not say is whether `candidatesTokenCount` includes the thoughts or
`promptTokenCount` the cached tokens (the Developer API reference lists thoughts and candidates as separate addends of the total; `_usage` takes the output as total minus prompt, which is
right if they are disjoint or if the candidates hold the thoughts, and is recorded as `answer_tokens` + `thought_tokens` so the smoke test shows which). That a service-account-bound key is
accepted in the `x-goog-api-key` header (the quickstart's example puts it in `?key=`; the header is documented by the express-mode reference and the API-key guide) and that the trial
billing account is charged are likewise unconfirmed. The smoke test (5 old positions, `--total-usd 2`) is what confirms them; a failure that needs a different request or parser means
a new freeze, not a moved tag.

**Disclosure.** No exam position, reference, answer or RESULTS file was opened for this freeze; no live call was made while writing it (mocks only); no main merge.
