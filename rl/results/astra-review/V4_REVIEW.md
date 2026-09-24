**Run 4 / v2.2 audit — September 20, 2026**

**Outcome: return to Opus before the pilot.** The new observation numbers passed the privacy review, but the trainer can fail to deliver updated weights to four of its five game-playing networks. There is also a stopping-rule mismatch. No fixes, pilot, actual network training, full practice chain, or project add-on installation were performed. The uploaded ZIP was inspected in an isolated temporary folder. Report artifacts are the only new files in the canonical project.

Reviewed input: run4.zip, SHA-256 77e4b726bc42ecdcf840166488831c840ae1d0ff68b45b1be610636a3c158fd5. The separately uploaded design and review request exactly match the copies in the ZIP. Every packaged source and supplied result remained unchanged throughout the audit. The attached review request was used as review context; it did not authorize changes or training.

**Actionable findings**

1. **P1: only the network selected on each global publication interval gets new weights into the game workers.** `train_v4.py:1098-1100`, with the publication helper at 941-945 and actor refresh at 317-321.

   `steps` counts training updates across all networks, but each 50th step calls `publish([d])` only for the deck trained on that particular step. Other decks can train repeatedly without ever being published. The lazy actor refresh then correctly leaves those decks unchanged because their version counters have never advanced.

   Reproduction executed the actual AST body of `while trained_now < 8`, with equal available credits and a stub in place of numerical learning. Over 250 updates every network trained exactly 50 times. Publications at global updates 50, 100, 150, 200 and 250 all went to the fifth deck, corresponding to Suicune in the default pool order. The other four received zero updates through this path. Full publication at an evaluation boundary eventually refreshes them, but that does not preserve the intended continuously improving self-play between checkpoints. This is a demonstrated scheduling failure, not a claim that every possible runtime credit sequence starves exactly these four decks.

   Fix direction for Opus: count publication intervals per network, or publish all changed networks at each global interval. Keep the two-deck lazy refresh if desired. Verification should show that every network which trains reaches the workers within the declared publication interval, including tied credits and credit replenishment.

2. **P2: the plateau test is stricter than the signed Run 4 rule.** `train_v4.py:874-880` versus `FEASIBILITY.md:799-800`.

   The design requires three recent margins within three percentage points and the newest checkpoint winning at most 55% of the games it decides differently from its predecessor. The code applies the 55% test to all three checkpoints' predecessor comparisons. The actual function rejected margins +10, +11 and +12 points with corresponding paired shares 60%, 54% and 50%, even though the newest share is 50% and the margin spread is only two points. This can extend the run unnecessarily and change which checkpoints reach confirmation.

   Fix direction: apply the predecessor-share test to the newest checkpoint, as specified. Separately, `st['leveled']` is recomputed from current windows, so the current implementation waits for all networks to satisfy plateau simultaneously. The design can reasonably mean that; I have not classified it as an additional bug.

3. **P3: the documented pilot command depends on the caller's current directory.** `run_training_v4.sh:6` and `FEASIBILITY.md:841`.

   The absolute launcher path is paired with `$(cat pilot_v4_settings.json)`, which the caller's shell evaluates before the launcher runs. From another folder that file is not found; the trainer receives an empty override and fails. Resolve the settings file relative to the script/project, or document the required working directory. The actual launcher was not executed during this audit.

**Two design clarifications for Opus/Fable**

- The statement that the threat 'certain' flag is gone is true of the action row, but not of the observation. `pdl_rl_env/src/v2.rs:360` still assigns `o[6] = thr.known.min(pot.known)` during free play, and `lib.rs:459-461` still appends it for v2.2. With the full 47-card vocabulary it is observation slot 764. The supplied 0.6.0 wheel returned 1 there at 1,440 of the 1,764 tested decisions, and 0 at the other 324. This is not hidden-information leakage. The review request also explicitly says the observation stays unchanged, so these statements leave the intended scope ambiguous rather than establishing an unambiguous implementation error. If the intent was to remove the certainty signal altogether, the observation copy still needs to be addressed for v2.2; old encodings must remain unchanged.

- The proposed pilot is more different from the full run than just its opponent draw. `pilot_v4_settings.json` has a two-deck pool, so it trains both Blaziken and Lucario networks, uses 23 card IDs instead of the full pool's 47, and judges the reverse Lucario-versus-Blaziken matchup through the general floor. It is not Blaziken alone using the final five-pool observation layout. The two-deck pairing can serve the stated Run 2 comparison, but it does not validate the exact final input layout. The already flagged pool-versus-Lucario choice should settle those details together. No pilot preference was inferred and no settings were changed.

**Highest-priority check: hidden information**

No new hidden-information path was found in the two fields. `v2::features` accepts `PlayerObservation` and offered actions, then builds its forecast state from `obs.search_state` with a fixed search seed (`v2.rs:339-345`). The new fields read only the observing player's own post-move board, the public opposing score and the visible Active card (`393-403`). They do not read the live `Game` or its private hand/deck data. The existing forecast boundary still refuses hidden-dependent continuations. In the engine observation boundary inspected for this audit, opposing hand/deck identities and private choice payloads are redacted, setup opposing boards are concealed, and own deck order is reconstructed from the known multiset rather than the actual draw order. This is a dependency check of the add-on path, not an unrelated engine audit.

