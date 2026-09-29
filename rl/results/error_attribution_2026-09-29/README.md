# Where kog3's 14.0 comes from, cell by cell (Sept 29, read-only)

**Why:** Dustin's item 4, done once before the next candidate is registered. Which cells carry the 14.0, and for each, how much is the chance floor, how much is list variation, and how much is left for the pilot. The decision it feeds: is the pilot's reachable share small enough that the next candidates should be list handling and data, and should the 5.5 target be restated as one the pilot alone can't reach.

**What this is:** an attribution built from existing results. No game, build or engine was run. Nothing is registered and nothing here gates a candidate. No post-freeze match file was opened. No kt file beyond the tables already read on Sept 29 was used.

**Files (this folder):** `attribute.py` (the analysis), `loader.py` (reads the tables), `run_attribute.sh`, `attribution_numbers.txt` (everything the script prints, with the checks), `cells.csv` (all 45 cells, every column below).

## In plain words

1. **The 14.0 is 73% of the squared miss.** The 45 cells' squared misses add to 12,112 (raw RMS 16.4). Chance takes 3,229 (27%). The other 8,882 is what τ̂ = 14.05 measures. Its own 90% interval is 11.2 to 16.8.
   - **Which cells carry it:** the top 15 by squared miss hold 96% of the excess (table below). By group: Rayquaza's 9 cells 43%, Altaria/Greninja's 8 cells 33%, the 28 panel cells 24%.
2. **Split of those 8,882 (the excess), by what the evidence supports:**

   | Piece | pts² | % of excess | Who can move it |
   |---|---:|---:|---|
   | A tested pilot fix reaches it: Rayquaza's 9 cells (koh3) | 2,980 | 34% (22% to 53%) | a pilot |
   | The target itself moves: Limitless's two halves disagree, almost all Altaria/Greninja | 1,543 | 17% | data |
   | List variation, middle assumption (range 503 to 2,014) | 1,007 | 11% (6% to 23%) | list handling |
   | Not reached by any tested pilot, not explained by the two lines above | 3,353 | 38% | unknown |

   - The last row holds Sceptile v Vespiquen 749, Altaria/Greninja's remainder 1,371, the other 27 panel cells 810 and Rayquaza's leftover 423.
