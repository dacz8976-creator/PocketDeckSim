# kta's reading (Sept 30): **adopted as the working pilot, "unconfirmed"**, through the fallback

**What was read:** kta's registration, `../kta_2026-09-29/REGISTRATION.md`, registered Sept 29 on Dustin's word. It is switch 1 alone (the Tool cut) on kog, with clause (d) on the census Rayquaza list at 2,000 fresh deals per row, the 20% Jasmine line with kog3's guard, and his coverage shortcut.
- **Code:** `../kta_2026-09-29/read_kta.py`, committed at 5f4657b before any fresh game. It was written blind, reviewed, and run unchanged. The footprint was committed alone first (2c035d2).
- **Numbers:**
  - `READING_numbers.txt` is the first run at `--reps 4000`, committed at 92fc9e0.
  - `READING_numbers_reps20000.txt` is the rerun the registration asks for when a bound sits near zero (cdd3199). **That run decides the label**, and it is the reading of record.
  - score45's page is `score45_kta3_vs_kog3.txt`: the 20,000-rep page, with the 4,000-rep page in 92fc9e0.
- **Build and replays:** every game was played by the kt build ec7e1a8. Program hashes were checked before the first game, between the phases and after the last. The 7,920 identity replays all match, and timing was 1.15×, under the 1.25× limit.
- **Two readers:** the laptop is the first. `second_reader/` holds:
  - an independent second reader with its own code, which never opened `read_kta.py` and agrees on every number that gates;
  - an outcome audit against the registration, which found no blocker;
  - a reconciliation, which reran score45 at 20,000 reps on the second reader's inputs and matched the committed page.

## In plain words

