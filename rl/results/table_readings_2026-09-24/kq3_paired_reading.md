# Paired readings: kq3 vs k3 (adoption) and kq3 vs kp3 (do the B5 habits help over kp?), Sept 25

Decision this informs: whether the two B5 habits go into the pilot on top of kp. **Under the pre-set adoption rule: not adopted.** Against kp3 it is **reliably worse**.

Diagnostic only; never for ranking decks.

**Source:**
- The per-game file `rl/results/kq_2026-09-25/kq3_500.jsonl` on branch `claude/pensive-ptolemy-spwc0b` (commit 434c46c; legality_scan at ba20dd8, no rule findings).
- All 28 pairings × the table's first 500 deals, paired with `k3_500` and `kp3_500` as in the kp3 reading.
- kq3 here is the cloud's rework at ba20dd8. Its spec was fixed in the commit messages before any kq table (a188c14, 440e239, ba20dd8):
  - next-attack reduction in the threat clock;
  - 250 × the best benched attacker's readiness.
- The rework fixes two of the three spec flaws the tier-1 read of a188c14 found: ties by slot, and the attacker pick switching. The third, the promotion cost with a free-attack Active, is still open and was not measured.

**How it was read:** `score.py`, paired mode, 4,000 replicates, Altaria v Sceptile quarantined.

## Numbers (decision set, 27 cells)

| | k3 | kp3 | kq3 |
|---|---|---|---|
| real error τ̂ | 11.5 | 9.3 | 11.1 |
| ΔMSE, kq3 − k3, 95% | | | −9.0 (−54.8 to +37.9): not below 0 |
| ΔMSE, kq3 − kp3, 95% | | | **+36.5 (+13.2 to +59.9): worse** |
| cell vetoes vs k3 (> 6) | | | Altaria v Hydreigon +10.7, Altaria v Vespiquen +9.6, Blaziken v Hydreigon +6.2, Hydreigon v Suicune +12.0, Sceptile v Suicune +9.0, Vespiquen v Weezing +6.6 |
| deck veto vs k3 (> 2) | | | Vespiquen +5.9 |
| PASS (c): decks off > 6 | Altaria, Hydreigon, Sceptile, Vespiquen | Sceptile, Vespiquen | Hydreigon, Sceptile, Vespiquen |

Deck averages (all cells), k3 / kp3 / kq3 (Limitless):
- Altaria 46.6 / 49.7 / 50.2 (54.0)
- Blaziken 56.4 / 55.6 / 57.5 (57.7)
- Hydreigon 34.6 / 47.4 / 49.7 (42.5)
- Lucario 52.5 / 52.0 / 53.8 (50.2)
- Sceptile 62.1 / 58.3 / 60.1 (48.2)
- Suicune 52.9 / 46.5 / 44.6 (48.2)
- Vespiquen 48.1 / 45.8 / 42.2 (56.5)
- Weezing 46.6 / 44.7 / 41.9 (42.7)

## Reading, plainly

- **The habits do what they were built to do, and on this table that is mostly the wrong direction.**
  - Lucario, Blaziken, Hydreigon and Sceptile go up: the decks that build an attacker behind a cheap front Pokémon.
  - Hydreigon and Sceptile were already overrated.
  - Lucario v Weezing, where the Lucario network's divergences found the habits, moves 52.8 → 62.8, past Limitless's 56.6. The habits copy the network's direction and overshoot.
- **Vespiquen gets worse again,** 45.8 → 42.2 against 56.5.
  - A mechanism, not tested: Chase Order discards a benched Basic [G] Pokémon for +70. Combee is a benched attacker under kq's filter, so when it holds the bench maximum, kq charges up to 250 for the discard.
  - Any bench-readiness term taxes decks that spend their Bench.
  - Counting Chase Order discards, kq3 vs kp3, would test it.