3. **The pilot's reachable share is not small, but it sits in one place.** Rayquaza's nine cells carry 3,806 of the 8,882 (43%). Three pilot builds bring that group's τ̂ down to 8.5 (koh3, from kog3's 20.6), 8.7 (kpf3, from kp3's 25.3) and 8.7 (kpr3, from kp3's 25.3). kpf3 and koh3 share the R′ projection; kpr3 uses a different one. koh3 was not adopted (its accuracy interval crossed zero, and vetoes counted). Across the cells it made worse it lost 2,727.
4. **Outside Rayquaza's cells, no tested pilot has a net gain.** koh3 on the other 36 cells helped +1,264 and hurt −2,384 (net −1,120).
5. **A/G's target is unreliable.** Its 8 non-Rayquaza cells score 56.3% (269 matches) in the development half and 41.5% (219) in the other half. Against the other half, kog3's A/G error is 9.0, not 19.1.
6. **List variation cannot explain the big misses.** The largest single list change in the variation check is 25.2 points and the typical one is 4 to 7. The top-15 misses are 17.5 to 38.5.
7. **Per cell, this is a description.** Only 6 of 45 cells have an excess whose own 90% interval stays above zero. They hold 63% of the excess. The thin cells (fewer than 25 real matches, 11 cells) are 52% chance by squared miss.
8. **The 5.5 target sits at or below what a perfect pilot would read** on these cells and single lists: about 7.5 (6.7 to 8.9), or 3.3 to 6.7 if the halves-disagree term is set aside. The pilot alone can be asked for about 11 (Rayquaza's gain alone: 11.3, 90% 9.4 to 12.8).

## The split, by group (pts²)

Every cell's raw squared miss (kog3 − Limitless, development half) is chance + halves + list + remainder. The sums are exact: 3,229 + 1,543 + 1,007 + 6,332 = 12,111 (rounding).

| Group | Cells | Raw miss² | Chance | Halves disagree | List (mid) | Remainder | koh3 helped | koh3 hurt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Rayquaza | 9 | 4,704 | 898 | 172 | 231 | 3,403 | +3,499 | −343 |
| Altaria/Greninja (not v Rayquaza) | 8 | 3,653 | 733 | 1,371 | 179 | 1,371 | +395 | −299 |
| Panel | 28 | 3,755 | 1,599 | 0 | 597 | 1,559 | +869 | −2,085 |
| **All 45** | 45 | **12,112** | **3,229** | **1,543** | **1,007** | **6,332** | **+4,763** | **−2,727** |

- "Remainder" is pilot, engine and anything else. The pieces cannot separate them (see "What the pieces do not support").
- koh3 helped/hurt is the change in each cell's excess against kog3, summed over cells it improved and cells it worsened. Net +2,037 (23% of the excess; 90% −64 to +4,169, so zero is inside).
- The Rayquaza tier above is koh3's gain in Rayquaza's cells, capped at each cell's remainder: 2,980 (uncapped 3,157; group bootstrap 90% 1,971 to 4,696).

## Top 15 cells by squared miss

Together they hold 82% of the raw sum (9,915 of 12,112) and 96% of the excess. All numbers are points or points². "Chance" is Limitless binomial noise plus the simulator's 500-deal noise. "Halves" is the group value (Rayquaza 19, A/G 171, panel 0). "List" is the middle value with the range in brackets. "Best" is the closest tested pilot for that cell (the envelope; it includes selection luck). Other half = the rest of the Limitless events.

| Cell | nL | kog3 | Lim | Miss | Miss² | Chance | Halves | List | Remainder | Other half | koh3 | Best | Reading |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| rayquaza v lucario | 58 | 34.8 | 73.3 | −38.5 | 1,480 | 38 (3%) | 19 | 24 (12–49) | 1,399 | 54.7 | 53.6 | 61.4 kpf3 | pilot lever: koh3 closes 1,094, best 1,340 |
| rayquaza v vespiquen | 36 | 25.2 | 61.1 | −35.9 | 1,290 | 70 (5%) | 19 | 27 (13–54) | 1,174 | 44.6 | 51.2 | 51.2 koh3 | pilot lever: koh3 closes 1,193 |
| altaria_greninja v sceptile | 33 | 31.0 | 66.7 | −35.7 | 1,272 | 72 (6%) | 171 | 17 (8–33) | 1,012 | 33.9 | 29.8 | 33.4 kpf3 | no pilot moved it; the other half agrees with the simulator |
| sceptile v vespiquen | 56 | 64.2 | 35.7 | +28.5 | 811 | 46 (6%) | 0 | 17 (9–34) | 749 | 32.5 | 64.0 | 64.0 koh3 | no pilot moved it; the target is stable (35.7 v 32.5) |
| rayquaza v sceptile | 50 | 17.6 | 45.0 | −27.4 | 751 | 52 (7%) | 19 | 20 (10–40) | 659 | 40.9 | 23.8 | 25.0 kpf3 | partly: koh3 closes 302 of 659 |
| altaria_greninja v blaziken | 17 | 44.3 | 70.6 | −26.3 | 691 | 127 (18%) | 171 | 15 (7–30) | 378 | 45.0 (n 10) | 42.6 | 49.2 ktb3 | thin; own interval includes zero |
| altaria_greninja v hydreigon | 17 | 39.4 | 64.7 | −25.3 | 640 | 139 (22%) | 171 | 19 (9–38) | 311 | 45.9 | 39.6 | 41.4 kpf3 | thin; own interval includes zero |
| rayquaza v blaziken | 8 | 27.3 | 50.0 | −22.7 | 515 | 316 (61%) | 19 | 18 (9–36) | 162 | 40.0 (n 15) | 39.0 | 41.5 kpr3 | 8 matches: mostly chance |
| altaria_greninja v weezing | 16 | 28.6 | 50.0 | −21.4 | 458 | 160 (35%) | 171 | 35 (18–71) | 91 | 50.0 (n 12) | 37.2 | 37.2 koh3 | thin; own interval includes zero |
| hydreigon v lucario | 55 | 43.6 | 63.6 | −20.0 | 401 | 47 (12%) | 0 | 17 (8–33) | 338 | 50.1 | 49.0 | 52.6 kpf3 | partly; the best tested Lucario list moves the miss 4.6 |
| blaziken v hydreigon | 24 | 48.2 | 66.7 | −18.5 | 341 | 98 (29%) | 0 | 10 (5–21) | 233 | 54.0 | 49.2 | 49.2 koh3 | thin; nothing moved it |
| vespiquen v weezing | 43 | 65.6 | 83.7 | −18.1 | 328 | 36 (11%) | 0 | 36 (18–71) | 256 | 83.3 | 71.8 | 72.3 kpf3 | koh3 closes 186 of 256 |
| altaria v blaziken | 34 | 58.6 | 76.5 | −17.9 | 319 | 58 (18%) | 0 | 13 (6–26) | 249 | 73.0 | 53.6 | 61.2 ktb3 | koh3 makes it worse (−204) |
| rayquaza v altaria_greninja | 36 | 35.2 | 52.8 | −17.6 | 309 | 74 (24%) | 19 | 27 (13–53) | 189 | 49.9 | 55.8 | 55.8 koh3 | koh3 lands 3 past Limitless |
| suicune v vespiquen | 72 | 46.0 | 28.5 | +17.5 | 307 | 33 (11%) | 0 | 27 (14–54) | 247 | 27.6 | 39.8 | 39.8 koh3 | koh3 closes 179 of 247 |
| **Top 15** | | | | | **9,915** | **1,366** | **781** | **322 (161–643)** | **7,446** | | | | |

- Rows 1 to 5 hold 5,604 of the table's 9,915. Rows 3, 6, 7 and 9 (Altaria/Greninja) are four of the top nine.
- The first five rows are the cells whose own 90% excess intervals stay above zero, plus Suicune v Vespiquen (lower end +6). Every other row's interval includes zero.
- Where the check varied a deck in the cell (Hydreigon v Lucario, Vespiquen v Weezing, Suicune v Vespiquen), the measured list swing is 4.2, 4.4 and 6.0 points. The best tested list moves those misses by +4.6, +1.6 and +1.0. The other 12 cells' list part uses the deck-level swing (measured for Lucario, Suicune and Weezing, assumed for the rest), not a swing measured in that cell.
- Rayquaza v Lucario: the other half is 54.7, koh3 is at 53.6 and kpf3 at 61.4. On this cell the Limitless figure itself is soft (73.3 in the development half, 54.7 in the other).
- Sceptile v Vespiquen is the largest cell that nothing has moved and whose target holds still: development 35.7 (n 56), other half 32.5 (n 83). Deeper search (k4 to k6) moved it 66.1 → 56.8 on the Sept 23 table; option B moved it −4.2.

## The pieces

### 1. Chance floor (exact)

- τ̂'s own terms: the Limitless cell's binomial variance L(1−L)/nL plus the simulator's S(1−S)/500. Limitless 3,024, simulator 206. It reproduces `eval_power_2026-09-29/analyst/noise_floor.json` on all 45 cells.
- Assumption A1: the observed Limitless rate stands in for the true one when the variance is computed (as score.py does).
- Chance is 3% to 7% of the squared miss in the six biggest cells and 61% in Rayquaza v Blaziken (8 matches).

### 2. The target moves: the two halves of the Limitless events (Assumption A2)

- **Method.** Each cell's development rate is compared with the other half of the events (pooled minus development, from `scoreboard_v3_2026-09-27/frozen_cells.csv`). z² = (dev − other)² / the binomial variance of the difference. Binomial noise alone gives 1.00 on average.
- **Result.** All 45 cells: mean z² 1.08 (sd of the mean about 0.21), so overall the halves agree. By group:

  | Group | Mean z² | Extra half-variance ω² per cell | 90% (cells resampled) |
  |---|---:|---:|---|
  | Rayquaza | 1.28 | 19.2 pts² | 0 to 118 |
  | Altaria/Greninja | 3.04 | 171.4 pts² (sd 13.1 points) | 26 to 320 |
  | Panel | 0.45 | 0 (floored) | 0 |

- A/G's worst cells: v Vespiquen z² 8.2 (61.4% v 24.0%), v Sceptile 6.9 (66.7 v 33.9), v Suicune 4.5 (53.9 v 26.1).
- A/G is not a skill or a few-players effect. The B6 skill proxy on its 269 matches gives +0.48 points (range −0.11 to +0.71). Its three busiest players play 20% of the matches, and its score is 56.3% with them and 56.0% without. Rayquaza's proxy is −0.13 points.
- **Use.** ω² is allocated to every cell of its group: 172 + 1,371 + 0 = 1,543 (17.4% of the excess). It is a real-side term that a perfect simulator would also show against the development half.
- **Cautions.** The estimate for A/G rests on 8 related cells. It uses the other half's counts, which are already public in scoreboard v3's pooled column, descriptively. Nothing is decided from it. The panel's mean z² of 0.45 is below 1. One possible reason is players shared across halves (not checked). If so, the halves understate the real-side spread a little.
- **Replication check (descriptive).** kog3's τ̂ by group, development half against the other half: Rayquaza 20.6 v 18.1, panel 8.8 v 8.9, A/G 19.1 v 9.0. Rayquaza's and the panel's misses replicate. A/G's does not.

### 3. List variation (Assumptions A3, A4, A5)

**What was measured** (the variation check, `gauntlet_runs_2026-09-26/`, kp3, 500 deals paired by deal, three versions per deck):

| Deck | Second list moves its 7-opponent average | Two swaps | ν = mean(change² − its paired variance), pts² (rms) | 90% over the 21 changes | Largest single change |
|---|---|---|---:|---|---:|
| Lucario | +4.7 | +4.2, −3.1 | 19.0 (4.4) | 10 to 30 | 11.2 |
| Suicune | +5.8 | +7.3, −0.4 | 29.9 (5.5) | 16 to 45 | 12.2 |
| Weezing | +9.0 | +3.8, +1.3 | 47.2 (6.9) | 12 to 103 | 25.2 |
| Charizard Y (not on the scoreboard) | −6.8 | −0.9, −1.9 | 22.0 (4.7) | 10 to 36 | 12.8 |

- The numbers reproduce the README's own table cell by cell.
- The same second lists under kog3 move the averages +4.7, +4.6, +8.3 and −5.9. Assumption A5: the kp3 shifts (older engine, Sept 25 references) are read as kog3 shifts. The deck averages agree within 1.2 points. Cell by cell the largest difference is 5.2 (Altaria v Suicune, where kog's opening switch changes Altaria).
- **A second list does not close a deck's gap.** kog3's 7-opponent gaps are Lucario +0.7, Suicune −0.8 and Weezing +2.4. The second lists take them to +5.4, +5.0 and +11.4.
- **B2e (lists that differ by design).** The archetype list against Dustin's file, per cell, kp3: rms 12.8 over 48 cells (26.1 for Hoopa/Absol; 7.7 for the other 40). A larger list change gives a larger swing.

**How it becomes a share of the miss.**
- A3: for a deck the check did not vary, the swing is the measured decks' mean (29.5 pts²) scaled by (1 − the share of its lists that are the most common list) / 0.86. Shares are from `gauntlet_proposal_2026-09-26/README.md` section 5. The scaled decks: Altaria 19.6, Sceptile 10.0, Vespiquen 24.2, Hydreigon 14.3, Blaziken 6.4, Rayquaza 29.8 and Altaria/Greninja 23.4 pts².
- A4: the list part of a cell's miss² is f × (the sum of its two decks' swings), with f = ¼ (low), ½ (mid) and 1 (high). f = 1 says the field's average list differs from ours by as much as one tested list change does. f = ¼ says most of the field is close to ours.
- Totals over the 45 cells: low 503 (5.7% of the excess), mid 1,007 (11.3%), high 2,014 (22.7%). This is an assumption range, not a statistical interval.
- Not measured at all: any list variation for Rayquaza, Altaria/Greninja, Sceptile, Vespiquen, Hydreigon, Blaziken and Altaria. In 7 of the top 9 cells neither deck was varied. The other two (Rayquaza v Lucario, Altaria/Greninja v Weezing) have one varied deck.

### 4. What a pilot change can reach (Assumption A6)

**Each tested pilot's table on the 45 cells** (excess per cell, pts²; τ̂ in brackets):

| Pilot | All 45 | Rayquaza 9 | Alt/Gren 8 | Panel 28 | Cells moved by more than 5 points against its base (base) |
|---|---:|---:|---:|---:|---|
| k3 | 232.7 (15.3) | 464.9 (21.6) | 367.1 (19.2) | 119.7 (10.9) | |
| kp3 | 240.5 (15.5) | 639.2 (25.3) | 368.9 (19.2) | 75.7 (8.7) | |
| kpg3 | 197.2 (14.0) | 421.4 (20.5) | 366.3 (19.1) | 76.9 (8.8) | 3 (kp3; largest 9.0) |
| kog3 | 197.4 (14.0) | 422.9 (20.6) | 365.0 (19.1) | 77.0 (8.8) | 3 (kp3; largest 9.0) |
| kta3 | 191.4 (13.8) | 395.3 (19.9) | 365.0 (19.1) | 76.3 (8.7) | 0 (kog3; largest 1.2) |
| ktc3 | 197.1 (14.0) | 428.1 (20.7) | 361.1 (19.0) | 76.0 (8.7) | 0 (kog3; largest 2.2) |
| ktb3 | 205.8 (14.3) | 424.8 (20.6) | 327.2 (18.1) | 100.7 (10.0) | 3 (kog3; largest 6.6) |
| kt3 | 198.4 (14.1) | 401.3 (20.0) | 336.7 (18.3) | 93.6 (9.7) | 3 (kog3; largest 6.6) |
| kpf3 | 156.1 (12.5) | 76.4 (8.7) | 313.9 (17.7) | 136.7 (11.7) | 21 (kp3; largest 35.6) |
| kpr3 | 155.7 (12.5) | 75.0 (8.7) | 318.0 (17.8) | 135.2 (11.6) | 21 (kp3; largest 33.4) |
| koh3 | 152.1 (12.3) | 72.2 (8.5) | 353.0 (18.8) | 120.4 (11.0) | 22 (kog3; largest 26.0) |

- ΔMSE per cell against the base: kpf3 −84.2, kpr3 −84.7, kpg3 −43.2, kog3 −43.1, koh3 −45.1, kt3 +1.0, kta3 −5.9, ktb3 +8.4, ktc3 −0.3. These match the registered readings.
- **What it shows.**
  - Three builds (kpf3, kpr3, koh3; kpr3 is a different design from the other two) land Rayquaza's group at the same level, 72 to 76 per cell. The reach is not one lucky table.
  - Every design that fixed Rayquaza made the panel worse (76.9 → 120 to 137 per cell). koh3's biggest losses: Hydreigon v Suicune −504, Rayquaza v Weezing −343, Hydreigon v Vespiquen −312, Blaziken v Weezing −241, Altaria v Blaziken −204, Hydreigon v Weezing −184. Hydreigon's nine cells net −891.
  - The Tool switches (kt) move few cells. kta3, the best of them, gains 5.9 pts² per cell (τ̂ 14.05 → 13.84).
  - Altaria/Greninja: the best tested table is 313.9, against 365.0 for kog3. No pilot has moved it much.
- The envelope ("best tested pilot in every cell", capped at each cell's remainder) is 4,861: 55% of the excess. It includes selection luck (A6) and is an upper bound, not a forecast. kpf3 and kpr3 are built on kp3, so they are left out of the envelope in Altaria's cells, where kog's own changes differ.

**Other evidence on reach** (all older, on the 28 panel cells only):
- **Deeper search** (k4 to k6 on both sides, Sept 23 table, old Limitless pull, 1,000 deals): cells move by an rms of 3.0 to 4.0 points, 5 to 8 of 28 by 5 or more, toward Limitless and away about equally (8 v 6, 11 v 9, 9 v 8). Raw MSE 149 → 139, 130 and 138. Sceptile v Vespiquen 66.1 → 59.2, 56.5 and 56.8 against 33.1.
- **Option B** (b3o3n1: guess the hand, search the reply) against k3 on the five worst cells of the time: squared miss 2,792 → 1,752 (37% less). Hydreigon v Lucario 566 → 94. Cell changes +2.0, +1.6, +4.5, +14.1 and −4.2. It was not adopted.
- **The see-everything test** (RUN5, Sept 24): Hydreigon v Lucario 30.8 → 44.7 with hands seen and 46.8 with everything seen; Altaria v Lucario, Altaria v Blaziken and Sceptile v Vespiquen did not move.
- **Engine repairs** so far: kp3's 28-cell τ̂ went 8.4 → 8.7 and k3's 10.8 → 10.9 (scoreboard v3). They did not reduce the misses.
- **B6 (skill):** it explains under 0.6 points of the Altaria, Vespiquen and Sceptile deck gaps; β = 0.29 (95% −0.06 to 0.43). By that proxy the panel's remainder is not the players. The proxy is weak (β's interval reaches below zero), so this rules out less than it sounds. The same proxy on the new decks is +0.48 (A/G) and −0.13 (Rayquaza) points.
- **BO1/BO3 (A7):** 33% of the development matches are best-of-three and the simulator plays single games. If a series were three independent games at the simulator's rate, real cells would sit 1.8 points (rms) off. That is 148 pts², 1.7% of the excess. It is not carved out of the split.

## What the pieces do not support

- **Pilot v engine v anything else inside the remainder.** The pieces give what tested pilots did, not what any pilot could do. The remainder (6,332) is labelled "pilot, engine and anything else" on purpose. Assumption A8.
- **A per-cell split.** 39 of 45 cells have an excess whose own 90% interval includes zero (9 of the top 15). Only the group totals and the six cells named above are supported. The 11 thin cells are 52% chance by squared miss.
- **List variation for the decks the check did not vary.** Their list part is an assumption (A3, A4), not a measurement. For the top 15 cells the middle list part is 10 to 36 pts² (at most 71 at the high value) against remainders of 91 to 1,399, so the conclusion does not hinge on it. For the total it is 6% to 23% of the excess.
- **Why A/G's halves disagree.** The pieces exclude skill and a few busy players. They do not say what it is (lists, time, partner cards). A/G's gap is an open cause in RUN5, and this does not look into it either.
- **Cross-engine tables.** kpf3, kpr3, koh3 and kt3 were played on different engine builds. kog3's tables are byte-identical between the Sept 28 composition run and kt's build (same sha256). k3 and kp3 replay identically at a823b6d, and the Sept 27 engine repairs moved the 28-cell τ̂ by 0.1 to 0.3. Nothing else was re-checked.
- **The size of the reach.** koh3's net gain has a 90% interval that includes zero (−64 to +4,169). The Rayquaza-only figure is firmer: the group bootstrap gives 1,971 to 4,696 (the group's own excess is 3,806), and its lower end is well above zero.

