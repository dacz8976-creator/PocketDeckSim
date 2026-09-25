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

## Candidates

| Candidate | What it is | Reading | Real error τ̂ (27-cell decision set) | ΔMSE vs k3, 95% | Vetoes | Verdict under the rule | File |
|---|---|---|---|---|---|---|---|
| k3 | the frozen table pilot | reference | 11.5 | — | — | reference | — |
| b3o3n4 | 4 list guesses + 3-move reply search | unpaired (indicative) | 10.3 | −25.2 (−73.0 to +21.7) | 5 cells, 1 deck (indicative only) | not adopted | `option_b_table_2026-09-24_reading.md` |
| b3n1 | 1 list guess, no reply search | paired | 9.2 | −46.8 (−84.7 to −7.5) | Altaria v Hydreigon +6.1; Vespiquen deck +2.1 | not adopted | `b3n1_vs_k3_paired_reading.md` |
| kp3 | public pricing, no list (tier-1 sound; conditions met at c7cb688) | paired | 9.3 | −45.5 (−84.4 to −4.8) | Altaria v Hydreigon +8.7; Hydreigon v Suicune +7.6; Vespiquen deck +2.3 | not adopted; Dustin's override question | `kp3_paired_reading.md` |
| kq3 | kp3 + next-attack-reduction clock term + benched-main-attacker readiness (weight 250, set in advance) | pending | | | | | |
| kd3 | kq3 + the defender's Weakness and damage reductions in the clock | pending | | | | | |

**Other comparisons:**
- **b3n1 vs kp3 (margin-rule quantity):** real error differs by only 0.07 (90% interval −0.70 to +0.83). Going list-free costs nothing measurable.
- **Mixed rows explain the vetoes** (only one deck changes bot):
  - Hydreigon: b3n1 on Hydreigon's side +15.0; b3n1 on its opponents' side −3.1. Hydreigon is piloted better.
  - Vespiquen: kp3 on Vespiquen's side +2.9; kp3 on its opponents' side −5.6. Its opponents gain more.
  - So the vetoes are real piloting gains exposing Altaria's and Vespiquen's own open blind spots.

**Checks that were not possible yet:**
- **The held-out-deck veto.** The six held-out archetypes (B2e) have Limitless rows and decklists, but no simulator runs yet.
- **Scoreboard v2** is Dustin's call.
