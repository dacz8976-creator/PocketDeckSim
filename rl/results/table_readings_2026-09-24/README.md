# Table readings, Sept 24–25: every candidate read against the frozen table

These readings follow the rules in section 8 of `docs/REVIEW_2026-09-24_direction.md`, using `score.py` in this folder.

**Every candidate was scored against the same frozen Sept 23 Limitless table in one night.**
- Six or more candidates on 28 cells is a multiple-comparisons risk.
- So **any adoption is confirmed on scoreboard v2's frozen holdout half before it becomes permanent.** That half is the untouched Limitless events in `rl/results/limitless_skill_model_2026-09-25/`.
- With ΔMSE intervals as far below zero as kp3's, this is not a live worry, but it is recorded here.

**What these numbers are for:**
- Diagnostic only; never for ranking decks.
- The pilot decision is Dustin's.
- The frozen table pilot stays k3 until he decides.

**Which veto rule each reading used.** `score.py --rules` is now required, and every reading prints its rule.
- **v1 (Sept 24):** every cell and deck veto counts. The b3o3n4, b3n1, kp3 and kq3 readings below used v1 and keep it.
- **v2 (pre-registered Sept 25, for tables read from then on, starting with kd3):** a veto counts only when mixed rows on the same deals show the changed pilot's own side got worse beyond their paired noise. It never counts on a cell whose Limitless band is wider than ±15. Otherwise it is an investigation item. If a veto has no mixed rows yet, the reading says "not decided" until they are in.
  - "About ±15" was fixed at exactly 15.0 on Sept 25, on the printed binomial band, before kd3's table and independently of any candidate (Fable and the laptop agreed). It is not moved after a reading.
  - A band is wider than 15.0 only for cells with fewer than 43 matches at a 50% score, and fewer still at lopsided scores.
  - Noted in advance: on v2, Hydreigon v Suicune (30.0%, 35 matches) has a band of ±15.2, so it is out of cell vetoes by 0.2. The deck veto still covers Hydreigon and Suicune.
  - kp3's status is unaffected either way, since it was adopted by Dustin's override under v1.