## Decision the attribution favours

For Dustin and the parent session to decide. Nothing below is registered.

1. **Data first, where the target moves.** A/G's misses are not shown to be a pilot problem: 1,371 of its 2,920 is the halves disagreeing, and against the other half kog3's A/G error is 9.0. Thin cells (11 cells under 25 matches) cannot be read either way. This favours the eval-power decision to fold the spent holdout into the development data (`eval_power_2026-09-29/README.md`, decision 1), and the post-freeze read. By assumption A2, folding the other half in halves the halves-disagree term.
2. **One pilot candidate, and it is not a new scoring term.** The attribution's one large reachable piece is Rayquaza's mechanism (34%, 2,980). The mechanism is built (kpf, kpr, koh). koh was not adopted: its accuracy interval crossed zero, and vetoes counted on Altaria, on Weezing's second list, and on B2e's Hoopa/Absol and Whimsicott. Its cost on the 45 cells is −2,727 in the cells it made worse. The nine cells it hurt by more than 100 sum to −2,256: Hydreigon v Suicune −504, Rayquaza v Weezing −343, Hydreigon v Vespiquen −312, Blaziken v Weezing −241, Altaria v Blaziken −204, Hydreigon v Weezing −184, Altaria v Lucario −178, Altaria v Hydreigon −176 and Blaziken v Sceptile −114. All three Rayquaza designs show the same panel cost (kpf3 and kpr3 panel 137 and 135 per cell, koh3 120, against 76 to 77 for their bases). The pilot-side candidate this favours is Rayquaza's gain without that spill onto the panel. Rayquaza's group alone gets τ̂ from 14.05 to 11.3. Whether such a candidate can be built is a design question this attribution does not answer.
3. **List handling is third.** It is 6% to 23% of the excess and cannot explain the top-15 misses. Its use is the target's floor (below), and mixing lists by field share rather than swapping in one second list, since a second list moved all three panel decks' averages away from Limitless.
4. **Sceptile v Vespiquen is a diagnosis, not a candidate.** 749 (8% of the excess) and a stable target (35.7 v 32.5). No tested pilot moved it more than 0.2 points toward Limitless. The deepest search moved it about 10 of a 33-point miss on the older table (66.1 → 56.5). Nothing in the pieces says whether the cause is the pilot or the engine.
5. **Not favoured:** another scoring term aimed at the panel or at A/G. Tested pilots move those cells by ±4 with no net gain (koh3 net −1,120 outside Rayquaza), and deeper search moves cells both ways.

