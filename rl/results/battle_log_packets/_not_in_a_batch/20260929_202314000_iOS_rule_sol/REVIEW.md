# Victory Star while the attacker is Confused: first rule test

**Reviewer:** sol_confusion_202314, 2026-09-29. **Scope:** Entire 249.538-second supplied clip. Source identity is in [SOURCE.json](SOURCE.json). This is an explicit rule test, not a ladder result. The owner's Auto toggle is off for the first attempt and on for the second; opponent automation and Solo/PvP mode are not established.

## Finding

Victini with **Victory Star** is on the owner's Bench. Its visible card says that once during the owner's turn, *after* coins are flipped for an attack by one of the owner's Fire Pokémon, the owner may ignore those results and begin flipping those coins again. Darmanitan's **Double Smash** visibly calls for **two attack coins**. [Victini card](evidence/t058.jpg), [Darmanitan attack](evidence/t086.jpg).

The owner tries to attack with a **Confused** Darmanitan twice. In both attempts, the screen labels the preliminary coin **“Coin flip — Confused,”** the result is **Tails**, and the screen says **“The attack did nothing.”** No Double Smash attack coins are flipped, and no Victory Star choice appears before the turn passes. [First tails](evidence/t90p7.jpg), [first failed attack](evidence/t92.jpg), [second tails](evidence/t152.jpg), [second failed attack](evidence/t153.jpg).

This establishes the visible **failed-Confusion path**: the attack stops before its own coin flips, so the clip does not show an opportunity to use Victory Star on attack coins. It does **not** establish what would happen after a Confusion heads result or whether Victory Star can reroll the Confusion check itself. The separately supplied `20260929_203025000_iOS.MP4` tests the heads continuation and is reviewed in its own packet. The explanatory Victory Star text shown near 01:01 accompanies Darmanitan's evolution, before the Confusion attempts; it is not a use or a reroll prompt. [Text display](evidence/t061.jpg).

## Whole-clip account

| Clip time | Observed sequence |
| --- | --- |
| 00:00–00:50 | The game starts with owner Darumaka against opposing Yungoos. Opponent develops two Litten and Stufful on the Bench. Owner benches Team Rocket's Moltres ex and Victini. Neither side has points. [Overview](evidence/sheet_01.jpg) |
| 00:50–01:15 | Yungoos Tackles Darumaka, reducing it from 60 to 40 HP. Owner inspects Victini's Victory Star card, evolves Darumaka into 120-HP Darmanitan, and uses Lucky Ice Pop to restore its displayed HP to 120. An explanatory Victory Star banner appears during the evolution, without any attack-coin result or yes/no choice. [Victini](evidence/t058.jpg), [banner](evidence/t061.jpg), [interval](evidence/focus_50_02.jpg) |
| 01:15–01:24 | Owner plays Team Rocket's Master Plan. Yungoos becomes Confused. Its reciprocal coin is Tails, and Darmanitan becomes Confused too. Victini remains on the owner's Bench. [Sequence](evidence/focus_50_03.jpg), [Confused Darmanitan](evidence/focus_50_04.jpg) |
| 01:25–01:34 | Owner chooses Darmanitan's Double Smash. The ensuing single check is labeled “Coin flip — Confused,” lands Tails at about 01:30.7, and is followed by “The attack did nothing” at about 01:32. Yungoos stays at 60 HP and turn 5 begins for the opponent. No Double Smash pair or Victory Star prompt is visible. [Attack](evidence/t086.jpg), [tails](evidence/t90p7.jpg), [failure](evidence/t92.jpg) |
| 01:34–02:15 | Both Actives remain Confused. The opponent's own Confusion checks are visible during attacks; a successful check permits a Tackle that reduces Darmanitan 120 to 100 HP, while other failed checks lead to “The attack did nothing.” Owner uses Poké Ball, Flame Patch and Lucky Ice Pop while Darmanitan's displayed HP fluctuates with Tackle and healing. Scores remain 0–0. [Intervals](evidence/focus_50_05.jpg), [mid clip](evidence/sheet_03.jpg), [opponent check](evidence/focus_125_01.jpg) |
| 02:15–02:34 | On the owner's later turn, Darmanitan is restored from 80 to 100 HP with Lucky Ice Pop. The owner attempts another attack while Darmanitan is still Confused and Victini is still Benched. Again, “Coin flip — Confused” lands Tails at about 02:32; “The attack did nothing” follows, and the opponent's turn begins. The owner Auto toggle is visibly on in this interval. No Double Smash pair or Victory Star prompt appears. [Precheck board](evidence/t149.jpg), [tails](evidence/t152.jpg), [failure](evidence/t153.jpg), [turn transition](evidence/t154.jpg) |
| 02:34–03:05 | The opponent's Confusion check fails on its next attack. Owner switches Active Darmanitan to Team Rocket's Moltres ex; Darmanitan's Confusion clears. Owner uses Flame Patch and develops a second Moltres ex. The Active Moltres uses Netherwing to Knock Out Yungoos, and the owner receives the first point. [Switch](evidence/focus_125_05.jpg), [Moltres](evidence/t168.jpg), [first point](evidence/tail_180_01.jpg) |
| 03:05–03:40 | Opponent promotes Stufful and uses Hammer In, reducing Active Moltres ex from 130 to 70 HP. The owner's next Netherwing Knocks Out Stufful and awards a second point. Opponent promotes Growlithe. [Interval](evidence/tail_180_01.jpg), [second point](evidence/tail_180_02.jpg) |
| 03:40–04:09.538 | Growlithe's Combustion reduces Moltres ex from 70 to 40 HP. The owner uses Netherwing to Knock Out Growlithe, the third point is shown, and the screen displays **Victory**. This is the end of the test battle; no Ladder Log entry is warranted. [Final interval](evidence/tail_180_03.jpg), [Victory](evidence/t246.jpg) |

## Limits

- The two owner-side Confusion checks both land Tails. This clip cannot prove whether a Confusion Heads check allows the following attack coins or Victory Star choice. The companion clip addresses that branch separately.
- “No prompt” is a visible observation only for these failed attack paths. It is not proof that Victory Star is globally suppressed while Confused.
- The recording shows the test battle's 3–0 win but does not establish a ladder match. It has no Ladder Log entry.
