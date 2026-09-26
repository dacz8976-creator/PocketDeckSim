# Gauntlet runs (Sept 26, 2026): prepared and checked; the two big runs are ready to launch

**Pre-repair: everything here is on the current official engine (commit 7fc6ccb, `rl/engine-2026-09-25/`), played
by the B2e scan. Re-run at the repaired engine when it becomes the baseline.**

Dustin approved growing the test gauntlet (`../gauntlet_proposal_2026-09-26/README.md`): (a) three new decks against
the eight panel lists, and (b) the variation check (Proposal B) on the four decks whose lists vary most. On Sept 26 he
then changed the CPU priority: the laptop also runs part of the cloud's engine-repair replays, which are the critical
path. So this folder holds everything **except the two big runs**, which the laptop session queues after its share of
the replays. Deck files: `decks/gauntlet_2026-09-26/` (with its own README and `card_check.md`).

## In plain words

- **What is ready.** The new lists are written and checked, and every new card was read in the engine's code. The
  tools that will play the games replay the reference games exactly, and short smoke games ran clean. The two launch
  scripts are written and dry-run, and the reader is tested. The laptop session only has to start two scripts.
- **What each run answers.**
  - **(a)** How close the simulator gets on two more of the most-used real decks, Dragonair / Mega Rayquaza ex and
    Mega Altaria ex / Greninja. They are scoreboard decks: with them the accuracy scoreboard grows from 28 cells to
    **45**. The 28 old cells stay frozen, and nothing already read moves.
  - **(b)** Whether swapping a Trainer or two, or playing another common list, moves a deck's result by 3 points or
    more. If it does, that deck needs a second list in the big gauntlet.
- **The Metal deck, Mega Scizor ex / Revavroom, is not run.**
  - Its main attacker is wrong in the engine in a way that changes games. After an end-of-turn Knock Out it gets a
    50-damage bonus Pocket wouldn't give it. All three skeptics agree (`decks/gauntlet_2026-09-26/card_check.md`).
  - The task's rule is not to run such a list. It was only a coverage row anyway, with too few real games to check it.
  - Check it again after the engine repair. Its real cells are listed below for reference.
  - **Laptop session, reading the cloud's fix 5bab907 (Sept 26):** the repair should cure this.
    - At 5bab907 the knocked-out player promotes before `advance_turn`.
    - `advance_turn`'s `end_turn_maintenance` then clears `moved_to_active_this_turn` on both players' Pokémon (`engine/src/state/mod.rs` 942-950 at 5bab907).
    - So a Pokémon promoted after an end-of-turn or Checkup Knock Out no longer counts as "moved this turn" on its owner's next turn.
    - This is from reading the code only. A Scizor smoke at the repaired engine confirms it before Scizor's pairings run.
- **The accuracy scoreboard is the 45 cells.** Gauntlet decks past about 10 to 11 are for brew realism and coverage,
  not an accuracy claim.
- **Two cautions for reading (a) later.**
  - **Rayquaza: answered Sept 26, no flattery.** Footage shows Rainbow Cave's Energy goes to the discard pile in Pocket too (`../recordings_check_2026-09-25/video_frame_checks.md` §6). The caution as first written: one rule is unknown and could flatter it. In the engine, the Energy that Rainbow Cave throws away goes
    to the discard pile, where Dragonair's ability can put it back on Rayquaza in the same turn. Nobody has checked
    what Pocket does. One look in the game would settle it: use Rainbow Cave, then check your discard pile.
  - **Altaria/Greninja.** Its real record differs a lot between the two halves of the Limitless data: 59.2% in the
    development half and 40.7% in the other (about ±7 each). Its gap will read very differently against each.
- **The variation rule (b)**, set in advance, reads only each deck's average over its opponents (7, or 8 for
  Charizard Y). One swapped Trainer moves a single matchup by about ±4 points at 500 games by chance alone, so the
  per-matchup numbers are shown for information only and never trigger the rule.

## How to launch (for the laptop session)

In WSL, when the laptop is free (each script refuses to start beside the training, a build or another game run, and
a refusal writes nothing, so it can simply be started again later):