The test in the request was "if the pilot's reachable share of the remaining error is small". It is 34% (22% to 53%), all in nine cells, so it is not small. Outside those nine cells the pieces point to data and lists, then a diagnosis, and not to another scoring term.

## The 5.5 target, restated (proposal)

τ̂ is score.py's real error on the 45 development cells. Today kog3 is 14.05 (90% 11.2 to 16.8).

| Level | τ̂ | What it means |
|---|---:|---|
| kog3 now | 14.05 | |
| koh3 as tested | 12.33 | whole pilot, with its cost elsewhere |
| Rayquaza's gain alone (kog3 in every other cell) | 11.3 (9.4 to 12.8) | the pilot lever shown; no cost elsewhere assumed |
| Best tested pilot in every cell | 9.45 | upper bound; includes selection luck |
| Best tested whole pilot per group | 10.84 | upper bound; ignores cost across groups |
| A perfect pilot and engine on today's cells and single lists | 7.5 (6.7 to 8.9) | halves-disagree 5.9, lists 3.3 / 4.7 / 6.7 (low / mid / high) |
| The same, if the halves-disagree term is set aside | 3.3 to 6.7 | lists only |
| A perfect pilot after the other half is folded in | 6.3 | halves-disagree term halved, mid list |
| The same, and list handling cuts the list term to the low value | 5.3 | data and lists together |

