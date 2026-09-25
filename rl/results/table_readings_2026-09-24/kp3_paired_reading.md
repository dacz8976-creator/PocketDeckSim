# Paired readings: kp3 vs k3 (adoption), and b3n1 vs kp3 (the cost of going list-free), Sept 25

Decision this informs: whether kp3 becomes the default pilot. **Under the pre-set adoption rule: not adopted.**
- The overall gain is clear.
- Three vetoes fire: the Altaria v Hydreigon miss grows 8.7, the Hydreigon v Suicune miss grows 7.6, and the Vespiquen deck gap grows 2.3.
- Whether to override is **Dustin's call alone.** The case for and against is below.

Diagnostic only; never for ranking decks.

**Source:** per-game files on branch `claude/pensive-ptolemy-spwc0b`
- `per_game_table_2026-09-25/k3_500.jsonl` (9922410) and `b3n1_500.jsonl` (546c3ad), with legality_scan at e18ab4b.
- `public_pricing_2026-09-25/kp3_500_worst5.jsonl` (a335ce1) and `kp3_500_rest.jsonl` (150a305), with kp3 at 858b6fe. At c7cb688 (the audited allowlist), kp3 replays these games move for move.
- All 28 pairings × the table's first 500 deals (seed = 72,000,000 + pairing × 10,000 + i). The two kp3 files join to 14,000 distinct (pairing, deal) pairs.

