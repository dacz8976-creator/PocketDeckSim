**Second-reader report: kt on kog (ec7e1a8), by the second reader**

**Result: I agree with the first reader on every number and on both verdicts. Nothing in the first reading is wrong.** Every disagreement count below is 0.

**How I worked**
- I wrote my own code from the registration text. It is in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_kt2\second-reader\`: `sr_lib.py`, `sr_step1.py`, `sr_step2.py`, `sr_step3.py`, `sr_extra.py`, `sr_extra2.py`.
- I never opened `read_kt.py`.
- Two things were visible to me before I computed. `footprint.txt` showed up in a directory listing, and `README.md` and the task text state the laptop's policy calls. The footprints are plain counts, so this cannot have changed them. The task text itself specifies the strict coverage reading.
- I ran `score45.py --rules v2` myself, with the same 4000 reps, for kt3 and kta3. My pages are identical to the first reader's saved pages once the path lines are removed.
- I opened `READING_numbers.txt` and `READING.md` only after all my numbers existed.
- Not re-verified: the identity replays for k3, kp3, kq3, kd3 and kpr3; the A/B, the counters and the traces. The kog3 identity replays are checked below.

**Comparison** (mine / first reader's)

| Item | Mine | First reader | |
|---|---|---|---|
| Footprint kt3 (moves differ) | 14,555 of 22,500 = 64.69%, ordinary rule | same | agree |
| Footprint kta3 | 559 = 2.48%, reserve route; 17 of 45 cells non-zero | same | agree |
| Footprint ktb3 | 14,713 = 65.39% | same | agree |
| Footprint ktc3 | 1,315 = 5.84% (9 cells) | same | agree |
| kt3 dMSE (kt3 - kog3) | +0.99; 95% -16.7 to +18.9 (score45); by event -17.3 to +19.7; my own bootstrap -16.1 to +18.4; delta method -15.4 to +17.4 | +1.0; -16.7 to +18.9 | agree; interval not below 0 |
| kt3 real error | kog3 14.05, kt3 14.08 | 14.0, 14.1 | agree |
| kt3 tau margin (kog3 - kt3) | -0.035; 90% -0.48 to +0.40 | -0.04; -0.48 to +0.40 | agree |
| kt3 rule-v2 vetoes | None count. Cell misses grow on hydreigon v vespiquen (+6.4, band +/-15.3) and sceptile v weezing (+6.6, band +/-15.2), and neither counts (band over 15). No deck gap grows more than 2 (Hydreigon +1.71). | same | agree |
| kta3 tau margin (kog3 - kta3) | +0.213; 90% +0.06 to +0.31 (score45); by event +0.07 to +0.30; my own bootstrap +0.069 to +0.299 | +0.21; +0.06 to +0.31; +0.07 to +0.30 | agree; lower bound is far above -1.0 |
| kta3 real error | 14.05 to 13.84 | 14.0 to 13.8 | agree |
| kta3 vetoes | None. Worst cell +0.4, worst deck +0.09. | none | agree |
| kta3 clause (c) | All 10 decks match line for line. Altaria 0.00 +/- 0.00, Altaria/Greninja +0.20 +/- 0.28, Blaziken -0.15 +/- 0.29, Hydreigon 0.00, Lucario +0.10 +/- 0.34, Rayquaza +0.64 +/- 0.32 (9 cells), Sceptile 0.00, Suicune -0.00 +/- 0.25 (9 cells), Vespiquen +0.20 +/- 0.48, Weezing +0.10 +/- 0.20. No deck worse; no single cell-side worse. | same | agree |
| kta3 clause (d) | Rayquaza list's own side +1.000 +/- 0.390 over 8 rows. Row means: 0.00, +0.20, +1.00, +0.20, +1.00, +1.40, +3.80, +0.40. Discordant games 52 better, 12 worse; exact sign-test p = 4.6e-7. | +1.00 +/- 0.39; rows identical | agree |
| kt3 clause (d), reported | +1.000 +/- 0.617; 101 better, 63 worse, p = 0.0037 | +1.00 +/- 0.62 | agree |
| Suicune's rows, reported | kta3 -0.00 +/- 0.25 over 9 rows; kt3 -0.77 +/- 0.70 | same | agree |
| Coverage, kt3 B2e held-out | Manectric -1.11 +/- 0.77 harm; Hoopa/Absol -1.05 +/- 0.61 harm; Garchomp -0.75 +/- 0.64 harm; Raticate -0.40 +/- 0.79; Whimsicott -0.23 +/- 0.26; Charizard Y Entei +0.16 +/- 0.28 | same | agree |
| Coverage, kt3 Scizor and second lists | Scizor -0.00 +/- 0.99; Lucario 2 -0.37 +/- 0.45; Suicune 2 +0.27 +/- 0.48; Weezing 2 -0.71 +/- 0.55 harm; Charizard Y list -1.70 +/- 0.86 harm | same | agree |
| Coverage, kta3 | B2e 0.00 to +0.05; Scizor +0.11 +/- 0.61; second lists 0.00 except Charizard Y list -0.03 +/- 0.05; no harm anywhere | same | agree |
| kog3 identity vs baselines | table 14,000, new17 8,500, B2e (i<40) 3,840, Scizor 320, second lists 280 / 280 / 280 / 320, all identical | same claims | agree |
| B2e kog3 sha256 | 853cdde252c8... matches the branch file | same | agree |
| Timing | 171.8 s vs 156.5 s wall, ratio 0.91 | 0.91 | agree |

**Independent checks that add weight**
- **Mixed rows are consistent with the footprint.** For both codes, in every cell, the games that differ in the first-only or second-only mixed rows are exactly the games that differ with the code on both sides. Zero-footprint cells show no differing mixed game.
- **ktb3 and ktc3 real errors:** ktb3 14.35 with margin -0.30, ktc3 14.04 with margin +0.01. This matches the first reader's attribution: switch 2 is the cause of the kt3 failure.
- **The two kt3 cell vetoes:** the band exclusion is what stops them. Both cells also have the opponent's own side worse beyond noise (Vespiquen -6.2 +/- 2.7, Weezing -6.0 +/- 2.7). They fail the band test by 0.3 and 0.2 points. That is rule v2 as registered, and it does not change the outcome.

**Verdict per code, on its own route**
- **kt3 (ordinary rule): FAILS.**
  - The dMSE interval is not below 0, which decides it.
  - It also fails Dustin's strict own-side coverage rule on 3 of 6 B2e held-out decks and 2 of 4 second lists.
  - The verdict does not depend on how strictly coverage is read, or on the route. If kt3 were on the reserve route it would pass (b) (margin -0.04, lower bound -0.48) and (d), but fail (c) with 5 decks worse beyond noise. Those decks are Blaziken -0.88, Hydreigon -0.94, Suicune -0.77, Vespiquen -1.04, Weezing -1.59.
- **kta3 (reserve route): PASSES (a) to (d) and coverage.**
  - Footprint 2.48%; tau margin lower bound +0.06 against the -1.0 line; no veto; no deck worse in (c); Rayquaza gain +1.00 +/- 0.39.
  - It would also clear the ordinary rule's dMSE: -5.9, 95% -11.0 to -1.4. This does not change its route; the footprint fixes the route.
- **Registered outcome for the pair:** "kt3 fails: nothing adopted". kt is not adopted and kog stays the working pilot. I agree with the first reader. Registering kta afresh is Dustin's call.

**Caveats for Dustin**
- **kta3's coverage tests are almost empty, except Scizor.** Games that differ from kog3 in kta3's mixed rows:
  - B2e: 28 of 48,000 (12 of 24,000 held-out).
  - Lucario 2 list: 7 of 3,500.
  - Suicune 2 and Weezing 2 lists: 0 each.
  - Charizard Y list: 2 of 4,000.
  - Scizor: 980 of 4,000, the one informative coverage row.
  - So "no harm" on the other rows is close to true by construction, not a strong test.
- **The (d) gain is small and partly one row.** The Vespiquen row supplies 0.475 of the 1.0; without it the pooled gain is about +0.6.
- **Suicune neither supports nor contradicts kta3.** Its own side does not move (-0.00 +/- 0.25).
