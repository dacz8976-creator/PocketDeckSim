# Reading: option B table (b3o3n4 vs k3), Sept 24

Decision this informs: whether b3o3n4 becomes the default pilot. **It does not, on this reading.** The pilot
decision waits for the paired whole tables (k3, b3n1 and kp3 with per-game output) from the cloud session.
Diagnostic only; never for ranking decks.

**Source:** `rl/results/option_b_table_2026-09-24.txt`
- k3 and b3o3n4 on all 28 table pairings, 500 table deals each.
- Seeds: 72,000,000 + pairing × 10,000 + i, i < 500; even i = the first-named deck in seat 0.
- Engine: laptop build from main 02d9a9b.
- Timing: k3 ran 18:17:13–18:28:48, b3o3n4 18:28:48–21:33:22 CDT. The Hydreigon run started at 21:33:22, after the table, so nothing ran beside the table except a few seconds of test runs.
- No legality findings in any game.

**How it was read:** `score.py` in this folder, which implements the rules in section 8 of
`docs/REVIEW_2026-09-24_direction.md`.
- The scan printed per-cell rates only, so this reading is **unpaired**.
- The vetoes and the adoption verdict are therefore **indicative**: a pilot that changes nothing trips a veto 30–40% of the time at 500 unpaired deals.
- Altaria v Sceptile is quarantined, because early and late play differ and the simulator matches early play.
- Sceptile v Vespiquen counts, but is drift-sensitive.

## What it says, plainly

- **Overall:**
  - Real error improves 11.5 → 10.1 (1.3 points).
  - The adoption test is not met: ΔMSE −28.8, 95% interval −72.5 to +16.1, which includes no change.
  - Favorites called right: 23 → 18 of 28 (reported only).
- **It moves points between decks rather than fixing the fit:**
  - **Sceptile, the simulator's biggest deck-level miss, improves a lot:** 62.1 → 53.8 against Limitless 48.2.
  - **Hydreigon overshoots:** 34.6 → 48.1 against 42.5. The Darkness Claw and Copycat pricing lifts the whole deck, which fixes Hydreigon v Lucario (30.6 → 45.4, real 54.4) but flips Altaria v Hydreigon (57.8 → 46.7, real 57.0) and Blaziken v Hydreigon (64.5 → 47.4, real 59.0).
  - **Suicune gets worse:** 52.9 → 56.5 against 48.2. Suicune v Weezing goes 60.8 → 79.0, real 64.2.
  - **Weezing falls:** 46.6 → 38.7 against 42.7.
  - **Altaria (46.6, real 54.0) and Vespiquen (48.1, real 56.5) do not move.** Nothing tonight targets them; the Sleep and Paralysis clock test (B2b) is the Altaria lead.
- **PASS:** neither bot passes.
  - Cells still off by more than 10 beyond noise: k3 has 4 (Blaziken v Sceptile, Hydreigon v Lucario, Sceptile v Vespiquen, Suicune v Vespiquen); b3o3n4 has 2 (Sceptile v Vespiquen, Suicune v Vespiquen).
  - Decks off by more than 6: k3 has Altaria, Hydreigon, Sceptile, Vespiquen; b3o3n4 has Altaria, Suicune, Vespiquen, plus Sceptile in the decision set.

## What decides next

- **The cloud's paired whole tables, with per-game files:** k3, b3n1 (one guess, about k3's cost) and kp3 (public pricing with no list; tier-1 read SOUND, commit 858b6fe). These get read by the same script in paired mode, where the vetoes are valid.
- **The questions they answer:**
  - Does kp3 give the Hydreigon and Sceptile gains without needing a list?
  - Where does the whole-deck Hydreigon lift come from? The mixed rows answer that.
  - Is the Suicune/Weezing shift about pricing Mars and Team Rocket's Boss? The unpriced census (B2a) answers that.

## Full output of score.py

