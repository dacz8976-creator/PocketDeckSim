Decision this informs: none on its own. This folder is a **cross-check** of the laptop's kt run, which is the run of record (Dustin via Fable, Sept 28 late evening). It holds game files and identity checks only, with no footprint, route, verdict or reading of any kind. Build commit ec7e1a8: the official engine 233bced (`rl/engine-2026-09-28/`, main 9b4df9b) plus kt's presets on kog, `engine/src/players/` only. The scan's and deckgym's sha256 are in `STATUS.txt`.

Seeds: the table's deals (72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0); the 17 new cells, pairings 8-24 of `../gauntlet_runs_2026-09-26/tsv/new_decks.tsv` (21,108,000,000 + pairing × 10,000 + i); B2e's deals (21,106,000,000 + pairing × 10,000 + i, i < 40) for one identity check. No new seed block.

# kt on kog: the cloud's cross-check (Sept 28-29)

## What happened, in order

1. **Dustin's message (via Fable, Sept 28 evening):** "kt tables: GO. Start kt's games now on your branch. [...]". The cloud read it as a go for its own run.
   - It committed a plan here and kt amendment 3 (f72cb77), and started the runner at 23:33 UTC.
   - The runner was still in the test suite; **no kt game had been played.**
2. **Dustin's correction** (via Fable, "Recommendations and advice", Sept 28 late evening), verbatim:
   > 1. kt amendment 3 is NOT in force. My go was given to the laptop with the koh-first order attached; your reading of it as "start kt's games now" is the cloud's interpretation, not my word. Mark amendment 3 as withdrawn, dated, in one line. Write no further amendments.
   > 2. The laptop's kt run is the run of record. Your identity and table runs may continue as a cross-check only. You write no footprint reading, no route choice, no verdict, and no reading of any kind. If your games differ from the laptop's on the same commit and seeds, that is a finding: stop and write it down.
   > 3. If you finish the cross-check, push the game files and go idle. Do not start coverage, mixed rows, clause (d), or the A/B; the laptop runs those.

   - **His word to the laptop** is recorded on main (f7defd1, `rl/results/kt_tables_2026-09-28/README.md`): "kt tables: go"; "Yes, all; build now". kt's first game there waits until koh's B2e rows are read.
   - **The laptop builds this commit** (ec7e1a8) and plays every game of record from it.
3. **What the cloud did:**
   - stopped the runner at 23:41 UTC;
   - marked amendment 3 withdrawn in one line (`../kt_2026-09-26/README.md`), with no further amendment;
   - removed the footprint script;
   - trimmed the runner to the suite, the identity checks and the four tables;
   - restarted it.

## What runs (`run_kt.sh`; progress in `STATUS.txt`)

Everything runs from this build's own programs, 4 threads. The official program answers kt3/kta3/ktb3/ktc3 with the old kp-based presets, so it plays no kt game here. Every kt file name starts with `ec7e1a8_`.

1. **The build checks:**
   - the kt tests, 14 passed at ec7e1a8;
   - the full suite (`suite.log`);
   - the diff of `engine/` from 233bced, which touches `engine/src/players/` only.
2. **Identity at the build.** Every game must be equal on moves, choices, openings, winner, points and seed (`identity.py`, written to `identity/identity_check.txt`). A difference stops the run and is written down.

   | run | reference | games |
   |---|---|---|
   | k3, all 500 table deals | `../engine_switch_2026-09-28/pin_identity_k3_500.jsonl` | 14,000 |
   | kp3, all 500 table deals | `../engine_switch_2026-09-28/pin_identity_kp3_500.jsonl` | 14,000 |
   | kog3, all 500 table deals | `../kog_2026-09-27/a823b6d_kog3_500.jsonl` | 14,000 |
   | kog3, the 17 new cells | `../kog_composition_2026-09-27/new17_kog3.jsonl` | 8,500 |
   | kog3, B2e's 96 pairings, i < 40 | `../koh_2026-09-28/reading/b2e_kog3.jsonl` | 3,840 |
   | kq3, all 500 table deals | `../kt_2026-09-26/identity/official_kq3_500.jsonl` | 14,000 |
   | kd3 and kpr3, 40 table deals | `../rules09_fixes_2026-09-26/af8489f_{kd3,kpr3}_40.jsonl` | 1,120 each |

3. **The four tables on the 45 cells**, each code on both sides, 500 deals per cell: kt3, kta3, ktb3 and ktc3. Each has two files: `ec7e1a8_table_<code>_500.jsonl` (28 cells) and `ec7e1a8_new17_<code>_500.jsonl` (17 cells), with their scan pages.
4. **Then:**
   - the game files are pushed;
   - if the laptop's kt games are on main for the same commit and seeds, the two are compared game by game (moves, choices, openings, results);
   - a difference is a finding, written down here, and the cloud stops. Nothing else is read.
   - Then the cloud goes idle.

**Not run here:** the timing run, the footprint, any score, clause (d), the A/B, coverage and mixed rows. The laptop runs those.

## Where it ended (Sept 29, 07:15 UTC)

- **The cross-check runs are complete**, all pushed to this folder.
  - **The suite:** 1,977 passed, 0 failed.
  - **Identity:** 8 of 8 checks pass, with every game equal and a clean rule check (`identity/identity_check.txt`).
  - **The four tables on the 45 cells:** kt3, kta3, ktb3 and ktc3, each 14,000 + 8,500 games, with no rule findings on any scan page.
  - A container restart at about 04:00 UTC cost only the run in progress, kt3's new cells. It was rerun from the start with the same program and calls (`STATUS.txt`, "RESUMED").
- **The comparison with the laptop's games (Sept 29 morning): all eight files match.** The laptop's game files arrived on main at 87a68d4. Each of the cloud's eight table files was compared with the laptop's file for the same code and cells, game by game on moves, winner, points and seed, keyed by pairing and deal. The only things counted were equal fields and matching keys; no result was read.

  | code | 28 table cells | 17 new cells |
  |---|---|---|
  | kt3 | 14,000 of 14,000 match | 8,500 of 8,500 match |
  | kta3 | 14,000 of 14,000 match | 8,500 of 8,500 match |
  | ktb3 | 14,000 of 14,000 match | 8,500 of 8,500 match |
  | ktc3 | 14,000 of 14,000 match | 8,500 of 8,500 match |

  - The same games are present in both, with the same code on both sides.
  - So the two builds of ec7e1a8 (cloud: scan e19703b1…; laptop: its own build) play kt's games identically. There is no finding.
- **One agreement that needs no reading:** the laptop's identity replays at ec7e1a8 (main 0fe3d7f) and these match the same reference files game for game. So the two builds of ec7e1a8 play those bots identically.
- **Nothing here was read, scored or chosen.** The cross-check is finished, and the cloud is idle on kt.
