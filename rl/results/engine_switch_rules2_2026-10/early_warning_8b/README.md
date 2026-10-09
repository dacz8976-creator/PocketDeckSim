Decision this informs: rules switch 2's trace-load gate (main `rl/results/engine_switch_rules2_2026-10/PLAN.md`, precondition
(d) and the gate before step 8: "step 8 starts only with `TRACE LOAD n ≤ ~50`, or with a `DUSTIN` line"). Set by the Fable
coordinator via Dustin, Oct 9, decision 14: "the step 8b early-warning rows on the P2 head (same four pairings and seeds as Oct
1's, plus brew-07 v t-altaria and brew-09 v t-altaria as pairings 36-37 at 40 deals, classified with probe v2 and the tightened
rule v2)". Played by the cloud on branch `claude/coin-prevention-round2`; nothing is merged or pinned.

# Rules switch 2, step 8b's early-warning rows (the cloud, Oct 9)

## In plain words

- **25 of 480 deals changed** between the official engine and the round-2 branch's final engine (P2, its off-switch and P3):
  km3 13 of 240, k3 12 of 240.
  - Pairings 32-34 (Oct 1's Victory Star, Tongue Whip and Chase Order rows): none, as expected.
  - Pairing 35 (l-sharpedo v meowth_carefree): km3 11, k3 7. This is Gyarados's Wild Swing, which now flips Meowth's coin
    (the later coin round). It was expected: the round-2 README says this row is no longer a Wild Swing control.
  - Pairing 36 (brew-07 v t-altaria): none.
  - Pairing 37 (brew-09 v t-altaria): km3 2, k3 5. This is P2: Cursed Jewel's hit back with Weakness.
- **Every changed game is explained, and none needs a hand trace: TRACE LOAD 0.**
  - 4 are on the board. An exact counter fired at or before the first difference, in its turn: `attack_return_weakness` in
    3 (pairing 37) and `coin_queued_by_attack` for Wild Swing in 1 (pairing 35). The probe's golden check finds the gate on the
    table in all 4.
  - 21 are look-ahead only, with both halves. The bots chose differently from the same board, and coin_probe v2 finds the gate
    inside their 3 plies:
    - the 17 in pairing 35 find Wild Swing's queued coin choice 3 moves ahead, in a frame the bots resolve for free;
    - the 4 in pairing 37 find P2's RETURN, the hit back with Weakness, 1 or 3 moves ahead.
  - The code-gate halves, read in the code: for RETURN, the probe's docstring (`handle_attack_retaliation`); for Wild Swing's
    queued choice, `coin_gated_choice` (`engine/src/actions/apply_attack_action.rs`:365 at `140c0be`, reached from the
    discard-then-damage path at :422; switch-2 PLAN.md line 112, and "The gates" in the round-2 README).
- **Every file check passes.** The pinned official `legality_scan` equals the "old" built from source on every field (240 of
  240, both bots). For pairings 32-35 it also equals Oct 1's recorded rows on main (`5a18d31_8b_new_<bot>.jsonl`, 160 of 160):
  that is the side the laptop reuses as "old". The watch build equals the plain one on every field (240 of 240).
- **The proposed line for `trace_load.txt`** is `TRACE LOAD 0` with this folder's commit (CLOUD_STATUS gives it).

## What was played

- **Pairings** (`pairs_8b.tsv`): main's `pairs_8.tsv` rows 32-35, unchanged, and two new rows:
  - 36: brew-07-hoopa-darkrai-sableye v `decks/screen/opponents/t-altaria.txt`;
  - 37: brew-09-sableye-obstagoon v t-altaria.
- **Seeds:** 23,100,000,000 + pairing × 10,000 + i, i < 40, so 36 is 23,100,360,000-039 and 37 is 23,100,370,000-039.
  - **Not yet in START_HERE's seed table.** Its 23.1B row (the first rules switch, this same work) names pairings 0-31, 32-35
    and 40-71; 36-37 are unused there.
  - **The plan said otherwise.** Switch 2's PLAN.md (line 218) asks that new 8b rows take seeds from a fresh block, for
    example 23,300,000,000, recorded before any game. The decision named the rows "pairings 36-37", which is the 23.1B
    numbering, so they were played there.
  - If the coordinator prefers 23.3B, replaying 36-37 takes a few minutes.
  - Either way, the laptop's rows for 36-37 must use the same seeds as these, so that its rows equal the cloud's (precondition
    (d)).
- **Bots:** km3, then k3, the same bot in both seats; the first-named list sits in seat 0 when i is even.
- **Programs**, each built from `git archive` into its own target folder (`run_8b.sh`; sha256s in `run_output.txt`):
  - old: main-8626a35's engine, the official program's source (`legality_scan`, `vs_trace`);
  - new: `140c0be`, the branch's final engine commit (`legality_scan`, `vs_trace`);
  - watch: new with both `instrument_scan.py` scripts, the round-2 and P2 counters (`legality_scan`);
  - probe: new with coin_probe v2 and the counters' lines it includes (`--features test-utils`); its self-test passes, 14 checks
    and 3 frame checks;
  - pinned: `rl/engine-2026-10-02/legality_scan` (its SHA256SUMS verify).
- **The decks** come from main `1163ebb`: `decks/` and the four scratch lists (sha256s in `decks_sha256.txt`). The tracer and
  the probe come from `2d3eec4`.
- **Scope.** Only the rows the decision names. The plan's own 8b list (PLAN.md line 228) also has the 5 other smoke pairings
  and 2 block-coin rows; those weren't asked for here.

## How each changed game was classified (`classify_8b.py`)

It is Oct 1's classifier (on `claude/pensive-ptolemy-spwc0b`), with tightened rule v2 and coin_probe v2.
- **The first difference** comes from both engines' traces (`vs_trace`). Every trace's move fingerprint equals its scan row.
  The two engines' state hashes are comparable: in all 25 changed games the hash is the same on both engines at every tick
  before the first difference (and a spot check of an unchanged game, pairing 32 deal 0 km3, matched at all 80 ticks; not kept).
- **ON THE BOARD:** an exact counter of a mechanic this switch changes fired at or before the first differing tick in its turn,
  or at the cause tick. The counters are `instrument_scan.py`'s EXACT list: the round-2 and P2 ones. The first round's counters
  are left out, since both engines have the first round.
  - `coin_queued_by_attack` counts only the later round's eight attacks. Its other keys (Chase Order, and the first round's
    helpers such as Tongue Whip and Diving Icicles) build the same choice on both engines.
  - For a "length" difference, the counter must fire at the longer new game's first extra tick.
