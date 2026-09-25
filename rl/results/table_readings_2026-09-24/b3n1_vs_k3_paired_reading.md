# Paired reading: b3n1 vs k3, whole table (Sept 25)

Decision this informs: whether b3n1 becomes the default pilot. **Under the pre-set adoption rule: not adopted.**
- The overall gain is clear.
- But two vetoes fire, narrowly, on a paired reading where vetoes are valid: Altaria v Hydreigon's miss grows 6.1, and Vespiquen's deck gap grows 2.1.
- kp3, the list-free version of the same pricing, is read the same way when its table lands.

Diagnostic only; never for ranking decks.

**Source:** per-game files on branch `claude/pensive-ptolemy-spwc0b`
- Files: `rl/results/per_game_table_2026-09-25/k3_500.jsonl` (commit 9922410) and `b3n1_500.jsonl` (commit 546c3ad).
- Both come from legality_scan at e18ab4b: all 28 pairings × the table's first 500 deals (seed = 72,000,000 + pairing × 10,000 + i, i < 500), no rule findings.
- The cloud's k3 cells equal the laptop's k3@500 cells in all 28, so the table deals reproduce across machines.

**How it was read:** `score.py` in this folder, in paired mode.
- Both bots are resampled on the same deals within each cell, and every Limitless cell is redrawn from Binomial(n, L); 4,000 replicates.
- Altaria v Sceptile is quarantined, so decisions use the other 27 cells.

## Numbers (decision set, 27 cells)

