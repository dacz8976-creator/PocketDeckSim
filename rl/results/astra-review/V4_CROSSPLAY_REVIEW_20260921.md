# Run 4 cross-play review

September 21, 2026. Reviewed `crossplay_v4.py` SHA-256 `add097af4b8b3679f352cd7e776f144205eddefff9f502a1115b6948dbbe1c00` and the supplied design/practice evidence. Audit only. No real games, training, engine changes, or changes to the proposed script or launcher.

## Decision and design choices

Keep the experiment as an exploratory description of frozen checkpoint matchups, after the corrections below. Do not yet launch the full test. This does not change the decision to let Run 4 finish under its existing protocol.

- Pairings: approve Blaziken-Lucario and Suicune-Blaziken. They answer the stated observed swings without adding a direct Altaria pairing. Do not add Suicune-Altaria now. Both selected networks still trained in the flawed five-deck simulator, so the existing rules caveat remains.
- Size: 400 games per cell, 200 from each seat, is a reasonable exploratory budget. At 12 scored checkpoints this is 57,600 games per pairing, 115,200 total. Use the actual final checkpoint count. Thirty minutes is an estimate, not a measured guarantee for this script on this laptop.
- Seeds: 97,000,000 through 97,000,399 do not overlap the actual Run 4 k3, random, bar, confirmation, or held-out schedules. Training starts at 3,000,000,000. Reusing these seeds across cells is intentional pairing. The claim applies to the inspected Run 4 steps, not every experiment ever run in the repository.
- Lag: fix the 1-2 checkpoint window before seeing cross-play results. Call it checkpoint-age proximity, not an exact record of exposure to those opponents. Training used continuously changing networks and a 20% historical-opponent mixture.
- Timing/output: after the normal Run 4 reports, under the original pinned runtime, in separate CROSSPLAY output. No launcher or trainer changes. The proposed test remains unexecuted.

## Changes required before spending the games

### 1. P1: Runtime identity and cache validation are incomplete

`crossplay_v4.py:208-220` hashes the checkpoint files, its own source, the trainer source, recorded deck hashes, and saved checkpoint evaluations. It omits the actual installed add-on, `model.py`, `pdl_env.py`, and behavior-relevant settings such as feature encoding and the pool defining the card vocabulary. Those determine the games and move scores through `train_v4.py:223-226,279-284` and its model/environment imports. `check_decks_unchanged` checks deck files only.

A changed engine or wrapper can therefore reuse a finished result under the claim that inputs are unchanged. A fresh result can also be produced with a runtime different from the one that trained and evaluated these checkpoints. This is especially relevant because an engine repair batch is pending.

Include actual runtime/code/settings identities in the cache key, and check that the engine, model and observation wrapper match the run's recorded identity for this frozen-simulator question. A different-engine experiment must be explicitly separate. Existing `train_v4.report_inputs` already shows most of the needed provenance pattern. Verify that changing each relevant input prevents reuse, while an unchanged invocation skips.

### 2. P1: The interpretation does not identify chasing versus drift

`crossplay_v4.py:166-177` interprets positive D as adaptation to recently encountered opponents and near-zero D as drift. The design document makes the same distinction. Subtracting additive row/column strengths removes only additive effects. It does not remove independently changing policy styles whose matchups are non-additive.

Using the actual submitted analysis functions, I constructed two externally prescribed cyclic policy paths with a fixed matchup rule and no reaction to the opponent. The population D is +0.779. A synthetic 12-by-12, 400-outcome-per-cell sample reports D +0.820 with a 90% interval +0.779 to +0.875. It would be labeled a strong chasing signal even though there was no opponent adaptation. This is an interpretation counterexample, not evidence of a bug in the arithmetic.

Keep the matrix and D, but report D as a temporal matchup pattern conditional on these fixed checkpoints. A positive result is compatible with chasing; it cannot distinguish chasing from independent style drift or other non-additive changes. A near-zero result also cannot rule out adaptation that this lag pattern misses. A correlation with k3 strength is likewise not specific to drift; general improvement can produce it too. Negative change correlations describe competing observed movements, not a demonstrated mechanism.

The seed bootstrap measures evaluation uncertainty for this one saved training trajectory. It does not quantify variability across independent training runs or confidence in a causal explanation. The synthetic null tests assume additive drift, which excludes the counterexample by construction. One small-effect example is not a power study, and four exclusions in 40 null trials are compatible with a nominal 10% error rate rather than a precise validation of that rate. Preserve the 90% intervals as exploratory, without a binary chasing/drift verdict across the two selected pairings.

### 3. P2: Preserve the individual outcomes used by the paired analysis

`crossplay_v4.py:227-233` computes the interval from the per-seed tensor, then saves only cell means and summary statistics. This loses the matched-seed dependence needed to verify or revise the interval without replaying the entire experiment.

I supplied two outcome tensors with exactly the same saved win-rate matrix. The actual bootstrap yields [0, 0] for one and approximately [-0.242, +0.258] for the other. The saved means cannot distinguish them.