- **Proposed wording.** 5.5 is the bar for the whole system (pilot, lists and data), not for the pilot alone. On today's data and single lists a perfect pilot would read about 7.5, so the pilot cannot be shown to miss 5.5 or to reach it.
- **The pilot alone** is asked for about 11 on the 45 cells as scored now. Below that, τ̂ is measuring the cells' own noise and the list, and no verdict should rest on it.
- **What lowers the floor:** more real data (6.3) and list handling (5.3). Both assume the halves-disagree and list terms are as estimated here.
- eval-power's finding still holds: on binomial noise alone a perfect simulator reads 0.9 to 1.1. The floor above adds the two real-side terms that reading left out.

## Assumptions

- **A1** Chance floor = τ̂'s own two terms, with the observed Limitless rate used for its variance.
- **A2** The other half is an independent draw of the same long-run cell. The extra variance beyond binomial is real-side. It is estimated per group, floored at 0 and given to every cell in the group.
- **A3** List swing for a deck the check did not vary = the measured decks' mean scaled by (1 − modal-list share) / 0.86.
- **A4** The list part = f × the tested swing, f = ¼, ½ or 1.
- **A5** Variation-check shifts (kp3, Sept 25 engine) are read as shifts for kog3.
- **A6** Pilot tables from different builds are comparable cell by cell. The best-pilot envelope includes selection luck. koh3's reach is capped at each cell's remainder.
- **A7** A BO3 series = three independent games at the simulator's rate.
- **A8** The remainder is pilot + engine + anything not named. No split between them is claimed.