```
bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/gauntlet_runs_2026-09-26/run_gauntlet_new.sh"        # (a), under half an hour
bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/gauntlet_runs_2026-09-26/run_gauntlet_variation.sh"  # (b), about 45 min
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/gauntlet_runs_2026-09-26" && python3 read_gauntlet.py
```

- Each run writes `STATUS_new.txt` or `STATUS_variation.txt`. Its last line starts with `RUN DONE` when everything
  passed (games, then the rows check), or `RUN FAILED:` with the reason. `grep -q '^RUN DONE' STATUS_new.txt` tells
  a watcher it finished.
- Either order works; they share nothing but the scan program. Times are for 14 threads at nice 10, from B2e's
  timings on this laptop.
- The reader writes `gauntlet_tables.md` and `gauntlet_summary.json` (`--part a` or `--part b` reads one run only).
  It refuses unless the run's STATUS ends in `RUN DONE`, the rows check passes again, and the frozen 28 cells
  reproduce scoreboard v2's own figures.

## What runs

**(a) The new decks** (`tsv/new_decks.tsv`, played as `tsv/new_decks_run.tsv`): each new deck against the eight
panel lists (`decks/screen/opponents/t-*.txt`), 500 deals per pairing, both seats, k3 on both sides, then kp3 on both
sides on the same deals, as B2e did.
- Pairings: p = 8 × d + o, with d = 0 Mega Scizor ex Revavroom (coverage row), 1 Dragonair Mega Rayquaza ex,
  2 Mega Altaria ex Greninja, and o in B2e's panel order (lucario, altaria, sceptile, vespiquen, suicune,
  hydreigon, weezing, blaziken).
- Pairing 24 is Rayquaza v Altaria/Greninja, the 17th new scoreboard cell. It is placed after the 24 so no
  other number shifts.
- Seeds: 21,108,000,000 + 10,000 × pairing + i, i < 500. Even i puts the new deck in seat 0.
- **Not run: pairings 0-7 (Mega Scizor ex Revavroom).**
  - Its Bullet Slugger is wrong in a way that changes play (`card_check.md`, S1; 3 of 3 skeptics).
  - So run (a) plays `tsv/new_decks_run.tsv`: pairings 8-24, 17 pairings × 500 deals × 2 pilots = 17,000 games.
  - The Scizor pairings' numbers and seeds stay reserved.
  - The 2-deal smokes played them before the card check finished: 32 games, never read.

**(b) The variation check** (`tsv/var_<version>.tsv`, kp3 only): 12 versions, each on the SAME deals as its main
list, so the comparison is paired deal by deal.
- **Lucario, Suicune, Weezing** (table decks): the table's own deals, seed 72,000,000 + table pairing × 10,000 + i.
  - The pairing numbers are legality_scan's own: the 28 pairs (a, b), a < b, over NAMES = altaria, blaziken,
    hydreigon, lucario, sceptile, suicune, vespiquen, weezing.
  - The table's first-named deck is held, so the seats are the table's.
  - The version stands in for its deck on whichever side that is; the other deck is the table's `decks/research`
    file.
  - The pairings are Lucario 2, 8, 13, 18, 19, 20, 21; Suicune 4, 10, 15, 19, 22, 25, 26; Weezing 6, 12, 17, 21,
    24, 26, 27.
- **Charizard Y**: B2e's deals, pairings 40 to 47 at base 21,106,000,000, with the version as the held deck, exactly
  B2e's rows with the held file swapped.
- **The versions**: a second list and two single-card Trainer swaps per deck (the list of changes is in
  `decks/gauntlet_2026-09-26/README.md`). 9 × 7 + 3 × 8 = 87 pairings × 500 = 43,500 games.
  - The scan takes each pairing number once per file, so each version is its own file and its own scan call, on
    the same numbers and seeds as its main list.
  - No new seeds are used.
- **The main list's side** of each comparison is the existing reference games on those deals: the table's kp3
  files (`../public_pricing_2026-09-25/kp3_500_*.jsonl`) and B2e's `../b2e_rows_2026-09-26/b2e_kp3_arch.jsonl`.
  Nothing is re-run for it.
