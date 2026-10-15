# Bounded difficult-facts check: 20260908_021327000

Assigned reviewer: GPT-6 Astra, astra_mode_012720. October 2, 2026. **Narrow result: needs repair because C8 misreads Flower Shield.** Other listed corrections are accepted within the limits below. This is not acceptance of the entire supplement.

| Question | Result | Source-grounded finding |
|---|---|---|
| C2, turn 8 Energy | Accepted | Comfey has zero at 03:59 and one by 04:09. Right Raticate retains one. The added Psychic belongs to Comfey. |
| C3, Copycat and Balls | Accepted | Copycat at 05:10; Drowzee is fourth replacement draw at 05:18; completed five-card fan at 05:20 is Elegant Cape, Poké Ball, Hypno, Drowzee, Poké Ball. Both Balls show no eligible target at 05:23 and 05:28. |
| C4, turn 10 Energy | Accepted | Orb targets Benched Hypno at 05:43/05:45 while Cape resolves on Active Raticate. Settled owner Energy is Active Raticate 2, Comfey 1, Hypno 1, right Raticate 1. |
| C5, turn 11 failure | Accepted | Confusion check at 06:31, explicit attack-did-nothing at 06:36. Mewtwo has two Psychic and the opponent's current Energy remains available at 06:39. |
| C6, Goo-zooka | Accepted | Printed text at 05:00.50 lasts through the end of the opponent's next turn. |
| C8, Flower Shield | **Needs repair** | Eligibility is based on Psychic Energy attached to each protected Pokémon, not to Comfey. Protection did not begin globally on turn 8. |
| Master Plan name | Accepted | Full name Team Rocket's Master Plan at 04:27; Hypno immunity message at 04:29. Resolves the older unnamed-Supporter limit. |

## Required Flower Shield repair

The native Comfey text in `t0188.00.jpg` says each of your Pokémon that has any Psychic Energy attached recovers from Special Conditions and cannot be affected by them. A lossless in-memory crop of that retained frame, bounds **[165,1700,440,2080]**, was used to read the text without full-frame display reduction. No new video extraction or saved image was created.

At **01:23**, Drowzee has one Psychic and a blue protection icon while Comfey has zero Energy. At **03:08**, Drowzee has two, center Raticate two, and right Raticate one; those eligible Pokémon have protection icons while Comfey still has none. Turn 8's Energy attachment makes **Comfey itself** eligible. It does not activate protection for everyone else.

Repair the supplement's C8 claim, turn 2/8 explanation, conflict records, and every effects restriction currently keyed to “while Comfey has Psychic Energy.” Apply the condition to **each affected Pokémon's own attached Psychic Energy**. At 04:29, Hypno's own two Psychic satisfy the condition. The older turn 2 statement is broadly compatible for eligible Pokémon; qualify it instead of claiming it is wholly disproved. Preserve the older packet.

## Direct evidence and ordering limits

- **Turn 8:** `t0239.00.jpg` shows Comfey zero and right Raticate one; `t0249.00.jpg` shows Comfey one. The exact claimed 242-second attachment timestamp was not inspected. The target is supported by before/after states.
- **Copycat:** `t0310.00.jpg`, `t0318.00.jpg`, `t0320.00.jpg`, `t0323.00.jpg`, `t0328.00.jpg` reconcile the replacement and two failed Balls. Drowzee existed in the old hand before Copycat and was shuffled/redrawn; the replacement reveal and completed fan establish its source here. The old first-Ball-finds-Drowzee claim is contradicted. Omitting Copycat was a separate omission.
- **Turn 10:** `t0343.00.jpg` and `t0345.00.jpg` show the Psychic orb over Hypno while the Cape animation/message runs. `t0399.00.jpg` and `t0408.00.jpg` show settled counts. Preserve overlap; these frames do not establish a strict input order between Cape and Energy. The old third-Energy-to-right-Raticate claim is contradicted.
- **Turn 11:** `t0391.00.jpg` and `t0396.00.jpg` establish attempted attack followed by failure. `t0399.00.jpg`, `t0404.00.jpg`, `t0408.00.jpg` retain Mewtwo at two Psychic and owner Active Raticate at 150 HP. The selected attack name is not exposed. Tails is inferred from the failed Confusion outcome rather than separately read from a landed coin label. “No attack occurs” should become “attack attempted but failed,” not merely “no damage.”
- **Goo-zooka:** `t0300.50.jpg` directly supplies duration. This checks the displayed card wording, not simulator behavior.
- **Master Plan:** `t0267.00.jpg` directly supplies the name and effect, `t0269.00.jpg` shows immunity, `t0271.00.jpg` shows the self-confusion coin condition. Later Mewtwo Confusion is visible. The selected coin still does not independently label the final outcome.

## Mode, source and metrics

No Auto control was visible in the 20 inspected frames. Named opponent and player timers are visible. Under the owner's rule, any observed Auto control would require computer classification even if OFF; this bounded check raises no such new finding and does not certify continuous absence.

Source is `20260908_021327000_iOS.MP4`, **767,232,143 bytes**, SHA-256 `95df14af59472ec02a077b5a5804f1a44e6c02048179952934b68c56eee1e387`. The completed root verification receipt supplies identity; no original-video read or duplicate hash was performed.

Inspected **20 unique retained native frames**, with one additional lossless in-memory crop view of an already inspected frame. Zero new video extractions, saved image files, source reads or mutable-packet hashes. Native frames are 1170 x 2532; full-frame tool previews were reduced to 946 x 2048. Times are requested source-local extraction targets, not independently measured presentation timestamps. Wall time, tokens and cost were not independently measured.

Only these new action-check files were written. Original packet, source, accepted outcome and logs remain unchanged.