- **The footprint fixed the route.** kta3 plays differently from kog3 in 528 of 22,500 games on the 45 cells (2.35%), all in the 17 Rayquaza and Suicune cells where switch 1 can act. That is under 15%, so the reserve route.
- **Accuracy is "inconclusive at this size" (RUN5's outcome 3).**
  - Real error goes 13.6 → 13.4.
  - ΔMSE is −4.3, 95% interval −8.8 to +0.0 at 20,000 reps. The unrounded upper edge (+0.03) is not below zero, so the interval spans zero.
  - It is nowhere near "wholly worsening", so kta3 can't fail on accuracy. The fallback applies.
- **The fallback's four tests all held:**
  - **No harm:**
    - τ̂ margin +0.16, 90% interval +0.02 to +0.25, where the rule asks for −1.0 or above.
    - No veto counts.
    - No meta deck's own side is worse beyond noise.
  - **Coverage:**
    - No B2e held-out deck is hurt.
    - Scizor's own side is −0.45 ± 0.65, which is noise.
    - No second list is hurt.
  - **(d) the gain on Rayquaza:** +1.03 ± 0.18 points over 8 rows × 2,000 fresh deals. The whole interval is above zero.
  - **Jasmine on deck 07:** played on 31.35% of the turns she was offered (1,738 of 5,544), against kog3's 0.39%, which is under the guard's 20%.
- **The held-out direction (RUN5: beside every verdict):**
  - Flat: 3 of B2e's six held-out archetypes closer, 2 further, 1 unchanged. The mean change in miss is +0.00, and no deck moves more than 0.1 point.
  - Dustin's six files, beside: 1 closer, 4 further, 1 unchanged, mean +0.03.
- **Deck 07, the reason kta exists, replicated on fresh deals:** +8.1 points (+6.2 to +10.0), against development's +8.5. It is reported and isn't the gate.
- **Caution:** score45's own page prints "ADOPTION RULE (v2): do not adopt". That is the ordinary rule's view, which asks for ΔMSE wholly below zero. kta3 is on the reserve route, so that line is not its test and must not be quoted as its verdict.
- **The 44-cell decision set** (without the quarantined Altaria v Sceptile cell) would read "below zero" (−9.06 to −0.03). The registered frame is the 45 cells, so this is a note only.

## Which condition carried kta3's verdict (Dustin, Sept 29: a column, not a rule)

| Condition | kta3's result | Changed games behind it | How informative |
|---|---|---|---|
| (a) footprint under 15% | 2.35% | 528 of 22,500 | fixes the route |
| ΔMSE label | spans zero (−8.8 to +0.0) | the same 528, 113 with a changed result | sends it to the fallback |
| (b) no harm on the 45 cells | τ̂ +0.16 (90% +0.02 to +0.25); no veto | 528 both-sides, 547 mixed-row | **little**: with 2% of games changed, no harm is nearly automatic |
| (c) no meta deck worse | none worse | 547 mixed-row | **little**, for the same reason |
| coverage: B2e held-out | no harm | 253 both-sides (117 held-out, 136 Dustin's files); 26 own-side mixed | **little**: 12 of 96 pairings changed at all |
| coverage: Scizor | −0.45 ± 0.65 | 1,227 both-sides; 1,007 own-side mixed | **the one real coverage test** |
| coverage: second lists | no harm | 46 both-sides; 8 own-side mixed | **little** |
| **(d) the gain on Rayquaza** | **+1.03 ± 0.18** | 862 of 16,000 kta3-arm games | **informative** |
| **Jasmine on deck 07** | **31.35% of offered turns** (kog3 0.39%) | 1,608 of 1,920 deck-07 games | **informative**: the mechanism acted |

**Clause (d) by cell** (kta3 on the census Rayquaza list v kog3 on it; kog3 on the panel in both arms; 2,000 fresh deals per row, paired by seed):

| v | kog3 | kta3 | Change | Share of the gain |
|---|---:|---:|---|---:|
| Altaria | 36.3 | 37.1 | +0.80 ± 0.41 | 10% |
| Blaziken | 30.0 | 30.4 | +0.40 ± 0.27 | 5% |
| Hydreigon | 27.3 | 28.2 | +0.90 ± 0.46 | 11% |
| Lucario | 38.6 | 39.1 | +0.50 ± 0.34 | 6% |
| Sceptile | 17.4 | 18.1 | +0.70 ± 0.54 | 8% |
| Suicune | 27.1 | 28.5 | +1.40 ± 0.57 | 17% |
| **Vespiquen** | 24.9 | 27.7 | **+2.85 ± 0.86** | **35%** |
| Weezing | 17.1 | 17.8 | +0.70 ± 0.50 | 8% |
| **pooled** | | | **+1.03 ± 0.18** | |

- Every row gains, and every row's own interval is above zero.
- Vespiquen carries about a third, down from about half at development size. The gain is spread across all eight rows, not held up by one.
- The Rayquaza traces agree. v Vespiquen, kta3 uses Scorching Interruption on 150 of 279 offered turns, against kog3's 121 of 262, and wins 62 games of 200 against 53. v Lucario barely changes (3 of 200 games differ).
- The test could detect a pooled gain of about 0.18 points half the time; the registration estimated 0.20.

## The Dustin-deck A/B (fresh; reported, gating nothing except through the Jasmine line)

1,920 games per deck and arm, paired with kog3 on the same deals.

| Deck | kog3 | kta3 | Paired change |
|---|---:|---:|---|
| **07 (Skarmory)** | 48.0% | 56.1% | **+8.1 (+6.2 to +10.0)** |
| 05 | 27.2% | 29.6% | +2.3 (+1.4 to +3.3) |
| 11 | 13.5% | 13.5% | +0.0 |
| 01 | 15.3% | 16.3% | +1.0 (+0.1 to +2.0) |
| 03 | 62.2% | 61.8% | −0.5 (−2.0 to +1.0) |

- **Where Tools go** (the predictions were written before the games):
  - Steel Apron goes on a qualifying holder 94% of the time, against kog3's 86% (predicted 70.8% → 84.7%).
  - Heavy Helmet: 46% → 68% on deck 01, 75% → 84% on deck 03.
  - Metal Core Barrier is unchanged at 81%, as predicted.
- **Stiffen's counter** is development-only, as section 4.6 provides: kog3 58 of 127 offered turns, kta3 84 of 152. The census tool has no fresh-deal (`--seed-base`) option, so it wasn't run on fresh deals. It gates nothing.

## Reported beside, gating nothing

- **Suicune** (Dustin, Sept 28: reported beside):
  - Its own side in the mixed rows over nine rows is +0.13 ± 0.28, the same direction as Rayquaza but within noise.
  - Its nine real cells' average miss goes 2.8 → 2.9.
- **Rayquaza's nine real cells** (the scoreboard's list): the average miss goes 17.8 → 17.2. Seven cells move closer; Weezing (2.4 → 3.8) and Blaziken (21.0 → 21.2) move further.
- **Detectable size of the 45-cell accuracy test:** a ΔMSE of about 4.4 points² half the time, that is, real error from kog3's 13.55 to about 13.39. The printed figures (13.60 → 13.44) convert from the rounded 13.6. The second reader caught this; it gates nothing.

## What stays provisional

- **Confirmation** comes at the post-freeze pull, read once at 804 panel matches and 303 on the new cells (about mid-October), or at the last pull before Mega Garchomp ex.
  - The check: the τ̂ margin's 90% lower bound at −1.0 or above on post-freeze events alone, and no veto.
  - kta joined that pull's list on Sept 30 (`../postfreeze_2026-09-27/README.md`), before any post-freeze result was opened.
  - **The lapse clause:** kta carries kog's A and F, so it isn't confirmed until kog's row, and the kpg and koa rows it inherits, have passed.
- **What no number here can show:** that kta plays closer to the real game. The real side of the 45 cells is the development half kta3 was chosen against.
- **Pinning:** adoption doesn't put kta into the official engine. An engine switch (RUN5's procedure) must carry kta's presets before the screen or the floor use it. It must also settle the name clash with the official program's kp-based `kta3`. Until then the screen and the floor stay on the official program's kog3.

## Records

- **The audit's three SHOULD_FIX items** (`second_reader/OUTCOME_AUDIT.md`) are handled here:
  - The verdict of record is the 20,000-rep run, as "the verdict waits for it" requires.
  - The held-out direction sits beside the verdict above.
  - Stiffen's counter is stated as development-only.
- **Two of the audit's notes for km's reader, which reuses this code:**
  - A printed "+0.0" lower edge is never called "wholly above zero". That is the lenient choice; km's reader should compare the unrounded bound.
  - The tool_census hash is reported, not gated.
- **Census counters:** they stayed on development deals because no `--seed-base` tool was supplied (STATUS.txt, 21:28 UTC). The registration's own trigger for that fallback is "if Dustin doesn't want the tool change", and he wasn't asked. It gates nothing either way. A fresh count can be added if he wants one.
