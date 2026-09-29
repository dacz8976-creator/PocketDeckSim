# ANALYSIS

This is the report on the 45-cell ΔMSE power analysis. It ran read-only: nothing was written in the repo, no kt file and no holdout file was opened, and no game or engine was run. I reproduced every past point estimate exactly (koh −45.1, kog3 vs kp3 −43.1, kpf −84.2, kpr −84.7, kpg −43.2, kog3 vs kpg3 +0.1; τ̂ 14.0 and 12.3). Intervals come out within Monte-Carlo error of the printed ones (koh −100.3 to +10.0, printed −100.4 to +10.4).

**Headline**
- The half-width of the ΔMSE interval runs from ±5.8 to ±65 depending on how much a candidate moves cells. It is a property of the candidate, not one fixed number.
- For koh the Limitless side dominates: 79% of the variance, and 73% of that sits in the nine Rayquaza cells.
- For small-footprint candidates (kog3 or kpg3 vs kp3) the simulator side is larger, about 65% of the variance.
- A koh-like candidate needs a true ΔMSE of −55 (real error 14.05 → 11.9) to clear zero half the time, and −79 (→ 10.9) to clear 80% of the time. koh's own estimate was −45. If that were the truth, a fresh table would clear about 34–36% of the time. The right wording stays "not confirmed at this size".

**Method**
- score45.py hands score.py the 45 cells. ΔMSE = mean over cells of (N−L)² − (O−L)² (N new, O current, L Limitless). The bootstrap redraws each Limitless cell as Binomial(nL, L)/nL and resamples the simulator by deal, paired. The by-event version redraws Limitless by tournament event instead.
- ΔMSE_k = d_k·(N_k + O_k − 2L_k) with d_k = N_k − O_k, so it is exactly linear in L. Limitless noise therefore enters only through d_k, the candidate's own movement of that cell.
- Simulator side: per cell, sd = (2/K)·sd of [(N−L)·N_i − (O−L)·O_i] over deals, divided by √500. This is mostly |N−L|·sd(paired difference).
- Limitless side: per cell, sd = (2|d_k|/K)·√(L(1−L)/nL).
- Cross term: (2/K)²·(VarD/n)·L(1−L)/nL.
- Total variance is the sum of the three. A resampling check with each side alone agrees within about 2% of the sd, and the brute-force run described further down agrees with the Normal power rule within about 2 points.

**1. Which side limits the interval (points²)**

| Reading | ΔMSE | sd sim | sd Limitless | cross | total sd | Limitless share of variance | ± both (printed score45 ±) | ± sim only | ± Limitless only | cells: sim larger / Limitless larger / no movement |
|---|---|---|---|---|---|---|---|---|---|---|
| koh3 vs kog3 | −45.1 | 11.6 | 25.0 | 5.8 | 28.2 | 79% | 55.3 (55.4) | 22.8 | 49.1 | 20 / 25 / 0 |
| kpf3 vs kp3 | −84.2 | 12.3 | 30.0 | 6.0 | 33.0 | 83% | 64.6 (64.3) | 24.2 | 58.8 | 20 / 25 / 0 |
| kpr3 vs kp3 | −84.7 | 12.2 | 29.6 | 6.0 | 32.6 | 83% | 63.9 (64.4) | 24.0 | 58.1 | 20 / 25 / 0 |
| kog3 vs kp3 | −43.1 | 7.0 | 5.5 | 2.8 | 9.3 | 35% | 18.3 (18.5) | 13.7 | 10.8 | 13 / 11 / 21 |
| kpg3 vs kp3 | −43.2 | 6.8 | 5.1 | 2.6 | 8.9 | 33% | 17.4 (17.9) | 13.2 | 10.0 | 12 / 5 / 28 |
| kog3 vs kpg3 | +0.1 | 1.8 | 2.0 | 1.0 | 2.9 | 49% | 5.7 (5.8) | 3.5 | 4.0 | 3 / 6 / 36 |

