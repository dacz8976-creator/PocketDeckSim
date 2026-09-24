# Astra review: RLCard add-on, September 18, 2026

No add-on legal-action or observation blocker found in the reviewed reset/step path. This is a review of Opus's add-on against the engine, not a certification of engine rules or an overall training-readiness audit. No gameplay fixes or refactors were made.

## 1. Original replay check, unchanged

Independently ran the original script and supplied wheel before reviewing item two:

- k3: 100/100 final-state matches, 50/50 from each replay seat.
- k2 control: 24/100 matches, 11 from replay seat 0 and 13 from replay seat 1.
- Identical to the expected result.

The first run's result file was subsequently overwritten by Opus's new run. `step1b_unchanged.json` preserves the first run's JSON reconstructed from this task's captured stdout. Its script hash matches the preserved original script. `opus_result_received.json` is the other session's result and is not represented as my rerun.

## 2. Legal actions and observation

**Updated independent rerun: PASS, 2,606 replayed decisions, zero move-list, state, or PlayerObservation fingerprint mismatches.** Final-state matches remain 100/100 for k3 and 24/100 for k2. Output is preserved independently in `step1b_updated_stdout.json`.

Opus supplied a newer script and wheel during this review. The updated script already compares all three fingerprints at each replayed decision and includes zero mismatches in its pass condition. I reran that supplied version unchanged, as requested in the follow-up. Consequently no extra assertion is needed in the final shared source. The test hooks/assertion I initially added were superseded by Opus's concurrent update; they are not part of the reviewed final source.

The legal-action fingerprint uses the full serialized Action list in canonical order, including actor, targets and stack flag. It does not use the shortened legal_actions labels or the hashed neural-network features. This is a 64-bit fingerprint comparison, rather than a direct byte-for-byte assertion. Across 2,506 adjacent-decision comparisons, only one move-list fingerprint repeated; no state or observation fingerprint repeated.

Why the skipped counter does not affect the mask:

- Add-on `pdl_rl_env/src/lib.rs:164`: advance obtains a fresh clone of the current Game state, calls generate_possible_actions, and applies the same canonical ordering as the engine. It caches that list only until a step; step applies an action to the same Game and calls advance again.
- Engine `src/game.rs:199`: play_tick generates and orders legal actions before accessing decision_counts. The counter at lines 220-221 only selects that seat's bot-search randomness. It is not a State field or a move-generation input.
- First-turn restrictions use State.turn_count. For example, `src/state/mod.rs:1221` implements is_users_first_turn as turn_count <= 2, and `src/move_generation/mod.rs:204` uses it for evolution. The shared apply_action path still performs the normal turn transitions (`src/actions/apply_action_helpers.rs:49`, `src/state/mod.rs:1194`). Skipping a network-seat decision counter does not freeze these transitions.
- The updated engine recorder generates its reference list from the pre-tick state. That is the same immutable State input and canonicalization used immediately inside play_tick; no intervening state mutation occurs.

Observation provenance:

- Add-on `pdl_rl_env/src/lib.rs:404` calls self.game().observation(player) anew each time, then encodes that observation.
- Engine `src/game.rs:270` constructs PlayerObservation from the live Game state and the same per-player revealed knowledge used by play_tick. Game::apply_action updates that knowledge at line 302 even when the caller is the add-on.
- PlayerObservation creates a fresh redacted copy for information hiding. It is not a separately advanced game state. There is no persistent shadow observation that can drift during ordinary reset/step play.
- Scope note: the explicit snapshot/restore utility reconstructs a Game and resets reveal memory, as documented in that API. It is a separate path and is not what these replay checks exercise.

Coverage is the brew-03a mirror and the 100 k3 replay trajectories, including setup and early turns. Automatically executed single-option actions are not network decisions and are not separately counted among the 2,606 comparisons. The source-path review covers their use of the same action generator and apply_action.

No separate engine bug was identified in this targeted review. No broader engine audit was performed.

## 3. Engine-loop k3 mirror baseline

Both players were k3 with the same brew-03a Arceus/Nihilego/Toxapex deck. Used the original supplied wheel's engine_play function, which calls Game::play, not the add-on's network step loop. Ran 1,000 distinct seeds, 18,900,000 through 18,900,999. The evaluated player alternated seats: 500 games from each seat, with no duplicated seed starts. Draws count as non-wins.

| Evaluated seat | Games | Wins | Losses | Draws | Win rate |
|---|---:|---:|---:|---:|---:|
| 0 | 500 | 244 | 239 | 17 | 48.8% |
| 1 | 500 | 257 | 232 | 11 | 51.4% |

Total draws: **28/1,000 (2.8%)**. The 55%-from-each-seat pass rule is above both observed k3 self-mirror baselines. These estimates have sampling variation; this run does not establish a precise inherent seat advantage.

All 1,000 game records were checked for unique seeds, seat counts and agreement with the summary. Raw games are in `mirror_games.jsonl`, summary in `mirror_summary.json`, and the runner in `mirror_runner.py`. The baseline took 261.8 seconds; concurrent work makes that elapsed time unsuitable as a throughput benchmark.

## Input identity and rerunning

Pinned engine commit: 237b0f8198308f3608c5b790cd81b33342de91fb (pdl-unified1-release). Exact script, wheel and deck SHA-256 values are in `input_identity.json` and `mirror_summary.json`. The newer Opus inputs are preserved under `updated_opus/`; original source backups are under `original/`.

The temporary WSL Python environment `/tmp/pdl-astra-rl-review/bin/python` now has Opus's updated wheel installed. From the project root, it can run the current `Boss Folder/rl-feasibility-2026-09-18/step1b_k3_replay_check.py`. No engine source, training settings or gameplay behavior was changed by this review.
