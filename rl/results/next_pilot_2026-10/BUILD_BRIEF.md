# The ky3 prototype, phase 1: the build brief (for the Sonnet API credit worker; Fable launches)

Read `DESIGN_NOTE.md` and `DESIGN_NOTE_CASES.md` in this folder first. They are audited and they decide; this brief only orders
the work. Answer in plain words. Report to the laptop when done; Dustin gets nothing from this job.

**Branch:** `sonnet/ky3-pilot`, from `laptop/kx3cand-on-rules2` 9a0bc5ac. No merge of main: main's engine equals 9a0bc5ac's outside
the kx players. Read the corrected positions and main's `pg_pos.rs` by path from origin/main.

**Order:** one commit per item, tests first, and each test must be shown failing on the unfixed code.
1. **ky3 with no switch** (a new pilot code that parses like the kx3 codes), with the closest-list fallback restored.
   - Its 12-game self-check must print F's `31d638dbc818b0fa`.
   - km3 must still print `81b572198c04d5d1`.
   - It must pick F's move at every seed on the position set.
2. **`_infer`,** declared and off by default; off keeps F's behaviour.
3. **`_punch`:** Mega Kangaskhan ex's per-punch forecast, with the note's tests:
   - the 110-HP Muk;
   - a Heavy Helmet holder at 61-80 HP and at 81-100 HP;
   - the carry-over, the clock totals, and the threat pick using 120.
4. **`_queue`:** resolve frames where every choice is from-attack damage, at any count, with the note's tests:
   - Tongue Whip with 1 and with 2 targets;
   - Diving Icicles;
   - a frame that isn't damage;
   - the VK_110 score.

   State the cap claim as the note corrects it.
5. **`_atk`:** Dustin's free-attack rule, with "free" judged by consequences. Each attack is applied to a copy of the board (every
   target, the queued second punch). The exception threshold is a parameter, default 0.25 points by more than 2 standard errors over
   the opponent's next turn.
6. **The position tools:**
   - a `skip_replay.rs` export mode that writes old-engine decision states as pg_pos positions. A position is kept only where km3 on
     the current engine makes its recorded `km3_move` in most of 12 seeds; the others are dropped and listed;
   - game 3 T4 of deck 12, built by hand from what the video showed. Its opponent list comes only from the cards seen.
7. **`EXPECTED.md`,** written before any gate run: each case's property, its baseline count, and for each negative the exception
   expected to hold it.

Then STOP. Gates 0-2 run only after the laptop has reviewed the code diffs (Fable audits that review).

**Item 7, the Kingambit pilot (approved Oct 15):** see `KINGAMBIT_ITEM7.md`. It is a separate launch by Fable after items 1-6
and `EXPECTED.md`, and it runs only once C: has 15 GB free. The driver running items 1-6 does not start it.

**Rules:**
- Never set `DECKGYM_*`.
- No change to `rl/strength/src/main.rs` or the slow-report pin.
- No change to km3's code path: its digest must stay.
- Push only to the branch.
- No frames or videos: positions and ledgers only.
- Points: a knock-out is worth 1 point, an ex 2, a Mega ex 3, and 3 points win.

**Size (estimate):**
- Items 1-5 are Rust changes in `engine/src/players/` with unit tests: about 1-2 days of agent work.
- Items 6-7 are tooling and data: about half a day.
- API credits: roughly $20-50 by token volume.

The gate runs that follow (phase 1, about 25-30 sandbox-hours) are separate, and Fable launches them.