- **Check of the new code:** the v1 reading of kp3 on scoreboard v2 reproduces `../scoreboard_v2_2026-09-25/kp3_vs_k3_v2.txt` number for number. The v2 mixed-row lines reproduce the Vespiquen table in `../vespiquen_mixed_rows_2026-09-25/`: +2.9 ± 1.5 on its own side, +5.6 ± 1.5 for its opponents.
- **For illustration only, not a reading (kp3 stays under v1 and Dustin's override):**
  - Under v2 on the Sept 23 table, kp3's Vespiquen deck veto would be an investigation item. The other two vetoes would wait for mixed rows.
  - Under v2 on scoreboard v2, both cell vetoes fall outside ±15: Blaziken v Hydreigon at ±18.9, Hydreigon v Suicune at ±15.2.

**The Limitless side's uncertainty by event (scoreboard v2).**
- Matches within one tournament share players, lists and a field, so the binomial band understates the Limitless side's noise.
- `score.py --limitless-events ../scoreboard_v2_2026-09-25/limitless_v2_dev_events.json` adds a second ΔMSE and real-error interval that resamples the 58 development events. The simulator draws are shared, and the binomial interval is unchanged.
- Both intervals are reported until the event interval is made standard.
- For kp3 v k3 on v2 they are close, because the simulator side's noise dominates:
  - ΔMSE over all 28 cells: −100.2 to +7.5 (binomial) against −98.3 to +7.0 (events).
  - ΔMSE on the decision set of 27: −101.1 to +9.2 against −100.9 to +8.2.
  - Real error on the decision set: +0.01 to +3.69 against +0.00 to +3.74.
  - None of the 4,000 event draws left a cell empty.

**The holdout confirmation of kp3, pre-registered Sept 25 afternoon.** Fable proposed it and the laptop agreed. It was written before any holdout file was opened, and it applies only if Dustin picks kp3 as the pilot the holdout is spent on.
- **What is compared:** kp3 against k3, paired by deal, on the decision set of 27 cells (Altaria v Sceptile quarantined, as everywhere else), under veto rule v2.
- **The holdout cells:** the frozen holdout half of B6's split, counted exactly as `../scoreboard_v2_2026-09-25/build_v2.py` counts the development half. That means cells and per-event cells, with one pairing entry counted as one match.
- **Confirmed only if all four hold:**
  1. The holdout's ΔMSE (kp3 − k3) has the same sign as the development half's, which is negative (−45.8 on v2).
  2. The pooled development + holdout ΔMSE 95% interval is entirely below zero, both binomial and by event.
  3. No veto counts under rule v2 on the holdout cells. The mixed rows are kp3 against k3 on all 28 pairings, both directions (`../kp3_mixed_rows_2026-09-25/`). They are simulator-side only, and were run on the official legality_scan before the holdout was opened.
  4. **Added Sept 25 afternoon, before the holdout was opened (Dustin, relayed by Fable): size and direction, judged on the holdout alone.** Without this, the rule's only independent condition was a sign test, which a candidate with no real effect passes half the time.
     - The real-error margin (k3 τ̂ minus kp3 τ̂), computed on the holdout cells alone over the decision set, must be at least half the development half's +2.36, that is **at least +1.18**.
     - Its 90% interval on the holdout alone must lie **entirely above zero**. The development half's was +0.01 to +3.69.
     - The quantities are the ones score.py prints on the decision set as "real error, current minus new", with current k3 and new kp3. The interval is the binomial one, the same statistic the +1.18 threshold was calibrated against on the development half. The by-event interval is printed beside it.
     - If the two intervals disagree on whether the lower bound clears zero, the reading says so in plain words. The by-event interval is **not** a second gate (agreed with Fable before opening).
     - **Known in advance:** if the development estimate were exactly the truth, the holdout would pass (4) about two times in three. At a similar standard error, about ±1.1 points, its 90% interval clears zero when the holdout estimate is above about +1.8. If the development estimate is inflated, the chance is lower. So a failure of (4) doesn't show kp3 is no better; it means the holdout didn't confirm it.
- **If all four hold:** kp3's adoption by override becomes a confirmed adoption.
- **If any fails** (including (4) failing while (1)–(3) hold): kp3 stays the working pilot by Dustin's override and is not recorded as confirmed. The next confirmation is on Limitless events after the freeze date.
- **Caveat on condition 2, written beside the rule:**
  - The pooled development + holdout table is essentially the Sept 23 pooled table rebuilt by pairings.
  - kp3's interval was already below zero there (−84.4 to −4.8), and that table informed which candidates were built.
  - So condition 2 is close to guaranteed, and **condition 1 is the real test**. Events after the freeze date are the truly unseen test.

**What the holdout can and can't show.**
- The Sept 23 pooled table included the events now reserved as the holdout, and that table informed which candidates were built.
- So the holdout checks against a table that no v2 adoption decision used, but it is not a completely unseen test.
- Events after the freeze date are.

## Candidates

| Candidate | What it is | Reading | Real error τ̂ (27-cell decision set) | ΔMSE vs k3, 95% | Vetoes | Verdict under the rule | File |
|---|---|---|---|---|---|---|---|
| k3 | the frozen table pilot | reference | 11.5 | — | — | reference | — |
| b3o3n4 | 4 list guesses + 3-move reply search | unpaired (indicative) | 10.3 | −25.2 (−73.0 to +21.7) | 5 cells, 1 deck (indicative only) | not adopted | `option_b_table_2026-09-24_reading.md` |
| b3n1 | 1 list guess, no reply search | paired | 9.2 | −46.8 (−84.7 to −7.5) | Altaria v Hydreigon +6.1; Vespiquen deck +2.1 | not adopted | `b3n1_vs_k3_paired_reading.md` |
| kp3 | public pricing, no list (tier-1 sound; conditions met at c7cb688) | paired | 9.3 | −45.5 (−84.4 to −4.8) | Altaria v Hydreigon +8.7; Hydreigon v Suicune +7.6; Vespiquen deck +2.3 | not adopted; Dustin's override question | `kp3_paired_reading.md` |
| kq3 (v1, a188c14) | kp3 + next-attack-reduction clock term + benched-main-attacker readiness (weight 250, set in advance) | **diagnostic, not an adoption candidate**; no table at a188c14 | | | | | |
| kq3 (rework, ba20dd8) | the same two habits, reworked before any table: best benched attacker's readiness (max), escape and timing rules | paired | 11.1 | −9.0 (−54.8 to +37.9); **vs kp3 +36.5 (+13.2 to +59.9): worse** | 6 cells (AvH +10.7, AvV +9.6, BvH +6.2, HvSu +12.0, ScvSu +9.0, VvW +6.6); Vespiquen deck +5.9 | not adopted | `kq3_paired_reading.md` |
| kv3 (kq v2) | kp3 + next-attack reduction + 250 × max over eligible attackers of readiness × min(1, strength / 150) | **not built**: it shares kq's bench-readiness core, and kq3 is reliably worse than kp3 | | | | | |
| kd3 | **kp3** + the defender's Weakness and damage reductions in the damage-aware clock (rebased from kv3 on Sept 25 at about 06:00 CDT, before any kd table, since kv is not built; the full spec is fixed in the build's commit message before its table) | paired against **kp3** on scoreboard v2, **rules v2**, with mixed rows on all 28 pairings; the table ran at 0c0e7f9 (spec 45a8030, amended before any table at 97ca8f4, fixes 5ae7490 and 8004222); the tier-1 read passed (`kd3_tier1_read.md`) | 9.4 (kp3 8.6) | **vs kp3 +14.2 (−11.1 to +39.6); by event −10.0 to +39.5: worse point estimate, within noise**; vs k3 −31.7 (−86.3 to +23.0) | none | **not adopted**; mixed rows: kd3 pilots Lucario (−2.2), Vespiquen (−1.5) and Hydreigon (−1.1) worse beyond noise, and Vespiquen's small gain is its opponents playing worse | `kd3_paired_reading.md` |

