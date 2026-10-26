# Check notes: recording g1sub

Independent check of out_review (REVIEW.md, OPPONENT.json, UNCERTAINTIES.md) against W\frames. Frame files: full = frames\full\t_SSSS.jpg, half = frames\half\t_SSSS.S.jpg, sheet = frames\sheets\sheet_from_NNNNs.jpg.

Checked and found right (no line here): every attack, its damage, HP before and after, all four Knock Outs, every point award and the final score 3-2; all Energy attachments (type and target) for both players; both evolutions plus Wallace's; the opening hand, first Active and Bench, both Energy Zones, and who went first; the end-of-turn boards; Soothing Shore heals (+20 on turns 6, 8 and 10); Confusion on turn 5 and its cure on turn 6.

## Corrections

turn | claim in the review | what the frames show | frame file(s) | class
---|---|---|---|---
6 | "t=170-172: Poke Ball played (Item): fetches Magikarp"; U3 guesses the Copycat draw was Poke Ball, Poke Ball, Mega Gyarados ex | Copycat's three draws are shown one at a time: Poke Ball (t=170.5-171.0), Mega Gyarados ex (t=171.5-172.0, next card back flipping in at t=172.0), Magikarp (t=172.5). Hand at t=173.5: Poke Ball, Mega Gyarados ex, Magikarp. Magikarp was drawn, not fetched | half t_0170.5, t_0171.0, t_0171.5, t_0172.0, t_0172.5, t_0173.5 | major (missed draw)
6 | "t=174-178: second Poke Ball played" (two Poke Balls; the first fetched Magikarp) | Only one Poke Ball is played (shown t=175.5), and it fetches nothing: "There are no cards in the deck that can be the target of the effect" (t=177.0-178.5); in the discard at t=179.5. Deck 9 before the Copycat shuffle (t=167) and 8 at t=198 = 9 + 2 - 3 with no fetch. The review's version would leave 7 | half t_0174.5, t_0175.5, t_0177.0, t_0178.5, t_0179.5; full t_0167, t_0198 | major (card played)
6 | Hand at end "Mega Gyarados ex (the only card seen)" | Exactly one card in hand: Mega Gyarados ex (3 drawn, minus Poke Ball and Magikarp) | half t_0179.5; full t_0191 | minor
Notes | Dustin's cards seen: "Poke Ball (two copies)" | One Poke Ball seen (follows from the line above) | half t_0175.5, t_0179.5 | minor
2, 6 (U8) | Mega Sharpedo ex "retreat cost none shown", not read as a number | Retreat cost 0: the "retreat" button shows no Energy cost (t=186.0); the retreat box is empty on both prints (t=59, t=300) | half t_0186.0; full t_0059, t_0300 | minor
7 (U2) | Item "X Speed", name read upside-down in the discard ("probable") | Full card face-up: "X Speed", Item, "During this turn, the Retreat Cost of your Active Pokemon is 1 less." | half t_0214.5 | minor
7 | Retreat of Mega Lopunny ex; cost not stated | Mega Lopunny ex's retreat cost is 1 Colorless; after X Speed the retreat is free, so Fighting x2 stays on it | full t_0090; half t_0224.5 | minor
8 (U6) | Mega Blaster text "read at low size" | Read at full card size: cost Water, Water, Water, Colorless; 140; "Discard the top 3 cards of your opponent's deck"; weakness Lightning +20; retreat 3. Same as the review | half t_0171.5 | minor
9 | Professor's Research played t=263-265 | X Speed is still the top discard at t=264; Professor's Research is shown at t=265.5 and is in the discard from t=267 | full t_0264, t_0267; half t_0265.5 | minor
10 (U4) | Full hand at the start of turn 10 not found | Soothing Shore is in the hand before the draw (t=298) and behind the drawn card (t=300) | full t_0298, t_0300 | minor
10 | "a second Mega Sharpedo ex" | A different print: regular art, illus. PLANETA CG Works, four diamond marks (the one in play is the full-art print, illus. Nurikabe, two stars) | full t_0059, t_0300 | minor
10 | Soothing Shore played t=303-305 | Arena of Antiquity is still in play at t=304; Soothing Shore is in play and Arena is in the opponent's discard at t=306. So t=304-306 | full t_0304, t_0306 | minor
10 | Turbo Shark attach t=314-317; heal banner at t=316; two bullets run together on one line | Attach at t=313-314 (Water x2 at t=312, x3 at t=318); "Soothing Shore" banner already at t=315. Bullets split | full t_0312, t_0315; sheet_from_0306s | minor
12 (U5) | Unclear whether Dustin chose not to attach Energy | t=339: dialog "End your turn? / Energy can be attached", and Dustin pressed OK; Turbo Shark banner at t=340. He chose not to attach | full t_0339; sheet_from_0324s | minor
12 | KO line: "the opponent has no Pokemon in play (no Bench)" | Mega Lopunny ex (90/190, Fighting x3) is still on the Bench at t=346; the review's own final board says so | full t_0346 | minor
Header, 12 | "t=352-354 loading, t=358 'Victory!' result screen" | The first "Victory!" screen (Mega Sharpedo ex, "Tap to Proceed") is at t=353; the statistics screen is at t=358 | sheet_from_0342s (t=353, t=358) | minor
Opening | Cabbie listed without its text | Cabbie: "Put a random Stadium card from your deck into your hand" | full t_0167 | minor
7 (OPPONENT.json) | X Speed entry "name read upside-down"; Mega Lopunny ex has no retreat cost | Same as the two turn 7 lines above; OPPONENT_FINAL.json updated | half t_0214.5; full t_0090 | (counted above)

## Uncertainties: status after the check

- U1 (deck list / QR): NOT settled. The QR is fully visible at t=0 (full t_0000), so it is settleable, but decoding needs the project's QR decoder, which is outside the folders this check may open. The "25" badge meaning stays unknown.
- U2 (Item on turn 7): settled. X Speed (half t_0214.5).
- U3 (hand after Copycat): settled. Poke Ball, Mega Gyarados ex, Magikarp (half t_0170.5-t_0173.5). This was a major correction.
- U4 (hand at the start of turn 10): settled. Soothing Shore (full t_0298, t_0300).
- U5 (no manual attach on turn 12): settled. His choice, confirmed through the "Energy can be attached" dialog (full t_0339).
- U6 (Mega Blaster text): settled. Same as the review (half t_0171.5).
- U7 (opponent hand counts): counts confirmed at t=29 (5), 44 (3), 50 (4), 88 (5), 94 (4), 129 (5), 141 (3), 167 (3), 226 (2), 260 (2), 265.5 (2), 267 (4), 280 (3), 328 (4). All fit one draw per opponent turn. The draws themselves are hidden information and cannot be settled from the frames.
- U8 (Mega Sharpedo ex retreat cost): settled. 0 (half t_0186.0; full t_0059, t_0300).
- U9 (opponent set numbers): not readable in any frame, so the frames cannot settle it.
- U10, U11: not video questions. Left as the review recorded them.

major | minor | unsettled-but-settleable | missed actions
---|---|---|---
2 | 15 | 1 | 1
