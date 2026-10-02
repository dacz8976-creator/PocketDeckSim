Decision this informs: step 8c of the rules switch (PLAN.md: every changed game of steps 8 and 8b explained, or the switch stops). Set by the Fable coordinator via Dustin, Oct 1 evening. The input is step 8's hand-off, on main at 1ba07d9: `handoff_8c.tsv` and `handoff_8c.md`. The laptop can cross-check every row here with a second run.
- **Not played:** no new game, only traces and probes of the hand-off's deals.
- **Not changed:** no engine file.

Seeds: the hand-off's own, 23,100,000,000 + pairing × 10,000 + i (START_HERE's 23.1B row).

# Step 8c: every changed game traced, by the cloud

## In plain words

- **All 3,813 changed games of the hand-off were traced:** step 8's 3,750 (km3 2,458, k3 1,292) and step 8b's 63.
  - Each was replayed on the old engine (`rl/engine-2026-09-30`'s source, main d363ba8) and on R (f8cfa9c, the candidate's engine tree 38af8b0), with its own bot.
  - **Every trace reproduces its game:** the move fingerprints equal the row's old_moves and new_moves in 3,813 of 3,813.
- **The verdicts, by `tightened_rule.py` (R's, unchanged) and the two accepted probes:**

  | | step 8 km3 | step 8 k3 | step 8b | all |
  |---|---:|---:|---:|---:|
  | on the board | 1,557 | 807 | 50 | 2,414 |
  | lookahead only, both halves hold | 895 | 483 | 13 | 1,391 |
  | needs a judgment | 1 | 0 | 0 | 1 |
  | **UNEXPLAINED** | **4** | **1** | 0 | **5** |
  | LENGTH (one game a prefix of the other; read by hand) | 1 | 1 | 0 | 2 |
  | changed games | 2,458 | 1,292 | 63 | 3,813 |

- **5 UNEXPLAINED games: PLAN.md's stop. They are written at the top of CLOUD_STATUS.md.**
  - All five are the same shape. An attack knocks out the Active, and the first difference is the knocked-out side's Promote: R promotes a sniper (Heatmor, Grovyle, or Chien-Pao ex), the old engine another Pokémon.
  - The snipe that would hit a coin-Ability Pokémon is on that player's next turn.
  - `coin_probe` never looks past the end of the opponent's turn. km3's and k3's own search does: the forced EndTurn costs no ply.
  - **By hand,** the repaired coin-path choice is inside the bots' 3 plies in all five. A scratch variant of the probe that crosses the forced end of turn as the bots do finds it in all five, and agrees with the accepted probe on 139 of 139 sampled games (`by_hand.md`).
  - **Whether that may count as the second half is the ruling needed.** Until then the stop stands.
- **The 2 LENGTH games are explained by hand: on the board, repair A.**
  - A Confused Mega Houndoom ex attacks with Victini in play. On R the Victory Star choice adds one tick, the old engine's game ends there, and the result is the same.
  - The reach counters fired at that tick and at its cause, in the same turn. `first_difference` can't place a tick when one game ends where the other goes on.
- **1 game needs a judgment** (`judgment.md`): km3, pairing 4, deal 106, a CONDITION 3 game.
  - `coin_probe` finds the queued choice only at the leaf of a mixed frame, because it counts a one-choice evolution pick (Quick-Grow Extract's) as a ply.
  - The bots don't count that pick as a ply, so by hand the choice is inside their search at ply 3.
- **The 296 CONDITION 3 games of step 8**, each listed with its probe result in `condition3.tsv` (with 8b's 1, 297 rows):
  - 295 are LOOKAHEAD ONLY with both halves (the coin probe finds the queued coin-path choice within the search);
  - 1 needs a judgment (the game above);
  - none is unexplained.
  - Under the coordinator's Oct 1 ruling, a game whose lookahead trace meets both halves is explained.
- **The tool checks pass:**
  - every row's deck files have the row's git blob ids, and are pairs_8.tsv's for its pairing;
  - golden probes on all 2,414 games explained on the board find the gate on the table (2,414 of 2,414);
  - 16 negative controls at unchanged deals find nothing.
  - The negative controls fall early in the game (the first tick from 8 on, as R's scripts choose them), so they are a weak check.
- **8b agrees with the cloud's early-warning rows:** the laptop's 8b rows equal the cloud's (160 of 160 per bot, old and new), and the same 13 lookahead games.

## What the probes found in the 1,391 lookahead games

Counted in the mover's own moves before the gate (`summary.txt`):
- a queued coin-path choice offered after 1 move in 596, after 2 in 593, after 3 in a pure frame in 193 (sometimes with a finite heads cut too);
- the Confusion-first branch (repair A) built within 2 moves in 9.

No lookahead game rests on a gate offered only at the leaf of a mixed frame, apart from the one judgment game.

## How it was done

- **`build_8c.sh`** (output in `build_output.txt`) builds from `git archive`, each in a fresh target folder:
  - the old engine's `vs_trace`;
  - R's `vs_trace` and `vs_probe`;
  - R's `coin_probe` (with `--features test-utils`).
  - The tracer and probes are R's files: the candidate's, since main has no `vs_trace.rs`, `vs_probe.rs` or `tightened_rule.py`, and `coin_probe.rs` is the same blob on main.
  - It lays out the deck root from main 1ba07d9: `decks/`, `carriers/`, `scratch_8b/`.
- **`trace_8c.py`** runs every hand-off row through these steps:
  1. the row's blobs and files are checked;
  2. the deal is traced on both engines with the row's bot, one (step, bot, pairing) group per file, since `load_trace` keys by i;
  3. the fingerprints are checked;
  4. `tightened_rule.first_difference` and `counter_hits` run on the row's exact_counters (every firing tick);
  5. both probes run on R at tick k for every lookahead game with no counter in the window (`--bot` = the row's bot);
  6. golden probes run on the board games.
  - The verdict logic is `classify_8b.py`'s (`../early_warning_8b/`), which is R's `first_diff.py` and `coin_lookahead.py` on both repairs at once.
  - It wrote `STOP.txt` the moment a game was UNEXPLAINED or LENGTH, and partial results were pushed as pairings finished.
- **`summarize_8c.py`** writes `results.tsv`, `condition3.tsv`, `judgment.md` and `summary.txt`.
- **`controls_8c.py`** runs the negative controls (`controls.txt`).
- **`make_coin_probe_xturn.py`, `xturn_check.py`** make and check the scratch cross-turn variant (`xturn.tsv`, `xturn_summary.txt`). It is support for the by-hand reading, not the accepted probe; no verdict uses it.

## For the laptop's cross-check

- **`results.tsv`** (one line per game): the first difference (kind, tick k, its turn, the cause tick), the counters that explain it, the probes' results, and the verdict.
- **`rows/*.jsonl`**: the same, with every field.
- **`firstdiff/*.jsonl.gz`**: the two engines' trace rows at k − 1 and k (chosen and offered moves, state hash, board).
- **`traces/*.jsonl.gz`**: the full traces, old and new, per (step, bot, pairing). A second run's traces should be byte-identical: the tracer is deterministic, and the programs here built byte-identical to the 8b early-warning builds.

## Files

- `README.md`, `by_hand.md`, `judgment.md`, `summary.txt`: the notes.
- `results.tsv`, `condition3.tsv`: the tables.
- `build_8c.sh`, `build_output.txt`, `trace_8c.py`, `summarize_8c.py`, `controls_8c.py`, `controls.txt`, `STOP.txt`: the run.
- `make_coin_probe_xturn.py`, `xturn_check.py`, `xturn.tsv`, `xturn_summary.txt`: the scratch variant.
- `rows/`, `firstdiff/`, `traces/`: the per-game records.
