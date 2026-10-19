# AI plan judge: harness (step 2 of rl/results/weekly_review_2026-10-18/PLAN.md)

Oct 18-19, 2026 (Sonnet 5.5 session "Opus agents progress", for the coordinator). Built, shaped and tested on the OLD positions only (stage A's 92 and the
diagnostic's 14). The laptop's exam folder and branch were not opened. No engine rules changed: `plans/` is a separate crate that calls the engine
by path (like `rl/strength`), and `engine/` is untouched. **The prompt and settings are frozen since Oct 19** (tag `judge-prompt-frozen-1`, `FROZEN.md`);
nothing here has been scored on fresh positions.

## What is here

| File | What it does |
|---|---|
| `plans/` (Rust, `judge_plans`) | Lists the engine's legal **whole-turn plans** of a pg_pos position; replays a bot's or a recording's move list into the same list |
| `judge.py` | Prompt, parser, API call, cost record, bot runner (`km3`, `kx3`, `judge`), shared result format, scoring against recorded plans |
| `tests/` | 33 tests: parser, prompt whitelist, cost, the plan list (count, dedupe, chance cut-off, no leakage, cap, replay), the live path with a fake API, the freeze |
| `FROZEN.md`, `FROZEN.json` | The frozen prompt and settings, the measurements behind them, and the fingerprint the freeze test checks |
| `runs/` | Every live run of the shaping work (position bias, prompt v1 against v2, voting, compact against full, the frozen check): 300 calls, raw replies, costs |
| `analyze_bias.py`, `compare_runs.py`, `vote_stability.py` | Reproduce the position-bias, version-comparison and voting numbers from `runs/` |
| `results_old_positions/` | Plan counts, prompt sizes, coverage of the recorded plans, km3 and kx3 on the 14 diagnostic positions |
| `smoke/` | The five live smoke calls (raw replies, tokens, cost) |

## Run it

```bash
# one-time build (separate crate, engine by path; one cargo at a time, 2 jobs, low priority)
cd rl/ai_judge/plans && CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=$HOME/ai_judge_target nice -n 19 cargo build --release --offline
export JUDGE_PLANS_BIN=$HOME/ai_judge_target/release/judge_plans        # default path is the same

cd rl/ai_judge
python3 judge.py plans --set diag14                       # how many whole-turn plans each position has (also --set stageA, --ids ...)
python3 judge.py prompt --id KW-261012_225319000-t06 --show      # the prompt and its token estimate; nothing is sent
python3 judge.py judge --set diag14 --out out.jsonl       # DRY RUN: prints prompt sizes, sends nothing
python3 judge.py judge --id <ID> --live --max-calls 1 --out out.jsonl     # a real call; --live is required, --max-calls caps them
python3 judge.py run --bot km3 --set diag14 --seeds 1,2,3 --out out.jsonl # any bot through pg_pos (PG_POS_BIN), same result format
python3 judge.py run --bot judge --set diag14 --out out.jsonl             # the judge through the same runner
python3 judge.py coverage --set stageA                     # is each recorded plan one of the listed plans? (completeness check)
python3 judge.py score --results out.jsonl                 # same listed plan as the recorded one (old positions only)
python3 -B -m unittest discover -s tests -v                # the tests (plan-list tests need the built binary and are skipped without it)
```

The key is read from `ANTHROPIC_API_KEY` or the last `export ANTHROPIC_API_KEY=` line of `~/.bashrc` and is never printed or stored.
The model is fixed at `claude-sonnet-5-5` (`--model` exists for experiments and makes the record `frozen: false`). With no flags, `judge` and `run --bot judge`
use the frozen settings (`FROZEN.md`); `--repeat N` asks the same prompt N times, `--workers W` runs calls side by side, `--stop-usd X` stops starting calls at
X dollars, `judge.py spend FILE...` totals the recorded cost.

## 1. The plan list (from the engine's full legal moves, never a bot's candidates)

From the position the player's own **observation** is built (`PlayerObservation`: the opponent's hand and deck are only counts, the player's own
deck is only a set of cards, no order), then the engine's `search_state` gives one fixed hypothetical deck order. A breadth-first search over
`generate_possible_actions` walks every legal action. km3 is not involved anywhere in the list. A **plan** is a path of actions:

- **It ends** at an **attack** (the turn ends; its result is the engine's own forecast of the attack, with the chances of each result if it has coins), at
  **End the turn**, or at its first **chance event**. The chance event is the last step of its plan and is not carried out.
- **A chance event** is any action that (a) the engine marks as depending on information the player cannot see or cannot price, (b) has more than one
  branch in the engine's exact forecast (a coin, a random pick), or (c) changes the order of the player's own deck (a draw, a search, a shuffle). So:
  Professor's Research, Poké Ball, Copycat, Mesagoza/Stadium coin flips, coin-flip Abilities. After it the judge decides again, with the result visible.
- **Plans that reach the same visible state are one plan**: the key is the engine's whole `State` (hands, discard piles and attached Energy put in a fixed order)
  plus the last step. Two orders of independent moves, or an Energy attached before or after a swap of the Active, are one plan. A different state is a
  different plan, even when the boards look alike (for example Energy that went to the discard pile instead of staying in the Energy Zone).
- **Cap:** at most 2,000 plans per position (`--max-plans`), 200,000 search nodes, 30 steps per plan. When a cap is hit the result says `capped: true` with
  the count found, and the prompt says the list was cut. In the 92 stage A positions none was hit (the largest list has 1,203 plans).

### No future leakage, and how it is checked
- Everything the lister reads comes from the observation. `--world-seed` changes the REAL unseen cards of the built position (own deck order, the
  opponent's hidden hand and deck); the output must not change. The tests run three world seeds and a position that **fixes the actual top cards of
  the deck**, and require the plan lists to be byte-identical (`plans_hash`) and the top cards not to appear in any plan.
- A plan that draws or searches stops before the draw. Its description gives only the deck sizes before and after and the hand size. The prompt lists
  the composition of the unseen deck (visible: the deck list minus every card seen), which is what a player knows.
- A coin flip is described by the engine's own chances (`50%, 50%`), not by an outcome.
- Attacks: the result lines are the engine's forecast for each branch, diffed on the boards and the points only (never hands or decks).
- The prompt is built from a whitelist of position fields. The recorded plan (`his_plan`), the deal's `filler` list and the source notes are never in it
  (a test checks this).

## 2. Prompt and parser

- **System prompt:** the role, what is visible, what a plan is, how chance steps work; asks for the single best plan.
- **User prompt:** turn, points, Energy Zone, Stadium, knock-out count, effects active this turn; the board and hand; the discard pile; the unseen deck
  composition; the opponent's board, hand and deck as counts, and discard pile; the **exact card text** (`lib/card.py`) of every card in the player's deck
  list, hand, discard pile, the opponent's board and the Stadium; then the numbered plans.
- **Plan form:** up to 80 plans, each is plain English steps, the board lines that changed, the hand, and the attack result. More than 80 plans: a short
  one-line form with move labels (`Attach:1Darkness@2 zone > Evolve:Kingambit@1 > Attack:Slash [opp ...]`) and a legend (`--compact-above`).
- **Answer:** exactly `PLAN: <number>` and `REASON: <one line>`. The parser accepts formatting variants (bold, `=`, "Plan 7", `#7`), refuses a number
  outside the list, several different numbers, or no number, and keeps a choice whose reason is missing but says so. It is not fooled by a number inside the
  reason. `--order forward|reverse|shuffle:N|shuffle-id` changes the order the plans are shown in; the frozen default is `shuffle-id` (a fixed shuffle per
  position); the record stores both the number shown and the listed plan number.
- **Frozen (Oct 19):** prompt v1, order `shuffle-id`, model `claude-sonnet-5-5`, 8,000 output tokens, compact form above 80 plans, one call per decision.
  See `FROZEN.md` for the settings and the measurements behind them (position bias, a rejected v2 prompt, voting, compact against full form), and
  `FROZEN.json` for the fingerprint that `tests/test_frozen.py` checks. A record carries `frozen: true` when it ran under those settings.
- The model reasons before it answers and that counts as output: a cap of 1,500 output tokens was too small for a 57-plan position (smoke call 3), so the
  default is 8,000 (`--max-tokens`). A reply cut off by the cap is recorded as an error, not guessed.

## 3. The runner and the shared result format

Every bot writes one JSON line per (position, seed) with the same fields, so km3, kx3, the judge and later any other bot are compared on the same file:

```
{"schema": "ai_judge_choice_v1", "position": id, "bot": "km3|kx3|judge|...", "seed": n|null,
 "plan": [move labels, cut after the first chance step or the attack], "cut": "attack|chance|end_turn|opponent_choice",
 "plan_number": n,            # the number of the listed plan this reaches (replayed through the engine, so orders and slot numbers do not matter)
 "plan_full": [...],          # km3/kx3: what the bot actually played (pg_pos plays on past a chance step)
 "reason": "...", "shown_number": n, "order": "forward", "n_plans": N, "capped": false, "prompt_form": "full|compact",
 "model": ..., "prompt_tokens_estimate": n, "stop_reason": ..., "seconds": s,
 "cost": {"input_tokens", "output_tokens", "usd", "price_per_mtok", "price_note"} | null,   # null for bots that cost nothing
 "dry_run": true|false, "match_error": text|null}
```

`plan_number` is what the exam scoring needs: the recorded move and any acceptable moves are each replayed into the same list
(`judge.match_plans`), so "agrees" means "the same listed plan", not the same label spelling.

**Adding the maintainer's bot (upstream `docs/bot-protocol.md`):** the protocol decides one action at a time (`decide` with the legal `actions`, reply
`{"i": index}`), so it plays a whole turn as a loop. An adapter needs three things that are **not built**: our engine has no external player (that is
upstream's #382, table A row 11 of `rl/results/upstream_compare_2026-10-16/README.md`), it needs a `ViewState` emitter from our `PlayerObservation`, and a
stepping loop that stops at the same cut (first chance step or attack) and then writes the record above with `bot = "maintainer"`. The record needs nothing else.

## Results on the old positions

**Plan counts, the 14 diagnostic positions** (`results_old_positions/plan_counts_diag14.txt`; all lists complete, none capped):

| Case | Position | Plans | attack / chance / end turn | Search nodes | Prompt tokens (est.) |
|---|---|---|---|---|---|
| 3 | 010837 t07 | 10 | 0 / 0 / 10 | 15 | 3,946 |
| 4 | 225319 t06 | 9 | 1 / 4 / 4 | 4 | 4,264 |
| 5 | 014423 t07 | 8 | 0 / 0 / 8 | 8 | 3,924 |
| 6 | 015659 t05 | 18 | 0 / 0 / 18 | 18 | 5,121 |
| 7 | 010837 t09 | 21 | 5 / 4 / 12 | 12 | 5,821 |
| 9 | 210041 t06 | 57 | 4 / 5 / 48 | 58 | 13,646 |
| 12 | 010706 t11 | 16 | 0 / 0 / 16 | 20 | 5,362 |
| 13 | 010837 t05 | 18 | 0 / 0 / 18 | 18 | 5,340 |
| 14 | 014423 t03 | 8 | 0 / 4 / 4 | 4 | 3,906 |
| 15 | 203719 t11 | 50 | 0 / 25 / 25 | 30 | 12,758 |
| E1 | 203719 t09 | 10 | 0 / 5 / 5 | 5 | 4,169 |
| E2 | 210823 t06 | 20 | 0 / 10 / 10 | 15 | 6,458 |
| G1 | 010706 t13 | 9 | 0 / 0 / 9 | 9 | 4,069 |
| G2 | 203719 t13 | 37 | 9 / 14 / 14 | 14 | 10,079 |

(3,906 to 13,646 prompt tokens, mean 6,347; a full pass of the 14 is about 89,000 input tokens. `prompt_sizes_diag14.txt` has the same numbers.)

**Stage A's 92 positions:** 2 to 1,203 plans (median 21.5, mean 62), none capped; 10 positions have more than 80 plans, 4 more than 300. Prompts: median
6,430 tokens, mean 9,917, largest 106,085 (the 1,203-plan position, compact form).

**Is the list complete?** For each of the 88 stage A positions with a recorded plan, the recorded move list was replayed through the engine
(`coverage_stageA.txt`): **87 of 88** reach one of the listed plans. The one that does not (020824 t03) records `Tool:Heavy Helmet@2`, but the engine only
offers slots 0, 1 and 3 at that step: the recorded slot numbers of that old plan do not reproduce, a conversion problem of the old position and not of the
list. (Before replaying through the engine, a label-only comparison gave 76/92 and then 91/92: the misses were slot numbers that shift with a retreat or
a promotion, which is why scoring replays instead of comparing labels.)

**km3 and kx3 through the shared format** (diagnostic positions, `km3_diag14.jsonl` 12 seeds, `kx3_diag14.jsonl` 3 seeds): all 168 + 42 records map to a
listed plan. They agree with the recorded plan in 24/168 and 6/42 records: G1 and G2 in every seed, as DIAGNOSTIC.md says km3 already plays his line there.
E2 (210823 t06) plays his line plus a Stadium flip first, which this plan list counts as a different plan (see "Unresolved", item 1). 014423 t03 varies by
seed (km3's line there is not stable), as DIAGNOSTIC.md notes. The other 11 positions disagree in every seed, matching DIAGNOSTIC.md's "km3 misses 11 of 14".

**Live smoke calls (5 of the 5 allowed, Oct 18 evening, `smoke/smoke_2026-10-18.jsonl`):**

| Call | Position | Plans | Form | Input tok | Output tok (reasoning included) | Cost* | Result |
|---|---|---|---|---|---|---|---|
| 1 | 225319 t06 | 9 | full | 4,190 | 300 | $0.017 | cut at the 300-token cap, no answer (cap too small) |
| 2 | 225319 t06 | 9 | full | 4,190 | 845 | $0.025 | plan 3, Energy then Mesagoza, a sensible reason |
| 3 | 210041 t06 | 57 | full | 14,237 | 1,500 | $0.065 | cut at the 1,500 cap, no answer |
| 4 | 210041 t06 | 57 | full | 14,237 | 1,203 | $0.061 | plan 52 (Ilima, retreat), parsed, a coherent reason |
| 5 | 020824 t03 | 568 | compact | 44,712 | 842 | $0.147 | plan 40, parsed (his plan used slot 2 for the Helmet, which the engine does not offer) |

*Dollars use an **assumed** price of $3 / $15 per million input / output tokens (the table in `judge.py`; the tokens are exact, the dollars are not). Total
about $0.32. **Cost per decision at that price: about $0.03 for a small position, $0.06 for a 57-plan one, $0.15 for a 568-plan one; a pass over the 14
diagnostic positions is about $0.27 of input plus about $0.2 of output (~$0.5); a pass over stage A's 92 about $2.7 + $1.4 (~$4).** Check the real prices
in the console before quoting these.

## Unresolved / for the coordinator
1. **A free chance step at the start of a plan.** `UseStadium` (Mesagoza's coin) is a chance event, so a plan that uses it ends there. km3 often uses it
   first and then plays his line (E2: "his line plus a free Stadium use"); by this definition that is a different plan from his recorded line, which has no
   Stadium use. The exam's "acceptable moves" lists need a rule for optional free chance steps (count the plan up to the step as acceptable, or add the
   variant to the acceptable set).
2. **The dollar figures rest on assumed prices** (see above); the token counts are exact.
3. **The model reasons by default** (hidden reasoning, about 0.8-1.2k output tokens); the output cap must stay high (8,000). Whether a smaller thinking
   budget or no reasoning changes the quality is untested and now frozen out.
4. **Position bias (measured Oct 19, FROZEN.md):** the same prompt repeats its plan 77% of the time on 30 positions (93% on the 14), another order agrees
   63-77%; the choice does not gravitate to a place in the list, the disagreements are between nearly equal plans. Voting over three orders did not help (73%).
   The scoring must use acceptable-move sets, and running the judge twice reports its consistency only (PLAN.md).
5. **Long lists:** the compact form (above 80 plans) costs about a third of the full form and loses nothing visible on four lists of 225-479 plans; such lists
   are noisy in either form (hundreds of near-equal plans). The largest prompt is 106k tokens.
6. **Old recorded plan 020824 t03** does not replay (slot numbers).
7. The maintainer-bot adapter (above) is not built.
8. The estimator for prompt tokens is calibrated on five calls (2.1 characters per token full form, 1.7 compact form); it is good to about 5% on those.
