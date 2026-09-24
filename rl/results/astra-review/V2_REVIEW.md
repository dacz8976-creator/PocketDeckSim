# Astra review of encoding v2 and train_v2.py — September 18, 2026

Review result: fixes are needed before the laptop run. The ongoing cloud pilot remains untouched and can continue to the owner's 400k budget. Its scores still describe the implementation it actually ran; the findings below do not rewrite or discard those measurements. No source, installed dependency, pilot checkpoint, or training process was changed.

Reviewed: `pdl_rl_env/src/v2.rs`, changes to `pdl_rl_env/src/lib.rs` against the prior reviewed add-on source, `train_v2.py` against the reviewed v1 trainer, and the small `pdl_env.py` integration change. A separate focused reviewer checked the Python trainer. Exact input hashes and reproducible probes are in `v2-review-evidence.zip` alongside this report.

## 1. P1 — a saved checkpoint can cause resume to skip the draw gate

`train_v2.py:458–461` schedules both checkpoint and draw gate at 250,000 games; tuple sorting puts the checkpoint first. Each event is committed separately at line 822. Resume keeps only events whose count exceeds the saved game count (lines 621 and 657).

An interruption after the 250k checkpoint commit but before the gate commit therefore restores `games=250000` and removes the still-unprocessed draw gate. Training can continue without enforcing that stop rule. A source-derived scheduling probe reproduces the missing gate without launching training.

Fix: persist completed event identities, or process all events at one game count as a single committed boundary. Simply reversing event order transfers the skip risk to the checkpoint. Add an interruption test between the two event actions.

## 2. P2 — Bench actions are not necessarily neutral to attack potential

`v2.rs:275–280` labels every Bench placement, attachment, and evolution as board-neutral. The fast path at lines 350–352 then reuses the before-action attack and threat values, even when the board hash changed.

Two reproducible examples use the actual pilot decks and the supplied 0.4.0 wheel:

- Seed 950000, network decision 8: attach this turn's Fighting Energy to Bench slot 3. The move predicts 10 damage of remaining Active attack potential, but after spending the Energy on the Bench the recomputed potential is 0.
- Seed 950162, decision 6: evolve Bench slot 2 into Lucario A2 092. The move predicts 10 damage, but Fighting Coach raises the recomputed potential to 30.

The feature rows report these projections as fully priced. This can teach the wrong tradeoff between attaching to the Active and Bench, or obscure a Bench ability's benefit.

Fix: remove the unconditional Bench shortcut or prove a narrower class of actions leaves all attack/response dependencies unchanged. Retest the two trajectories; they include no unknown-card requirement or ambiguous chance outcome.

## 3. P2 — the threat cache key omits damage modifiers and Stadiums

`v2.rs:284–289` hashes only Pokémon in play, points, and the Energy Zone. `features()` reuses the old threat numbers when this hash is unchanged. Turn effects and the active Stadium are absent.

Reproduced on the pilot decks:

- Seed 950137, decision 8: play Korrina B3 149. Predicted remaining attack damage is 40; recomputing after the move gives 70.
- Seed 950139, decision 11: play Arena of Antiquity B3 154. Predicted damage is 10; recomputing gives 30.

Fix: include every relevant state dependency in the cache key, or recompute after effects that can change attacks or responses. Expanding the key alone does not fix finding 2, because `board_neutral(a)` bypasses it.

## 4. P2 — the same draw window can satisfy both shaping checks

At the shared 250k boundary, the checkpoint invokes `check_draws()` at `train_v2.py:779`, followed by the gate invoking it at line 765 without another game. The function increments `low_draw_checks` on both calls (lines 717–726).

A source-executed probe with a zero initial streak and a single sub-5% window leaves shaping on after the first call and switches it off after the second. Thus one window can be mistaken for two consecutive low-draw checks. Fix by checking once per distinct game boundary, or track the last checked game count. This can be addressed together with finding 1.

## 5. P3 — duplicate deck filenames can evade the resume identity check

`train_v2.py:517–521` keys input hashes by basename. If two deck paths in different directories both end in `deck.txt`, the opponent hash overwrites the first deck hash. Editing that first deck then leaves `input_identity()` unchanged and passes the comparison at line 542. A temporary-file probe reproduces this.

The chosen Blaziken and Lucario filenames differ, so this does not affect the current pilot. Key deck hashes by role or full/project-relative path and test same-basename inputs.

## Verification and limits

- Independently reproduced all four feature errors by replaying saved seeds and move-index sequences. Compared each offered move's post-action projection with a fresh observation after applying that same move. Exact selected actions and position descriptions are preserved.
- Repeated the existing v1 compatibility check: 3,965 decisions across 60 games yielded `18e818dfef01e2ca1caa`, matching the old encoding.
- A bounded independent hidden-information rerun: 478 comparisons, zero differences; the visible-hand control changed in all 157 nontrivial cases.
- Immediate points/win check: 779 priced moves out of 842 offered, all 779 agreed with the engine's sampled outcomes. This check does not validate post-action attack/threat columns 8–13, which is why it can pass alongside findings 2 and 3.
- Cross-seat observation calls did not corrupt the cached action rows in the four replayed cases. No additional actionable issue was found in the lib.rs integration or pdl_env.py wrapper within this review.
- Baseline and confirmation deck/seat assignment and paired seeds are consistent. Training both deck roles, discounting, fixed checkpoint panels, and the level-off rule follow the documented design choices.
- These are focused code and reproduction checks, not a full re-audit of engine rules or a new playing-strength experiment. No training run or Rust rebuild was launched. Known limited lookahead and branch caps remain approximations; the review does not establish exact next-turn threat probabilities.

Before the longer laptop run, address findings 1–4 and rerun their focused tests. Keep the current pilot's source/wheel identity with its results; a corrected encoding changes what its saved network sees and should be versioned rather than silently substituted underneath it.