## How to re-run

`bash rl/results/error_attribution_2026-09-29/run_attribute.sh` in WSL (about 15 seconds, `nice -n 10`). It writes `attribution_numbers.txt` and `cells.csv` here.

- It needs koh3's per-game files from the cloud copy at `/tmp/koh_cloud/{table,new17}_koh3.jsonl` and `b2e_kog3.jsonl` (not in the repo). `table_koh3.jsonl` sha256 c87b77f392da83b9127fd00971e7f030427c834bb31f85915c72fe0b20eb0d18. koh3's per-cell rates are saved in `cells.csv`.
- The bootstrap draws (600) are seeded, so a rerun gives the same numbers.
- Sources read: `eval_power_2026-09-29/analyst/noise_floor.json`, `gauntlet_runs_2026-09-26/` (variation check, cells), `koh_2026-09-28/laptop_runs/var_*`, `public_pricing_2026-09-25/kp3_500_*`, `b2e_rows_2026-09-26/`, `limitless_skill_model_2026-09-25/` (B6; development matches and skills only), `deep_search_table/STATUS.txt`, `option_b_attribution_2026-09-24/`, `scoreboard_v3_2026-09-27/`, `kog_composition_2026-09-27/`, `kpf_2026-09-26/reading/`, `kt_tables_2026-09-28/` (tables already read), `gauntlet_proposal_2026-09-26/README.md` (list shares) and `RUN5.md`.

## Check (Sept 29)

Independent checker (attribution-checker). Own code, written from the raw files: it does not import `loader.py`, `attribute.py` or `score.py`. Nothing else in the repo was edited. The checker's scripts and outputs are in the session scratchpad (`scratchpad/wf_post/attribution-checker/`: `check1.py` to `check5.py`, `out*.txt`), not in the repo. No game, build or engine was run, and no post-freeze file was opened. The other half was read from the holdout rows of `gauntlet_cells.csv` (the same counts as scoreboard v3's pooled column), descriptively, as in the README.

### What agrees (recomputed, same numbers)

