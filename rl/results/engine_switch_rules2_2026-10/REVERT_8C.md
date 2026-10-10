# Step 8c's revert-check driver (rules switch 2; Sonnet "Opus agents progress", Oct 10; for the laptop's review)

PLAN.md section 6, change 3: a changed game is "in lookahead" only if the code gate holds, v2 finds the condition in the bots'
search at the first differing tick, **and** the revert check reproduces the old choice and its scores. `pin/pin_rules.sh`
(lines 444-470) refuses unless `8c_RESULT.txt` says `revert L of L reproduced`. `revert_8c.py` produces that number.
Nothing here has been run against the real programs: the tests use fakes (`test_revert_8c.py`). The real run is 8c's, on the
laptop, after sitting 2.

## What it does, per lookahead game

Input: classify_8c.py's `lookahead.tsv` (every game whose verdict is `LOOKAHEAD ONLY, both halves hold` or `NEEDS A JUDGMENT`).
For each game it asks the pinned score dump (`score_dump_round2.rs`, `revert_score_dump` in tools_8c.tsv) for the decision at the
first differing tick `k`, four ways:

| run | program | gates |
|---|---|---|
| `official` | the official engine's dump (rl/engine-2026-10-02) | none: it is the official engine |
| `p` | P's dump | every gate at its default (on) |
| `gate_off` | P's dump, `--revert <the game's gates>` | the game's own gate(s), see below |
| `all_off` | P's dump, `--revert all` | the master switch (`with_round2(false)`), always asked |

**PASS** = `gate_off` chooses the official move, its candidate list equals the official one's (the number of candidates, each score
within 1e-9, each candidate text equal: Oct 1's `revert_check.py` rule), **and** `all_off` reproduces the official move and
candidates too. Anything else is **FAIL**, and any FAIL is a stop that goes to Dustin through the laptop session.

Two more FAIL reasons I added (they would otherwise be silent passes), reported in the `reason` column:
- `replay`: P with every gate on chooses the *same* move as the official engine at `k`. A lookahead game is one where the two
  engines chose differently from the same state, so a dump that does not show the difference cannot say anything about it.
- `process`: a program returned non-zero, or printed no `chose` line, or printed no candidates (an empty list equals an empty list).

## The gate: from the probe's finding, through counters.tsv

The probe cell of `lookahead.tsv` (classify_8c.py's `parse_probe` output as JSON) is read strictly. Its findings become counters,
the counters' `revert_switch` cells in `counters.tsv` become environment-variable names, and those become the score dump's
`--revert` tokens:

| finding | counters | switch(es) | `--revert` |
|---|---|---|---|
| `queued`, `cut` | coin_queued_by_attack | DECKGYM_NO_PLAIN_HIT_COIN + DECKGYM_PLAIN_QUEUED_SITES | `g1,g2` (G2 alone is not the official engine: reader one's N2) |
| `ret` | attack_return_weakness | DECKGYM_FLAT_RETURN_DAMAGE | `p2` |
| `will` | will_confused_attack, will_block_coin_attack | DECKGYM_WILL_SKIPS_GATE_COINS | `g4` |
| `vs` | vs_block_coin_built, vs_block_coin_choice_offered | DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN | `g5` |
| `trap`, `trapleaf` | trap_territory_offer_changed, trap_territory_outcome_changed | DECKGYM_TRAP_TERRITORY_ONCE | `g6` |
| `own` | coin_own_side_split | DECKGYM_NO_OWN_SIDE_COIN | `g3` |
| `guts` | guts_own_side_split | DECKGYM_NO_OWN_SIDE_GUTS | `g7` |
| `plain` | coin_plain_damage_chosen, coin_plain_damage_by_attack | DECKGYM_NO_PLAIN_HIT_COIN | `g1` |
| `perish` | perish_plain_hit_chosen, perish_plain_hit_offered | DECKGYM_NO_PERISH_ON_QUEUED_HIT | `g8` |

A game with several findings (a mixed frame, reader one's N5) gets the **union** of their gates. `trapleaf` has no counter of its
own (the probe says "no counter sees it"); it is read as the Trap Territory kind. The env-name-to-token table is the one place a
name is written by hand: it is checked in `test_revert_8c.py` against every switch `counters.tsv` names and against
`apply_action_helpers.rs` at P (`round2_switch!` lines 691-745, P2 at 618).

**Refused, never guessed** (exit 2, nothing run, nothing written): a probe field or round-2 kind this script does not know, a
ply that is not a number, a probe that found nothing, a probe run at another tick than `k`, a counter missing from counters.tsv, a
kind's counters naming different switches, a switch cell of `-` or one the table does not have (DECKGYM_ROUND2_OFF included: it
is the `all_off` run, not a counter's switch), a verdict that is not a lookahead verdict, a game twice, a game not in the hand-off,
a seed that disagrees between `lookahead.tsv` and the hand-off, a deck file that is not the hand-off's blob.

## Environment

The gates are turned off **inside** the score dump (`--revert`, for the one decision, on that thread), not through `DECKGYM_*` in the
environment, because a variable would also change every replayed tick before `k` and the replay would no longer be the game's.
So the driver sets no `DECKGYM_*` anywhere. It **refuses to start** if the caller's environment has any `DECKGYM_*`, or
`PDL_EQUIV_DEALS`, `GOLDFISH_TRACE` (the sittings refuse these too) or `PG_DUMP` (the dump sets it itself for the one decision). Each
program gets its own copy of the environment through `env=`; the caller's `os.environ` is never written.

## Running it in 8c

```
python3 revert_8c.py --lookahead OUT/lookahead.tsv --counters counters.tsv --handoff handoff_8c.tsv --root W/root \
  --seed-base 23100000000 \
  --p-program <P's score_dump_round2 binary>       --p-cwd <the engine/ it was built in (P's tree)>       --p-sha256 <64 hex> \
  --official-program <official score_dump binary>  --official-cwd <rl/engine-2026-10-02/engine>            --official-sha256 <64 hex> \
  --out OUT/revert [--jobs N]
