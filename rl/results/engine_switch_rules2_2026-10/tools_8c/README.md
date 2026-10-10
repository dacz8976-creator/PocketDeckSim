# tools_8c/: Sonnet's step-8c tools for rules switch 2 (Sonnet "Opus agents progress", Oct 10; for the laptop's review)

Everything of mine that step 8c uses is in this folder, so none of it shares a path with the files on P's branch
(`tightened_rule.py`, `test_tightened_rule.py`, `classify_8c.py`, `coin_lookahead.py` in the folder above) and the merge in step 4 has
nothing to clash with. Nothing here has been run against the real programs or the real hand-off; the tests use fakes and
made-up rows.

| file | what it is | replaces / pinned as |
|---|---|---|
| `revert_8c.py`, `test_revert_8c.py` | the revert-check driver and its tests (sections 1-2) | new: `tools_8c.tsv` needs a row |
| `handoff_for_classify.py`, `test_handoff_for_classify.py` | the hand-off adapter and its tests (section 3) | new |
| `tightened_rule.py`, `test_tightened_rule.py` | the pinned classifier and its tests with `control_clean` changed to `nothing_found` and a path (section 4) | the `classifier` and `classifier_tests` rows |
| `classify_8c.py`, `coin_lookahead.py` | the pinned scripts, copied here so they import *this* `tightened_rule.py` (section 4) | the `classify_8c` and `coin_lookahead` rows |
| `changes_vs_pinned.patch` | what differs from the four pinned files, for reading (not for applying) | |

Tests, from this folder: `python3 -m unittest test_revert_8c test_handoff_for_classify test_tightened_rule` (49 + 20 + 45). The
driver's tests read `../counters.tsv`; the adapter's read `../sitting2_check.py` (its header) and `classify_8c.py`.

## Running it in 8c (the order)

```
python3 tools_8c/handoff_for_classify.py --in handoff_8c.tsv --out handoff_for_classify.tsv
python3 tools_8c/classify_8c.py --work W --tsv handoff_for_classify.tsv --out OUT ...      # classify_8c.py's own arguments
python3 tools_8c/revert_8c.py --lookahead OUT/lookahead.tsv --counters counters.tsv --handoff handoff_for_classify.tsv --root W/root \
  --seed-base 23100000000 \
  --p-program <P's score_dump_round2 binary>       --p-cwd <the engine/ it was built in (P's tree)>  --p-sha256 <64 hex> \
  --official-program <official score_dump binary>  --official-cwd <rl/engine-2026-10-02/engine>      --official-sha256 <64 hex> \
  --out OUT/revert [--jobs N]
```
Run `classify_8c.py` from this folder's copy: the copy on P's path imports P's `tightened_rule.py` (`sys.path.insert(0, HERE)`), whose
`control_clean` is the old, weaker one.

## 1. The revert-check driver (`revert_8c.py`)

PLAN.md section 6, change 3: a changed game is "in lookahead" only if the code gate holds, v2 finds the condition in the bots'
search at the first differing tick, **and** the revert check reproduces the old choice and its scores. `pin/pin_rules.sh`
(lines 444-470) refuses unless `8c_RESULT.txt` says `revert L of L reproduced`. For each game in `lookahead.tsv` it asks the pinned
score dump (`score_dump_round2.rs`) for the decision at the first differing tick `k`, four ways:

| run | program | gates |
|---|---|---|
| `official` | the official engine's dump (rl/engine-2026-10-02) | none: it is the official engine |
| `p` | P's dump | every gate at its default (on) |
| `gate_off` | P's dump, `--revert <the game's gates>` | the game's own gate(s), see below |
| `all_off` | P's dump, `--revert all` | the master switch (`with_round2(false)`), always asked |

**PASS** = `gate_off` chooses the official move, its candidate list equals the official one's (the number of candidates, each score
within 1e-9, each candidate text equal: Oct 1's `revert_check.py` rule), **and** `all_off` reproduces the official move and candidates
too. **FAIL** otherwise. Two more FAIL reasons I added, so that nothing passes silently: `replay` (P with every gate on chooses the
*same* move as the official engine, so the game's difference did not show up in the dump) and `process` (a program returned non-zero,
or printed no `chose` line, or printed no candidates).

**ROOT_CONTINUATION** (reader one's N3, added at the laptop's request): a switch flipped at a root that already holds a continuation
made under the other setting evaluates a state the official engine never reaches. If any of the four runs' root candidates is an
`ApplyQueuedAttackDamage` or `ApplyDamage` (a queued hit or punch frame) or a `KeepAttackCoinResults` or `RerollAttackCoins` (a
pending attack coin choice, Victory Star's pause: `state.pending_attack_coin_choice`, apply_action.rs:268-282), the game is neither
PASS nor FAIL. The row says `ROOT_CONTINUATION` and names the kinds (`root_holds`), the other columns are kept but decide nothing, the
raw dumps are kept, and it counts as not reproduced and is a stop that goes to Dustin through the laptop session, as a FAIL does.
A program that failed is a FAIL (`process`) before this, since its root was not seen. **What it cannot see:** the dump prints only the
root's candidates, not the stack below them, so a continuation under another frame (a queued punch under a promotion: N3's second
example) is not recognised. For that example reader one found that the gate-off run panics in `modify_damage`, which would show as FAIL
`process`; otherwise the classifier's "hash equal before the first difference" precondition (F10) is what covers it. Seeing the stack would
need a print added to the dump's patch (a rebuild and a re-pin).

### The gate: from the probe's finding, through counters.tsv

The probe cell of `lookahead.tsv` (classify_8c.py's `parse_probe` output as JSON) is read strictly. Its findings become counters,
the counters' `revert_switch` cells in `counters.tsv` become environment-variable names, and those become the dump's `--revert` tokens:

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

A game with several findings (a mixed frame, N5) gets the **union** of their gates. `trapleaf` has no counter of its own (the probe
says "no counter sees it"); it is read as the Trap Territory kind. The env-name-to-token table is the one place a name is written by
hand; `test_revert_8c.py` checks it against every switch `counters.tsv` names, and it was read against `apply_action_helpers.rs` at
P (`round2_switch!` lines 691-745, P2 at 618).

**Refused, never guessed** (exit 2, nothing run, nothing written): a probe field or round-2 kind it does not know, a ply that is not a
number, a probe that found nothing, a probe run at another tick than `k`, a counter missing from counters.tsv, a kind's counters naming
different switches, a switch cell of `-` or one the table does not have (DECKGYM_ROUND2_OFF included: it is the `all_off` run), a
verdict that is not a lookahead verdict, a game twice, a game not in the hand-off, a seed that disagrees between `lookahead.tsv` and
the hand-off or is not `seed base + pairing * 10000 + i` for a base the caller gave, a deck file that is not the hand-off's blob, a
program that is not the sha256 given.

**Environment.** The gates are turned off **inside** the dump (`--revert`, for the one decision), not through `DECKGYM_*` in the
environment, because a variable would also change every replayed tick before `k`. So the driver sets no `DECKGYM_*` anywhere. It
**refuses to start** if the caller's environment has any `DECKGYM_*`, or `PDL_EQUIV_DEALS`, `GOLDFISH_TRACE` or `PG_DUMP`. Each program
gets its own copy of the environment through `env=`; the caller's `os.environ` is never written.

**Arguments** are all required, none defaulted. `--seed-base` may be given more than once. `--root` holds the decks as the hand-off's
`held_file`/`panel_file` paths name them. The driver reads only these hand-off columns: `step bot pairing i seed held_file held_blob
panel_file panel_blob`. Per game that is 4 dump runs (each replays `k` ticks, then one decision).

**Outputs** in `--out`: `revert_8c.tsv` (step, bot, pairing, i, k, verdict, kind, gates, tokens, the four moves, replay_ok, move_equal,
scores_equal, all_off_equal, process_ok, root_holds, result, reason); `revert_8c_summary.txt` (the one line `revert R of L reproduced`
for `8c_RESULT.txt`: L the number of lookahead games, R the PASS count); `revert_8c.json` (inputs and programs with their sha256, the
driver's own sha256, the argv, the failed and ROOT_CONTINUATION games); `raw/` (the raw dump text of every game that is not a PASS).
Exit 0: R == L. Exit 1: a FAIL or a ROOT_CONTINUATION (a stop). Exit 2: a refusal. `L = 0` writes `revert 0 of 0 reproduced`.

## 2. Its tests (`test_revert_8c.py`, 49)

A fake runner prints what the dump prints. They cover a PASS; FAIL on the move; on the scores alone (and a candidate text or count,
and the 1e-9 tolerance); on the all-off run alone; no replay; a failed program; one failure among three; the root guard (each of the
four kinds, a kind in one run only, several kinds, an ordinary root with a lookalike action name, a comparison that would have
failed, a program that failed, counts among games); an unknown kind and every other refusal above; a `DECKGYM_*` (and the other
variables) in the parent; clean per-call copies of the environment; a mixed frame's union; each finding's gate against the real
`counters.tsv`; the exact `--revert` arguments and programs/cwd of the four runs; and one real subprocess (a shell script) showing
the working directory and a clean environment. The test comparing this file's copies of `R2_KINDS`, `R2_COUNTER_KIND`, `BOTH_HALVES`
and `JUDGMENT` with `tightened_rule.py` now runs here (the file is in this folder).

## 3. The hand-off adapter (`handoff_for_classify.py`)

`classify_8c.py` reads the hand-off's `exact_counters` and `offgate_counters` (its lines 173 and 186); `sitting2_check.py`'s `handoff`
writes `reach2_counters`, `offgate2_counters`, `round1_counters`, `superset_counters` and nine more columns (its `HEADER`, 23). The
adapter renames the first two in place and carries every other column, `round1_counters` and `superset_counters` included, through
unchanged. It accepts exactly three headers (sitting-2's; the cloud's 13 columns of `classify_check_8b/handoff_8b.tsv`, copied
unchanged; its own output, copied unchanged) and refuses anything else: an unknown or missing column, the old and new names together,
a column twice, a row of another width, a counter cell that is not a JSON object (for the sitting-2 shape, a list of ticks or an
object of such lists), a pairing or deal that is not a number, a cell starting with a double quote, an output that exists. Nothing is
written on a refusal. 20 tests, on a real-shaped sitting-2 row and a row of the cloud's 8b shape; one reads `classify_8c.py`'s source
for every hand-off column it uses and checks the output has it; one passes the output through `tightened_rule.watch_from_counters`.

## 4. `control_clean`, and why `classify_8c.py` and `coin_lookahead.py` are copied

`tightened_rule.py`'s `control_clean(c)` is now `nothing_found(c)`: no QUEUED, CUT or RETURN, none of round 2's seven kinds, no
trapleaf (`free` is not a condition). Before, round 2's kinds and trapleaf were not required to be absent. Tests first (3 replace 1:
they failed before the change). `tightened_rule.py` here is byte for byte the patched file I announced (blob 6b6a83649f4299af974c1b8a0dc4900b3e27f011,
pinned 9817f8bc). `test_tightened_rule.py` also has its one path made `../..` (it reads `coin_prevention_repair_2026-09-30/instrument_scan.py`).

`classify_8c.py` and `coin_lookahead.py` both call `control_clean` (lines 283 and 143) and both import `tightened_rule` from their
own folder, so left on P's path they would run P's old rule and the change would do nothing. Their copies here differ from the pinned
files only in the controls sentence of the docstring, the `--instrument` default's path (one folder further up), and a note saying so
(`changes_vs_pinned.patch`). A control that now finds a Will in hand or two Ariados in play makes `classify_8c.py` exit 1 ("negative
controls that found something"): it is looked at, not a surprise.

## 5. F1's G2 arm: the f601abcb test (read, not run; no cargo)

`meowth_carefree_steps_test.rs`, `g2_copied_second_punch_waits_for_the_copiers_promotion_after_rocky_helmet` (lines 1361-1425 at P).
With G1+G2 off (`seven_sites(false, ..)`, then the same body with them on), for seeds 0-4: Mew ex copies Mega Kangaskhan ex's
Double-Punching Family (Genome Hacking); Rocky Helmet Knocks Out Mew ex after the first punch; Mew's player is offered `Promote
{ player: 0, in_play_idx: 1 }`; the first offered choice is never an `ApplyDamage` or `ApplyQueuedAttackDamage` before that promotion;
the new Active is Bulbasaur; the damage is 180 minus the Kangaskhan's remaining HP = **120 (80 + 40)** on every seed, switches off and
on. `f1_promotion/tests_after_fix.log` passes; `tests_before_fix.log` fails at line 1412 (seed 0).

So **yes** for what P does with G2 off. **Not yet shown** (the laptop routes the first to the cloud through Fable):
1. The test never runs on the official program. "120, promotion first, as the official engine" is the author's reading, written as
   constants. What supports it is my code reading: with G2 off the new arm in `state/mod.rs` (1411-1440) is `false && ..` and the other
   arm is the old `ApplyDamage` arm (EQUIVALENCE_reader2_sonnet.md 4.11). That is an argument, not a run. **Missing:** the test's
   `play` body (without `seven_sites`) run once on the official engine (rl/engine-2026-10-02), printing per step the actor and the
   choice kinds and the final damage per seed, and the same at P with G1+G2 off; the two should be equal.
2. The pre-fix log cannot say which call failed: the panic at 1412 has no mode in it and the off call runs first. **Missing:** the on
   and off calls as two tests (or a message naming the mode) on the pre-fix engine.
3. It looks at `choices[0]` only, for one board.

## Limits

Never run against a real score dump. It assumes the official engine's `score_dump` takes the flags Oct 1's did (`--a --b --seed-base
--pairing --bot --deal --tick`) and prints the same `PGTICK ... asked about` / `PGDUMP score text` / `deal i, tick t: chose X` lines
as `score_dump_round2.rs` (the sample dumps under `switch_gates/revert_dumps/` have that shape). A program that prints candidates
somewhere else shows up as `process`, not a pass. The earlier revert gate run (`revert_switches/README.md`, 21 of 21 ticks at
31616338) is the evidence that the dump and gates behave this way on a few boards; its listed gaps (G2's pending-hit arm has no
revert test of its own; the `with_round2` test is P2-only; G5's old-paths test lacks a switch-on control) are not closed here.
I broke the driver and the adapter 37 ways on purpose (ignore each comparison, the environment check, the copies, each guard kind,
each refusal); every one makes a test fail.