Save each cell's seed, seat and result, or an equivalent compact outcome tensor with explicit axis/seed/seat metadata and input hashes. Retain wins, draws and losses. Analysis corrections should be possible from the preserved game outcomes. With draws counting half, label the displayed quantity as win-plus-half-draw score, or keep the explicit draw definition adjacent to every headline; it differs from the ordinary win fraction used by the k3 checkpoint reports.

### 4. P2: Make result replacement recoverable after an interruption

`crossplay_v4.py:216-233` archives the existing canonical result before computing its replacement, then writes the new JSON directly. A failure before completion leaves only the archived copy. A kill during the final write can leave truncated JSON; the next invocation loads it unconditionally before considering `--redo`, so normal retry fails with a decoding error.

Write a complete replacement to a temporary file and replace atomically, preserving the prior result with a unique archive name. Handle/quarantine an incomplete cache so retry works. Verify failure during replacement and successful rerun using an isolated fixture. This concerns the new analysis output only, not the live training checkpoint mechanism.

## Additional interpretation and input notes

- The best-earlier-to-last comparison at lines 106-110 is a selected maximum, so it exaggerates apparent forgetting. In a constructed example where every checkpoint has the same true 50% score, this selection alone produced an average apparent loss of 3.94 points at 400 outcomes per cell; 91% of comparisons were positive. Keep it explicitly descriptive/selected, or use a prespecified comparison with appropriate paired uncertainty. This example does not claim those rates for the real policies.
- Accepting a `STOPPED` status is not sufficient to ensure enough scored checkpoints. A stop at the draw gate can leave no scored checkpoints, and analysis then fails. Validate checkpoint count, positive/even game count and the reserved seed block before launching workers. The real Run 4 already had seven scored checkpoints at this review, so the empty-checkpoint edge is not a blocker for this particular run.
- The current unstratified seed bootstrap can vary the seat proportions, while the design fixes 200 games in each seat. Resampling seeds within seat strata, with the same resample across cells, would align the interval with that fixed balanced design.
- The two pairings are selected from observed swings. Interpret the results as follow-up descriptions of this selected trajectory, not population-wide evidence about self-play.

## What checked out

The script holds the trainer's exclusive run lock throughout state/checkpoint reads, games and output; it rejects an actively locked or unfinished run. It uses the same greedy scorer and tie-breaking function as evaluation, with a fresh per-game seeded RNG. The even seed base and `k % 2` give the stated seat allocation. Each cell uses the same seeds, independent of worker scheduling. The untrained `ckpt_0` is correctly excluded because the trainer records `decks=None` for it. Worker model caching is bounded and scoring-only. Checkpoint weights and saved checkpoint evaluation summaries are fingerprinted.

The supplied cloud practice log reports 11 successful checks and exercises the advertised normal skip/redo/refusal cases. I inspected the driver and log; I did not rerun its games. It does not exercise the omitted runtime inputs or interrupted/corrupt-cache recovery, and it does not bind the captured log to a source hash. The original trainer still matches the approved memory-fix hash `74d54db888a830fe296cc107131829019c039e624917370667d4faab0420e80f`.

## Existing evaluation observations, requiring no new games

At the reviewed seven-checkpoint snapshot (500k through 3.5M), there are only six adjacent changes. The proposed descriptive calculation gives:

| Target matchup | Other matchup for the same network | Change correlation |
| --- | --- | ---: |
| Blaziken vs Lucario | Blaziken vs Weezing | -0.57 |
| Blaziken vs Lucario | Blaziken vs Altaria | -0.07 |
| Blaziken vs Lucario | Blaziken vs Suicune | -0.34 |
| Suicune vs Blaziken | Suicune vs Lucario | -0.04 |
| Suicune vs Blaziken | Suicune vs Weezing | +0.62 |
| Suicune vs Blaziken | Suicune vs Altaria | +0.93 |

These are small-sample, temporally related observations. In particular, Suicune's movements against Blaziken, Weezing and Altaria mostly move together, rather than showing a simple trade-off among those matchups. This does not establish drift as the cause. Altaria-related observations retain the engine-rules limitation.

## Evidence

`crossplay_review_20260921/` preserves the submitted source and source hashes, seed-range checks, synthetic counterexamples, the exact saved checkpoint summaries used above, and `reproduce_statistics.py`. No engine games were run. No trainer, launcher, engine, checkpoint or proposed cross-play source was edited.

### Isolated cache-path verification

A source-bound fixture confirmed both operational findings. It ran the submitted main/cache path against temporary files, with the trainer/deck helpers, file lock, game runner and statistics replaced by stubs. This verifies cache behavior, not actual engine execution or lock behavior. No installed module, real deck or live run was changed.

After an initial cache was produced, changing the fixture's feature setting and mock runtime file bytes still caused the next invocation to print "same inputs; skipped" and keep the identical cache bytes without calling the game stub again. Separately, malformed result JSON with `--redo` raised `JSONDecodeError` before calling that stub. Source inspection independently establishes which actual runtime inputs are omitted. See `cache_fixture_evidence.json` and `reproduce_cache_fixture.py` in the evidence folder.