- koh arithmetic: 11.6² + 25.0² + 5.8² = 135.5 + 626.8 + 33.9 = 796, so sd = 28.2 and ±1.96·28.2 = ±55.3. Alone, the simulator side gives interval −67.8 to −22.2 (width 45.6) and the Limitless side gives −94.0 to +4.1 (width 98.1).
- Resampling Limitless by event instead gives koh −102.2 to +11.4, and its Limitless-only variance is 658 against 624 binomial. Event clustering changes little.
- koh cell by cell (sd of the cell's part of ΔMSE, Limitless vs simulator):
  - Limitless dominates in the Rayquaza cells: v vespiquen 9.4 vs 3.2, v blaziken 9.2 vs 1.9, v suicune 8.1 vs 1.5, v weezing 7.9 vs 1.8, v Altaria/Greninja 7.6 vs 1.8, v hydreigon 7.6 vs 1.2. Also blaziken v weezing 5.7 vs 1.4 and hydreigon v vespiquen 4.9 vs 1.7.
  - The top 6 cells carry 66.5% of the Limitless variance, and the top 10 carry 83%.
  - The simulator dominates in cells with a huge miss that koh barely moved: Altaria/Greninja v sceptile 3.3 vs 0.4, A/G v blaziken 3.0 vs 0.8, sceptile v vespiquen 2.9 vs 0.06.
- Worked example, Rayquaza v Vespiquen: kog3 25.2 → koh3 51.2 (d = +26.0), Limitless 61.1% on 36 matches.
  - Limitless side: cell sd = 100·√(0.611·0.389/36) = 8.1, weight 2·26.0/45 = 1.156, so the cell's part is 9.39.
  - Simulator side: 2·9.9/45·63/√500 = 1.24 (miss term) and 2·26.0/45·43/√500 = 2.25 (level term), 3.16 together with their covariance.
- Worked example, A/G v Sceptile: d = −1.2, so the Limitless part is 2·1.2/45·8.2 = 0.44. The simulator part is 2·36.9/45·46/√500 = 3.34, 3.29 with the small level term.
- By group of cells, Rayquaza's 9 cells carry these shares of the Limitless variance: koh 73%, kpf 84%, kpr 83%, kog3 vs kp3 86%, kpg3 vs kp3 99%.
- Simulator variance is more spread out. In koh it is Rayquaza 31%, A/G 29%, panel 40%.
- Paired per-deal difference: 29–31% of deals differ in score for koh, kpf and kpr (sd about 54 points per deal). For kog3 vs kp3 it is 6%, for kpg3 vs kp3 4%, and for kog3 vs kpg3 2%.

**2. Minimum detectable effect**

The interval clears zero when the estimate + 1.96·sd < 0. At true effect T, the chance of clearing is Φ((|T| − 1.96·sd)/sd). That gives 50% at 1.96·sd and 80% at 2.80·sd. The bootstrap skew is at most 0.2. Real error after = √(14.05² − δ), because ΔMSE ≈ Δτ̂² (koh: 12.33² − 14.05² = −45.4).

A: plug-in, a future candidate that moves the 45 cells as each past one did:

| Configuration | koh-like MDE50 → real error | koh-like MDE80 → real error | small-footprint (kog3 vs kp3-like) MDE50 → real error | small MDE80 → real error |
|---|---|---|---|---|
| now (500 deals, 2,214 matches) | 55.3 → 11.92 | 79.1 → 10.88 | 18.3 → 13.38 | 26.1 → 13.09 |
| simulator ×2 | 52.3 → 12.05 | 74.7 → 11.08 | 15.0 → 13.51 | 21.4 → 13.27 |
| simulator ×4 | 50.7 → 12.11 | 72.5 → 11.18 | 13.0 → 13.58 | 18.6 → 13.37 |
| Limitless ×0.5 (post-freeze read alone, 1,107) | 74.8 → 11.07 | 106.9 → 9.51 | 21.9 → 13.25 | 31.3 → 12.89 |
| Limitless ×1.5 (dev + post-freeze read, 3,321) | 47.0 → 12.26 | 67.2 → 11.41 | 16.9 → 13.44 | 24.1 → 13.16 |
| Limitless ×2 | 42.3 | 60.5 | 16.1 | 23.1 |
| simulator ×4 + Limitless ×1.5 | 41.9 → 12.47 | 59.9 → 11.73 | 11.4 → 13.64 | 16.2 → 13.46 |
| simulator ×4 + Limitless ×4 | 27.2 → 13.05 | 38.9 → 12.59 | 8.8 | 12.6 |
| floor with unlimited simulator deals | 49.1 | — | 10.8 | — |
| floor with unlimited Limitless data | 22.8 | — | 13.7 | — |

- A tiny tweak like kog3 vs kpg3 (sd 2.9) has MDE50 of 5.7 (13.85) and MDE80 of 8.1 (13.76). Its floor with unlimited deals is 4.0 and with unlimited Limitless data 3.5.
- Real error 14.05 → 12.34 (koh's own size) is cleared 36% of the time now. Other sizes give 41% (simulator ×4), 47% (Limitless ×1.5), 57% (Limitless ×2.13, dev plus the spent holdout, sizes only) and 70% (simulator ×4 plus Limitless ×2.13). It drops to 22% for a post-freeze read alone.
- To clear a koh-sized effect 80% of the time you need about 6,244 Limitless matches (×2.8) with simulator ×4, or 11,835 matches at 500 deals.
- Brute-force check, 4,000 whole experiments per row (the reading's own joint deal distribution as truth):

| Reading | Configuration | Brute force | Normal rule |
|---|---|---|---|
| koh | now | 33.5% | 35.7% |
| koh | simulator ×4 | 40.8% | 42.7% |
| koh | Limitless ×1.5 | 44.3% | 46.5% |
| koh | both | 56.1% | 55.2% |
| kpf | now | 71.9% | 73.6% |

B: scenario, a well-aimed candidate that removes a fraction f of every cell's real miss, so true ΔMSE = −(2f − f²)·τ²:
- With the footprint of kog3 vs kp3 (6% of deals differ): MDE50 is 13.9 (f = 3.6%, real error 13.55) and MDE80 is 20.1 (13.31). Simulator ×4 gives 7.0.
- With the footprint of koh (29% of deals differ): MDE50 is 25.2 (13.12) and MDE80 is 36.0 (12.70). Simulator ×4 gives 12.9.
- In these scenarios the Limitless side is only 3–6% of the variance, so simulator deals are the lever.
- A candidate that moves cells a lot, some of them the wrong way (koh overshoots Rayquaza v weezing and v suicune), pays through the Limitless term.

**3. Where kog3's 14.0 comes from**

The 14.0 is score.py's τ̂ and already has the expected sampling noise of both sides subtracted. Raw sum of squared misses is 12,112 (mean 269.2, raw RMS 16.4). Of that, 25% is Limitless noise (mean 67.2, sum 3,024), 2% is simulator noise (mean 4.6), and 73% is real bias (mean 197.4, τ̂ = 14.05).
- Noise-floor real error, the raw RMS a perfect simulator would still show: 8.2 from Limitless alone, 8.5 with the simulator's own 500-deal noise. The average absolute miss would be about 6.5, against 13.0 observed.
- On τ̂'s own scale a perfect simulator gives median 0.9, mean 2.0, 95th percentile 6.2, and 91% of draws at or below the 5.5 target. The 5.5 target sits inside τ̂'s own noise.
- 17 of 45 cells miss by more than 2 sd of pure noise, where a perfect simulator would give about 2. 19 cells have squared miss below expected noise.
- The 9 Rayquaza cells hold 43% of the excess (group τ̂ 20.6), the 8 A/G cells hold 33% (19.1), and the 28 panel cells hold 24% (8.8). 76% of the bias is in the 17 new cells, which have the thinnest Limitless data (606 matches).

Top 10 cells by squared miss, kog3 vs Limitless:

| Cell | kog3 / Limitless | nL | miss | miss² | % of sum | Limitless-noise share of miss² |
|---|---|---|---|---|---|---|
| rayquaza v lucario | 34.8 / 73.3 | 58 | −38.5 | 1480 | 12.2% | 2% |
| rayquaza v vespiquen | 25.2 / 61.1 | 36 | −35.9 | 1290 | 10.6% | 5% |
| altaria_greninja v sceptile | 31.0 / 66.7 | 33 | −35.7 | 1272 | 10.5% | 5% |
| sceptile v vespiquen | 64.2 / 35.7 | 56 | +28.5 | 811 | 6.7% | 5% |
| rayquaza v sceptile | 17.6 / 45.0 | 50 | −27.4 | 751 | 6.2% | 7% |
| altaria_greninja v blaziken | 44.3 / 70.6 | 17 | −26.3 | 691 | 5.7% | 18% |
| altaria_greninja v hydreigon | 39.4 / 64.7 | 17 | −25.3 | 640 | 5.3% | 21% |
| rayquaza v blaziken | 27.3 / 50.0 | 8 | −22.7 | 515 | 4.3% | 61% |
| altaria_greninja v weezing | 28.6 / 50.0 | 16 | −21.4 | 458 | 3.8% | 34% |
| hydreigon v lucario | 43.6 / 63.6 | 55 | −20.0 | 401 | 3.3% | 10% |

The top 10 hold 69% of the raw sum. Limitless noise is 12% of their squared miss, and their excess is 82% of all excess. The cells with genuinely unreliable misses are the thin ones (Rayquaza v Blaziken n = 8, A/G v Blaziken n = 17).

**4. Conclusions**
1. Can it confirm a candidate like koh? Not at these sizes. koh's −45 is below its own 50% line of 55, and only 34–36% of fresh tables would clear it even if −45 were real. It can confirm small-footprint candidates of about −18 (real error −0.6) half the time, and anything of −26 or more 80% of the time. Effects worth less than about 0.2–0.3 of real error, such as kog3 vs kpg3, are invisible.
2. What helps most depends on the candidate:
   - Big-footprint candidates (koh, kpf, kpr and similar): Limitless matches, especially in the thin Rayquaza and A/G cells. Simulator ×4 only moves the MDE from 55 to 51.
   - Small-footprint candidates and well-aimed ones: simulator deals. ×4 cuts the MDE by 29–48%, and Limitless ×1.5 cuts only 8%.
   - Doing both ×4 halves the MDE everywhere.
   - The post-freeze pull read alone is worse than today (×0.5, MDE 75). It only helps once added to development data.
   - Folding the spent Sept 25 holdout into development would make Limitless ×2.13 (4,712 vs 2,214 matches). That is a rule change for Dustin and Fable, and I have not proposed it formally.
   - Pooling to 10 deck averages gives no gain. The signed z is −1.3 vs −1.6 for koh, −2.6 vs −2.5 for kpf, −2.7 vs −2.6 for kpr, −4.7 vs −4.6 for kog3 vs kp3, −4.6 vs −4.9 for kpg3, and the Limitless share rises to about 90% for big movers.
   - Down-weighting thin cells gives only about 8–10% more z. I did not test smoothing Limitless with an additive deck-strength model.
3. Hill-climb: the stalls are a mix.
   - koh's ΔMSE interval is a power problem.
   - kpf and kpr cleared ΔMSE and stalled on vetoes.
   - koh's counted Altaria veto (own side −1.8 ± 1.4 over 4,500 deals) is simulator-internal and not a power problem.
   - Every ΔMSE reading should print its own sd and MDE50/MDE80 beside the interval, computed from the same games with the same script.

**Uncertain**
- Plug-in and scenario MDEs assume a new candidate moves cells like a past one, or in the idealised proportional way. The real range is about 13 to 55 in ΔMSE.
- The Normal rule is about 2 points optimistic in the brute-force check. "Power at the observed effect" carries winner's-curse bias.
- Post-freeze per-cell counts are unknown; I scaled the dev counts uniformly. README says most panel cells had under 10 matches at 176 + 83 (Sept 27), so ×0.5 probably understates the noise. I did not run count_n.py or open matches.csv, to keep the outcome-blind rule.
- A rough post-freeze confirmation power on the ΔMSE scale, not the registered τ̂-margin statistic: about 32% for a koh-like, 59% for a kpf-like and 99% for a kpg-like effect.
- Simulator ×4 cost: timing.txt shows 14,000 kog3 games in 1,621 s on the laptop, so about 45 minutes per 45-cell table at 500 deals and about 3 hours per candidate at ×4, plus the baseline once. Seed ids i ≥ 500 exist in the seed formula's 10,000-wide blocks, but I did not check that they are unclaimed.
- I saw frozen_cells.csv's pooled rates when listing it. I used only its n columns (pooled total 4,712).

**Files** (all in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_power\analyst\`)
- `common.py`, `t0_check.py`: loader mirroring score45.py, and the reproduction check.
- `decompose.py` with `decompose_all.sh`: decomposition. Outputs `decomp_<reading>.txt` and `.json` for koh3_vs_kog3, kog3_vs_kp3, kpf3_vs_kp3, kpr3_vs_kp3, kpg3_vs_kp3 and kog3_vs_kpg3.
- `summary.py` → `summary.txt`: totals, group shares, worked arithmetic.
- `mde.py` → `mde.txt`, `needs.py` → `needs.txt`, `power_mc.py` → `power_mc.txt`.
- `noise_floor.py` → `noise_floor.txt` and `noise_floor.json`.
- `other_stats.py` → `other_stats.txt`, `run_py.sh`.

# VERIFY

**Verifier report: the 45-cell ΔMSE power analysis (independent recompute)**

The analysis holds up. Every key number reproduces within Monte-Carlo error, and I found no conclusion the numbers contradict. A few wordings need care and a few claims I could not check (below).

**How I checked it**
- I wrote my own script and read `score45.py` and `score.py` first; I did not reuse the analyst's scripts.
- Inputs were the 45 development Limitless cells (v2's 28 plus the gauntlet's 17), the kog3 table and new17 files, and koh3's files from `/tmp/koh_cloud` in WSL (they are not in the repo).
- No kt file or holdout file was opened. I did not open `frozen_cells.csv` either, because it carries pooled rates.
- Scripts and outputs are in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_power\verifier\`: `ver.py`, `ver2.py`, `out_*.txt`.

**Point estimates and totals: all reproduce**
- Point estimates match: koh −45.11 (τ̂ 14.05 → 12.33), kog3 vs kp3 −43.09, kpf −84.18, kpr −84.66, kpg −43.23, kog3 vs kpg3 +0.14.
- Dev Limitless matches total 2,214: 1,608 in the 28 table cells and 606 in the 17 new cells. The thinnest cell has 8 matches, and every cell has 500 deals.
- The koh interval from the analytic formula is −100.4 to +10.2, against −100.4 to +10.4 printed. My bootstrap gives −100.7 to +11.4.

**Variance split for koh: agrees**

| Quantity | Mine | Analyst |
|---|---|---|
| sd, simulator side | 11.64 | 11.6 |
| sd, Limitless side | 25.04 | 25.0 |
| sd, cross term | 5.82 | 5.8 |
| sd, total | 28.22 | 28.2 |
| Limitless share of variance | 78.7% | 79% |
| Half-width, both sides | 55.3 | 55.3 |
| Half-width, simulator only | 22.8 | 22.8 |
| Half-width, Limitless only | 49.1 | 49.1 |
| Cells: simulator larger / Limitless larger / none | 20 / 25 / 0 | 20 / 25 / 0 |

- Rayquaza's 9 cells carry 73.3% of the Limitless variance. The top 6 cells carry 66.5% and the top 10 carry 82.8%.
- The Rayquaza cells are v vespiquen 9.39 vs 3.16, v blaziken 9.19 vs 1.89, v suicune 8.13 vs 1.45, v weezing 7.90 vs 1.77, v altaria_greninja 7.62 vs 1.78, and v hydreigon 7.58 vs 1.15. All match the analyst's per-cell numbers.
- Simulator variance shares are 31% Rayquaza, 29% Altaria/Greninja and 40% panel.
- 29.4% of deals differ, with a per-deal sd of about 53 points, so the analyst's 29% and 54 points hold.
- The other rows of the analyst's table also match:

| Reading | Mine: simulator / Limitless / cross / total sd | Limitless share | Both-sides half-width |
|---|---|---|---|
| kpf | 12.33 / 30.0 / 5.97 / 32.97 | 83% | 64.6 |
| kpr | 12.2 / 29.6 / 6.0 / 32.6 | 83% | 63.9 |
| kog3 vs kp3 | 6.98 / 5.49 / 2.83 / 9.32 | 35% | 18.3 |
| kpg3 vs kp3 | 6.76 / 5.12 / 2.65 / 8.88 | 33% | 17.4 |
| kog3 vs kpg3 | 1.81 / 2.03 / 1.03 / 2.91 | 49% | 5.7 |

- The Rayquaza share of Limitless variance is 83.5% for kpf, 83.2% for kpr, 86.1% for kog3 vs kp3 and 99.0% for kpg3 vs kp3.

**Minimum detectable effect at current sizes: agrees**
- A koh-like candidate has MDE50 (true effect needed to clear zero half the time) of 55.3, giving real error 11.92. MDE80 is 79.1, giving 10.88.
- A small-footprint candidate (kog3-vs-kp3-like) has MDE50 of 18.3 and MDE80 of 26.1, giving 13.38 and 13.09 from the kog3 base of 197.4.
- The whole scaling table matches to the first decimal:

| Configuration | koh-like MDE50 | koh-like MDE80 |
|---|---|---|
| simulator ×2 | 52.3 | 74.7 |
| simulator ×4 | 50.7 | 72.5 |
| Limitless ×0.5 | 74.8 | 106.9 |
| Limitless ×1.5 | 47.0 | 67.2 |
| simulator ×4 + Limitless ×4 | 27.2 | 38.9 |

- The floors are 49.1 with unlimited simulator deals and 22.8 with unlimited Limitless data.
- The power of a fresh table at koh's own effect of −45.1 is 35.9% by the Normal rule. My brute-force run of 4,000 whole experiments gives 34.2%. Other configurations by the Normal rule:

| Configuration | Power |
|---|---|
| simulator ×4 | 41.4% (brute force 41.4%) |
| Limitless ×1.5 | 46.8% |
| Limitless ×2.13 | 57.0% |
| simulator ×4 + Limitless ×2.13 | 69.6% |
| Limitless ×0.5 | 21.8% |

- The kpf brute-force check gives 72.2%, against 71.9% for the analyst.
- The sample sizes to clear a koh-sized effect 80% of the time are 6,241 matches with simulator ×4 and 11,825 at 500 deals, against 6,244 and 11,835.
- Scenario B (a well-aimed candidate that removes a fraction f of every cell's miss):
  - kog3-vs-kp3 footprint: 13.9 and 20.2, against 13.9 and 20.1. Simulator ×4 gives 7.0, matching.
  - koh footprint: 25.9 and 37.6, against 25.2 and 36.0. Simulator ×4 gives 13.1, against 12.9.
  - The Limitless share of variance is only about 5–10% in these scenarios, as the analyst said.

**Noise-floor real error and top cells: agrees**
- Raw sum of squared miss is 12,112 (mean 269.2, RMS 16.41). Limitless noise is 25.0% (mean 67.2), simulator noise 1.7% (4.6), and bias 73.3% (197.4, τ̂ 14.05).
- The noise-floor RMS is 8.20 from Limitless alone and 8.47 with simulator noise added. The average absolute miss would be about 6.5 for a perfect simulator against 12.97 observed.
- 17 cells miss by more than 2 sd of pure noise, and 19 cells have squared miss below expected noise.
- The 10-row top-cells table is identical to the analyst's (cells, nL, miss, miss², share of the sum, noise share). The top 10 hold 68.6% of the raw sum, their Limitless-noise share is 12.3%, and their excess is 81.5% of all excess.
- Excess by group matches: Rayquaza 42.9% (τ̂ 20.6), Altaria/Greninja 32.9% (19.1), panel 24.3% (8.8), and the 17 new cells 75.7%.
- A perfect simulator, over 10,000 draws:

| Statistic | Mine | Analyst |
|---|---|---|
| τ̂ median | 1.10 | 0.9 |
| τ̂ mean | 1.98 | 2.0 |
| τ̂ 95th percentile | 6.14 | 6.2 |
| Share of draws at or below 5.5 | 91.0% | 91% |

**Disagreements (all small)**
1. The perfect-simulator τ̂ median is 1.10, not 0.9. The other three statistics agree.
2. The analyst says Limitless-only variance is 658 by event against 624 binomial, so events are 5% wider. In 20,000 reps I get 639 by event against 631 binomial (ratio 1.01). My 4,000-rep run gave the opposite sign (627 vs 654), so that difference is Monte-Carlo noise. "Event clustering changes little" stands, but the specific 658 vs 624 is not reproduced.
3. Scenario B with koh's deal footprint gives 25.9 and 37.6 (3–4% above the analyst's 25.2 and 36.0). This is immaterial.
4. "About 2 points optimistic" for the Normal rule is 1.7 points for koh but about 0 for kpf, and my Monte-Carlo error is about ±0.7. Say "within Monte-Carlo error".
5. Small-footprint MDE50 of 18.3 is real error −0.67, not "−0.6".

**Claims to reword or treat with caution**
1. **"Power at the observed effect" (34–36%).** It is a function of koh's own z and adds nothing beyond the interval. Report MDE50 and MDE80 from sd alone instead. The sd is computed from koh's own moves, so 34–36% is not a probability that koh's true effect gets confirmed.
2. **A single MDE has no fixed meaning.** The koh-like MDE of 55 is koh as built: big moves in the nine thin Rayquaza cells, some overshooting (v weezing goes further from Limitless by +17.2, and v suicune moves +20.2). Scenario B with the same deal footprint gives about 26–38. The honest answer to "how big can it detect" is roughly 14 to 55 ΔMSE points, or 0.5 to 2 points of real error, depending on how the candidate moves those cells. The analyst says this, but the headline should lead with it.
3. **Which side limits it.** For big movers it is the Limitless data in 6 Rayquaza cells (8 to 36 matches each, 66.5% of the variance), not the 2,214 total. Uniform "Limitless ×k" understates the gain from adding matches there and overstates it elsewhere.
4. **The "both ×4" row** uses Limitless ×4 (about 8,900 matches), which is not attainable. The realistic rows are simulator ×4 and Limitless ×1.5 to 2.1, which give koh-like MDE50 of 41.9 to 47.
5. **Post-freeze confirmation power (about 32% / 59% / 99%).** I cannot reproduce it. Uniform ×0.5 Limitless scaling gives 22% / 46% / 97%, and no single scale gives both 32% and 59%. It depends on unstated assumptions, so treat it as unverified.

**Not verified**
- The Limitless ×2.13 scale (4,712 matches), which needs the pooled counts.
- The 10-deck pooling claim (signed z values).
- The down-weighting gain of about 8–10%.
- The post-freeze counts.
- The veto statements for kpf and kpr. I confirmed only koh's printed Altaria figure, own side −1.8 ± 1.4 over 4,500 deals, which is on the printed page.
- The laptop timing.
- The seed-block availability.
