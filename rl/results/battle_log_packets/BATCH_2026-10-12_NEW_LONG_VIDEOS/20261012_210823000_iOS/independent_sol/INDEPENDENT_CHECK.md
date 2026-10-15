# Independent source-bound check

Reviewer: /root/check_210823. Outcome: rejected pending material repairs. Exact source: 20261012_210823000_iOS.MP4, frozen SHA-256 ca0f516306d5ffd8bf18326d4057d357160f77aaa019efdfd87303336b1291b9. No primary packet file, source, index or external artifact was changed.

Read START_HERE_VIDEO_REVIEW.md, Review_Log/README.md, PAUSE_GAMES_REVIEW_PROTOCOL.md and the assignment template. This is a bounded semantic acceptance check, not a second full decode. All eight supplied final files were read or queried, and their current hashes are frozen in CHECK_RESULT.json as rejected inputs.

## Required repairs

1. At 430, 430.5 and 431 seconds the native source says **Your opponent conceded**. The packet's claim that dense ending inspection found no cause wording is false. A fresh direct extraction at 430 seconds independently verifies the message. Record observed opponent concession consistently, remove the terminal-cause uncertainty, and add the terminal system event to turn 12. Keep the last observed 0-1 board separate from final score or unopened result statistics.
2. At 428 and 428.5 seconds the source says **No cards left in deck; unable to draw cards**. The no-added-card conclusion is correct, but empty owner deck is directly observed rather than an arithmetic possibility. Record the failed draw system event and remove that false uncertainty. Three cards persist and no owner voluntary play occurs.
3. Recheck Energy Zone phase binding. At 87 seconds the opponent current circle is visibly empty, contrary to the turn 3 start record of one available Darkness. At 117, 206.5 and 292 seconds the owner next glyph is absent during generation, contrary to the next Darkness count. At 200 seconds both next glyphs are absent in the animation. Null with an explicit phase limit or an independently cited later pre-action zone frame is appropriate where visibility does not establish a value. Recheck all boundary records, since the present helper appears to default the next glyph to Darkness even when absent.

## Supported checks

- Twelve ledger rows cover displayed turns 1 through 12 exactly once, with setup separate. Prose and coverage intervals span source 0 through 439.96 seconds.
- The opening at 25.5 seconds visibly contains Lucky Ice Pop, Professor's Research, Copycat, Alolan Muk and Alolan Grimer in that order. Grimer is the selected Active. Fresh extraction at 25.5 seconds agrees with retained source evidence.
- Selected hands at 117, 206.5 and 355.5 seconds still precede their first plays. The turn 4 Regigigas is in the five-card hand and not yet benched. Turn 6 has six cards and Pawniard remains on the right Bench. Turn 10 has five cards and Glimmet remains Active. Fresh source frames at 206.5 and 355.5 agree with retained evidence. At 355.5 the current Energy circle is empty, correctly captured as empty in the ledger.
- Copycat's individual reveal frames at 149, 149.5, 151, 151.5, 152.5 and 153.5 seconds show Kingambit, Ilima, regular Glimmora, Lucky Ice Pop, Rare Candy and full-art Glimmora, in order. Six draws, then evolution, reconcile to five cards.
- Ordinary turn 6 first plays Rare Candy into right Pawniard/Kingambit, then attaches Darkness to right Kingambit. The ending hand at 219.5 contains Ilima, Glimmora, Lucky Ice Pop and Glimmet. Six minus Candy minus Kingambit equals four.
- Ordinary turn 10 first evolves Active Glimmet, then Research draws Poké Ball and Heavy Helmet. Helmet is on right Kingambit, which remains 140 HP. Regigigas is benched at full 150 HP. The ending hand at 378 is two Lucky Ice Pop plus Poké Ball. Five minus evolution minus Research plus two draws minus Helmet minus Regigigas equals three.
- The turn 11 retreat sequence clears Poison; before/after attached icons support paying one Darkness and one Colorless, leaving one Darkness on the damaged first Mega. At 420 the coin result is zero heads and three tails; 422 explicitly says The attack did nothing.
- The dense ending retains a three-card owner hand, full 90 HP Glimmora, unused Darkness, and Victory versus Hons at 439. The terminal cause correction above is directly visible, not inferred from the 0-1 board.
- Filmed QR/New deck 16 binding remains separate from the missing live-log deck snapshot. No opened discard-pile contents and unreadable opponent ability/Colorless origin limits remain valid. No Auto control is observed in inspected evidence and the event queue is explicit.

Independent direct extractions used ffmpeg with one thread at 25.5, 206.5 and 355.5 seconds. The consequential ending contradiction justified one additional direct frame at 430 seconds. No repeat source hash or full decode was performed. The root shared writer must repair and request recheck before acceptance or archival.