- **The rule, set in advance (Proposal B):** a version whose average over its opponents moves by 3 points or more,
  either way, puts that deck's second list into the big gauntlet (Proposal A for that deck only).
  - The difference is paired by deal. Its 95% interval is 1.96 × sqrt(Σ per-cell variance of the mean
    difference) / K.
  - Per-cell differences are printed for information only.
- **The seat convention** is the table's everywhere: `first_seat` = i mod 2.

## The real (Limitless) cells for the new decks

`gauntlet_cells.py` → `gauntlet_cells.csv`, B2e's rules (its `cells.py`: the new deck by exact deck name, the panel
deck by its label; a tie is half a point; double losses are left out; one record per match). Both halves are shown.
The development half is the scoreboard's half (scoreboard v2 is built from it). Pooled (both halves) is B2e's
reference and is descriptive, since the holdout was spent on Sept 25. The Rayquaza v Altaria/Greninja cell matches
exact deck names on both sides.

| New deck v | lucario | altaria | sceptile | vespiquen | suicune | hydreigon | weezing | blaziken | Equal-weight average |
|---|---|---|---|---|---|---|---|---|---|
| Rayquaza, development | 73.3 (58) | 47.1 (86) | 45.0 (50) | 61.1 (36) | 35.7 (28) | 35.0 (20) | 20.0 (15) | 50.0 (8) | 45.9 ± 6.9 |
| Rayquaza, pooled | 63.7 (120) | 49.7 (173) | 43.1 (94) | 53.9 (64) | 40.7 (54) | 40.0 (50) | 35.7 (28) | 43.5 (23) | 46.3 ± 4.8 |
| Altaria/Greninja, development | 68.9 (45) | 37.5 (68) | 66.7 (33) | 61.4 (35) | 53.9 (38) | 64.7 (17) | 50.0 (16) | 70.6 (17) | 59.2 ± 6.5 |
| Altaria/Greninja, pooled | 63.3 (90) | 39.7 (117) | 50.8 (64) | 45.8 (60) | 43.4 (61) | 53.7 (41) | 50.0 (28) | 61.1 (27) | 51.0 ± 4.9 |
| Scizor (coverage), development | 75.0 (4) | 16.7 (6) | 0.0 (1) | 0.0 (2) | 62.5 (4) | none | 0.0 (1) | none | 25.7 ± 11.7 (6 opp.) |
| Scizor (coverage), pooled | 71.4 (7) | 46.2 (13) | 0.0 (3) | 25.0 (4) | 75.0 (6) | 40.0 (5) | 0.0 (1) | 0.0 (1) | 32.2 ± 10.2 |