**Why kq3 is a diagnostic only.** The tier-1 read of a188c14 found that the code implements its pre-set spec exactly, with no leak, and that k3 and kp3 are identical (14,000 of 14,000 replays). But it confirmed three flaws in the spec itself (value_functions.rs 490-498, 1564-1566, 1597-1620):
1. The bench credit is tied to the Bench, so promoting a ready benched attacker costs −250 where kp pays 0. The risk is stalling with a free-attack front.
2. Ties go to the lower slot, so up to 250 depends on bench order.
3. The main-attacker pick switches, so benching a stronger line drops the credit.

The kq3 table still runs as registered, to see whether these flaws show in play. It counts promotions into, and retreats to, a ready main attacker, kq3 vs kp3.

**What kv changes.** kv (kq v2) was registered with the corrected formula before any of its tables:
- Eligible attackers are every benched Pokémon, plus the Active only at its target form, with a damaging attack that costs Energy.
- Strength is the best such attack over all highest evolutions, estimated as if its cost were paid.
- S = 150 is set in advance.
- The opponent's side is priced from the board only.
- A ready Active attacker gets both the 500 Active term and this term. That is intended: it makes promotion neutral, like kp.

**The official engine changed on Sept 25:**
- It is now `rl/engine-2026-09-25/deckgym`, built from main at 7fc6ccb.
- Dustin approved the switch conditional on an identity replay, and the replay passed. k3 and kp3 replay this table's reference per-game files on 14,000 of 14,000 games each, move for move, and `deckgym` matches rules4 on the screen's seeds (`rl/results/engine_identity_2026-09-25/`).
- So every reading above is unchanged under the new build.

**Other comparisons:**
- **b3n1 vs kp3 (margin-rule quantity):** real error differs by only 0.07 (90% interval −0.70 to +0.83). Going list-free costs nothing measurable.
- **Mixed rows explain the vetoes** (only one deck changes bot):
  - Hydreigon: b3n1 on Hydreigon's side +15.0; b3n1 on its opponents' side −3.1. Hydreigon is piloted better.
  - Vespiquen: kp3 on Vespiquen's side +2.9; kp3 on its opponents' side −5.6. Its opponents gain more.
  - So the vetoes are real piloting gains exposing Altaria's and Vespiquen's own open blind spots.

**Checks that were not possible yet:**
- **The held-out-deck veto.** The six held-out archetypes (B2e) have Limitless rows and decklists, but no simulator runs yet.
- **Scoreboard v2** is Dustin's call.
