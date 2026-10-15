# Source coverage

Reviewer: /root/added_210823. Status: full source review submitted for independent acceptance. No source move or completion registration performed.

| Interval | Covered phase | Evidence |
|---|---|---|
| 0-24 seconds | Filmed QR, New deck 16 editor, selected event deck, matchmaking, opponent reveal and second-player setup order | intake/t0000.00.jpg; native 2, 3, 20-24; overview sheet 1 |
| 24-34 seconds | Original five-card opening, chosen Alolan Grimer Active and opponent setup | native 25.5, 26.5, 27, 34 |
| 34-50 seconds | Turn 1, opponent; meaningful actions and both boundary states | TURN_LEDGER.json row 1; native boundary 35 and 50; retained targeted native event frames |
| 50-86 seconds | Turn 2, owner; meaningful actions and both boundary states | TURN_LEDGER.json row 2; native boundary 50 and 85.5; retained targeted native event frames |
| 86-114 seconds | Turn 3, opponent; meaningful actions and both boundary states | TURN_LEDGER.json row 3; native boundary 85.5 and 114; retained targeted native event frames |
| 114-161 seconds | Turn 4, owner; meaningful actions and both boundary states | TURN_LEDGER.json row 4; native boundary 114 and 160; retained targeted native event frames |
| 161-201 seconds | Turn 5, opponent; meaningful actions and both boundary states | TURN_LEDGER.json row 5; native boundary 160 and 200; retained targeted native event frames |
| 201-221 seconds | Turn 6, owner; meaningful actions and both boundary states | TURN_LEDGER.json row 6; native boundary 200 and 220.5; retained targeted native event frames |
| 221-288 seconds | Turn 7, opponent; meaningful actions and both boundary states | TURN_LEDGER.json row 7; native boundary 220.5 and 287; retained targeted native event frames |
| 288-314 seconds | Turn 8, owner; meaningful actions and both boundary states | TURN_LEDGER.json row 8; native boundary 287 and 314; retained targeted native event frames |
| 314-353 seconds | Turn 9, opponent; meaningful actions and both boundary states | TURN_LEDGER.json row 9; native boundary 314 and 352; retained targeted native event frames |
| 353-387 seconds | Turn 10, owner; meaningful actions and both boundary states | TURN_LEDGER.json row 10; native boundary 352 and 388; retained targeted native event frames |
| 387-426 seconds | Turn 11, opponent; meaningful actions and both boundary states | TURN_LEDGER.json row 11; native boundary 388 and 426; retained targeted native event frames |
| 426-433 seconds | Turn 12, owner; meaningful actions and both boundary states | TURN_LEDGER.json row 12; native boundary 426 and 432; retained targeted native event frames |
| 433-439.96 seconds | Result transition, explicit Victory versus Hons and Glimmora Card of the Game; file end | native 433.5, 434, 435, 439 |

The complete file contains one game. All 12 displayed turns are represented once in TURN_LEDGER.json; setup is not a fabricated turn 0. Source-local native evidence is 1170 by 2532. Bottom crops span full width and y=2025-2532; top crops span y=0-1050. Reduced three-second seek overview supports continuity only. The first continuous coarse decoder was stopped after 14 samples because it was slow; the complete seek overview replaced it and its coverage is not attributed to the interrupted extraction.

Owner turns have named starting and ending hands, ordered plays, individually identified normal/Research/Copycat/search cards and draw-relative native candidates, or the precise turn 12 no-draw limitation. Both boards, Energy Zones, HP, conditions, tools, Stadium and points are reconciled. The only knockout is full-art Glimmora on turn 9. Shattering Crystal tails grants Hons the sole displayed point. The last board is 0-1, while the explicit final result is owner victory following the observed opponent concession at 430-431 seconds. The last board is not a final result-statistics score.

No opened discard views, hidden opponent identities, exact unreadable ability label, absent result statistics, or unavailable live deck snapshot are reconstructed. These are enumerated in UNCERTAINTIES.json. There are no unreviewed source intervals. Independent source-bound acceptance is still required.

Independent repair revision: all eight rejected files were preserved with matching hashes. Turn 12 includes the explicit empty-deck normal-draw failure at 428-428.5 seconds and the explicit opponent concession at 430-431 seconds. Every chosen start/end frame was audited for both Energy Zone lines; current empty circles remain zero, while transiently absent or obscured next glyphs remain null. This is submitted for independent recheck, not acceptance.
