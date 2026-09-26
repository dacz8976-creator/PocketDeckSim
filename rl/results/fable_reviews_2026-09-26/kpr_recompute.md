# kpr3 recompute (Fable's review, Sept 26)

Decision this informs: whether kpr (projected readiness for the Active, on top of kp3) goes into the pilot. This file
only checks the cloud's numbers and puts them on the plan's scoreboard. The laptop's rule-v2 reading with the mixed
rows (`../kpr_mixed_rows_2026-09-26/`) decides; those rows had not run when this was written.

## Bottom line, plainly

- **The cloud's readout reproduces.** Its "mean squared miss 176.1 against kp3's 112.2" is on the **Sept 23 Limitless
  table, all 28 cells**, with the Limitless cells taken as the one-decimal percentages printed in
  `limitless_check_2026-09-23.md` (that is what the cloud's `deck_averages.py` reads through `analyze_tables.limitless()`).
  With those rounded cells I get exactly 176.1 / 112.2 (and k3 159.3). With the exact W-L-T fractions that `score.py`
  uses, the same cells give 176.5 / 112.4 / 159.5. Same conclusion either way: kpr3's fit is the worst of the three.
- **On the plan's scoreboard (v2, development half, decision set of 27 cells) kpr3 is reliably worse than kp3.**
  Mean squared miss 131.7 to 206.4; real error 8.6 to 12.2; paired ΔMSE **+74.7 (95% +27.4 to +122.7)**, the whole
  interval above zero; real-error margin (kp3 minus kpr3) **−3.60 (90% −4.33 to −1.44)**. The adoption rule fails on
  the metric itself, before any veto. The reserve route's no-harm test (lower bound at −1.0 or above) fails too.
- **Every per-deck number in the cloud's table reproduces exactly** (Hydreigon +5.8 ± 1.9, Blaziken +4.3 ± 1.7,
  Weezing −4.7 ± 1.7, Altaria −3.0 ± 1.9, Vespiquen −2.9 ± 1.8, Lucario −2.7 ± 1.8, Suicune +2.4 ± 1.8,
  Sceptile +0.9 ± 1.6), as do its twelve "cells that changed most". The Limitless Hydreigon average is 42.5 exact
  (the cloud printed 42.6 from the rounded cells).
- **Veto candidates are many, but whether any counts is the laptop's call**: eight cells grow their miss by more than
  6 and five decks grow their gap by more than 2 on v2. Three of the eight cells (Blaziken v Weezing, Hydreigon v
  Suicune, Hydreigon v Vespiquen) have a Limitless band wider than ±15 on v2 and can never count. The rest await the
  mixed rows. None of this changes the verdict: the ΔMSE interval alone says do not adopt.

## What was recomputed, from what

Script: `rl/results/fable_reviews_2026-09-26/recompute_kpr.py` (this folder). Command used:

```
python recompute_kpr.py --kpr3 <scratchpad>/reviews/branch/kpr3_500.jsonl
```

Output: `recompute_kpr_output.txt` (every cell, every set) and `recompute_kpr_summary.json`.

Inputs, all read only:

| what | file | provenance |
|---|---|---|
| kpr3 table | branch `rl/results/kpr_2026-09-25/kpr3_500.jsonl` (blob 7a33bda…, branch head aa87fa3), copied with `git show` | kpr3 v kpr3, 28 pairings × 500 table deals, engine e09fb46; sha256 19b95ae0… |
| kp3 table | `rl/results/public_pricing_2026-09-25/kp3_500_worst5.jsonl` + `kp3_500_rest.jsonl` (laptop; same blobs on the branch) | the laptop's kp3 reading files; identical field by field (a, b, seed, seats, moves, winner, points, turns, score) to `engine_identity_2026-09-25/kp3_500.jsonl`, 14,000 of 14,000, which is byte-identical (sha256 cc1e1c4f…) to the branch's `identity_kp3_500.jsonl` |
| k3 table | `rl/results/per_game_table_2026-09-25/k3_500.jsonl` | reference row only |
| Limitless, Sept 23 | `rl/results/deep_search_table/deep_table.py` LIMITLESS (W-L-T) | the cells `score.py` uses by default |
| Limitless, v2 | `rl/results/scoreboard_v2_2026-09-25/limitless_v2_dev.json` | development half, 1,608 matches, 58 events |

Note for the task as written: kp3's per-game file is not in `per_game_table_2026-09-25/` (that folder holds k3 and
b3n1); it is the worst5 + rest pair above, and the three copies agree.