```
Every argument is required; nothing is defaulted. The two programs are checked against the sha256 the caller gives (the caller
takes it from the sitting's recorded hashes of the builds; the P dump is built from the blob tools_8c.tsv names). `--seed-base` may be given
more than once; each game's seed minus `pairing * 10000 + i` must be one of them, and that base is what the dump is run with. `--root` holds the decks as the
hand-off's `held_file`/`panel_file` paths name them. Per game that is 4 dump runs (each replays `k` ticks, then one decision).

Outputs in `--out`: `revert_8c.tsv` (one row per lookahead game: step, bot, pairing, i, k, verdict, kind, gates, tokens, the four
moves, replay_ok, move_equal, scores_equal, all_off_equal, process_ok, result, reason); `revert_8c_summary.txt` (the one line
`revert R of L reproduced`, for `8c_RESULT.txt`: L is the number of lookahead games, R the PASS count); `revert_8c.json` (the
inputs and programs with their sha256, the driver's own sha256, the argv); `raw/` (the raw dump text of every failed game).
Exit 0: R == L. Exit 1: a FAIL (a stop). Exit 2: a refusal. `L = 0` writes `revert 0 of 0 reproduced`.

## Tests

`python3 -m unittest test_revert_8c` from this folder: 42 tests, a fake runner printing what the score dump prints. They cover a
PASS; FAIL on the move; FAIL on the scores alone (and on a candidate text or count, and the 1e-9 tolerance); FAIL on the all-off run
alone; no replay; a failed program; one failure among three; an unknown kind and every other refusal above; a `DECKGYM_*` (and
the other variables) in the parent; clean per-call copies of the environment; a mixed frame's union; each finding's gate against the
real `counters.tsv`; the exact `--revert` arguments and programs/cwd of the four runs; and one real subprocess (a shell script) to
show the working directory and a clean environment. I also broke the driver 16 ways on purpose (ignore the scores, the move, the
all-off run, the replay, the process check, the environment check, the copies; a looser tolerance; no sha256 check; no seed-base check; no deck-blob
check; G2 alone for a queued finding; no all-off run; a union that keeps one gate; an empty probe let through): every one makes a
test fail. The test `test_the_vocabulary_copies_are_the_classifiers` compares this file's copies of `R2_KINDS`,
`R2_COUNTER_KIND`, `BOTH_HALVES` and `JUDGMENT` with `tightened_rule.py` and **skips** when that file is not in the folder (it is
on the round-2 branch until merged): run the tests once where both are.

## Item 2: `control_clean` (a control must find nothing)

`control_clean.patch` (two files, `git apply`, paths as the folder's) changes `tightened_rule.py`'s `control_clean(c)` to
`nothing_found(c)`: no QUEUED, CUT or RETURN, none of round 2's seven kinds, no trapleaf (`free` is not a condition). Tests first:
`test_a_negative_control_needs_no_coin_round_or_return_condition` (which said a Will in hand is fine) is replaced by three tests,
which failed before the code change and pass after (45 tests; was 43).

| file | pinned blob (tools_8c.tsv) | blob after the patch |
|---|---|---|
| `tightened_rule.py` | 9817f8bcacd2398d3b4a0f1b9e686a876abd059d | 6b6a83649f4299af974c1b8a0dc4900b3e27f011 |
| `test_tightened_rule.py` | 6a5e792404dd8d58f2a4263b8f7274a55b1d8b8c | 9cec3bc089525fd9211e9cea24f3b8664426b912 |

Applied to the pinned blobs it gives exactly those blobs. It is a patch, not a copy at the same path, so it cannot collide with the
cloud branch's files when that branch is merged; apply it at the path the classifier lives at, commit, and re-pin the two
`tools_8c.tsv` rows (`classifier`, `classifier_tests`) to that commit and those blobs. Two other pinned tools call `control_clean`
and so get the stricter rule without changing their blobs: `classify_8c.py` (line 283, the 4 controls) and `coin_lookahead.py`
(line 143, the smoke's 3). Their docstrings (classify_8c.py line 23, coin_lookahead.py line 13: "no queued coin-path choice, cut or
return ply") now understate the rule; they are comments, and I did not change those blobs. A control that now finds a Will in hand
or two Ariados in play makes `classify_8c.py` exit 1 ("negative controls that found something"): it is looked at, not a surprise.

## Item 3: F1's G2 arm, the f601abcb test (read, not run; no cargo)

`meowth_carefree_steps_test.rs`, `g2_copied_second_punch_waits_for_the_copiers_promotion_after_rocky_helmet` (lines 1361-1425 at P).
What it asserts, with G1+G2 off (`seven_sites(false, ..)`, then the same body with them on), for seeds 0-4: Mew ex copies Mega
Kangaskhan ex's Double-Punching Family (Genome Hacking); Rocky Helmet Knocks Out Mew ex after the first punch; Mew's player is
offered `Promote { player: 0, in_play_idx: 1 }`; the first offered choice is never an `ApplyDamage` or `ApplyQueuedAttackDamage`
before that promotion; the new Active is Bulbasaur; and the damage is 180 minus the Kangaskhan's remaining HP = **120 (80 + 40)** on
every seed, switches off and on. `f1_promotion/tests_after_fix.log`: passes; `tests_before_fix.log`: fails at line 1412
("the second punch waits for Mew's player's new Active", seed 0).

So **yes** for what P does with G2 off: the promotion comes before the second punch and the damage is 120. **Not yet shown**, and
what the laptop would route to the cloud:
1. The test never runs on the official program. "120, promotion first, as the official engine" is the author's reading, written as
   constants. What supports it is code reading, mine: with G2 off the new arm in `state/mod.rs` (1411-1440) is `false && ..` and the
   other arm is the old `ApplyDamage` arm (EQUIVALENCE_reader2_sonnet.md 4.11), so P's off path is the official code. That is an
   argument, not a run. **The missing piece:** run the test's `play` body (without `seven_sites`) once on the official engine
   (rl/engine-2026-10-02), printing per step the actor and the choice kinds and the final damage for each seed, and the same at P with
   G1+G2 off; the two should be equal.
2. The pre-fix log cannot say which call failed. The panic message at line 1412 has no mode in it and the off call runs first, so a
   failure of the *off* call would print the same line. "Fails with G2 on, passes off" is the test's doc comment, not what the log
   shows. **The missing piece:** the on and off calls as two tests (or a message naming the mode), run on the pre-fix engine.
3. It looks at `choices[0]` only (the deterministic first choice), for one board.

I did not find these to be reasons to doubt the arm: only that this test is evidence about P with G2 off, not about the official
program, and the driver's per-game revert checks are what compare P-with-gate-off against the official program on real games.

## Two things I noticed on the way (not part of this driver)

- `classify_8c.py` reads the hand-off's `exact_counters` and `offgate_counters` columns (its lines 173 and 186); `sitting2_check.py`'s
  `HEADER` writes `reach2_counters`, `offgate2_counters`, `round1_counters` and `superset_counters`. I found no adapter in main's
  folder; the cloud's own check hand-off (`classify_check_8b/handoff_8b.tsv`) has the names classify_8c.py reads. This driver
  reads only the hand-off columns both name (`step bot pairing i seed held_file held_blob panel_file panel_blob`).
- `tools_8c.tsv` still says "Still to add before 8c: the revert-check driver". Pinning it needs a row for `revert_8c.py` at the
  commit the laptop reviews.

## Limits

Never run against a real score dump. It assumes the official engine's `score_dump` takes the same flags Oct 1's did
(`--a --b --seed-base --pairing --bot --deal --tick`) and prints the same `PGTICK ... asked about` / `PGDUMP score text` /
`deal i, tick t: chose X` lines as `score_dump_round2.rs` (the sample dumps under `switch_gates/revert_dumps/` have that shape). A
program that prints candidates somewhere else shows up as `process`, not a pass. The earlier revert gate run
(`revert_switches/README.md`, 21 of 21 ticks at 31616338) is the evidence that the dump and gates behave this way on a few boards;
its listed gaps (G2's pending-hit arm has no revert test of its own; the `with_round2` test is P2-only; G5's old-paths test lacks a
switch-on control) are not closed by this driver.
