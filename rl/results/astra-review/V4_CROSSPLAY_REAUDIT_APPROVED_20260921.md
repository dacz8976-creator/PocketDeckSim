# Run 4 frozen-checkpoint test: re-audit approved

September 21, 2026. GO for the previously proposed descriptive cross-play analysis after Run 4's normal reports finish. Do not alter or restart training for this analysis. This review did not launch the test.

Approved source: `crossplay_v4.py`, SHA-256 `cc40cedb1f648d7701a33a89bf1508b91d9775f9443756f8921b753dfa5fe4db`.

Scope remains Blaziken-Lucario and Suicune-Blaziken, 400 games per checkpoint pair, 200 from each seat, using the original approved runtime recorded for this run (including the approved memory-fix amendment). The 97,000,000 seed block and game-count limit remain appropriate. At 12 scored checkpoints the two pairings require 115,200 games; use the actual final count. Runtime on the laptop is still an estimate, not a measured guarantee.

## Findings resolved

1. Interpretation: the output now explicitly describes one selected training trajectory and does not identify a cause. D is a checkpoint-age pattern, the lag window is fixed, independent changing styles are acknowledged, correlations are not called mechanisms, and the earlier sensitivity claim is withdrawn. The selected-best comparison has been replaced by a fixed last-versus-all-earlier comparison.
2. Identity: the script compares actual trainer/model/wrapper/add-on/deck hashes and Python/NumPy versions against the recorded run identity. The complete runtime identity, settings bytes, cross-play source, checkpoint bytes, saved checkpoint evaluation summaries, seeds and windows enter cache validation. Mismatched runtime roles refuse before results are changed. The actual laptop runtime currently matches the run's recorded identity.
3. Raw data: every cell retains its W/D/L string, checkpoint axes, seed formula and seat rule. The W-plus-half-D score is labeled separately from k3's ordinary win fraction. Statistical recomputation uses the saved outcomes and the preserved run state; the cross-play JSON alone does not contain all other-matchup k3 inputs. Keep state.json with the results, as the current workflow does.
4. Recovery: the old valid result remains canonical while replacement games and analysis run. Prior results are copied aside; a complete flushed temporary file replaces the canonical result atomically. Invalid JSON is retained as damaged and retried. Stale temporary files are removed. The combined CROSSPLAY.txt also uses whole-file replacement.

No blocking finding remains for the specified run and experiment.

## Verification

- The supplied practice2.log contains 42 PASS and zero FAIL lines. Both the practice and synthetic logs name the exact approved source hash above. The test driver and full log were inspected; the advertised recovery checks really include a process-group SIGKILL during games, byte-identical preservation of the prior valid result, successful retry, malformed/truncated JSON recovery, retained damaged copies and stale-temp cleanup. The driver also exercises changed input refusal/recomputation and unchanged-cache reuse.
- Independently ran 18 small checks without engine games: actual laptop runtime match; detection of each of the eleven recorded hash roles plus Python and NumPy mismatches using temporary identity fixtures; exact statistical recomputation after a JSON round trip with preserved checkpoint summaries; correct W/D/L decoding and axes; identical cross-cell bootstrap samples with 200 seeds per seat; and the fixed oldest-opponent comparison.
- The trainer still matches `74d54db888a830fe296cc107131829019c039e624917370667d4faab0420e80f`. The launcher and report retain their preceding reviewed hashes. No training, engine, checkpoint, proposed script, launcher or report source was changed by this re-audit.
- Did not rerun the cloud practice driver on the active laptop. It deliberately alters installed source/binary files as test inputs. Independent mismatch tests altered only temporary recorded identities, leaving installed files intact.

## Scope of the approval

The intervals concern evaluation variability for these frozen checkpoints. The stated one-in-ten rate is nominal and approximate, not a guaranteed finite-sample property of a bootstrap interval. It does not support a causal verdict, and the script now says so. This wording qualification is not a blocker for the exploratory analysis.

The recovery checks establish ordinary process-interruption behavior, not every possible storage failure. Each result and the combined text are replaced atomically on their own. If interrupted between pairings, completed pair results can be reused on retry before the aggregate text is refreshed.

Run 4's engine-rules caveat still applies. Avoiding a direct Altaria pairing does not remove the fact that these networks trained in the flawed five-deck simulator. This approval is for describing that frozen experiment, not for establishing real-game deck strength or usability.

The approved source, submitted logs and independent evidence are preserved in `crossplay_reaudit_20260921/`. No real cross-play games were run during this audit, and no automatic launch was arranged.
