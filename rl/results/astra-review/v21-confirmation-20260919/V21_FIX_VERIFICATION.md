# Verification of Opus's v2.1 fixes, September 19, 2026

**Result: the five findings in V2_REVIEW.md are resolved in the reviewed source and supplied add-on 0.5.0. Training was not started.** This is a focused confirmation of those fixes, not a new playing-strength result or a full engine audit. No project source was edited.

## Results independently rerun on the laptop

Ran `train_v2_checks.py` and `v2_checks.py` in the temporary WSL review environment with the supplied 0.5.0 wheel. The encoding checks completed in 131 seconds. Results agree with Opus's supplied report:

| Check | Independently verified result |
|---|---|
| Original v1 encoding | 3,965 decisions, hash 18e818dfef01e2ca1caa, unchanged |
| Hidden-card invariance | 4,666/4,666 unchanged; visible-hand control changed 1,628/1,628 times |
| Priced immediate points/wins | 6,698/6,698 within the engine outcomes sampled by the test |
| Damage dealt/taken | 5,349/5,349 agree where all four sampled chance seeds gave the same result; 3/3 varying cases within their sampled ranges |
| Remaining attack and next-turn threat after a move | 1,846/1,846 agree with a fresh calculation in the checked no-intervening-opponent-choice cases |
| End-turn row versus position threat | 2,862/2,862 agree |
| Original four reproductions | All agree: Bench Energy 0; Korrina 70; Arena of Antiquity 30; Lucario evolution 30 |

The six differences among 25 cases involving an intervening k3 choice remain classified separately: the projection assumes an opponent choice adverse to our attack, while k3 sometimes chooses differently. They are not repetitions of the four stale-value defects. Four matching sampled chance seeds are evidence from that sample, not proof that an action has only one possible outcome.

## Disposition of the original findings

1. **Resume skipping the draw gate: fixed.** The trainer collects every event at a game count, processes the gate first, and commits once after the batch. I executed the actual boundary block with temporary files and the real commit/recovery methods, while replacing evaluations and weight serialization with test doubles. Interruptions after the gate but before the checkpoint, and after the checkpoint but before the shared commit, both retained the prior saved boundary. Recovery kept both 250k events pending. Completing that boundary saved both, with no duplicate draw count. A failing gate correctly saved STOPPED without continuing into checkpoint evaluation. This is a focused interruption probe, not a rerun of Opus's full training smoke.

2. **Bench shortcut: fixed.** The unconditional board-neutral shortcut is gone. Each action branch is projected from its resulting state. The Bench Energy and Lucario examples pass.

3. **Incomplete projection cache key: fixed.** Memoization uses the full State hash. Turn effects and the Stadium are no longer omitted. Korrina and Arena pass. Each projection starts its own fixed-seed random stream, and the memo is local to one feature calculation.

4. **Double-counted draw window: fixed.** `draw_checked_at` and `last_draw_rate` persist with the state. Calling the actual draw function twice at 250k counts once; calling it at the next distinct low-draw boundary counts twice and disables shaping. The boundary interruption probe also verified a single count.

5. **Same-basename deck identity collision: fixed.** Input hashes are keyed by role. The supplied temporary-file test confirms editing one of two different `deck.txt` inputs changes the identity.

**Version separation also verified in both directions:** 0.4.0 accepts v2 and refuses v2.1; 0.5.0 accepts v2.1 and refuses v2. The old wheel was extracted temporarily for that check; no pilot environment or checkpoint was changed.

## Remaining limits and launch details

- **HOURS is a soft checkpoint limit.** The trainer checks elapsed training plus previously accumulated evaluation time at checkpoints. The current checkpoint's evaluation is added afterward. Final confirmation games and the shell's subsequent knockout/transfer reports can extend total runtime further. `HOURS=6` therefore does not promise shutdown within six wall-clock hours. The shell comments describe this behavior; a strict total-runtime cap would require a separate change.
- **The encoding check script is a diagnostic report.** Most failures are printed rather than asserted, so an exit code of zero alone is not a pass. I inspected the measured outputs, including the four reproductions. No test-script fix was made.
- The runner-up-within-seven-points confirmation and the final audit/transfer commands are present in the source. The automatic reports run for PASSED or FINISHED, not an early STOPPED failure. I inspected this wiring but did not execute those large end-of-training runs or retrain a network.
- The known limited threat lookahead remains. The calibration output includes 23.6% scoring and 11.3% wins on the next k3 turn among 406 positions labeled no knockout by the bounded projection. That forecast is not a guarantee of safety. This was not introduced by the stale-value fixes.
- Opus's pilot defensive results and the estimated 35% slowdown were not independently remeasured here. A corrected laptop run remains the test of playing strength and actual training throughput.

## Evidence

This folder contains the independent check outputs, Opus's pre-rerun report, exact input SHA-256 values, the interruption-probe script and receipt, and the version-guard result. Source locations: `train_v2.py` event batch at line 785, commit at 862, draw guard at 727, input identity at 526; `pdl_rl_env/src/v2.rs` state_key/project and the per-action project call; version selection in `pdl_rl_env/src/lib.rs` at 507.

The user selected verification and report only. No long training run, post-training matchup campaign, or scheduled monitor was launched. All installations for this verification were confined to the existing temporary review environment.