Rayquaza v Altaria/Greninja (Rayquaza's score): 52.8% (36 matches) in the development half, 51.6% (62) pooled.
Score % (matches); W-L-T, double losses and bands are in the CSV.

**Checks on the cells:**
- `gauntlet_cells.py` reproduces all 144 of B2e's cells (6 archetypes × 8 × 3 halves) from `limitless_cells.csv`.
- It recomputes the frozen 28 development cells equal to `limitless_v2_dev.json`.
- Each new deck has exactly one Limitless deck id and no archetype label, so matching by exact name is clean.

## Checks done, and their results

| Check | Result |
|---|---|
| **Deck files** (`make_decks.py`) | DECKS OK. Each of the 14 files equals its list in `gauntlet.json`, card for card; ids resolve; names match the database; 20 cards each; the `t-` files equal the table's `decks/research` files in card order. |
| **`lib/deck_check.py files`** (14 files + `l-charizardy.txt`) | "decks clean", no warnings (`decks/gauntlet_2026-09-26/deck_check.txt`). |
| **`goldfish --coverage`, 0 games** (the official binary; no build) | Every card in all 14 files is "Fully implemented". The pricing flags are listed in the deck README. |
| **Card check** (code reading; 17 cards not checked before; 3 checkers, then 3 skeptics) | 16 of 17 cards do nothing their text doesn't allow in these games. **Mega Scizor ex's Bullet Slugger is wrong in a way that changes play** (it comes from the promotion-timing bug; upheld 3 to 0), so the Scizor list is not run. Open: where Rainbow Cave's discarded Energy goes (could flatter Rayquaza and the Charizard Y lists); Sada with fewer than 3 types; Rainbow Cave after the attachment. New engine deviations for the repair list: Bullet Slugger, Guts on Ability damage, Metal Core Barrier's missing side check. Details: `decks/gauntlet_2026-09-26/card_check.md`. |
| **TSVs** (`gauntlet_checks.py tsvs`) | TSVS PASS, 18 files. Every table-deck file has exactly that deck's 7 table pairings, with the decks in the table's order (read from the official scan's own per-game file). The Charizard Y files equal B2e's rows 40-47. |
| **Staging** (`stage_inputs.sh`) | The TSVs and deck files are copied into `/home/dacz8976/engine-b2e-7fc6ccb` at the same relative paths. The ones the tree already had equal the working copy. Hashes are in `inputs_sha256.txt`, origins in `inputs_source.txt`. The new files are "working copy only (not committed yet)"; once committed, their bytes must hash the same. |
| **Identity** (`run_identity.sh` → `identity/identity_check.txt`) | **GAUNTLET IDENTITY PASS** for scan sha256 45ecfda4…3b5b (the B2e scan, whose own identity check passed). The main lists, played through the same TSV rows the versions use (kp3, 2 pairings × 20 deals each), replay the reference games. **Lucario (2, 18), Suicune (4, 25), Weezing (6, 27):** compare.py IDENTICAL against the table's kp3 files, 40 of 40 each, and equal to the official 7fc6ccb scan's own lines once `a_file` and `b_file` are dropped. **Charizard Y (40, 47):** byte for byte B2e's lines, 40 of 40. So the pairing numbers, seeds and seats reproduce the table and B2e. |
| **Smokes** (same script) | (a): all 25 pairings × 2 deals under k3 and kp3. (b): all 87 pairings × 2 deals under kp3. ROWS PASS; no legality finding of any kind (no RULE, no CHECK). They are played at the real seeds, so the big runs replay them; the reader checks that they do. |
| **Reader test** (`read_gauntlet.py --test` → `identity/reader_test.md`) | Runs end to end on the smokes. Fed each identity replay as a "version" of its own main list, every difference is exactly 0.0. The frozen 28 cells reproduce scoreboard v2 exactly: k3 real error 10.8 (28 cells) and 10.9 (27), average miss 10.3 and 10.4, favourites 23/28 and 22/27, correlation 0.64; kp3 8.4 and 8.6, 9.0 and 9.3, 21/28 and 20/27, 0.72 and 0.71. Clear ones right (12/15 and 13/15) and beyond chance (7) agree too. |
| **Dry run of both launch scripts** (2 deals, scratch folder) | `GAUNTLET_DRY_RUN=1` into the session scratchpad. Both STATUS files end in `RUN DONE`, and the rows checks pass: 17 pairings under k3 and kp3, 87 under kp3. A second launch refused (STATUS exists). The four misuse cases refused with the right reason and wrote nothing: a dry run into this folder, a dry run over 20 deals, a real run with `GAUNTLET_OUT`, and a real run with `GAUNTLET_GAMES`. The reader then read the dry run in full mode, and every dry-run game equals its smoke game byte for byte, so the games are deterministic. This folder has no STATUS or run file. |

## Where this differs from the task, and why

- **The big runs were not started** (Dustin's CPU-priority change, via the coordinator). Everything else was done.
- **The identity checks and smokes ran without the idle refusal**, at `nice -n 19` with `RAYON_NUM_THREADS=2`, while
  the laptop ran the engine-repair replays (the coordinator's instruction). They are a few hundred games in all. The
  two big-run scripts keep B2e's `idle_or_die` unchanged, and use nice 10 with cores − 2 threads.
- **Smokes were added** (2 deals per pairing, at the real seeds). They test every list and TSV under the scan before
  the big runs, and give the reader real files to test on. The big runs replay them, and the reader checks it.
- **One TSV per version.** The scan takes each pairing number once per file, so the 12 versions are 12 files and 12
  scan calls, on the same numbers and seeds as their main lists.
- **Version files place the new card on the replaced card's line** (deck README). This keeps the pairing by deal as
  tight as possible.
- **Charizard Y's second list is `l-charizardy.txt`,** as the task and the proposal's README say. `gauntlet.json`'s
  `proposal_B_sensitivity` twin for Charizard Y is a different, 5-copy list. It is flagged in the deck README and not
  used.
- **The launch scripts can dry-run** (`GAUNTLET_DRY_RUN=1` with a scratch `GAUNTLET_OUT` and at most 20 deals). This
  path refuses to write into this folder, and the real path refuses those variables.

## Flags

1. **The Scizor list is not run** (S1 above).
   - The same bug belongs on the repair list. Repairing the promotion timing fixes Bullet Slugger only if the new
     Active is chosen before the turn resets, or if a promotion stops counting as "moved".
   - `rules/05` #20 and `rules/07` line 185 say the engine gets opponent-turn promotion right. That only holds for
     Knock Outs from attacks. Not edited here.
2. **Rainbow Cave's discarded Energy (R1) is an open rule that reaches three decks here:**
   - Rayquaza (Dragonair's ability);
   - the Charizard Y versions' Flame Patch: `l-charizardy.txt` and swap 1 carry a 2nd Rainbow Cave, so a Charizard Y
     difference in (b) may partly be this rule;
   - Blaziken's Flame Patch.

   Also open: whether the Cave can be used after the attachment (R4). One in-game look settles each.
3. **Altaria/Greninja's real record differs between the halves:** 59.2 ± 6.5 in the development half against
   40.7 ± 7.3 in the holdout half. That is far beyond noise (clustered events). Read its gap against both columns.
4. **Thin real cells.** Some of the 17 new cells rest on few matches: Rayquaza v Blaziken 8 in the development half
   (23 pooled), v Weezing 15 (28). The reader marks bands over 15 points "wide", as rule v2 does.
5. **Charizard Y has two different "second lists" inside the proposal.** The README's `l-charizardy.txt` (used) and
   `gauntlet.json`'s `proposal_B_sensitivity` twin (a 5-copy list with Charizard B1a 013; not used).
6. **Two versions can face each other's main list.** Pairings 19 (Lucario v Suicune), 21 (Lucario v Weezing) and
   26 (Suicune v Weezing) are in two decks' variation sets. Each version plays the other deck's main list, by design:
   one deck varies at a time.
7. **Times are estimates** from B2e's laptop timings (about 0.05 to 0.06 s of wall time a game with 14 threads).

## Seed block (one row for START_HERE's seed table; the laptop session adds it, not edited here)

| Seeds | Used by |
|---|---|
| 21,108,000,000 – 21,108,240,499 | Gauntlet run (a), Sept 26: new decks v the panel, seed 21,108,000,000 + pairing × 10,000 + i, pairings 0-24, i < 500, k3 and kp3 on the same deals; smokes at i < 2 of the same seeds. Pairings 0-7 (Scizor) are reserved but not played by run (a) (Bullet Slugger deviation); only the 2-deal smokes, i < 2, used them. Sub-blocks 25-99 spare. Run (b) uses no new seeds (the table's 72,000,000 block and B2e's 21,106,000,000 block, on purpose, for pairing). |

## Files

| File | What it is |
|---|---|
| `make_decks.py` | Writes `decks/gauntlet_2026-09-26/*.txt` from `gauntlet.json` and checks them. |
| `gauntlet_cells.py`, `gauntlet_cells.csv` | The Limitless cells (new decks by B2e's rules; the frozen 28 with pooled beside), with the two cross-checks. |
| `make_tsvs.py`, `tsv/` | The pairings files: `new_decks.tsv` (25), `new_decks_run.tsv` (what (a) plays), `not_run.json` (why a deck is left out), `var_<version>.tsv` (12), `id_<deck>_main.tsv` (4, for the identity check). |
| `gauntlet_checks.py` | `tsvs` (the TSVs against the references) and `rows` (a run's files against its TSVs). |
| `stage_inputs.sh`, `inputs_sha256.txt`, `inputs_source.txt` | Copies the played inputs into the scan's tree and records their hashes. |
| `run_identity.sh`, `identity/` | The identity checks and smokes (`identity_check.txt` ends in the PASS line), their games, and the reader test (`reader_test.md`). |
| `run_gauntlet_new.sh`, `run_gauntlet_variation.sh` | The two big runs, ready to launch. |
| `read_gauntlet.py` | The reader. |