| | k3 | b3n1 |
|---|---|---|
| real error τ̂ (points) | 11.5 | 9.2 |
| improvement, 90% interval (margin rule quantity) | | +2.26 (+0.63 to +3.37) |
| ΔMSE new − current, 95% interval | | −46.8 (−84.7 to −7.5): **below 0** |
| cell veto (a cell's miss grows > 6) | | **Altaria v Hydreigon +6.1** (57.8 → 50.2, Limitless 57.0) |
| deck veto (a deck's 7-opponent gap grows > 2) | | **Vespiquen +2.1** (48.1 → 46.0, Limitless 56.5) |
| PASS (a) τ̂ ≤ 5.5 | no | no |
| PASS (b) cells off > 10 beyond noise | BvSc, HvL, SvV, SuvV | AvL, SvV |
| PASS (c) decks off > 6 | Altaria, Hydreigon, Sceptile, Vespiquen | Sceptile, Vespiquen |
| reported only: correlation / average miss / favorites right | 0.66 / 9.6 / 22 of 27 | 0.74 / 8.4 / 22 of 27 |

Deck averages (k3 → b3n1, Limitless):
- Altaria 46.6 → 49.0 (54.0)
- Blaziken 56.4 → 56.4 (57.7)
- Hydreigon 34.6 → 46.4 (42.5)
- Lucario 52.5 → 52.3 (50.2)
- Sceptile 62.1 → 57.8 (48.2)
- Suicune 52.9 → 47.2 (48.2)
- Vespiquen 48.1 → 46.0 (56.5)
- Weezing 46.6 → 44.7 (42.7)

## Reading, plainly

- **The guess helps the table overall, and the paired interval says it is real.** Hydreigon, Sceptile, Suicune and Altaria all move toward Limitless. b3n1 costs about the same as k3.
- **The vetoes are narrow but not noise.** With paired data at 500 deals, a pilot that changes nothing trips a cell veto about 1% of the time and a deck veto about 3% (simulated tonight). What they flag is redistribution:
  - Pricing Darkness Claw and Copycat lifts Hydreigon in every cell. That is right on average: its deck gap shrinks from −7.9 to +3.9.
  - It is wrong against Altaria, which is itself still underrated everywhere, for a cause not yet found. The Sleep clock was ruled out tonight.
  - So the Altaria v Hydreigon veto is probably collateral from Altaria's open blind spot, not a flaw in the guess.
  - Vespiquen gets slightly worse: its opponents now price Copycat, and Vespiquen's own miss is unexplained.
- **What would change the verdict:**
  - kp3 (the same pricing with no list) could land differently. Its table is next.
  - The mixed Hydreigon rows separate "Hydreigon plays better" from "its opponents play worse".
  - Finding Altaria's blind spot could make the Altaria v Hydreigon veto disappear. The candidates are the network-divergence mining (B2c), and the Weakness and status features before the weight fit (B3).
- **The rule is Dustin's to keep or loosen.** The vetoes were set before any results. Loosening them after seeing this table would be tuning to it. The honest options are:
  - keep them, and wait for kp3 and the Altaria work;
  - or decide deliberately, in advance of the next table, that a veto on a cell adjacent to an unexplained deck-level miss counts differently.

## Full output of score.py

```
Reading: b3n1 (new) against k3 (current), 28 common pairings.
Source: /tmp/pds_reading/k3_500.jsonl (current) vs /tmp/pds_reading/b3n1_500.jsonl (new), paired by deal

== all cells: 28 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.7, favorite right 23/28, clear 14/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
        b3n1: real error  9.1 | reported only: correlation 0.74, average miss 8.3, favorite right 23/28, clear 15/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: altaria v lucario, sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
  dMSE new - current: -48.2 points^2, 95% interval -84.3 to -10.5 (below 0)
  real error, current minus new: +2.35 points, 90% interval +0.72 to +3.39 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +6.1
  deck veto (gap grows > 2): vespiquen +2.1
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  46.6 /  49.0 /  54.0   -2.3
     blaziken:  56.4 /  56.4 /  57.7   -0.0
    hydreigon:  34.6 /  46.4 /  42.5   -4.0
      lucario:  52.5 /  52.3 /  50.2   -0.2
     sceptile:  62.1 /  57.8 /  48.2   -4.3
      suicune:  52.9 /  47.2 /  48.2   -3.7
    vespiquen:  48.1 /  46.0 /  56.5   +2.1
      weezing:  46.6 /  44.7 /  42.7   -1.9

== decision set (Altaria v Sceptile quarantined): 27 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.6, favorite right 22/27, clear 14/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
        b3n1: real error  9.2 | reported only: correlation 0.74, average miss 8.4, favorite right 22/27, clear 15/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: altaria v lucario, sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
  dMSE new - current: -46.8 points^2, 95% interval -84.7 to -7.5 (below 0)
  real error, current minus new: +2.26 points, 90% interval +0.63 to +3.37 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +6.1
  deck veto (gap grows > 2): vespiquen +2.1
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  48.1 /  50.0 /  54.8   -1.9
     blaziken:  56.4 /  56.4 /  57.7   -0.0
    hydreigon:  34.6 /  46.4 /  42.5   -4.0
      lucario:  52.5 /  52.3 /  50.2   -0.2
     sceptile:  62.1 /  57.9 /  47.7   -4.2
      suicune:  52.9 /  47.2 /  48.2   -3.7
    vespiquen:  48.1 /  46.0 /  56.5   +2.1
      weezing:  46.6 /  44.7 /  42.7   -1.9

Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)
    altaria v blaziken    56.0 |  59.4 |  74.2 ±  8.8 | -3.4
    altaria v hydreigon   57.8 |  50.2 |  57.0 ±  8.4 | +6.1
    altaria v lucario     56.6 |  54.6 |  71.9 ±  4.9 | +2.0
    altaria v sceptile    37.8 |  42.8 |  49.1 ±  6.6 | -5.0  (quarantined)
    altaria v suicune     39.2 |  48.8 |  52.3 ±  8.0 | -9.6
    altaria v vespiquen   42.6 |  47.6 |  38.8 ±  6.8 | +5.0
    altaria v weezing     36.5 |  39.4 |  34.8 ±  9.2 | +2.9
   blaziken v hydreigon   64.5 |  52.1 |  59.0 ± 12.3 | +1.4
   blaziken v lucario     46.5 |  48.3 |  44.8 ±  8.1 | +1.8
   blaziken v sceptile    59.6 |  69.1 |  82.8 ±  9.0 | -9.5
   blaziken v suicune     53.0 |  56.6 |  60.8 ± 12.4 | -3.6
   blaziken v vespiquen   79.5 |  83.8 |  81.4 ± 12.9 | +0.4
   blaziken v weezing     47.9 |  44.6 |  49.0 ± 14.1 | +3.3
  hydreigon v lucario     30.6 |  42.8 |  54.4 ±  8.0 | -12.2
  hydreigon v sceptile    27.8 |  44.6 |  39.4 ± 10.7 | -6.3
  hydreigon v suicune     38.8 |  44.8 |  34.7 ± 11.8 | +6.0
  hydreigon v vespiquen   30.8 |  42.6 |  38.4 ±  9.8 | -3.4
  hydreigon v weezing     36.8 |  52.6 |  47.1 ± 13.7 | -4.7
    lucario v sceptile    33.6 |  35.8 |  37.9 ±  6.3 | -2.2
    lucario v suicune     53.0 |  57.2 |  58.5 ±  7.7 | -4.2
    lucario v vespiquen   64.2 |  64.6 |  69.3 ±  6.4 | -0.4
    lucario v weezing     50.4 |  54.4 |  56.6 ±  8.3 | -4.0
   sceptile v suicune     56.6 |  62.0 |  47.2 ±  9.5 | +5.4
   sceptile v vespiquen   66.6 |  64.6 |  33.1 ±  8.2 | -2.0
   sceptile v weezing     70.4 |  70.4 |  66.2 ± 10.4 | +0.0
    suicune v vespiquen   50.4 |  42.6 |  27.0 ±  7.7 | -7.8
    suicune v weezing     60.8 |  57.4 |  64.2 ± 10.4 | +3.4
  vespiquen v weezing     70.9 |  68.0 |  83.5 ±  7.9 | +2.9
```
