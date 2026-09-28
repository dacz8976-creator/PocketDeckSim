Decision this informs: kt's registered reading on kog (`../kt_2026-09-26/README.md`, amendments 1-3): does pricing Tools and temporary damage cuts by what they do (kt3; kta3 = switch 1 alone) beat the working pilot kog3 on the 45 cells? This file is the plan for Sept 28-29 night, committed before any kt game on kog. Build commit ec7e1a8: the official engine 233bced (`rl/engine-2026-09-28/`, main 9b4df9b) plus kt's presets on kog, `engine/src/players/` only. The scan's and deckgym's sha256 are recorded in `STATUS.txt` when the runner starts.

Seeds: the table's deals (72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0); the 17 new cells, pairings 8-24 of `../gauntlet_runs_2026-09-26/tsv/new_decks.tsv` (21,108,000,000 + pairing × 10,000 + i); B2e's deals (21,106,000,000 + pairing × 10,000 + i, i < 40) for one identity check. No new seed block.

# kt on kog: the plan for tonight (Sept 28, before any kt game)

## Why now

**Dustin, Sept 28 evening, via Fable ("Recommendations and advice"):**
> kt tables: GO. Start kt's games now on your branch. Write the plan to a dated results folder and commit before starting, per convention. Run the full table overnight; do not stop for check-ins. [...] When kt finishes or blocks, write a one-paragraph readout in the results README and commit. Dustin will read it in the morning.

How this is read is recorded in kt's registration, amendment 3 (`../kt_2026-09-26/README.md`), in the same commit as this plan. In short:
- **The GO covers** the build on kog, kt's tables, and amendment 2's text as the registration they run under.
- **It overrides amendment 2's order.** Amendment 2 put koh's verdict first; kt runs now.
- **What's held:** clause (d)'s rows still wait for amendment 1's confirmation, from Dustin or the laptop. The Dustin-deck A/B and the coverage rows aren't part of tonight's "full table".

## What runs, in order (`run_kt.sh`; progress in `STATUS.txt`)

Everything runs from this build's own programs, with 4 threads on the cloud.
- The official program answers kt3/kta3/ktb3/ktc3 with the old kp-based presets, so it plays no kt game here (amendment 2, item 1).
- Every kt file name starts with the build commit, `ec7e1a8_`.

1. **The build checks** (amendment 2, item 7):
   - the kt tests (14 passed at ec7e1a8, before this plan);
   - the full suite (`suite.log`);
   - the diff of `engine/` from 233bced to ec7e1a8, which touches `engine/src/players/` only.
2. **Identity at the build.** Every game must be equal on moves, choices, openings, winner, points and seed (`identity.py`, written to `identity/identity_check.txt`). A failure stops the run.

   | run | reference | games |
   |---|---|---|
   | k3, all 500 table deals | the pinned engine's `../engine_switch_2026-09-28/pin_identity_k3_500.jsonl` (equal to af8489f's) | 14,000 |
   | kp3, all 500 table deals | `../engine_switch_2026-09-28/pin_identity_kp3_500.jsonl` | 14,000 |
   | kog3, all 500 table deals | `../kog_2026-09-27/a823b6d_kog3_500.jsonl` (the laptop's `table_kog3` equals it) | 14,000 |
   | kog3, the 17 new cells | `../kog_composition_2026-09-27/new17_kog3.jsonl` | 8,500 |
   | kog3, B2e's 96 pairings, i < 40 | `../koh_2026-09-28/reading/b2e_kog3.jsonl` | 3,840 |
   | kq3, all 500 table deals | `../kt_2026-09-26/identity/official_kq3_500.jsonl` | 14,000 |
   | kd3 and kpr3, 40 table deals | `../rules09_fixes_2026-09-26/af8489f_{kd3,kpr3}_40.jsonl` | 1,120 each |

   - kog3's Scizor and second-list baselines are the laptop's runs (`../koh_2026-09-28/laptop_runs/`). They are checked, or run here in full, before any kt coverage row. No coverage row runs tonight.
3. **Timing:** kog3 and then kt3 on the first 40 table deals, back to back. kt3 must be within 1.25× kog3's wall time (`timing.txt`); otherwise the run stops, as the registration says.
4. **The four tables on the 45 cells**, each code on both sides, 500 deals per cell: kt3, kta3, ktb3, ktc3, in that order. Each has two files, `ec7e1a8_table_<code>_500.jsonl` (28 cells) and `ec7e1a8_new17_<code>_500.jsonl` (17 cells), each with its scan page.
5. **The footprint, read first** (`footprint.py` → `footprint.txt`, moves only). For each code, the share of the 45 cells' 22,500 paired games whose moves differ from kog3's (`table_kog3` + `new17_kog3`). It fixes kt3's and kta3's routes (under 15%: the reserve route; otherwise the ordinary rule) and is committed alone before anything else is read.
6. **Mixed rows against kog3 on the 45 cells, as time allows:**
   - kt3 first, then kta3: the code on the first-named deck with kog3 on the other, and the reverse, 500 deals each (`ec7e1a8_mixed_{table,new17}_<code>_{first,second}.jsonl`).
   - They are what the vetoes need under the ordinary rule, and what clause (c) needs under the reserve route (a superset of the cells with a non-zero footprint).

## The readout (Dustin's request)

When the tables finish, or the run blocks, a one-paragraph readout goes at the top of this file and is committed.
- **It is the cloud's first reading.** The laptop's reading under the registration (step 5; score45.py) is still owed as the second reader.
- **Contents:** the footprints and the routes they fix. Then, by `score45.py --rules v2` against kog3 on the 45 cells, kt3's result under its route and kta3's under its route.
- **What it can't settle yet, stated as provisional:**
  - vetoes until the mixed rows are in;
  - any "not adopted" until coverage is read (amendment 2, item 4);
  - clause (d), until its confirmation and rows;
  - confirmation, at the post-freeze pull.
- If mixed rows finish later in the night, the readout is updated with them.