- **kv (kq v2) shares the bench-readiness core.** With kq3 reliably worse than kp3, kv is not worth its multiple-comparisons cost. It is not built, unless Dustin wants it.
  - The cloud offered a per-feature split (each habit alone, two new player codes) as a diagnostic. That is Dustin's call.
- **The rule is unchanged, and so is the pilot:** k3 stays the frozen table pilot.

## Full output of score.py

### kq3 vs k3

```
Reading: kq3 (new) against k3 (current), 28 common pairings.
Source: /tmp/pds_reading/k3_500.jsonl (current) vs /tmp/pds_reading/kq3_500.jsonl (new), paired by deal

== all cells: 28 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.7, favorite right 23/28, clear 14/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
         kq3: real error 10.9 | reported only: correlation 0.64, average miss 9.4, favorite right 19/28, clear 13/16, beyond chance 12
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen, vespiquen v weezing | (c) decks off by >6: hydreigon, sceptile, vespiquen
  dMSE new - current: -11.9 points^2, 95% interval -57.9 to +33.4 (not below 0)
  real error, current minus new: +0.53 points, 90% interval -1.06 to +2.07 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +10.7, altaria v vespiquen +9.6, blaziken v hydreigon +6.2, hydreigon v suicune +12.0, sceptile v suicune +9.0, vespiquen v weezing +6.6
  deck veto (gap grows > 2): vespiquen +5.9
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  46.6 /  50.2 /  54.0   -3.6
     blaziken:  56.4 /  57.5 /  57.7   -1.1
    hydreigon:  34.6 /  49.7 /  42.5   -0.8
      lucario:  52.5 /  53.8 /  50.2   +1.3
     sceptile:  62.1 /  60.1 /  48.2   -2.1
      suicune:  52.9 /  44.6 /  48.2   -1.1
    vespiquen:  48.1 /  42.2 /  56.5   +5.9
      weezing:  46.6 /  41.9 /  42.7   -3.2

== decision set (Altaria v Sceptile quarantined): 27 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.6, favorite right 22/27, clear 14/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
         kq3: real error 11.1 | reported only: correlation 0.65, average miss 9.6, favorite right 18/27, clear 13/16, beyond chance 12
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen, vespiquen v weezing | (c) decks off by >6: hydreigon, sceptile, vespiquen
  dMSE new - current: -9.0 points^2, 95% interval -54.8 to +37.9 (not below 0)
  real error, current minus new: +0.40 points, 90% interval -1.19 to +1.89 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +10.7, altaria v vespiquen +9.6, blaziken v hydreigon +6.2, hydreigon v suicune +12.0, sceptile v suicune +9.0, vespiquen v weezing +6.6
  deck veto (gap grows > 2): vespiquen +5.9
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  48.1 /  51.4 /  54.8   -3.3
     blaziken:  56.4 /  57.5 /  57.7   -1.1
    hydreigon:  34.6 /  49.7 /  42.5   -0.8
      lucario:  52.5 /  53.8 /  50.2   +1.3
     sceptile:  62.1 /  60.6 /  47.7   -1.5
      suicune:  52.9 /  44.6 /  48.2   -1.1
    vespiquen:  48.1 /  42.2 /  56.5   +5.9
      weezing:  46.6 /  41.9 /  42.7   -3.2

Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)
    altaria v blaziken    56.0 |  57.3 |  74.2 ±  8.8 | -1.3
    altaria v hydreigon   57.8 |  45.6 |  57.0 ±  8.4 | +10.7
    altaria v lucario     56.6 |  59.8 |  71.9 ±  4.9 | -3.2
    altaria v sceptile    37.8 |  43.0 |  49.1 ±  6.6 | -5.2  (quarantined)
    altaria v suicune     39.2 |  52.8 |  52.3 ±  8.0 | -12.7
    altaria v vespiquen   42.6 |  52.2 |  38.8 ±  6.8 | +9.6
    altaria v weezing     36.5 |  40.8 |  34.8 ±  9.2 | +4.3
   blaziken v hydreigon   64.5 |  47.3 |  59.0 ± 12.3 | +6.2
   blaziken v lucario     46.5 |  48.4 |  44.8 ±  8.1 | +1.9
   blaziken v sceptile    59.6 |  65.2 |  82.8 ±  9.0 | -5.6
   blaziken v suicune     53.0 |  64.2 |  60.8 ± 12.4 | -4.5
   blaziken v vespiquen   79.5 |  84.2 |  81.4 ± 12.9 | +0.8
   blaziken v weezing     47.9 |  50.8 |  49.0 ± 14.1 | +0.8
  hydreigon v lucario     30.6 |  44.6 |  54.4 ±  8.0 | -14.0
  hydreigon v sceptile    27.8 |  43.0 |  39.4 ± 10.7 | -7.9
  hydreigon v suicune     38.8 |  50.8 |  34.7 ± 11.8 | +12.0
  hydreigon v vespiquen   30.8 |  49.2 |  38.4 ±  9.8 | +3.2
  hydreigon v weezing     36.8 |  53.2 |  47.1 ± 13.7 | -4.1
    lucario v sceptile    33.6 |  34.0 |  37.9 ±  6.3 | -0.4
    lucario v suicune     53.0 |  60.8 |  58.5 ±  7.7 | -3.3
    lucario v vespiquen   64.2 |  71.8 |  69.3 ±  6.4 | -2.6
    lucario v weezing     50.4 |  62.8 |  56.6 ±  8.3 | -0.0
   sceptile v suicune     56.6 |  65.6 |  47.2 ±  9.5 | +9.0
   sceptile v vespiquen   66.6 |  68.2 |  33.1 ±  8.2 | +1.6
   sceptile v weezing     70.4 |  71.8 |  66.2 ± 10.4 | +1.4
    suicune v vespiquen   50.4 |  43.4 |  27.0 ±  7.7 | -7.0
    suicune v weezing     60.8 |  63.1 |  64.2 ± 10.4 | -2.3
  vespiquen v weezing     70.9 |  64.3 |  83.5 ±  7.9 | +6.6
```

