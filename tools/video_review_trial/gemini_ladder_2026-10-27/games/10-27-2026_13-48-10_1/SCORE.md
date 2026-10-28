# Score: ScreenRecording_10-27-2026 13-48-10_1 (G = Gemini, X = Codex)

Game: Dustin (Water, Koffing/Weezing ex/Horsea-Seadra-Kingdra ex) went first and lost 1-3 on points to a Type: Null / Silvally / Igglybuff deck. 10 global turns. Frames opened: 36 of 120 allowed (0, 1, 3, 24, 67, 74, 80, 98, 101, 104, 152, 185, 337, 339, 341, 349, 352, 354-360).

## Facts where both reviews agree and the frames I opened do not contradict
- Dustin went first; both Energy Zones are Water; opening hand (Poke Ball, Small Balloon, Professor's Research, Sabrina, Koffing), Copycat drawn on turn 1; Dustin 1 - opponent 3 on points, 10 turns, damage done 180, Defeat, Master Ball Rank 999 pts (frames 349, 356, 359).
- Turn-by-turn attacks, damage and HP: Quick Blow 40 (T2), Boiler Smog Poison+Burn (T3, "Type: Null is now Poisoned and Burned" at frame 152), Brave Buddies 100/50/100/100, Stormy Prison 90/90, Weezing ex KO (+2), Silvally KO (+1), Kingdra ex KO (+2). Soothing Shore heals. Both give the same numbers on every turn.
- At frame 337 the score is Dustin 1, opponent 2 (before the last KO), Silvally 110 HP with two Water, Kingdra ex 90 HP, Horsea (right bench) holds a Water, Gladion is on top of the opponent's discard.

## Disagreement table

| Turn | Item | G says | X says | Frames | Verdict |
|---|---|---|---|---|---|
| 1 (Dustin) | When Hiking Trail was played, and its order against the second Horsea | Second Horsea benched left at 72-75, then Hiking Trail played at 79-82 | Hiking Trail played about 67-69, then second Horsea benched 72-75 | 67: Hiking Trail card is shown large as a Copycat draw reveal (one Horsea benched, hand not yet used). 74: shiny Horsea being benched, Hiking Trail, Weezing ex and Shore still in hand. 80: Hiking Trail glowing into the Stadium spot with both Horsea already on the Bench | G right |
| 2 (opponent) | When Field Blower was played and the Small Balloon discarded; order against the second Type: Null bench | Field Blower 97-98, Balloon discarded 100-101, then bench Type: Null 103-104 | Bench about 102-104, Field Blower about 102-105 | 98: Balloon still on Koffing, effect animation running. 101: Balloon already in Dustin's discard (top of right pile), opponent Bench still empty. 104: Type: Null now on the Bench and Field Blower on top of the opponent's discard | G right |
| 10 (opponent) | Water Energy attachment to benched Igglybuff | Not mentioned; final board lists Igglybuff with 0 Energy; sheet attachment list stops at turn 8 | Attaches Water to benched Igglybuff about 338-340 | 337: Igglybuff has no Energy icon, Energy Zone orb is lit (ready). 339: Igglybuff now shows a Water Energy icon, orb empty. 341: Brave Buddies attack on Kingdra ex | X right |

Not graded (not a game fact, 1-second frames cannot fully settle it): the order of the result screens. G puts Kingdra ex as Dustin's Card of the Game at 356 and Silvally as the opponent's at 357; X says Silvally first, then Kingdra ex and the statistics. The frames show Kingdra ex plus the statistics at 356 (Went first, 10 turns, points 1 and 3, damage 180) and Silvally ("Your opponent's cards") at 357, which fits G. Both name the same two cards of the game.

## Claims only one review makes
- G: "Deck 15" (deck slot). Frame 1 shows the deck name "New deck 13" and the 20/20 list; no slot number is visible in the frames I opened. Not contradicted, not confirmed, not graded.
- G: Master Ball Rank 999 pts: confirmed (frame 359).
- X: QR decode, numeric IDs, SHA/source notes, "Ladder routing" remarks: not checked against frames, not part of the game record, not graded. The opening QR and the deck view that follows (frames 0, 1) are as both describe.
- Nothing either review states only on its own was found contradicted by the frames, except the items in the table above.

## Errors by review

G (Gemini): 1 major, 0 minor
- Major, turn 10: omits the Water Energy attached to benched Igglybuff (absent at 337, present at 339). Its final board state repeats the error (Igglybuff 0 Energy). Frames 337, 339.

X (Codex): 0 major, 2 minor
- Minor, turn 1: Hiking Trail given as about 67-69 and before the second Horsea; truth is about 79-82, after the Horsea bench. The play itself is right. Frames 67, 74, 80.
- Minor, turn 2: Field Blower given as about 102-105 and alongside the Type: Null bench; truth is played about 97-98 with the Balloon gone by 101, before the bench. The play and its effect are right. Frames 98, 101, 104.

## Opponent sheets (12 fields: went_first, global_turns, final_score, end, energy zone, Pokemon names, attack names, Trainer names, special_conditions, healed, bench_damage, card of the game)

| Field | Truth (frames / agreed) | gemini | gemini_cheap | codex |
|---|---|---|---|---|
| went_first | dustin (356) | right | right | right |
| global_turns | 10 (356) | right | right | right |
| final_score | 1-3 (356) | right | right | right |
| end | points | right | right | right |
| energy zone | Water (opp orb at 98, 101, 337) | right | right | right |
| Pokemon names | Type: Null, Igglybuff, Silvally (Igglybuff readable at 185, 337, 339) | right | WRONG: lists Chingling, no Igglybuff | right |
| attack names | Quick Blow, Brave Buddies (cards at 98, 185) | right | right | right |
| Trainer names | Poke Ball, Field Blower, Silver, Gladion, Professor's Research (Gladion seen at 337, Silver at 152; both reviews and sheets list the same six plays) | right | right | right |
| special_conditions | none from opponent cards/attacks (the only Poison/Burn is Dustin's own, frame 152) | right | right | right |
| healed | true (Soothing Shore) | right | right | right |
| bench_damage | false | right | right | right |
| card of the game | Silvally (357) | right | right | right |
| **Total right of 12** | | **12** | **11** | **12** |

Outside the 12 fields (not counted): both Gemini sheets omit the turn-10 Water to Igglybuff in `opponent_energy_attached` (same omission as G's review); the codex sheet has it. The cheap sheet gives Silvally 4 points taken and one entry only, which is a way of recording two Silvally Knock Outs; not counted.

## Which record to rely on

For this game, Review X (Codex) is the record to rely on. Its turn-by-turn events, attacks, damage, HP, Knock Outs, points, score and ending all match the frames and it catches the turn-10 Energy attachment to Igglybuff that G misses; its only slips are two timestamps and orderings in the opening turns (Hiking Trail on turn 1, Field Blower on turn 2), where the events themselves are right. Review G (Gemini) gets those two orderings and the result-screen order right and agrees with X on every attack, damage number, Knock Out and point, but drops one Energy attachment and carries it into its final board state and sheet. A player studying sequencing within a turn could use G's order of plays; a player counting Energy on the board at the end should use X. Both reviews are strong on this game; neither contains a wrong card, attack, damage number, Knock Out, point or score. The cheap Gemini sheet is the only wrong-name error found (Chingling for Igglybuff).