Pairing: all 28 pairings, 500 deals each, the same seed on every deal in all three files (72,000,000 + pairing × 10,000
+ i). Cell = the first-named deck's mean score. Definitions follow `score.py` and were re-implemented from scratch:
MSE = mean (S − L)² over cells; real error τ̂ = 100·√max(0, mean[(S − L)² − L(1−L)/n_L − S(1−S)/n_S]); ΔMSE and the
τ̂ margin paired by deal with 4,000 bootstrap replicates (deals resampled within each cell for both bots at once,
Limitless cells redrawn binomially; my resampler draws a multinomial over the (kp3, kpr3) outcome pairs, the same
distribution as `score.py`'s index draws but a different code path and seed).

## The numbers on every cell set

| Limitless cells | set | k3 MSE | kp3 MSE | kpr3 MSE | kp3 τ̂ | kpr3 τ̂ | ΔMSE kpr3 − kp3 (95%) | τ̂ margin kp3 − kpr3 (90%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Sept 23, rounded (the cloud's) | 28 | 159.3 | 112.2 | 176.1 | | | | |
| Sept 23, exact | 28 | 159.5 | 112.4 | 176.5 | 9.2 | 12.2 | +64.1 (+30.1, +98.6) | −3.00 (−3.85, −1.52) |
| Sept 23, exact | 27 (decision) | 160.6 | 115.1 | 181.6 | 9.3 | 12.4 | +66.5 (+31.3, +102.6) | −3.07 (−3.89, −1.56) |
| v2 development half | 28 | 173.2 | 127.2 | 199.3 | 8.4 | 11.9 | +72.1 (+26.2, +119.0) | −3.55 (−4.28, −1.38) |
| **v2 development half** | **27 (decision)** | 177.5 | **131.7** | **206.4** | **8.6** | **12.2** | **+74.7 (+27.4, +122.7)** | **−3.60 (−4.33, −1.44)** |

The bold row is the plan's scoreboard. kp3's 8.6 and k3's 10.9 on it match the laptop's `kp3_vs_k3_v2.txt`, which
checks the τ̂ implementation. Mean |miss| on the bold row: k3 10.39, kp3 9.26, kpr3 11.86.

## Per-deck averages over each deck's opponents

v2 development half, decision set (Altaria and Sceptile have six cells here, the others seven). The paired change is
kpr3 minus kp3 on the deck's own side, all its deals pooled, 95% range.

| deck | Limitless | k3 | kp3 | kpr3 | kpr3 − kp3 | gap change (+ = further from Limitless) |
|---|---:|---:|---:|---:|---:|---:|
| Altaria | 55.0 | 48.1 | 50.9 | 47.4 | −3.5 ± 2.0 | +3.5 |
| Blaziken | 55.9 | 56.4 | 55.6 | 59.8 | +4.3 ± 1.7 | +3.6 |
| Hydreigon | 42.2 | 34.6 | 47.4 | 53.2 | +5.8 ± 1.9 | +5.8 |
| Lucario | 50.4 | 52.5 | 52.0 | 49.3 | −2.7 ± 1.8 | −0.6 |
| Sceptile | 49.7 | 62.1 | 58.5 | 59.5 | +1.0 ± 1.7 | +1.0 |
| Suicune | 47.1 | 52.9 | 46.5 | 48.9 | +2.4 ± 1.8 | +1.2 |
| Vespiquen | 56.6 | 48.1 | 45.8 | 42.9 | −2.9 ± 1.8 | +2.9 |
| Weezing | 43.8 | 46.6 | 44.7 | 40.0 | −4.7 ± 1.7 | +2.8 |

Sept 23 table, all 28 cells (the cloud's set; its table reproduces line for line, Limitless from exact fractions):

| deck | Limitless | k3 | kp3 | kpr3 | kpr3 − kp3 |
|---|---:|---:|---:|---:|---:|
| Altaria | 54.0 | 46.6 | 49.7 | 46.7 | −3.0 ± 1.9 |
| Blaziken | 57.7 | 56.4 | 55.6 | 59.8 | +4.3 ± 1.7 |
| Hydreigon | 42.5 | 34.6 | 47.4 | 53.2 | +5.8 ± 1.9 |
| Lucario | 50.2 | 52.5 | 52.0 | 49.3 | −2.7 ± 1.8 |
| Sceptile | 48.2 | 62.1 | 58.3 | 59.1 | +0.9 ± 1.6 |
| Suicune | 48.2 | 52.9 | 46.5 | 48.9 | +2.4 ± 1.8 |
| Vespiquen | 56.5 | 48.1 | 45.8 | 42.9 | −2.9 ± 1.8 |
| Weezing | 42.7 | 46.6 | 44.7 | 40.0 | −4.7 ± 1.7 |

Reading: seven of eight decks move beyond their paired noise, so kpr's footprint is the whole table, not Hydreigon
alone (the registration warned of this: the turn's attach and next turn's Energy are counted for every Active).
Hydreigon (53.2 against 42.2) and Blaziken (59.8 against 55.9) move further above Limitless; Vespiquen (42.9 against
56.6), Altaria and Weezing further below. Only Lucario moves toward Limitless.

## Cells that moved, and the veto candidates (v2, decision set)

Paired kpr3 − kp3, first-named deck's score, 95% range; then the change in the cell's miss on v2:

- Hydreigon v Vespiquen +15.8 (+10.2, +21.4), miss +15.8 (band ±15.3: never counts)
- Blaziken v Weezing +11.7 (+7.6, +15.8), miss +11.7 (band ±23.4: never counts)
- Blaziken v Lucario +10.9 (+5.8, +16.0), miss +10.9
- Hydreigon v Suicune +9.4 (+4.4, +14.4), miss +9.4 (band ±15.2: never counts)
- Lucario v Suicune −9.2 (−13.8, −4.6), miss +9.2
- Hydreigon v Lucario +8.8 (+4.0, +13.6), miss −8.8 (toward Limitless)
- Suicune v Weezing +8.5 (+4.1, +12.9), miss +1.0
- Altaria v Hydreigon −7.8 (−12.9, −2.7), miss +7.8
- Vespiquen v Weezing +6.8 (+2.1, +11.5), miss −6.8 (toward Limitless)
- Suicune v Vespiquen +6.6 (+1.5, +11.7), miss +6.6
- Altaria v Suicune −6.6 (−11.7, −1.5), miss +6.6
- Altaria v Blaziken −6.0 (−11.0, −1.0), miss +6.0

Cell veto candidates (miss grows by more than 6): Altaria v Hydreigon +7.8, Altaria v Suicune +6.6, Blaziken v
Lucario +10.9, Lucario v Suicune +9.2, Suicune v Vespiquen +6.6, plus the three marked "never counts". Deck veto
candidates (gap grows by more than 2): Hydreigon +5.8, Blaziken +3.6, Altaria +3.5, Vespiquen +2.9, Weezing +2.8.
Under rule v2 each counts only if the mixed rows show kpr3 piloting that deck's own side worse beyond paired noise;
that is the laptop's reading to make. It does not change the verdict here.

## Cross-check with the laptop's own tool

`rl/results/table_readings_2026-09-24/score.py` (the laptop's reading tool) was run on the same files, rule v2,
without mixed rows, twice: `score_v2_kpr3_vs_kp3.txt` (v2 cells, with the by-event interval) and
`score_sept23_kpr3_vs_kp3.txt` (Sept 23 cells). It agrees with the recompute on every point estimate: real errors,
ΔMSE, τ̂ margins, deck averages, the eight cell-veto candidates and the five deck-veto candidates, and the same three
cells marked "never counts". The bootstrap intervals differ by at most 1.0 point², a different random path:

| set | ΔMSE 95%, score.py | by event | τ̂ margin 90%, score.py | by event | recompute (ΔMSE; margin) |
|---|---|---|---|---|---|
| v2, decision set | +28.4 to +123.1 | +29.9 to +123.2 | −4.37 to −1.45 | −4.34 to −1.60 | +27.4 to +122.7; −4.33 to −1.44 |
| v2, all 28 | +25.9 to +117.8 | +26.6 to +119.0 | −4.22 to −1.34 | −4.23 to −1.55 | +26.2 to +119.0; −4.28 to −1.38 |
| Sept 23, decision set | +31.6 to +101.6 | | −3.89 to −1.56 | | +31.3 to +102.6; −3.89 to −1.56 |
| Sept 23, all 28 | +31.3 to +98.4 | | −3.83 to −1.58 | | +30.1 to +98.6; −3.85 to −1.52 |

Its verdict on both tables and both sets: "do not adopt (dMSE interval not below 0)". Every veto candidate that is not
"never counts" reads "AWAITS mixed rows", which is the laptop's next step, and which cannot change the verdict here.
Reported only: kpr3 gets the favorite right in 15 of 27 cells against kp3's 20, and correlation falls 0.71 to 0.50.

## What this does and does not say

- It confirms the cloud's arithmetic and puts kpr3 on the scoreboard the plan uses. It is not the reading; the reading
  is the laptop's, with the mixed rows, under rule v2.
- Under the plan's rules kpr3 as built cannot be adopted as the table pilot: ΔMSE against kp3 is above zero with 95%
  confidence on v2 (and on the Sept 23 cells), and the τ̂ margin is below −1.0 with 90% confidence, so the reserve
  route's no-harm test fails as well.
- The registered reading still applies for what kpr was built for: Hyper Ray without a knockout goes from 21% to 90%
  (the cloud's counts in `kpr3_500.txt`; not recounted here), which is the network's and the searched bots' play. A
  change that is right by the rules and moves Hydreigon further from Limitless points at the other side of those
  matchups (or the population), not at undoing the change. What the mixed rows can add is whether Hydreigon's own side
  gains under kpr3 and its opponents' side loses; the table alone cannot separate the two.
- Not checked here: the kpr code, the identity replays, the mutation results, or the Hyper Ray counts.
