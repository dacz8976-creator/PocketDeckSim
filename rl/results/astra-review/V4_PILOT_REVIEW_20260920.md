# Run 4 pilot review
September 20, 2026. Audit only. No training launched and no trainer, add-on, or reporting source changed.

**Recommendation: GO for the planned five-network Run 4, with its existing floors and 6,000,000-game cap.** The pilot clears the practical strength and benching checks after correcting the benching comparison. This is permission to proceed in the design review sense, not an instruction or record of launching it.

## What I verified
- Independently recounted all 6,000 checkpoint outcomes and 3,000 confirmation outcomes from the saved game log.
- Blaziken ckpt_250k: 580/1,000 wins versus the paired k3 bar's 478/1,000, or +10.2 percentage points. Seats are balanced at 500 each; the paired-only counts are 258 versus 156. No draws for this network confirmation.
- Blaziken ckpt_200k: 568/1,000, or +9.0 points. Lucario ckpt_300k: 506/1,000 versus 521/1,000, or -1.5 points, with seven draws. The selected results satisfy the predeclared point-estimate rules.
- The three saved knockout audits are complete with zero reported replay failures. Their checkpoint hashes, record fingerprints, and other code hashes match. Pool and held-out decks match the run identity.
- The installed-wheel binary matches the add-on in the run identity. Today's trainer differs from the pilot's trainer only in the plateau explanation: reverting that text reconstructs the original trainer hash exactly.
- Independently replayed all 1,000 selected Blaziken and 1,000 selected Lucario confirmation games using their recorded actions. All winners, points, and final turns reproduced. The original audit's attack and bench counts also reproduced exactly. This replay did not rerun the expensive knockout counterfactual analysis.

## Finding for Opus: setup placements inflate the benching comparison
The old benchmark in results/run3_checks/bench_run2_vs_run3.py:39 excludes turn 0. audit_v4.py:103-127 includes it and counts starting placements as successful benching. The report's 37% to 18% comparison therefore mixes definitions.

Using the historical definition, excluding turn 0:

| Network | Eligible turns | Benched | Skipped | Skip rate |
|---|---:|---:|---:|---:|
| Blaziken ckpt_250k | 2,055 | 1,599 | 456 | **22.2%** |
| Lucario ckpt_300k | 2,546 | 1,597 | 949 | **37.3%** |

The original Blaziken audit adds 533 setup turns, all counted as successful placement, yielding 456/2,588 = 17.6%. Removing them gives 456/2,055 = 22.2%. This still comfortably clears the pilot's below-37% criterion. It improves the observed skip rate by about 15 percentage points, rather than halving it.

Both versions of my corrected tally agree: excluding setup from the current audit definition, and directly applying the historical script's definition to all decisions.

Opus should exclude setup from this historical benching comparison, review the intended player-turn denominator for giveaway/checkup rates, regenerate affected report outputs, and correct FEASIBILITY.md. This is a reporting correction; the pilot's training and win-rate result remain usable. No new wheel or retraining is needed. It need not delay training, but the final Run 4 report should use the corrected measure.

## Interpretation and remaining risks
- The older 37% benchmark used Run 2's specialist at 1M training games, 150 evaluation seeds and 356 eligible turns. The current figure is a 250k checkpoint on different evaluation seeds. It is the agreed practical reference, not a controlled comparison at identical checkpoints and seeds.
- Run 2's pilot strength confirmation used 400 games, versus 1,000 here. The approximately +11-point historical margin and current +10.2 are compatible with similar performance. They do not prove equivalence or that learning speed is identical. The pilot is sufficient to justify the next bounded experiment.
- The encoding and per-deck network design changed together. The results support the combined design; they do not establish that the two new inputs caused the improvement. Do not claim the new inputs alone worked.
- Lucario's -1.5 margin does not establish inferiority, but its behavior remains weak: 67.5% attack use, 37.3% corrected bench skips, and 115/1,239 sure knockouts missed (9.3%, from the saved knockout audit). Every ordinary pilot game supplies each network its own side's decisions; Lucario did not uniquely receive half of Blaziken's practice. Earlier-checkpoint games train only the current side, symmetrically. Keep Lucario visible in the full run's existing per-network evaluations and floors.
- The saved held-out test against Ninetales remains poor: Blaziken -9.3 points and Lucario -26.7 versus k3. I checked the saved results and input identities, but did not rerun these games. This limits generalization claims; the held-out result was not a pilot pass rule.
- The reported p value is evidence against equal win probabilities under the paired test, not a one-in-1.6-million probability that the result is luck. It also does not establish that the true margin exceeds the +10-point gate.
- The two-network training rate is 71.5 games/s. Training plus recorded evaluation time is 67.1 games/s; the 60.2 figure is the latest recorded rate, not the overall evaluation-inclusive average. None is a guaranteed floor or estimate of five-network throughput.

## Evidence
The companion V4_PILOT_REVIEW_20260920_evidence.json contains corrected replay counts, the record identity, and verification details. Original run records and reports were preserved.

Run trainer SHA-256: b8456765bd36cea327ebc20af124d08a13e3eb11fe3945c7af17bb57fcf3c46c
Current trainer SHA-256: e05c1e3aed33437832e6c16dfecd0952318b267dfe5e4a6bb79494f660aaa339
Add-on binary SHA-256: 797c211f007bceec7288b111c398ef63c898c1eb40447292494b0feb18c62ab1