```
Reading: b3o3n4 (new) against k3 (current), 28 common pairings.
Source: rl/results/option_b_table_2026-09-24.txt (per-cell rates only: UNPAIRED, vetoes and verdict indicative)

== all cells: 28 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.7, favorite right 23/28, clear 14/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
      b3o3n4: real error 10.1 | reported only: correlation 0.69, average miss 9.2, favorite right 18/28, clear 14/16, beyond chance 11
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, suicune, vespiquen
  dMSE new - current: -28.8 points^2, 95% interval -72.5 to +16.1 (not below 0)
  real error, current minus new: +1.34 points, 90% interval -0.41 to +2.78 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +9.6, blaziken v hydreigon +6.1, blaziken v suicune +6.2, lucario v sceptile +6.9, suicune v weezing +11.4 [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals]
  deck veto (gap grows > 2): suicune +3.6 [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals]
  ADOPTION RULE: do not adopt [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals] (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  46.6 /  46.8 /  54.0   -0.1
     blaziken:  56.4 /  54.5 /  57.7   +1.9
    hydreigon:  34.6 /  48.1 /  42.5   -2.4
      lucario:  52.5 /  54.2 /  50.2   +1.7
     sceptile:  62.1 /  53.8 /  48.2   -8.3
      suicune:  52.9 /  56.5 /  48.2   +3.6
    vespiquen:  48.1 /  47.4 /  56.5   +0.7
      weezing:  46.6 /  38.7 /  42.7   -0.0

== decision set (Altaria v Sceptile quarantined): 27 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.6, favorite right 22/27, clear 14/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
      b3o3n4: real error 10.3 | reported only: correlation 0.68, average miss 9.5, favorite right 17/27, clear 14/16, beyond chance 11
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, sceptile, suicune, vespiquen
  dMSE new - current: -25.2 points^2, 95% interval -73.0 to +21.7 (not below 0)
  real error, current minus new: +1.16 points, 90% interval -0.63 to +2.69 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +9.6, blaziken v hydreigon +6.1, blaziken v suicune +6.2, lucario v sceptile +6.9, suicune v weezing +11.4 [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals]
  deck veto (gap grows > 2): suicune +3.6 [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals]
  ADOPTION RULE: do not adopt [INDICATIVE: unpaired; a no-change pilot trips a veto 30-40% of the time at 500 deals] (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  48.1 /  46.5 /  54.8   +1.6
     blaziken:  56.4 /  54.5 /  57.7   +1.9
    hydreigon:  34.6 /  48.1 /  42.5   -2.4
      lucario:  52.5 /  54.2 /  50.2   +1.7
     sceptile:  62.1 /  54.1 /  47.7   -8.0
      suicune:  52.9 /  56.5 /  48.2   +3.6
    vespiquen:  48.1 /  47.4 /  56.5   +0.7
      weezing:  46.6 /  38.7 /  42.7   -0.0

Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)
    altaria v blaziken    56.0 |  58.4 |  74.2 ±  8.8 | -2.4
    altaria v hydreigon   57.8 |  46.7 |  57.0 ±  8.4 | +9.6
    altaria v lucario     56.6 |  59.0 |  71.9 ±  4.9 | -2.4
    altaria v sceptile    37.8 |  48.3 |  49.1 ±  6.6 | -10.5  (quarantined)
    altaria v suicune     39.2 |  37.2 |  52.3 ±  8.0 | +2.0
    altaria v vespiquen   42.6 |  39.0 |  38.8 ±  6.8 | -3.6
    altaria v weezing     36.5 |  38.9 |  34.8 ±  9.2 | +2.4
   blaziken v hydreigon   64.5 |  47.4 |  59.0 ± 12.3 | +6.1
   blaziken v lucario     46.5 |  48.8 |  44.8 ±  8.1 | +2.3
   blaziken v sceptile    59.6 |  65.0 |  82.8 ±  9.0 | -5.4
   blaziken v suicune     53.0 |  46.8 |  60.8 ± 12.4 | +6.2
   blaziken v vespiquen   79.5 |  79.2 |  81.4 ± 12.9 | +0.3
   blaziken v weezing     47.9 |  52.6 |  49.0 ± 14.1 | +2.6
  hydreigon v lucario     30.6 |  45.4 |  54.4 ±  8.0 | -14.8
  hydreigon v sceptile    27.8 |  45.6 |  39.4 ± 10.7 | -5.3
  hydreigon v suicune     38.8 |  44.6 |  34.7 ± 11.8 | +5.8
  hydreigon v vespiquen   30.8 |  43.0 |  38.4 ±  9.8 | -3.0
  hydreigon v weezing     36.8 |  51.9 |  47.1 ± 13.7 | -5.4
    lucario v sceptile    33.6 |  49.1 |  37.9 ±  6.3 | +6.9
    lucario v suicune     53.0 |  54.8 |  58.5 ±  7.7 | -1.8
    lucario v vespiquen   64.2 |  66.6 |  69.3 ±  6.4 | -2.4
    lucario v weezing     50.4 |  61.8 |  56.6 ±  8.3 | -1.0
   sceptile v suicune     56.6 |  50.6 |  47.2 ±  9.5 | -6.0
   sceptile v vespiquen   66.6 |  61.2 |  33.1 ±  8.2 | -5.4
   sceptile v weezing     70.4 |  72.8 |  66.2 ± 10.4 | +2.4
    suicune v vespiquen   50.4 |  50.8 |  27.0 ±  7.7 | +0.4
    suicune v weezing     60.8 |  79.0 |  64.2 ± 10.4 | +11.4
  vespiquen v weezing     70.9 |  71.9 |  83.5 ±  7.9 | -1.0
```
