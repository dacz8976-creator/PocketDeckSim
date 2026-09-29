# kt's reading on kog (Sept 29, the laptop, first reader): **not adopted, as registered**. kta3 passed every one of its own tests.

**What was read:** kt's registration on kog, which is amendment 2 of `../kt_2026-09-26/README.md` over the original text (amendment 3 is not in force), under Dustin's rulings recorded in `README.md`.
- **Code:** `read_kt.py`, committed at b33a96c before any kt result was read. It was written blind, reviewed twice, and run unchanged.
- **Numbers:** `READING_numbers.txt`, with score45's full pages in `score45_<code>_vs_kog3.txt`.
- **Build and replays:** everything was played by the kt build ec7e1a8. Its 13 identity replays all match game for game, and the timing check passed (0.91×).

## In plain words

- **The footprint fixed the routes** (committed alone at 6c900fd):
  - kt3, all three switches: 64.7% of games differ, so the ordinary adoption rule.
  - kta3, switch 1 alone (the Tool cut): 2.5%, so the reserve route.
- **kt3 fails the ordinary rule.**
  - Real error goes 14.0 → 14.1. ΔMSE is +1.0, 95% interval −16.7 to +18.9, not below zero.
  - Coverage: its own side is worse on three of B2e's held-out decks (Manectric, Hoopa / Absol, Garchomp) and on two second lists (Weezing −0.7 ± 0.6, Charizard Y −1.7 ± 0.9).
  - The ΔMSE failure alone decides it. The coverage vetoes use the reading's strict "own-side harm alone" rule, but they don't change the verdict.
  - Switch 2 is the cause: ktb3 alone takes real error to 14.3 with a 65% footprint. ktc3 (switch 3) leaves it at 14.0.
- **kta3 passes every test on its route:**
  - (a) footprint 2.5%;
  - (b) the τ margin is **+0.21, 90% interval +0.06 to +0.31**. That is a small real improvement, since the whole interval is above zero, where the rule only asks for −1.0 or above. Real error goes 14.0 → 13.8. No veto counts;
  - (c) no meta deck's own side is worse. Rayquaza's own side gains +0.64 ± 0.32;
  - (d) **the census Rayquaza list's own side gains +1.00 ± 0.39 over its eight rows**, a gain beyond noise. The biggest single row is v Vespiquen, +3.8;
  - coverage: no held-out, Scizor or second-list harm.
- **The outcome the registration fixed before any game** (lines 401-404): "kt3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh."
  - So **kt is not adopted, and kog stays the working pilot**, although kta3 passed.
  - The "nothing adopted" stands, since kt3 was read on every coverage row (line 152).
- **Reported beside, gating nothing:**
  - Suicune's own side under kta3 is −0.00 ± 0.25 over its nine rows: no change either way.
  - Hydreigon's deck gap goes 7.3 → 9.0 under kt3 and 7.3 → 7.1 under kta3.
  - kt3's Rayquaza (d) also shows +1.00 ± 0.62.
  - The power line: kt3's reading could detect a ΔMSE of about −18 half the time.

## What this leaves for Dustin

- **Register kta, the Tool cut alone, afresh?** The registration's outcome says the next candidate is registered afresh. kta3's case is strong: a small gain on the whole table, a real gain on its gating archetype, and no harm anywhere.
  - Tonight's 45 cells are now development data for it. So a fresh kta registration would need its own confirmation on new data, e.g. the post-freeze pull (RUN5).
  - The registration names Dustin's override only for "kt3 passes and kta3 fails" (line 403). This case would be his call.
- **Switch 2** (ktb3) is the switch to diagnose before any re-use: a 65% footprint, and no gain.

## Still owed

- **A second reader:** the registration asks for one. An independent Sonnet recomputation of the verdict-deciding numbers comes next.
- **Separate, gating nothing:** the Dustin-deck A/B (running since 11:52 UTC), the readout counters, and the Rayquaza traces (in).
- **Confirmation** belongs to any adopted pilot, so none applies now. kog's own confirmation row is unchanged.
