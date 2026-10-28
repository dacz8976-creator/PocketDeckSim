# Score: ScreenRecording_10-26-2026 07-29-50_1 (G = Gemini review, X = Codex review)

Frames opened: about 46 of the 120 allowed (full-resolution `frames/t_SSSS.jpg`).

## What both reviews got right (confirmed from the frames)

Opponent went first (t=24 "You are going second"). Opening hand Kingdra ex, Poke Ball, Horsea, Small Balloon, Professor's Research. Opponent Energy Zone Fighting. Horsea Active vs Hitmonlee 80. Every turn's cards, retreats, evolutions and Abilities agree and match the frames: Poke Ball and Riolu T1; two Poke Balls, Small Balloon, Research, benches, Water, Hook 30 (80 to 50) T2; opponent Research, second Riolu, Field Blower on the Balloon, Riolu to Lucario, Fighting on Hitmonlee, Stretch Kick 30 to Benched Horsea (50 to 20) T3; Rare Candy Horsea to Kingdra ex, Stormy Prison 90 KO of Hitmonlee, point 1, Riolu promoted T4; Fighting on Benched Lucario, Small Balloon on Riolu, free retreat, Lucario Active T5; Sabrina, Riolu promoted, Water on Benched Horsea, Stormy Prison 90 KO of Riolu, point 2, Lucario promoted T6; Fighting on Lucario (2), Korrina (+30 to Active ex), Submarine Blow 90 (Kingdra 170 to 80) T7; Koffing to Team Rocket's Weezing ex, Boiler Smog Poisoned and Burned on Lucario, opponent concedes (frame 272 "Your opponent conceded") T8. Final score 2-0, 8 turns, 210 damage, Kingdra ex card of the game for Dustin, Lucario for the opponent, 986 to 999 pts (frames 281-284).

## Disagreement table (G vs X)

| Turn | Item | G says | X says | Frames | Verdict |
|---|---|---|---|---|---|
| Setup / all | Dustin's Energy Zone type | Water, "Darkness Energy also appears in the zone during the match" | Water only | t=1 deck screen Energy slot shows one Water icon; t=23, 24, 56, 62, 144, 214, 217, 268 zone and "Next Energy generated" shows Water every time | X right |
| 4 (t=154) | Energy attached to Kingdra ex | Darkness Energy attached; Kingdra then "1 Water + 1 Darkness" in every later board line (T4 to T8) | Second Water attached; "two Water" | t=154 Water Energy mid-attach to Kingdra; t=161/167/178/194/204/217/227/246/250/254/268 Kingdra shows two Water icons, no Darkness | X right |
| 2, 4, 6, 8 | Next Energy / generated Energy in the turn header | "next Energy shown: Darkness" (T2, T6), "Darkness Energy generated" (T4 t=144, T8 t=260) | Water generated | t=62, 144, 214, 217, 268 show a Water icon | X right |
| 3 | When Field Blower was played | t=118 played, Balloon discarded t=120-121 | about 122-123 | t=118 face-down card in play with Balloon still to go; t=121 Balloon already in Dustin's discard and Field Blower in the opponent's discard; t=123 both settled | G right (X 4-5 s late) |

No verdict is `both wrong` or `unsettled`. Differences of 3 s or less (concession G 270 vs X 272, true 272; Poke Ball, Research, Balloon, Rare Candy and attack times) are not counted.

## Claims only one review makes that the frames contradict

- G only: Darkness Energy exists in Dustin's Energy Zone and was attached to Kingdra ex (see rows 1 to 3). Nothing in the frames shows a Darkness Energy anywhere; the deck's Energy is Water only (t=1).
- X only: nothing contradicted. (Field Blower time is the only X slip.)

## Errors by review

### G
| Grade | Turn | Item | G says | Truth | Frames |
|---|---|---|---|---|---|
| Major | Opening | Dustin's Energy Zone type | Water plus Darkness | Water only | 1, 23, 24, 62, 144 |
| Major | 4 | Energy attached to Kingdra ex (and the later board lines T4-T8 that repeat "1 Water + 1 Darkness") | Darkness | Water | 154, 161, 178, 227, 268 |
| Minor | 2, 4, 6, 8 | Next/generated Energy in turn headers | Darkness | Water (same root misreading as above, listed once) | 62, 144, 214, 217, 268 |

G totals: major 2, minor 1.

### X
| Grade | Turn | Item | X says | Truth | Frames |
|---|---|---|---|---|---|
| Minor | 3 | Field Blower time | about 122-123 s | played about 118, effect done by 121 | 118, 121, 123 |

X totals: major 0, minor 1.

## Opponent sheets (12 fields: went_first, global_turns, final_score, end, Energy Zone, Pokemon names, attack names, Trainer names, special_conditions, healed, bench_damage, card of the game)

All three sheets carry identical values for all 12 fields, and each value matches the frames.

| Field | Value on all sheets | Frames | gemini | gemini_cheap | codex |
|---|---|---|---|---|---|
| went_first | opponent | 24 | right | right | right |
| global_turns | 8 | 281 | right | right | right |
| final_score | Dustin 2, opponent 0 | 233, 281 | right | right | right |
| end | opponent conceded | 272 | right | right | right |
| Energy Zone | Fighting | 23, 194, 246 | right | right | right |
| Pokemon names | Hitmonlee, Riolu, Lucario | 56, 123, 144 | right | right | right |
| Attack names | Stretch Kick, Submarine Blow | 138, 254 | right | right | right |
| Trainer names | Poke Ball, Professor's Research, Field Blower, Small Balloon, Korrina | 48, 118, 123, 204, 250 | right | right | right |
| special_conditions | none from the opponent | whole game | right | right | right |
| healed | false | whole game | right | right | right |
| bench_damage | true (Stretch Kick 30 to Benched Horsea) | 138 | right | right | right |
| card of the game | Lucario | 282 | right | right | right |

Sheet totals: gemini 12/12, gemini_cheap 12/12, codex 12/12. (Codex sheet leaves Hitmonlee `first_seen_turn` null; that is not one of the 12 fields.)

## Which record to rely on

For this game a player could rely on X (Codex) more. Both records get the whole story right: turn order, every card played, every attack and damage number (30, 30, 90, 90, 90), both Knock Outs, both points, the concession, the 2-0 score and the opponent's cards. They differ only in two ways. G invents a Darkness Energy that does not exist in this Water-only deck and says it was attached to Kingdra ex on turn 4, then repeats "1 Water + 1 Darkness" in every later board line, which would mislead anyone checking the Energy count or the deck. X has that right and its only slip is a Field Blower time 4-5 s late. G is otherwise a little richer (HP lines, Result-screen points, 210 damage), so its non-Energy details are usable, but its Energy facts should not be trusted without checking.