- **LOOKAHEAD ONLY, both halves hold:** a look-ahead difference where the probe finds QUEUED or CUT (the coin rounds) or RETURN
  (P2) inside 3 plies.
  - **The strict reading.** QUEUED can't tell a first-round site from a later-round one. So the classifier reads the attack
    named on the probe's path. A game resting on a first-round site alone would be UNEXPLAINED under the strict reading.
  - **Here no game needed it:** all 17 coin paths name Wild Swing.
- **UNEXPLAINED:** anything else. That includes "length" with no counter at the extra tick, and a new game shorter than the
  old one (tightened rule v2's open case). No game here was a "length" case.
- **Golden checks:** at the explaining tick, `attack_return_weakness` must read RETURN 1 and `coin_queued_by_attack` QUEUED 0.
  All 4 pass.
- **Negative controls:** 2 per bot, unchanged games of pairing 33, at the first tick from 8 on (turn 1 or 2) with two or more
  offered moves and no Meowth in play. Nothing is found in any of the 4.

| Pairing | km3 changed | k3 changed | On the board | Look-ahead, both halves | Hand |
|---|---:|---:|---:|---:|---:|
| 32 fire_victini v psychic_confuse | 0 | 0 | | | |
| 33 fire_heatmor v meowth_carefree | 0 | 0 | | | |
| 34 t-vespiquen v meowth_carefree | 0 | 0 | | | |
| 35 l-sharpedo v meowth_carefree | 11 | 7 | 1 (k3 i 9, Wild Swing queued at the tick) | 17 (QUEUED 3, free: Wild Swing) | 0 |
| 36 brew-07 v t-altaria | 0 | 0 | | | |
| 37 brew-09 v t-altaria | 2 | 5 | 3 (km3 i 0; k3 i 0, 25: `attack_return_weakness`) | 4 (RETURN 1 or 3) | 0 |

**The implied load for step 8.** Switch 2's step 8 is km3 17,500 and k3 8,750 deals: the last switch's 32 pairings plus the
Will rows. Each bot's share of changed games that no exact counter explains, times those deals, gives about 1,203 games for
the probe. The share needing a hand trace gives 0. This sample's rows aren't step 8's pairings: they are the early-warning rows,
as on Oct 1.

## Limits

- coin_probe v2 looks for the coin rounds' queued choice and finite cut and for P2's hit back, and for nothing else of round 2.
  The plain-hit coin, the own-side coin or Guts, Will, the Victory Star gate pause, Trap Territory and Perish Body on a queued
  hit have no probe condition yet (switch-2 PLAN (a), "still to do"). None of these 25 games needed one: each was on the board
  or found by QUEUED (Wild Swing) or RETURN.
- The revert check (precondition (e)) wasn't run here. For P2 the off-switch now exists, and its gate 2 showed the old choices
  coming back at the smoke's three games (`../../coin_prevention_round2_2026-10-01/switch_gates/`).
- The 8c cross-check (an independent classification) comes when the laptop hands off, as the decision says.

## Files

- `README.md`: this note.
- `run_8b.sh`, `run_output.txt`: the run, with the programs' sha256s.
- `classify_8b.py`, `classify_output.txt`, `summary.json`: the classification and its output.
- `pairs_8b.tsv`, `decks_sha256.txt`: the pairings and the decks played.
- `8b_{old,new,watch,pinned}_{km3,k3}.jsonl`: every game, one row each, as legality_scan writes them. The watch rows carry the
  counters.
- `scan_page_*.txt`: the scan pages.
- `traces/`: the traces of every changed game on both engines (`trace_{old,new}_<bot>_<pairing>.jsonl.gz`) and of the control
  games (`trace_control_<i>_<bot>_<pairing>.jsonl.gz`).
- After the review (an Opus workflow, before the classification ran), `run_8b.sh` clears cached traces at the start and stops
  if the pinned programs' SHA256SUMS don't verify. The recorded run predates those two lines; its SHA256SUMS verified.