- **Inputs.** Limitless development cells from `gauntlet_cells.csv` equal `limitless_v2_dev.json` (28 cells) and the sums of `limitless_45_dev_events.json` (all 45). Pooled equals development plus holdout in all 45 cells. kog3's `table` and `new17` files have the same sha256 as `ec7e1a8_id_kog3_500.jsonl` and `ec7e1a8_id_kog3_new17.jsonl` in `kt_tables_2026-09-28/`. `table_koh3.jsonl` has the sha256 the README gives. All 11 pilots are on the same seeds.
- **Totals.** Raw 12,112 (RMS 16.41). Limitless noise 3,024 plus simulator noise 206 = 3,229 (26.7%). Excess 8,882, τ̂ 14.05. Groups: Rayquaza 3,806, Altaria/Greninja 2,920, panel 2,156, and the group τ̂ of 20.6, 19.1 and 8.8. Top 15 by squared miss: 9,915 raw, 1,366 chance, 8,549 excess (96.2%). Thin cells: 11, chance 51.7% of their squared miss.
- **All 45 cells against `cells.csv`.** Squared miss, chance, excess and koh3 gain differ by at most 0.005. Halves z² differs by at most 0.06, the other-half rate by at most 0.12 and the remainder by at most 0.2 points².
- **Halves.** Mean z² 1.08 (all), 1.27 (Rayquaza), 3.04 (A/G), 0.45 (panel). ω² 19.1 (Rayquaza), 171.2 (A/G), 0 (panel); total 1,541 against the README's 1,543. A/G 56.3% (269 matches) against 41.5% (219). kog3's τ̂ against the other half: Rayquaza 18.15, A/G 8.96, panel 8.89, all 11.37.
- **Lists.** Own-side changes and ν agree for all four decks (19.0, 29.9, 47.2, 22.0; mean 29.5). A3 scaled swings agree (Altaria 19.6, Sceptile 10.0, Vespiquen 24.2, Hydreigon 14.3, Blaziken 6.4, Rayquaza 29.8, A/G 23.4). List totals 503 / 1,007 / 2,014. kog3 second-list shifts +4.7, +4.6, +8.3, −5.9. B2e rms 12.8 (7.7 without Hoopa/Absol). Deck gaps +0.7, −0.8, +2.4.
- **Pilots.** The 11-row pilot table, the ΔMSE per cell, koh3's helped +4,763 / hurt −2,726 (the README rounds to −2,727; net +2,037), the outside-Rayquaza +1,264 / −2,384, the nine losses that sum to −2,256, Hydreigon's nine cells net −891.
- **The split.** Reach 2,980 (uncapped 3,157); tiers 33.5% / 17.4% / 11.3% / 37.8%; remainder pieces 749, 1,371, 810, 423; envelope 4,861 (54.7%); Rayquaza alone τ̂ 11.28; floors 6.7 / 7.5 / 8.9, folded 6.3, folded plus low list 5.3.
- **Other evidence.** Deep search rows and counts; option B 2,792 → 1,752 (the five rows are the `b3o3n1` column of `option_b_attribution_2026-09-24.md`); see-everything 44.7 and 46.8 (`see_everything_2026-09-24.md`, RUN5); B6 +0.48 and −0.13 points; BO3 33.2%, rms 1.81, 148 pts².
- **Sources cited correctly**, with two small gaps: Rayquaza's 19/143 and A/G's 40/125 list shares are in the "next two" note of `gauntlet_proposal_2026-09-26/README.md` (lines 142 to 149), not in its section 5. The option B numbers are typed into `attribute.py`, not read from a file.

### Where the checker disagrees or the text goes further than the numbers