### kq3 vs kp3

```
Reading: kq3 (new) against kp3 (current), 28 common pairings.
Source: /tmp/pds_reading/kp3_500.jsonl (current) vs /tmp/pds_reading/kq3_500.jsonl (new), paired by deal

== all cells: 28 pairings
         kp3: real error  9.2 | reported only: correlation 0.74, average miss 7.9, favorite right 21/28, clear 15/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
         kq3: real error 10.9 | reported only: correlation 0.64, average miss 9.4, favorite right 19/28, clear 13/16, beyond chance 12
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen, vespiquen v weezing | (c) decks off by >6: hydreigon, sceptile, vespiquen
  dMSE new - current: +35.1 points^2, 95% interval +11.9 to +58.0 (not below 0)
  real error, current minus new: -1.75 points, 90% interval -2.36 to -0.72 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): hydreigon v vespiquen +8.2
  deck veto (gap grows > 2): hydreigon +2.3, vespiquen +3.6
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  49.7 /  50.2 /  54.0   -0.5
     blaziken:  55.6 /  57.5 /  57.7   -2.0
    hydreigon:  47.4 /  49.7 /  42.5   +2.3
      lucario:  52.0 /  53.8 /  50.2   +1.8
     sceptile:  58.3 /  60.1 /  48.2   +1.8
      suicune:  46.5 /  44.6 /  48.2   +1.9
    vespiquen:  45.8 /  42.2 /  56.5   +3.6
      weezing:  44.7 /  41.9 /  42.7   -1.3

== decision set (Altaria v Sceptile quarantined): 27 pairings
         kp3: real error  9.3 | reported only: correlation 0.74, average miss 8.0, favorite right 20/27, clear 15/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
         kq3: real error 11.1 | reported only: correlation 0.65, average miss 9.6, favorite right 18/27, clear 13/16, beyond chance 12
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen, vespiquen v weezing | (c) decks off by >6: hydreigon, sceptile, vespiquen
  dMSE new - current: +36.5 points^2, 95% interval +13.2 to +59.9 (not below 0)
  real error, current minus new: -1.79 points, 90% interval -2.43 to -0.76 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): hydreigon v vespiquen +8.2
  deck veto (gap grows > 2): hydreigon +2.3, vespiquen +3.6, sceptile +2.1
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  50.9 /  51.4 /  54.8   -0.5
     blaziken:  55.6 /  57.5 /  57.7   -2.0
    hydreigon:  47.4 /  49.7 /  42.5   +2.3
      lucario:  52.0 /  53.8 /  50.2   +1.8
     sceptile:  58.5 /  60.6 /  47.7   +2.1
      suicune:  46.5 /  44.6 /  48.2   +1.9
    vespiquen:  45.8 /  42.2 /  56.5   +3.6
      weezing:  44.7 /  41.9 /  42.7   -1.3

Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)
    altaria v blaziken    58.6 |  57.3 |  74.2 ±  8.8 | +1.3
    altaria v hydreigon   47.6 |  45.6 |  57.0 ±  8.4 | +2.0
    altaria v lucario     62.4 |  59.8 |  71.9 ±  4.9 | +2.6
    altaria v sceptile    42.8 |  43.0 |  49.1 ±  6.6 | -0.2  (quarantined)
    altaria v suicune     48.8 |  52.8 |  52.3 ±  8.0 | -3.1
    altaria v vespiquen   47.4 |  52.2 |  38.8 ±  6.8 | +4.8
    altaria v weezing     40.4 |  40.8 |  34.8 ±  9.2 | +0.4
   blaziken v hydreigon   48.0 |  47.3 |  59.0 ± 12.3 | +0.7
   blaziken v lucario     45.1 |  48.4 |  44.8 ±  8.1 | +3.3
   blaziken v sceptile    65.1 |  65.2 |  82.8 ±  9.0 | -0.1
   blaziken v suicune     59.6 |  64.2 |  60.8 ± 12.4 | +2.1
   blaziken v vespiquen   81.4 |  84.2 |  81.4 ± 12.9 | +2.7
   blaziken v weezing     48.4 |  50.8 |  49.0 ± 14.1 | +1.3
  hydreigon v lucario     43.8 |  44.6 |  54.4 ±  8.0 | -0.8
  hydreigon v sceptile    43.6 |  43.0 |  39.4 ± 10.7 | -0.6
  hydreigon v suicune     46.4 |  50.8 |  34.7 ± 11.8 | +4.4
  hydreigon v vespiquen   41.0 |  49.2 |  38.4 ±  9.8 | +8.2
  hydreigon v weezing     52.8 |  53.2 |  47.1 ± 13.7 | +0.4
    lucario v sceptile    35.6 |  34.0 |  37.9 ±  6.3 | +1.6
    lucario v suicune     58.8 |  60.8 |  58.5 ±  7.7 | +2.0
    lucario v vespiquen   68.2 |  71.8 |  69.3 ±  6.4 | +1.4
    lucario v weezing     52.8 |  62.8 |  56.6 ±  8.3 | +2.4
   sceptile v suicune     60.6 |  65.6 |  47.2 ±  9.5 | +5.0
   sceptile v vespiquen   64.4 |  68.2 |  33.1 ±  8.2 | +3.8
   sceptile v weezing     70.0 |  71.8 |  66.2 ± 10.4 | +1.8
    suicune v vespiquen   43.0 |  43.4 |  27.0 ±  7.7 | +0.4
    suicune v weezing     56.5 |  63.1 |  64.2 ± 10.4 | -6.6
  vespiquen v weezing     65.9 |  64.3 |  83.5 ±  7.9 | +1.6
```
