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
| kd3 | **kp3** + the defender's Weakness and damage reductions in the damage-aware clock (rebased from kv3 on Sept 25 at about 06:00 CDT, before any kd table, since kv is not built; the full spec is fixed in the build's commit message before its table) | pending: spec registered at 45a8030 before any table, then amended before any table (97ca8f4, Dustin's option 3: a fallback attacker when the main threat can't damage a Pokémon, which closes the review's one-attacker gap, and victims in the defender's promotion order), plus second-review fixes at 5ae7490. The laptop's 45a8030 correctness check is superseded; the tier-1 read is redone at the table's commit. Read against kp3 on scoreboard v2 under veto rule v2, with mixed rows on all 28 pairings run before the table (`../kd_mixed_rows_2026-09-25/`) | | | | | |

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
