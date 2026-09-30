# km's reading (Sept 30): **adopted as the working pilot in the tables, "unconfirmed"**, replacing kta3, through the fallback

**What was read:** km's registration, `../trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, as registered Sept 29 on Dustin's word. It is read with two amendments:
- **Amendment 1** (3aed736, Dustin's choice B) re-issues km on kta. km3 is kta3 plus N2, the lasting Stadium damage bonus counted in the threat clock, and it is read against kta3 in every test.
- **Amendment 2** (e308a65) writes in the Stadium thresholds.
- **Build and programs:**
  - B = 1f6319e. The cloud's round at B passed in full (53fc5a1): 114,840 games, every one equal.
  - The laptop built its own programs from B, pinned their hashes, and checked them against the pins before and after every part.
  - Its identity games at B agree on the tested games: 15 checks, 5,240 games (fcb3901).
  - Timing: 1.06×, under the 1.25× limit.
- **Order kept:**
  - the threshold sample (1fc9e0b), then the independent check (80d77cf), then the amendment (e308a65);
  - the footprint committed alone (dac7dcf) before anything else was read;
  - Dustin's go-ahead for the tables (RUN5, c74d8df).
- **Code:** `../trainer_pricing_2026-09-28/km_run/read_km.py`, committed at a14014e before any km game. It was written blind, reviewed, and run unchanged. Numbers: `READING_numbers.txt`. score45's page: `score45_km3_vs_kta3.txt`.
- **Two readers:** the laptop is the first. `second_reader/` holds:
  - an independent second reader, with its own code, that never opened `read_km.py` and agrees on every number that gates;
  - an outcome audit against the registration as amended, with no blocker;
  - a reconciliation that computed clause (d) a third time.

## In plain words

- **The footprint fixed the route.**
  - km3 plays differently from kta3 in 3,117 of 22,500 games on the 45 cells (13.85%).
  - Every changed game is in the 17 cells holding the panel Altaria or Lucario list, where a damage Stadium can be in play.
  - That is under 15%, so the reserve route.
- **Accuracy is "inconclusive at this size" (RUN5's outcome 3).**
  - Real error goes 13.8 to 13.9, and the change is well within noise.
  - ΔMSE is +1.1, with a 95% interval of −7.0 to +10.1. Neither edge is near zero, so no rerun was needed.
  - The registration expected a positive sign, because the simulator already over-rates Lucario. That leads to the fallback.
- **The fallback's four tests all held:**
  - **No harm:**
    - τ̂ margin −0.04, 90% interval −0.26 to +0.18; the rule asks for −1.0 or above.
    - No veto counts.
    - No meta deck's own side is worse. Suicune's own side even gains (+2.5 ± 1.2).
  - **Coverage:**
    - No B2e held-out deck is hurt.
    - Scizor −0.23 ± 0.42.
    - No second list is hurt.
  - **(d), the gain on Lucario:** +0.444 ± 0.418 over 9 rows × 2,000 deals. The interval runs +0.026 to +0.863, so the whole of it is above zero.
  - **The mechanism, M1 and M2,** compared exactly with Amendment 2's thresholds:
    - **Arena of Antiquity on Lucario's side:** km3 plays it on 35.7% of offered turns (918 of 2,574). The threshold is 27.6%, and kta3's own rate (22.4%) stays below it. It rises in all 9 cells.
    - **Training Area on Altaria's side:** km3 plays it on 33.8% (533 of 1,579). The threshold is 32.1%, and kta3's rate (28.5%) stays below it.
- **The held-out direction (RUN5: beside every verdict):** flat. Of B2e's six held-out archetypes, 2 moved closer, 3 further and 1 is unchanged; the mean change in miss is −0.02. Dustin's six files, reported beside: 4 closer, 2 further, mean +0.23.
- **Caution:** score45's own page prints "do not adopt". That is the ordinary rule's view, which asks for ΔMSE wholly below zero. km is on the reserve route, so that line is not its test.

## Two thin margins (both pass as registered; neither can be re-run)

1. **Clause (d) clears zero by 0.026 points.** Three separate computations agree to the last digit: the second reader, the audit (exact fractions), and the reconciliation.
   - The pooled mean is exactly 4/9 and the half-width 0.418054, giving a lower edge of +0.02639.
   - No rule reopens it. The near-zero rerun rule covers only the ΔMSE and τ̂ edges, the (d) interval is a formula with no Monte-Carlo noise, and (d) is "read once".
   - The gain is carried by two rows, **Lucario v Suicune (+2.65)** and **Lucario v Weezing (+2.35)**, which are also the cells where km3's Arena play rises most.
   - Dropping either of those rows, or Altaria/Greninja's, puts an 8-row lower edge at or below zero. This is reported only; the registered gate is the nine-row interval.
2. **Training Area clears its threshold by 1.7 points.** The registration predicted Training Area's rise would show in the five gating cells and not in the four Stage 1 control cells. It didn't show that way: the control cells rose about as much (+5.9 against +5.3; contrast −3.2 to +1.1). M2 passes as registered; the prediction was reported only.

## Which condition carried km3's verdict (Dustin, Sept 29: a column, not a rule)

| Condition | km3's result | Changed games behind it | How informative |
|---|---|---|---|
| footprint under 15% | 13.85% | 3,117 of 22,500 | fixes the route |
| ΔMSE label | spans zero (−7.0 to +10.1) | the same 3,117, 615 with a changed result | sends it to the fallback |
| no harm (τ̂, vetoes, (c)) | τ̂ −0.26 lower bound; no veto; no deck worse | 3,634 mixed-row games | **moderate**: about 14% of games changed, far more than kta's 2% |
| coverage: B2e held-out | no harm | 5,761 both-sides (3,183 held-out); 2,710 own-side mixed | **informative**: 40 of 96 pairings changed |
| coverage: Scizor | −0.23 ± 0.42 | 1,361; 846 | informative |
| coverage: second lists | no harm | 3,037; 1,826 | informative |
| **(d) the gain on Lucario** | **+0.444 ± 0.418** (lower edge +0.026) | 7,046 of 18,000 km3-arm games | **informative, and thin** |
| **M1 Arena of Antiquity** | **35.7%** against T 27.6% (kta3 22.4%) | km3 918 of 2,574 | **informative**: the mechanism acted, in 9 of 9 cells |
| **M2 Training Area** | **33.8%** against T 32.1% (kta3 28.5%) | km3 533 of 1,579 | informative, thin |

**Clause (d) by row** (km3 on Lucario v kta3 on it, kta3 on the other deck in both arms; 2,000 deals per row, paired by seed; Lucario's own-side score):

| v | kta3 | km3 | Change | Share of the gain |
|---|---:|---:|---|---:|
| Altaria | 37.8 | 37.4 | −0.45 ± 0.87 | −11% |
| Blaziken | 49.9 | 49.9 | +0.05 ± 0.69 | +1% |
| Hydreigon | 57.1 | 57.4 | +0.25 ± 1.33 | +6% |
| Sceptile | 38.2 | 38.2 | +0.00 ± 0.24 | 0% |
| **Suicune** | 56.5 | 59.1 | **+2.65 ± 1.69** | **+66%** |
| Vespiquen | 70.3 | 69.9 | −0.45 ± 1.64 | −11% |
| **Weezing** | 48.6 | 51.0 | **+2.35 ± 1.70** | **+59%** |
| Rayquaza | 64.5 | 63.8 | −0.75 ± 1.40 | −19% |
| Altaria/Greninja | 44.3 | 44.6 | +0.35 ± 0.84 | +9% |
| **pooled** | | | **+0.444 ± 0.418** (95% +0.026 to +0.863) | |

## Reported beside, gating nothing

- **Altaria v Suicune moved the most:** Altaria's score went 50.6 to 44.4, and its miss against real results went 5.6 to 11.8.
  - It is an investigation item, not a veto. In the mixed rows, Altaria's own side under km3 isn't worse (−0.6 ± 1.8), while Suicune's own side under km3 gains +5.0 ± 2.1. So km3 plays Suicune better in that cell, and Altaria loses games for it; Altaria's own play isn't worse. Why km3's Suicune gains there wasn't traced.
- **Lucario's real cells:** the average miss goes 6.5 to 6.3.
  - v Weezing moves closer (12.9 to 9.1).
  - v Vespiquen moves further (1.4 to 6.4).
  - v Altaria moves closer (8.4 to 7.0).
- **Altaria's real cells:** the average miss goes 0.3 to 1.0, mostly from the Suicune cell above.
- **Deck averages over the 45 cells:** every deck's gap changes by 0.8 points or less. The largest are Vespiquen (−0.8, closer) and Altaria and Suicune (+0.7 each, further).
- **The sentinels, cards N2 doesn't touch,** are unchanged:
  - X Speed 19.2% to 19.8%;
  - Team Rocket's Boss 2.7% to 2.8%;
  - Copycat 51.1% to 51.2%.
- **Field Blower's Stadium targets (M3)** rose from 57 to 257: km3 removes the opponent's damage Stadiums more.
- **A simplification to note** (the tier-1 read of B): for attacks that can roll 0 damage, the clock adds the full Stadium bonus to the expected damage. For example, Marowak ex under Arena is priced at 100 a hit against the engine's expected 95. It is within the registered formula.
- **Detectable size of the 45-cell accuracy test:** about 8.6 points² half the time. That is real error from 13.84 to about 13.52, where the printed 13.80 → 13.49 converts from the rounded figure; the second reader caught it, and it gates nothing.

## What stays provisional

- **Confirmation** comes at the post-freeze pull, read once at 804 panel matches and 303 on the new cells, or at the last pull before Mega Garchomp ex.
  - The check: the τ̂ margin's (kta3 minus km3) 90% lower bound at −1.0 or above on post-freeze events alone, and no veto.
  - Lucario's and Altaria's post-freeze cells are reported.
  - km joined that pull's list on Sept 30, before any post-freeze result was opened.
  - **The lapse clause:** km carries kta's switch 1 and, through kta, kog's A and F. So it isn't confirmed until kta's row, kog's, and the kpg and koa rows have passed.
- **What no number here can show:** that km plays closer to the real game. The 45 cells are development evidence.
- **Pinning:** adoption doesn't put km (or kta) into the official engine. The screen and the floor stay on kog3 from the official program until an engine switch carries the kog-based kta and km. That switch must replay kta3 against kta's recorded games, game for game (Amendment 1 (d) item 6; RUN5).

## Records

- **The audit's two SHOULD_FIX items** are about printing and are handled here:
  - the held-out direction now sits beside the verdict;
  - (d) is given to three decimals with its interval.
- **The reader still has three items to fix before the next reading** (flagged in kta's audit too):
  - it reads the ΔMSE lower edge only as printed;
  - it prints the held-out direction away from the verdict;
  - it converts the detectable size from a rounded figure.

  None mattered here.
- **`GO_km_tables` says it was written "about 09:45 UTC".** The file's own time is 09:31:34 UTC: 14 s after the thresholds amendment's commit and 10 s before part R started. That was a record slip in the file's text, and the order holds.
- **Dustin's go-ahead** ("The cloud has the message go ahead on the tables", Sept 30 about 02:20 UTC) came before the preparation had run. The laptop read it as "run the tables once the preparation passes", as its reply that turn said, and wrote that down before any km game (RUN5, c74d8df). The audit asks for his confirmation of that reading.
