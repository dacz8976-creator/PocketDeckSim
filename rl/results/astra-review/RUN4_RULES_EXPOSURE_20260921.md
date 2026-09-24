# Run 4 rules exposure and report qualification

Reviewed September 21, 2026. Scope: qualify the running, frozen experiment and record the next review order. No trainer, engine, deck, checkpoint, run identity, or pass-rule changes. No training or full report execution.

## Decision

Finish Run 4 under the existing protocol, as Dustin requested. Its original numerical verdict remains a result in the frozen simulator. It is not a real-game usability verdict. Altaria does not count as validated usable until trained and evaluated on a corrected engine. Results with Altaria on either side, and averages containing those results, require this qualification. Other networks also trained against the faulty opponent, so effects need not be confined to direct Altaria cells.

A shared engine makes the comparison internally consistent; it does not make shared rule errors cancel. Search and learned policies can exploit or suffer from a rule error differently. The run remains evidence that this training pipeline runs and produces these simulator results. Comparative strength, learning difficulty, and transfer to the real game remain conditional on the rules being simulated. This does not measure how much the conclusions would change after repair.

## Direct reproduction and frozen-deck reachability

The runtime probe used the installed Run 4 add-on and actual Altaria and Lucario decks. At seed 1013, turn 1, seat 0, Eevee was Active and Swablu was on the Bench. The legal-action list offered Mega Altaria ex onto that Swablu. Only ordinary setup actions were applied; the illegal evolution was not applied. This demonstrates an offered illegal real-game action, not its frequency or effect during training. The visible state, setup action trace, deck hashes and offered action are in `run4_rules_exposure_20260921/eevee_first_turn_probe.json`.

The exact add-on SHA-256 was `797c211f007bceec7288b111c398ef63c898c1eb40447292494b0feb18c62ab1`, matching the running experiment's recorded identity. The source path is `deckgym-fork-s193/src/move_generation/mod.rs`, around lines 195-222: Active Eevee bypasses the first-turn gate before the engine iterates candidate Pokemon.

The source and card-effect review of all five frozen pool lists and both held-outs gives this reachability result:

| Deck | Conditions it can inflict |
| --- | --- |
| Altaria | Sleep |
| Weezing | Confusion, Poison, Burn |
| Blaziken | Burn |
| Lucario | None |
| Suicune | None |
| Held-out Manectric | Paralysis |
| Held-out Ninetales | None |

These effects target the opponent. No listed card applies an exclusive condition to its own Pokemon, reflects conditions, copies an attack, transfers control, or introduces an outside card. In Altaria versus Weezing, Sleep and Confusion land on opposite boards. Poison and Burn may coexist with Confusion. Consequently the Asleep/Paralyzed/Confused replacement defect is not reachable in these exact frozen matchups. Lum Berry (A2 149) is absent from all seven lists and cannot be generated, so its ordering against Bad Dreams is also unreachable here. These are static reachability conclusions; the general engine bugs still require repair.

The general source defects are visible in `src/state/played_card.rs` around lines 411-422 (independent status flags), via `src/state/mod.rs` around 1125-1176, and in `src/hooks/core.rs` (berries around 412 before Bad Dreams around 569). They should not be reported as measured causes of Run 4's Altaria results. The proven Eevee defect already establishes the required caveat. Nor is Weezing globally unaffected: it trained and was evaluated against the faulty Altaria deck.

## Report-only change and verification

`report_v4.py` now inserts the qualification near the top of the eventual report when the pool contains Altaria and the recorded add-on matches the affected binary above. It preserves all recorded numbers, pass criteria and numerical verdicts. It excludes the two-deck pilot and an unrelated engine identity. The report script is not part of the trainer identity or audit/transfer input fingerprints, so this text change does not require a trainer amendment or invalidate those result caches.

The original report source, exact diff, rendered caveat and verification evidence are preserved in `run4_rules_exposure_20260921/`. Verification: source compiles; new text renders from the actual frozen settings and identity; pilot and different-engine cases omit it; diff is limited to the new text function and its call. The active trainer and identity hashes still match their pre-edit values. The real run's REPORT.txt was not generated early and no run file was edited.

## Review order before Run 5

1. Damage calculation order.
2. Eevee's first-turn evolution exception, restricted to the qualifying Pokemon.
3. Quick-Grow and Wallace target choice, separate from random evolution-card selection.
4. Replacement among Sleep, Paralysis and Confusion.
5. Lum Berry and Bad Dreams ordering by whose turn ends.
6. Simultaneous victory/double-KO resolution and promotion order. Preserve the distinction between official wording, interpretation, and one observed Auto battle.
7. Gladion/Grunt single-source qualifiers, Wallace's HP condition, and the inexpensive lower-priority findings recorded in the rules folder. Keep unresolved Darkrai ex and Ogerpon/Serperior interpretations labeled unresolved.

This is the requested order for reviewing the forthcoming repair batch, not a claim that those repairs have been made or audited. After the batch is verified, rerun the entire k3 screen with the corrected, identified engine. Choose Run 5's pool from that new screen; preserve previous screens as historical simulator results. Skarmory, Altaria and Sceptile especially cannot be carried forward as real-game rankings.

The 57 cards with no card-specific issue found provide useful positive source-review coverage. That is not certification of 57 cards under all engine rules or a runtime regression suite.


September 22 evidence update: see [Rules evidence update](RULES_EVIDENCE_UPDATE_20260922.md). Gladion now has documented in-game support, including the empty-Supporter bonus; Grunt retains its separate qualification. Simultaneous victory priority remains open. The numbered list above is preserved as the September 21 record.