Independent checks on the actual supplied wheel:

- 1,764 deciding positions across 20 games and both seats: shuffling opposing hidden hand/deck contents and the observing player's deck order changed neither observation bytes nor any offered action's feature bytes. Zero failures. This included 70 setup positions.
- 241 positive controls changed the observing player's visible hand; all 241 were detected. Cases where the reshuffle left the same hand were excluded as non-controls.
- Ten additional setup pairs used different concealed Active cards, such as Torchic versus Heatmor and Bonsly versus Riolu. The other player's visible description, legal list, observation and full action-feature matrix remained identical. Both observer seats were covered.
- 9,495 priced action rows stayed within the new fields' stated ranges; 504 refused rows had all consequence fields zero. The obsolete v2 spelling remained refused.

These are source and bounded counterfactual checks, not an assertion that every card/state combination was exhaustively tested.

**Compatibility and field-value checks**

The old 0.5.0 and supplied 0.6.0 wheels were run separately on the same fixed 1,762-decision fixtures. Both legacy outputs matched exactly, including the supplied cloud digests:

- v1: 316df62aadad116612e33615ad15ed23590dcb969d727a54fd72da3191a838f1
- v2.1: 253306507a66f4384eb27f76055fcea4e5a5ea5ad625974d6e8f8579b85a3346

The supplied v2_2_checks.py was also rerun with only filesystem paths redirected in the temporary harness. Its reported counts reproduced: 9,882 matching layout rows; 8,034 in-play-count checks with zero errors; 6,810 Active-loss-flag checks with zero errors. Its exclusions were also reproduced: refused forecasts and self-damage for the count check; terminal states, pending follow-up choices and changed Actives for the loss check. This confirms the provided test result within that test's coverage; it is not an independent exhaustive validation of the skipped classes. Observation size remains 865 and action size changes from 193 to 194 for the full pool.

**Trainer, resume, seeds and verdict checks that passed**

- Actual actor probes routed each seat's decisions and targets only to its own deck. A past-checkpoint seat contributed no training rows. Only the two decks in play were loaded; a version change refreshed only the affected network. The problem in finding 1 is the trainer's publication schedule, not this actor-side refresh.
- Buffers, insertion, replay credit and training selection are keyed by deck (`train_v4.py:957-962,1002-1010,1085-1094`). Resume starts each replay credit at zero. No cross-deck path was found.
- Five-file save consistency passed fault injection using real tiny MLPs with actual save_net/load_net. Failures before the first network file, after the second file, and before state replacement all reloaded the prior committed count and all five prior weight markers. Failure immediately after state replacement reloaded the new count and all five new markers. No mixed-generation set occurred.
- Interrupted saves can leave unreferenced completed resume files until a later successful commit, and partial `.npz.tmp` files are not cleaned by recovery. This is housekeeping, not a mixed-weights or training blocker.
- Training retains the locked unique game claim and `3,000,000,000 + resume_epoch * 100,000,000 + game_no` seed. The startup cap guard remains, and the epoch is persisted before workers start. Deck/past-seat selection does not reset or replace game_no. The relevant control flow matches the previously verified Run 3 scheme; this audit did not repeat the earlier 31,000-claim concurrency test.
- Actual extracted judge() tests passed +10.0 versus +9.9, -5.0 versus -5.1, all four zero-margin requirements, and rejection when any of the 20 matchups fell below the floor.
- Actual extracted finish() tested different checkpoint rankings for each deck, best-plus-close-runner-up confirmation, and a runner-up winning confirmation. It selected the expected different checkpoints for the five networks, assembled all 20 margins only from those selected networks, and returned the expected verdict. Confirmation evaluation was stubbed with synthetic scores; no games or learning were required.

**Reports and remaining test limits**

The report review found no new material regression in failed-replay exclusion, incomplete marking, stale-result refusal, or per-network identity. Focused fingerprint probes showed that an audit binds its own deck's checkpoint and records while ignoring another network's checkpoint; transfer binds all verdict-selected checkpoints. Changing a relevant record or checkpoint invalidated the corresponding fingerprint. The report loader rejected stale and incomplete results and accepted complete matching results. Held-out game specifications use pool networks facing held-out decks, never a network assigned to pilot an unseen deck.

The supplied package contains encoding-check results and legacy hashes, but not the full raw cloud practice-run artifacts claimed in the handoff. Those end-to-end training, kill/resume, ten-audit and launcher claims were not independently reproduced here. Independent verification used source inspection, actual wheel privacy/encoding games, mocked actor games, real tiny save/load fixtures, and synthetic scheduler/verdict/report probes. No laptop throughput or training-strength claim is made.

Evidence is preserved beside this report in `v4-review-evidence/` and `v4-review-evidence.zip`, including the exact original ZIP, reviewed source snapshots, file hashes, probe programs and outputs. Source fixes are left to Opus.
