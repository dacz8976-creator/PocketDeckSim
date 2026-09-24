# Run 4 crossplay results review, September 22, 2026

The completed experiment passes the integrity review and Opus's arithmetic reproduces. The claim that all remaining structure is ordinary noise does not follow. Overall checkpoint strength dominates both grids, but Blaziken-Lucario has modest evidence of additional opponent-version structure. Suicune-Blaziken is less conclusive. Neither establishes chasing, independent drift, or a learning-rate cause.

## Completed experiment

Both files contain 12 by 12 cells with 400 valid W/D/L outcomes per cell, 57,600 games per pairing and 115,200 total. Blaziken-Lucario has 27,407 wins, 610 draws and 29,583 losses; Suicune-Blaziken has 15,953 wins, 72 draws and 41,575 losses. Every cell uses seeds 97,000,000 through 97,000,399, 200 games from each seat. The same seed index is deliberately shared across cells.

The approved crossplay source SHA remains `cc40cedb1f648d7701a33a89bf1508b91d9775f9443756f8921b753dfa5fe4db`. Both complete results match all current recorded inputs: runtime identity, Python/NumPy, settings, script, checkpoint files and saved checkpoint evaluations. An independent read-only check reproduced every approved statistics field and both summaries exactly. CROSSPLAY.txt equals the combined saved summaries. Recorded durations are 837 and 526 seconds, 22.7 minutes total. No engine games were replayed for this review.

## Requested extra analysis

Scores are W=1, D=0.5, L=0. The residual is cell score minus row mean minus column mean plus grand mean. Spread is the square root of residual sum of squares divided by 121. The denominator is the dimension left after fitting 23 row/column parameters to 144 cells; it does not make the cells independent.

| Spread, in score percentage points | Blaziken-Lucario | Suicune-Blaziken |
|---|---:|---:|
| Observed residual, exact requested calculation | 2.576 | 1.876 |
| Opus noise estimate, k mod 4 split | 2.711 | 1.707 |
| Noise estimated from all seeds | 2.236 | 1.705 |
| Approximate residual-above-noise spread estimate | 1.279 | 0.782 |
| Joint seed bootstrap p, no interaction null | 0.0199 | 0.0798 |

Opus's split method is sound as a noise-variance estimate under independent, exchangeable seed draws within each seat. Each half has 100 games per seat. The half-difference divided by two has the same noise variance as the full-sample mean. Shared seeds across cells are not a defect here: using the same partition for every cell preserves their covariance. However, a single partition is a noisy estimate, and comparing two spread estimates does not supply a significance test. The square-root subtraction is only an effect-size estimate, not proof of a real effect.

The Blaziken-Lucario partition happens to give a high estimate. Across 1,000 random balanced partitions, the median is 2.219, with a central 90% range of 1.994 to 2.486. For Suicune-Blaziken those values are 1.706 and 1.515 to 1.881. These ranges describe sensitivity to the partition of the observed sample, not confidence intervals for true noise.

For the all-seed estimate, project each seed's entire 12 by 12 outcome matrix through the same residual calculation, estimate its variance separately within each seat, then calculate the variance of the balanced mean. For the null check, center these seed residuals within each seat and resample 200 even and 200 odd seed indices, identically across every cell. The statistic is residual mean square. This retains observed cross-cell dependence instead of treating 57,600 games or 144 cells as independent observations. There are 10,000 replicates with RNG seed 20260922.

This gives modest evidence of non-additive structure for Blaziken-Lucario, and weaker, borderline evidence for Suicune-Blaziken. A simple correction for testing two pairings gives p=0.0398 and p=0.1596. A supplemental delta-method check on the approved analysis's log-odds scale gives p=0.0210 and p=0.1237, respectively. These are approximate exploratory checks on selected pairings and fixed checkpoints, not preregistered discoveries, run-to-run uncertainty, or causal tests.

The additive fit accounts for 87.8% and 84.7% of the observed grid variance. Thus broad strength changes are the dominant pattern. The defensible qualification is that some smaller opponent-version effects may coexist with them. The roughly 0.8-point Suicune estimate is not established as nonzero; the stronger evidence in this analysis is for Blaziken-Lucario. Merely changing the page to say Suicune is above noise and Blaziken is at noise would get that distinction wrong.

## Interpretation corrections

1. Replace "whatever a checkpoint does to one version it does to all of them" with a dominant-pattern statement. It is not an exact property of the observed grids, and the residual check does not justify treating all deviations as noise. Blaziken's last checkpoint is the strongest row on average but leads only 8 of 12 columns, not every Lucario version.
2. Replace "nobody lost ground against old opponents" with the actual fixed comparison. Blaziken's last checkpoint improves by 7.2 points over its earlier-checkpoint average against the oldest three opponents, 90% interval +5.0 to +9.5. Suicune is -1.8, interval -4.1 to +0.6. That uncertainty permits a meaningful decline. As a descriptive example, its last checkpoint is below its first against every Blaziken checkpoint; this is not a new causal forgetting test.
3. D remains +1.0 and -0.6 approximate score points, with both intervals including zero. That finds no clear effect in the specified 1-2 checkpoint age window; it neither disproves adaptation nor exhausts possible opponent-version effects. The extra residual finding does not identify chasing either.
4. Opus is right that the mixed small Blaziken correlations do not support the proposed simple trade-off pattern. They also do not establish statistical independence or rule out trade-offs hidden by other changes. Suicune's positive correlations are descriptive evidence of co-movement, not proof of whole-network drift. There are only 11 differences per series.
5. The crossplay did not answer the causal question for which freezing was proposed. Freezing can be omitted as a practical scope choice, but not because this experiment made the causal distinction. Learning-rate decay can change both adaptation and other instability; the cause remains open.
6. Weight averaging and a decaying learning rate remain reasonable candidates to test. The observed instability motivates them, but their benefits have not been measured here. Evaluate averaged and live weights alongside each other. If their separate causal contribution matters, a design changing several training features together cannot identify it without the appropriate comparison.

The held-out losses remain a separate limitation. All crossplay conclusions concern the frozen, flawed Run 4 engine and networks trained with its Altaria defect. No result establishes corrected-engine performance or general self-play behavior. The engine repairs, corrected screen, and then a concrete Run 5 design remain the order. This review neither starts the engine batch nor authorizes training.

## Suggested replacement for the crossplay conclusion

Across these two selected pairings, most variation follows broad changes in each checkpoint's strength against the opponent deck, and those changes correlate with the k3 evaluations. Smaller opponent-version effects remain: a seed-preserving exploratory check finds modest evidence for Blaziken-Lucario and weaker evidence for Suicune-Blaziken. Neither pairing has a clear effect in the specified recent-checkpoint age window. These results do not distinguish chasing from independent drift, establish a learning-rate cause, or show that no strength was lost against old opponents. They motivate testing stability controls alongside the separate capability question.

## Reproduction and scope

`crossplay_results_20260922/reproduce.py` reads preserved copies of the two raw result files and reproduces the added analysis without games. `statistics.json` contains exact values, source hashes and method settings. `FEASIBILITY.as_reviewed.md` preserves the wording reviewed here. The original crossplay files, script, engine, checkpoints, FEASIBILITY.md and LOG.md were not changed by this review. Findings and replacement wording are ready for Opus to incorporate.
