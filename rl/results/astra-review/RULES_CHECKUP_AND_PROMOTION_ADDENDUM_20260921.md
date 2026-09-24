# Updated rules evidence and promotion-order review
September 21, 2026. Read-only review; no engine, add-on, trainer, rules document, installed package or active job changed. Only this report and its companion evidence were added. This is an addendum to RULES_AND_V4_3M_REVIEW_20260921.md, not a new training-status check.

## Promotion order: confirmed in the exact Run 4 binary
Two isolated legal-action probes used the installed add-on whose SHA-256 matches Run 4: 797c211f007bceec7288b111c398ef63c898c1eb40447292494b0feb18c62ab1.

Each side had Voltorb (A2 054), Rocky Helmet, and at least two Benched Pokemon to ensure a real choice. Each Voltorb used Big Explosion once. Before the second attack both Actives had 30 HP; the second attack knocked out both. The fixtures were ordinary 20-card decks, seed 123, with no state injection.

| Seat causing the double KO | First promotion choice | Second promotion choice |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 0 | 1 |

Full deck contents, action traces, exposed choices, source hashes and image hashes are in DOUBLE_KO_PROMOTION_PROBE_20260921.json. These are two targeted examples, not a frequency estimate for training.

The source explains it: apply_action_helpers.rs:878-890 collects knocked-out Pokemon from seat 0 then seat 1; :835-842 queues promotions in that order. state/mod.rs:1401-1402 inserts each at the start of the stack, while move_generation/mod.rs:45 consumes the last entry. Thus seat 0 resolves first when both Actives enter the same knockout batch. Do not generalize this to every multi-wave or sequential knockout case.

A bounded review of eight existing frames from battle 225430 found both Actives empty at t163, bottom Mega Blaziken visibly promoting at t165 while the opponent's Active is empty, and opponent Electrode promoting at t167. This supports turn-player-first presentation. Because this was Solo with Auto enabled, it does not independently establish hidden choice timing or that the second chooser sees the first choice. A manual double-KO example with at least two Bench options on both sides would settle the information/choice-order issue. No new video extraction or broader battle review was performed.

## Checkup: new primary wording supersedes earlier uncertainty
The updated transcript at rules/_research_notes/in_app_tips_about_battle_rules.md:75-86 explicitly states ending-player-first Special Conditions, Poison/Burn/Sleep/Paralysis order, Checkup outside either turn, and Knock Outs at Checkup's end. This supersedes the prior report's statement that these particular rules lacked primary evidence. The original Tips screenshots were not independently inspected in this review; the saved transcription was read.

Current source does not implement the stated timing. apply_action_helpers.rs:247-276 calls handle_damage for individual Poison/Burn applications; handle_damage at :487-505 immediately calls handle_knockouts. That function scores/removes Pokemon and checks winners before later Checkup effects. Snowy Terrain/Sand Slammer and Blessed Salt run afterward at :314-315. The Blessed Salt comment claiming this agrees with official timing is therefore unreliable. The rules document's claim that deckgym already permits same-Checkup healing to rescue such a Pokemon is also incorrect.

There is also an ordering mismatch: targets are collected seat 0 then seat 1 (:205-232), then processed in global condition phases (:246-312), rather than completing the ending player's conditions first. These are source findings, not runtime reproductions in the pinned wheel. The inspected helper hash is preserved in the companion JSON and matches the previously recorded source manifest; that alone does not prove compiled behavior.

Run 4 contains Burn, Poison and Sleep, so affected timing states cannot be dismissed solely from its deck lists. The pool contains none of the three named Checkup-damage/healing abilities. Neither frequency nor outcome impact has been measured. Ability timing relative to conditions remains unresolved; do not prescribe a particular healing order from the Tips alone.

## Remaining evidence qualifications
- t168 visibly reads "Opponent's turn" and "Current turn: 6". Say game turn 5 followed by game turn 6, not the player's fifth personal turn. Source state/mod.rs:1193-1197 advances the combined counter and ties after turn 30. This clip does not show the actual turn-limit ending or verify every mode's numerical cap.
- Guaranteed opening Basic is supported as recorded owner experience, but does not settle the dealing algorithm. The difference need not be negligible: with exactly two Basics in 20 cards, a random five conditioned on containing a Basic gives two Basics 11.8% of the time; forcing one Basic then drawing four from the other 19 gives 21.1%. These are illustrative mathematical models, not measured app odds.
- Paralysis blocks attack/retreat until normal expiry; it does not always cost an entire turn. Evolution, switching and cures can remove it earlier, and other actions remain available.
- Checkup being outside either turn does not by itself settle every temporary-effect expiry edge case. Keep blanket expiry claims labeled inference pending a specific ruling/test.
- The no-Pokemon loss wording is strong primary evidence. The transcript still contains no worked simultaneous points/empty-board example; distinguish its application to that edge case from an explicit official example. Both-empty and simultaneous-threshold ties remain interpretations/community-supported cases.

## Run 4 disposition
Continue the frozen experiment under its existing stopping rules; do not swap its engine midway. The promotion behavior is shared engine/add-on behavior, not evidence that the add-on offers a different legal set from its own engine. It can affect decision sequencing and information, so it belongs on the engine-correctness list with the Checkup findings. Matching k3 and network environments does not guarantee that errors cancel or that the result transfers faithfully to the app. Verify and correct these issues separately before treating a later run as a game-faithful comparison. No training decision or job state was changed here.