**kp3's tier-1 status:**
- The read found it SOUND: no leak, and k3 bit-identical when it is off.
- Both follow-up conditions are met at c7cb688: a test through get_player, and the rule lifted only for the 62 audited texts.
- Known bias: payoffs that need a specific hidden card get no credit (Penny, Portrait, Team Rocket's Boss, Miraculous Memory, the random Item discard).

**How it was read:** `score.py`, paired mode, 4,000 replicates, with Altaria v Sceptile quarantined.

## kp3 vs k3 (decision set, 27 cells)

| | k3 | kp3 |
|---|---|---|
| real error τ̂ | 11.5 | 9.3 |
| improvement, 90% interval | | +2.19 (+0.53 to +3.35) |
| ΔMSE, 95% interval | | −45.5 (−84.4 to −4.8): **below 0** |
| cell vetoes (> 6) | | **Altaria v Hydreigon +8.7, Hydreigon v Suicune +7.6** |
| deck veto (> 2) | | **Vespiquen +2.3** |
| PASS (b): cells off > 10 beyond noise | BvSc, HvL, SvV, SuvV | SvV |
| PASS (c): decks off > 6 | Altaria, Hydreigon, Sceptile, Vespiquen | Sceptile, Vespiquen |
| reported only: correlation / average miss / favorites right | 0.66 / 9.6 / 22 of 27 | 0.74 / 8.0 / 20 of 27 |

Deck averages (all cells), k3 → kp3 (Limitless):
- Altaria 46.6 → 49.7 (54.0)
- Blaziken 56.4 → 55.6 (57.7)
- Hydreigon 34.6 → 47.4 (42.5)
- Lucario 52.5 → 52.0 (50.2)
- Sceptile 62.1 → 58.3 (48.2)
- Suicune 52.9 → 46.5 (48.2)
- Vespiquen 48.1 → 45.8 (56.5)
- Weezing 46.6 → 44.7 (42.7)

## b3n1 vs kp3: what the list adds (margin rule quantity)

- **Real error: b3n1 is better than kp3 by only 0.07 points** (90% interval −0.70 to +0.83). ΔMSE is −1.3 (95% −21.5 to +17.8).
- **Going list-free costs nothing measurable on this table.** Every deck average is within about a point.
- **The one cell where they differ is Altaria v Lucario:** b3n1's miss is 7.8 larger than kp3's.
- **Most of option B's effect is the pricing.** kp3 gets it without assuming anyone's decklist, which is the property a brew tester needs: the meta side never plays around the brew's exact tech.

## What the mixed rows say about the vetoes

The Hydreigon mixed rows (e31b536): across Hydreigon's seven cells, with b3n1:

| | Hydreigon's score | change |
|---|---|---|
| k3 both sides | 34.6 | |
| b3n1 both sides | 46.4 | +11.8 |
| b3n1 Hydreigon v k3 opponent | 49.7 | +15.0 |
| k3 Hydreigon v b3n1 opponent | 31.5 | −3.1 |

- **The lift is Hydreigon being piloted better** (it prices Darkness Claw and Copycat), not its opponents getting worse.
- So the Altaria v Hydreigon and Hydreigon v Suicune vetoes are a real improvement to Hydreigon, seen from the other side.
- In Altaria v Hydreigon, the real score (57.0) against a better-piloted Hydreigon fits Altaria's own piloting being the weak side. Altaria is still underrated everywhere, with a +7 gap that isn't explained yet; the Sleep clock was ruled out.
- The Lucario network divergence (B2c) found two general habits k3 lacks that are candidates there:
  - an attack that cuts the opponent's next attack, which k3's clock ignores;
  - Energy on a benched main attacker.
- The Vespiquen mixed rows have not been run yet.

## The override question, written plainly (Dustin decides; agents do not)

- **For overriding:**
  - The adoption metric is clearly met: ΔMSE −45.5 (95% −84.4 to −4.8), real error 11.5 → 9.3, at about k3's cost.
  - kp3 is card-agnostic and needs no list, so the gain carries over to brews.
  - The worst known blind spot (Copycat and three other cards scored as doing nothing) is closed.
  - The vetoes were set from noise arguments, not harm arguments.
- **Against:**
  - It lifts Hydreigon everywhere (deck gap −7.9 → +4.9).
  - It widens Vespiquen's gap.
  - Altaria's blind spot is still open. The table would trade one known distortion for another, and three cells get clearly worse.
- **Middle path** (the plan's own order): keep k3 as the frozen table pilot. Meanwhile build B5's first two fixes as evaluation features: the next-attack-reduction clock term, and readiness credit for a benched main attacker. Re-read kp3 with them. If the Altaria cells recover, the vetoes may clear under the rule as set.
- **Any change to the veto thresholds is decided before the table after next, never after a reading.**

## Full output of score.py

### kp3 vs k3

```
Reading: kp3 (new) against k3 (current), 28 common pairings.
Source: /tmp/pds_reading/k3_500.jsonl (current) vs /tmp/pds_reading/kp3_500.jsonl (new), paired by deal

== all cells: 28 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.7, favorite right 23/28, clear 14/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
         kp3: real error  9.2 | reported only: correlation 0.74, average miss 7.9, favorite right 21/28, clear 15/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
  dMSE new - current: -47.0 points^2, 95% interval -85.4 to -8.2 (below 0)
  real error, current minus new: +2.28 points, 90% interval +0.59 to +3.40 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +8.7, hydreigon v suicune +7.6
  deck veto (gap grows > 2): vespiquen +2.3
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  46.6 /  49.7 /  54.0   -3.1
     blaziken:  56.4 /  55.6 /  57.7   +0.9
    hydreigon:  34.6 /  47.4 /  42.5   -3.0
      lucario:  52.5 /  52.0 /  50.2   -0.5
     sceptile:  62.1 /  58.3 /  48.2   -3.8
      suicune:  52.9 /  46.5 /  48.2   -3.0
    vespiquen:  48.1 /  45.8 /  56.5   +2.3
      weezing:  46.6 /  44.7 /  42.7   -1.9

== decision set (Altaria v Sceptile quarantined): 27 pairings
          k3: real error 11.5 | reported only: correlation 0.66, average miss 9.6, favorite right 22/27, clear 14/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: blaziken v sceptile, hydreigon v lucario, sceptile v vespiquen, suicune v vespiquen | (c) decks off by >6: altaria, hydreigon, sceptile, vespiquen
         kp3: real error  9.3 | reported only: correlation 0.74, average miss 8.0, favorite right 20/27, clear 15/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
  dMSE new - current: -45.5 points^2, 95% interval -84.4 to -4.8 (below 0)
  real error, current minus new: +2.19 points, 90% interval +0.53 to +3.35 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v hydreigon +8.7, hydreigon v suicune +7.6
  deck veto (gap grows > 2): vespiquen +2.3
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  48.1 /  50.9 /  54.8   -2.8
     blaziken:  56.4 /  55.6 /  57.7   +0.9
    hydreigon:  34.6 /  47.4 /  42.5   -3.0
      lucario:  52.5 /  52.0 /  50.2   -0.5
     sceptile:  62.1 /  58.5 /  47.7   -3.6
      suicune:  52.9 /  46.5 /  48.2   -3.0
    vespiquen:  48.1 /  45.8 /  56.5   +2.3
      weezing:  46.6 /  44.7 /  42.7   -1.9

Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)
    altaria v blaziken    56.0 |  58.6 |  74.2 ±  8.8 | -2.6
    altaria v hydreigon   57.8 |  47.6 |  57.0 ±  8.4 | +8.7
    altaria v lucario     56.6 |  62.4 |  71.9 ±  4.9 | -5.8
    altaria v sceptile    37.8 |  42.8 |  49.1 ±  6.6 | -5.0  (quarantined)
    altaria v suicune     39.2 |  48.8 |  52.3 ±  8.0 | -9.6
    altaria v vespiquen   42.6 |  47.4 |  38.8 ±  6.8 | +4.8
    altaria v weezing     36.5 |  40.4 |  34.8 ±  9.2 | +3.9
   blaziken v hydreigon   64.5 |  48.0 |  59.0 ± 12.3 | +5.5
   blaziken v lucario     46.5 |  45.1 |  44.8 ±  8.1 | -1.4
   blaziken v sceptile    59.6 |  65.1 |  82.8 ±  9.0 | -5.5
   blaziken v suicune     53.0 |  59.6 |  60.8 ± 12.4 | -6.6
   blaziken v vespiquen   79.5 |  81.4 |  81.4 ± 12.9 | -1.9
   blaziken v weezing     47.9 |  48.4 |  49.0 ± 14.1 | -0.5
  hydreigon v lucario     30.6 |  43.8 |  54.4 ±  8.0 | -13.2
  hydreigon v sceptile    27.8 |  43.6 |  39.4 ± 10.7 | -7.3
  hydreigon v suicune     38.8 |  46.4 |  34.7 ± 11.8 | +7.6
  hydreigon v vespiquen   30.8 |  41.0 |  38.4 ±  9.8 | -5.0
  hydreigon v weezing     36.8 |  52.8 |  47.1 ± 13.7 | -4.5
    lucario v sceptile    33.6 |  35.6 |  37.9 ±  6.3 | -2.0
    lucario v suicune     53.0 |  58.8 |  58.5 ±  7.7 | -5.3
    lucario v vespiquen   64.2 |  68.2 |  69.3 ±  6.4 | -4.0
    lucario v weezing     50.4 |  52.8 |  56.6 ±  8.3 | -2.4
   sceptile v suicune     56.6 |  60.6 |  47.2 ±  9.5 | +4.0
   sceptile v vespiquen   66.6 |  64.4 |  33.1 ±  8.2 | -2.2
   sceptile v weezing     70.4 |  70.0 |  66.2 ± 10.4 | -0.4
    suicune v vespiquen   50.4 |  43.0 |  27.0 ±  7.7 | -7.4
    suicune v weezing     60.8 |  56.5 |  64.2 ± 10.4 | +4.3
  vespiquen v weezing     70.9 |  65.9 |  83.5 ±  7.9 | +5.0
```

### b3n1 (new) vs kp3 (current)

```
Reading: b3n1 (new) against kp3 (current), 28 common pairings.
Source: /tmp/pds_reading/kp3_500.jsonl (current) vs /tmp/pds_reading/b3n1_500.jsonl (new), paired by deal

== all cells: 28 pairings
         kp3: real error  9.2 | reported only: correlation 0.74, average miss 7.9, favorite right 21/28, clear 15/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
        b3n1: real error  9.1 | reported only: correlation 0.74, average miss 8.3, favorite right 23/28, clear 15/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: altaria v lucario, sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
  dMSE new - current: -1.2 points^2, 95% interval -21.0 to +18.4 (not below 0)
  real error, current minus new: +0.07 points, 90% interval -0.70 to +0.83 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v lucario +7.8
  deck veto (gap grows > 2): none
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  49.7 /  49.0 /  54.0   +0.7
     blaziken:  55.6 /  56.4 /  57.7   -0.9
    hydreigon:  47.4 /  46.4 /  42.5   -1.0
      lucario:  52.0 /  52.3 /  50.2   +0.3
     sceptile:  58.3 /  57.8 /  48.2   -0.5
      suicune:  46.5 /  47.2 /  48.2   -0.8
    vespiquen:  45.8 /  46.0 /  56.5   -0.2
      weezing:  44.7 /  44.7 /  42.7   +0.0

== decision set (Altaria v Sceptile quarantined): 27 pairings
         kp3: real error  9.3 | reported only: correlation 0.74, average miss 8.0, favorite right 20/27, clear 15/16, beyond chance 10
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
        b3n1: real error  9.2 | reported only: correlation 0.74, average miss 8.4, favorite right 22/27, clear 15/16, beyond chance 9
              PASS (a) real error <= 5.5: no | (b) cells over by >10 beyond noise: altaria v lucario, sceptile v vespiquen | (c) decks off by >6: sceptile, vespiquen
  dMSE new - current: -1.3 points^2, 95% interval -21.5 to +17.8 (not below 0)
  real error, current minus new: +0.07 points, 90% interval -0.72 to +0.83 (margin rule: E = 3; 'current' is the cheap bot when comparing variants)
  cell veto (miss grows > 6): altaria v lucario +7.8
  deck veto (gap grows > 2): none
  ADOPTION RULE: do not adopt (held-out-deck veto checked separately)

  Deck averages over these cells (current / new / Limitless; change in miss, + = further from Limitless):
      altaria:  50.9 /  50.0 /  54.8   +0.9
     blaziken:  55.6 /  56.4 /  57.7   -0.9
    hydreigon:  47.4 /  46.4 /  42.5   -1.0
      lucario:  52.0 /  52.3 /  50.2   +0.3
     sceptile:  58.5 /  57.9 /  47.7   -0.5
      suicune:  46.5 /  47.2 /  48.2   -0.8
    vespiquen:  45.8 /  46.0 /  56.5   -0.2
      weezing:  44.7 /  44.7 /  42.7   +0.0

Per cell (first deck's score): current | new | Limitless ± 95% | change in miss (+ = further)
    altaria v blaziken    58.6 |  59.4 |  74.2 ±  8.8 | -0.8
    altaria v hydreigon   47.6 |  50.2 |  57.0 ±  8.4 | -2.6
    altaria v lucario     62.4 |  54.6 |  71.9 ±  4.9 | +7.8
    altaria v sceptile    42.8 |  42.8 |  49.1 ±  6.6 | +0.0  (quarantined)
    altaria v suicune     48.8 |  48.8 |  52.3 ±  8.0 | +0.0
    altaria v vespiquen   47.4 |  47.6 |  38.8 ±  6.8 | +0.2
    altaria v weezing     40.4 |  39.4 |  34.8 ±  9.2 | -1.0
   blaziken v hydreigon   48.0 |  52.1 |  59.0 ± 12.3 | -4.1
   blaziken v lucario     45.1 |  48.3 |  44.8 ±  8.1 | +3.2
   blaziken v sceptile    65.1 |  69.1 |  82.8 ±  9.0 | -4.0
   blaziken v suicune     59.6 |  56.6 |  60.8 ± 12.4 | +3.0
   blaziken v vespiquen   81.4 |  83.8 |  81.4 ± 12.9 | +2.3
   blaziken v weezing     48.4 |  44.6 |  49.0 ± 14.1 | +3.8
  hydreigon v lucario     43.8 |  42.8 |  54.4 ±  8.0 | +1.0
  hydreigon v sceptile    43.6 |  44.6 |  39.4 ± 10.7 | +1.0
  hydreigon v suicune     46.4 |  44.8 |  34.7 ± 11.8 | -1.6
  hydreigon v vespiquen   41.0 |  42.6 |  38.4 ±  9.8 | +1.6
  hydreigon v weezing     52.8 |  52.6 |  47.1 ± 13.7 | -0.2
    lucario v sceptile    35.6 |  35.8 |  37.9 ±  6.3 | -0.2
    lucario v suicune     58.8 |  57.2 |  58.5 ±  7.7 | +1.1
    lucario v vespiquen   68.2 |  64.6 |  69.3 ±  6.4 | +3.6
    lucario v weezing     52.8 |  54.4 |  56.6 ±  8.3 | -1.6
   sceptile v suicune     60.6 |  62.0 |  47.2 ±  9.5 | +1.4
   sceptile v vespiquen   64.4 |  64.6 |  33.1 ±  8.2 | +0.2
   sceptile v weezing     70.0 |  70.4 |  66.2 ± 10.4 | +0.4
    suicune v vespiquen   43.0 |  42.6 |  27.0 ±  7.7 | -0.4
    suicune v weezing     56.5 |  57.4 |  64.2 ± 10.4 | -0.9
  vespiquen v weezing     65.9 |  68.0 |  83.5 ±  7.9 | -2.1
```