1. **"Not reached by any tested pilot" (3,353, 38%) is mislabelled.** Section 4 says the best tested pilot cell by cell moves 4,861 (55%). Only 1,472 (17%) is left where no tested pilot moved the cell, and its own 90% interval is −1,385 to 3,645. The 3,353 is "not credited to a pilot in the tier accounting": outside Rayquaza no whole pilot has a net gain. Say that.
2. **The halves term has no interval in the headline table.** The 17% (1,543) has a 90% interval of about 410 to 3,035 (5% to 34%) when the cells are resampled; the README's own numbers file gives 212 to 3,628 (a sum of the group bounds, so wider). 89% of it is A/G. A/G's estimate rests on three cells: without the three largest z² cells (v Vespiquen, v Sceptile, v Suicune) it is 0, and without v Vespiquen alone it is 108 per cell (171 with all eight). The MLE agrees with the moment estimate (183 v 171). So "data first" is a judgement; the 17% does not outrank the pilot's 34% (22% to 53%) on these numbers. A2 also has a mild flag: the panel's z² sum is 12.75 on 28 cells (lower-tail chance p 0.006), which independent halves do not usually give. The README says shared players were "not checked"; the tables here cannot check it.
3. **The restated 5.5 target holds at central values, not as a bound.** "7.5 (6.7 to 8.9)" brackets only the list assumption (¼ to 1). With the halves 90% interval added, the perfect-pilot floor is 5.6 to 9.5 at the mid list, and 4.5 to 8.9 at the low list. So 5.5 is inside the range at the low list. Label the bracket "assumption range, not an interval". Also, "0.9 to 1.1" is the median of a perfect simulator (eval-power: mean 1.96, 95th percentile 6.17); write "median".
4. **"The pilot alone is asked for about 11. Below that, τ̂ is measuring the cells' own noise and the list" is not supported.** At 11.3 (Rayquaza's gain alone) the excess left is 5,726; halves plus lists are 2,548 of it (45%) and the rest is remainder. The floor is 7.5, so readings between 7.5 and 11.3 still hold pilot, engine or unnamed error. About 11 is a proposed near-term level, not a number the pieces derive.
5. **Item 6 ("list variation cannot explain the big misses") is stronger than the evidence.** 7 of the top 9 cells have no varied deck, and Rayquaza and A/G (the two decks with the most list spread, modal share 13% and 32%) were not varied. The tested changes are one to three cards. Second lists alone give ν 60.2 (29 changes; rms 7.8) against 13.8 for the single-card swaps (58 changes), and B2e's by-design changes give rms 26.1 (Hoopa/Absol). The 6% to 23% is an assumption range, not a bound. The four-deck mean ν of 29.5 has a 90% interval of 14.8 to 49.4 when decks and versions are resampled (the README's per-deck intervals treat the 21 changes as independent). A3's scaling has no support in the data: across the four measured decks, (1 − modal share) ranges only 0.84 to 0.91 and correlates +0.02 with ν, while it is applied down to 0.19. What holds: on the tested decks a list change moves a cell 4 to 7 points, far below a 17 to 38 point miss. Charizard Y has 24 changes, not 21.
6. **Item 5 of the decision ("tested pilots move those cells by ±4") is wrong for the panel.** koh3 moves the panel by rms 6.5 (12 of 28 cells by more than 5; largest 14.0) and kpf3/kpr3 by rms 6.1 (10 of 28; largest 15.6). A/G's rms is 3.7 to 3.9, so ±4 fits A/G only. The conclusion "no net gain" is too soft: koh3's panel net is −1,216 with a 90% interval of −2,341 to −198, a cost with zero outside it.
7. **koh3's Rayquaza gain is in-sample.** RUN5 ("Development data, stated with each reading") says the 17 new cells were used to diagnose Rayquaza and design kpf, and that their holdout is the post-freeze events. So the other half of those 17 cells is not a clean holdout, and the README's A6 does not mark the in-sample point. Descriptively (not a test): against the other half koh3's Rayquaza τ̂ is 0.0 (kog3 18.15), its panel cost replicates (−1,122), and its all-45 τ̂ is 8.98 (kog3 11.37). Against the pooled halves it is 10.3 (kog3 12.4). Three designs reaching 8.5 to 8.7 answer sim-side luck only; they share the same 500 deals and the same Limitless target.
8. **Cell counts that are on the edge.** The README says 6 cells have a 90% interval above zero (63%). The checker's 1,000 draws give 5 (60%): Suicune v Vespiquen's 5th percentile is −18 here and +6 in the README. Hydreigon v Lucario (−21) and Vespiquen v Weezing (−27) are also close. Say "5 or 6". Likewise koh3's net gain interval is −64 to +4,169 in the README and +96 to +4,031 here. "Zero is inside" is on the edge, not settled. Neither changes a verdict.
9. **τ̂ interval convention.** 11.2 to 16.8 is a bias-corrected bootstrap (each draw has the chance floor taken out again). The plain percentile of score.py's τ̂ gives 14.1 to 18.8, centred on the raw 16.4. The delta method gives 11.4 to 16.3, so the README's interval is the better one. Name the convention.
10. **Smaller points.**
    - "3% to 7% in the six biggest cells" is true for the five biggest; the sixth (A/G v Blaziken) is 18%.
    - The 9.45 row ("best tested pilot in every cell") caps each cell's reach at its remainder. The actual best-cell table reads 7.94. Label the 9.45 as capped.
    - Sceptile v Vespiquen: "no tested pilot moved it more than 0.2 points" is against kog3. k3 to kp3 moved it 2.6 (66.8 → 64.2).
    - Rayquaza v Weezing (−343) is a Rayquaza cell (8 of the 9 nine-cell losses are panel cells), so "spill onto the panel" is −2,085 gross.
    - `"altaria" in k` is a tuple test. It leaves kpf3 and kpr3 out of the panel Altaria cells and A/G v Altaria only. In the other A/G cells kog3 and kp3 differ by at most 0.4, so the envelope is fine (4,861; 4,657 if they were left out of every A/G cell).
    - The other-half rates come from pooled minus development with 1-decimal percentages. The holdout rows of `gauntlet_cells.csv` give them directly and differ by at most 0.12.
    - The Limitless variance L(1−L)/n is low by a factor (n−1)/n. Using n−1 adds 148 to the chance floor and takes τ̂ to 13.93. It is score.py's own formula, so this is a note.

### Assumptions

A1 to A8 are all listed. Not marked: (a) the list part adds the two decks' swings as if independent (in A4's formula); (b) ν, measured against 7 or 8 panel opponents, is applied to cells against Rayquaza and A/G; (c) the in-sample point in item 7; (d) the bootstrap's re-subtraction of the chance floor (item 9).

### Bottom line

Every number reproduces. The findings that stand: chance 27%, Rayquaza/A/G/panel shares 43/33/24, the pilot lever sits in Rayquaza's nine cells and three designs reach it, the panel pays for it (a real cost), A/G's target moves (against the other half kog3 is at 9.0), and Sceptile v Vespiquen is untouched by any pilot. The wording that needs changing: items 1, 2, 3, 4, 5 and 6 above. The ordering "data first, then one pilot candidate" is a judgement the numbers allow but do not force.
