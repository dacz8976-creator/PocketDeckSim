# kog's composition check on the 45 cells: the reading plan (Sept 27, laptop; written before any laptop game)

**What is being checked:** Dustin's ruling (RUN5 "Composing candidates into one pilot"). kp3 + koa's switch A + kpg's F become one pilot through a composition check, not a new candidate:
- the combined code's identity checks;
- one table on the 45 cells;
- no veto;
- accuracy no worse than the better component alone.

**The build:** the cloud's kog at a823b6d (branch `claude/pensive-ptolemy-spwc0b`, scan sha256 1fbf3606…; `../kog_2026-09-27/BUILD.md` on that branch). Its composition checks 1-3 and the k3/kp3 replays already pass there.

## Runs (`run_kog_composition.sh`)

1. The laptop's build of a823b6d. k3 and kp3 on the table's first 40 deals equal the official references.
2. `table_kog3`: all 14,000 table games. This must equal the cloud's `a823b6d_kog3_500.jsonl` game for game (moves, choices, openings, result), which is the laptop's identity check of the composed code.
3. `new17_kog3`: the 17 new cells (21,108,000,000 block, pairings 8-24).
4. Mixed rows, kog3 against kp3 (the pilot in force), on all 45 cells, both directions.

## The reading, fixed now

1. **Identity:** step 2 at 14,000 of 14,000, and k3 and kp3 at 1,120 of 1,120 each. Any difference stops the reading.
2. **The table:** `score45.py --rules v2`, kog3 against kp3, with kog3's mixed rows.
3. **No veto:** no cell or deck veto counts under rule v2. A veto counts only when the mixed rows show kog's own side worse beyond the row's paired noise (about ±4), and never on a cell whose band is wider than about ±15. One that counts fails the check.
4. **Accuracy no worse than the better component:**
   - On the 45 cells the better component is kpg3 (real error 14.0; koa3 15.5).
   - Test, on the same deals: `score45.py` with kpg3 as current and kog3 as new. The τ̂ margin (kpg3 minus kog3) must have its 90% lower bound at −1.0 or above.
   - That is RUN5's no-harm bound. It is used because koa's share, the only thing kog adds to kpg, was measured at −0.01 (−0.15 to +0.12) against kp3 and isn't meant to move accuracy.
   - kog3 against koa3 is reported the same way.
5. **Where the parts meet**, reported: the cells where both switches can act, Altaria v Blaziken on the table and Rayquaza v Altaria among the new cells. Also kog3's score there beside koa3's and kpg3's.
6. **Not part of this check:** B2e and the coverage decks. Each component's own held-out and coverage readings stand (koa's reading, kpg's `heldout_check.md`), and the composed pilot is confirmed on post-freeze data under RUN5's rule.

**If it passes:** kog is the pilot for the table and the screen together, "unconfirmed" until the post-freeze read. It joins that pull's list.
- kph is then built on it as `koh` (the cloud's proposal), and kt is re-issued on it.

**If it fails:** kp3 stays. The failing item is reported, and nothing is re-read until it passes.
