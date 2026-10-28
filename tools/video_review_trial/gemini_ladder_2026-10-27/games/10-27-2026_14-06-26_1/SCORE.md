# Score: ScreenRecording_10-27-2026 14-06-26_1 (G = Gemini, X = Codex)

Frames opened: about 66 of the 120 allowed (t = 0, 2, 3, 20-23, 25, 26, 30, 35, 40, 45, 49, 52, 54, 58, 61, 63, 64, 66, 69, 72, 74, 76-80, 82, 85, 95, 98, 101, 110, 119, 124, 128, 132, 134, 136, 139, 141, 143, 146, 148, 150, 153, 155, 157, 160, 168-172).

## Summary of the game as the frames show it

Dustin (Darkness Energy Zone) won the flip and went first; the opponent (Lightning Energy Zone) opened Magnemite. 3 global turns. Turn 1: Poncho on the benched Deino, Professor's Research (draws Cyrus + Professor's Research). Turn 2 (opponent): Professor's Research, Poke Ball, second Magnemite to the Bench, Lightning to the Active Magnemite, Electro Ball for 30 (Deino 60 to 30). Turn 3: Deceptive Needle on the Active Deino, Professor's Research (draws Poke Ball + Poncho), Poke Ball (Hoopa ex) and Hoopa ex benched, Rare Candy to Hydreigon (120/150), 1 Darkness attached, Roar in Unison (2 more Darkness, 30 to itself: 90/150), Hyper Ray 130 KO on Magnemite (t=150), 1 point (t=153), opponent concedes (t=155). Final 1-0, damage done 130, +1 pt and 4 win-streak pts, 1,001 pts.

## Disagreement table

The two reviews agree on every game event: first player, opening hand, Energy Zones, every card played, every attachment, evolution and Ability, both attacks and their damage, HP before and after, Knock Out, points, score, end and the Pokemon seen. All timestamp differences are 3 s or less (for example Lightning attach G t=78 vs X t=76-77, point G t=153 vs X t=152-154, Ability G t=139 vs X t=138-141), so none counts. The only disagreement is below.

| Turn | Item | G says | X says | Frames | Verdict |
|---|---|---|---|---|---|
| Result screens | Opponent's Card of the Game display | Result screen at t=170 shows "Opponent's Card of the Game: Magnemite" | Independent check: frame at 170 "actually displays owner Hydreigon", so the opponent display claim was removed; REVIEW.md: Magnemite is "not a separately verified result display" | t_0168 and t_0169 show the owner's Card of the Game (Hydreigon). t_0170 and t_0171 show the page "Your opponent's cards" with "Card of the Game" = Magnemite (Electro Ball 30, 50 HP). | G right |

## Claims only one review makes (checked against frames)

G only, all confirmed or not contradicted:
- Deck preview at t=2: Hoopa ex, Mega Sableye ex, 2 Deino, 2 Hydreigon, 2 Poke Ball, Rare Candy, 20/20 (t_0002). True.
- Master Ball Rank 1,000 pts at start (t_0003). True.
- Coin flip heads at t=23 (t_0021 shows the logo side, t_0022 and t_0023 the Absol face, "Going first"). Not contradicted; not scored.
- Board states and hands after each action (hand before the turn 1 draw: Professor's Research, Hydreigon, Poncho; hand at turn 3 start: Hydreigon, Rare Candy, Cyrus, Professor's Research; end board Hydreigon 90/150 with Needle, Hoopa ex 150, Deino 60 with Poncho; opponent bench Magnemite 50). All true (t_0040, t_0084/0085, t_0124, t_0157).
- Rank result: +1 pt and 4 win-streak pts, "2 win streak" (t_0172). True.
- Result stats (went first, 3 turns, 1-0, damage 130) (t_0168). True.

X only, none contradicted except the one error listed:
- Poncho/Needle/Rare Candy/Hoopa details, "Hydreigon 150 max HP", "Cyrus and second Poncho remain in hand", "Mega Sableye ex is deck evidence only, not played", "do not invent an extra 10 damage from Deceptive Needle" (Needle text: 10 damage at the end of the turn; the opponent conceded before the turn ended, t_0095, t_0157). All true.
- VERIFICATION.json correction "frame at 170 displays owner Hydreigon" and REVIEW.md "opponent card-of-the-game ... not a separately verified result display": false (see table).

## Errors by review

G: 0 major, 0 minor.

X: 0 major, 1 minor.
- Minor (X): missed the opponent's Card of the Game result screen (t=170-171, Magnemite) and its independent check wrongly "corrected" G, saying the frame at 170 shows the owner's Hydreigon. The field value (Magnemite) in X's own sheet is right; only the support is wrong. No game event is affected.

## Opponent sheets (12 fields each)

Fields: went_first, global_turns, final_score, end, Energy Zone type, Pokemon names, attack names, Trainer names, special_conditions, healed, bench_damage, card of the game.

| Field | Truth (frames) | gemini | gemini_cheap | codex |
|---|---|---|---|---|
| went_first | dustin (t_0026) | right | right | right |
| global_turns | 3 (t_0168) | right | right | right |
| final_score | 1-0 (t_0153, t_0168) | right | right | right |
| end | concede_opponent (t_0155) | right | right | right |
| Energy Zone type(s) | Lightning (t_0025, t_0058) | right | right | right |
| Pokemon names | {Magnemite} | right | right | right |
| attack names | Electro Ball (t_0080) | right | right | right |
| Trainer names | Professor's Research (t_0063/0069), Poke Ball (t_0069) | right | right | right |
| special_conditions | none | right | right | right |
| healed | false | right | right | right |
| bench_damage | false | right | right | right |
| card of the game | Magnemite (t_0170) | right | right | right |
| Total | | 12/12 | 12/12 | 12/12 |

Note (not one of the 12 fields): codex/OPPONENT.json lists one Magnemite entry with first_seen_turn null, while the two Gemini sheets list two entries (turn 1 and turn 2) as in the frames; the set of names is the same.

## Which record to rely on

For this game both records are reliable, and a player could use either one for the plays, the Ability, both attacks, the KO, the points and the concession; they match on every event and number, and their timestamps stay within 3 s of each other. G is slightly better: it has zero errors, gives the full hand-by-hand and board-by-board state (opening hand, hands at each turn start, HP lines), the deck screen, the rank result and the correct opponent Card of the Game result screen. X is just as correct about the game itself and is more careful about things the video cannot show (it states the Needle's end-of-turn damage did not happen), but it contains one minor error: it missed the opponent's Card of the Game screen and wrongly told G it was not there. A player who wants the exact hands and HP at each step should use G; for the record of what happened they are equal.
