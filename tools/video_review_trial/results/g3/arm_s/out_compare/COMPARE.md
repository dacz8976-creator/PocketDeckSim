# Review C vs Review X: Dustin (Dacz8976) vs Zavs65, ranked

Review C is `out_check/REVIEW_FINAL.md` and `OPPONENT_FINAL.json`. Review X is `codex/REVIEW.md` read together with FINDINGS, COVERAGE, UNCERTAINTIES and LEAD_ACCEPTANCE. The only correction X records is the order in turn 9, and C agrees with it.

## Where both reviews agree (the frames were not opened for these unless noted)
- The opponent went first.
- Dustin's opening hand was Magikarp, Cabbie, Copycat, Poké Ball and Mega Gyarados ex.
- Energy Zones: Dustin Water, opponent Lightning.
- All attacks, damage and HP changes match:
  - Expert Splasher did 0 (Fur Coat).
  - Double Headbutt did 30 twice and Knocked Out Magikarp, then Feebas.
  - Turbo Shark did 50 to Furfrou (70→20) and later 70 to Luxray (130→60). Both times its Water went to the Bench.
  - Zzzap did 70 (with Weakness) three times.
  - Volt Bolt did 140, taking a Mega Sharpedo ex from 220 to 80.
- Healing matches: every Soothing Shore and Soothing Ribbon heal, and Irida's +40.
- Evolutions match: Mega Sharpedo ex twice (once through Wallace), Sylveon ex, and Luxray through Rare Candy.
- Retreats match. Neither review records a Special Condition.
- Final score 0–2. Dustin conceded during global turn 15 (about t=498-499).

## Disagreements

| Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|
| 1 (opp) | Poké Balls played | Two (t≈37, t≈42) | One (37-40) | t=42: a second Poké Ball is shown while the first is already in the discard pile | t_0037, t_0042 | **C right** |
| 5 (opp) | Energy attachment | Lightning to Benched Oricorio | Lightning left unspent | t=192: Oricorio has no Energy and the Zone is full. t=196: Oricorio has 1 Lightning and the Zone is empty | t_0192, t_0196, t_0200 | **C right** |
| 7 (opp) | Card played at t≈302-308 | Face-down, not identified | Copycat | t=303: a Supporter, faintly "Copycat". t=309: Copycat is on top of the discard pile | t_0303, t_0308, t_0309 | **X right** |
| 7 (opp) | When Shinx is benched | By t≈308 | 313-314 | The Bench slot is empty at t=308-312. Shinx appears at t=314 | t_0308, t_0312, t_0314 | **X right** |
| 12 (Dustin) | Card drawn | Not identified | Irida | t=411: the hand has no Irida. t=414: Irida is drawn | t_0411, t_0414 | **X right** |
| 13 (opp) | Lightning target | Luxray | Shinx (before Rare Candy) | Shinx still has 2 Lightning after Rare Candy (t=458). The Benched Luxray has 3 at t=459 | t_0455, t_0457-t_0459 | **C right** |
| 13 (opp) | Order of the attachment | After Oricorio retreats (to the Active Luxray) | Before Rare Candy | Rare Candy → attach to the Benched Luxray → Oricorio retreats | t_0455, t_0458, t_0459, t_0462 | **both wrong** |
| End | Result-screen statistics | "Not shown" | Went second, 15 turns, 0-2, 120 damage | t=507 shows exactly X's numbers | t_0507 | **X right** |
| Header | Deck name | Not readable | New deck 17 | t=1: "New deck 17", Feebas cover | t_0001 | **X right** |

## Facts only C records (confirmed by the frames)
- The opponent had no Bench at setup (t=37).
- Dustin's hand at the start of each of his turns (for example, at t=411 the hand is Wallace, Mega Gyarados ex, Soothing Shore, Milotic ex).

## Facts only X records (confirmed by the frames)
- Turn 1: the opponent played Professor's Research (t≈50-55, seen in the discard pile).
- The ranked screen reads "Season B4b SP" (t=1).
- Dustin's two Carvanha are different printings: Sharp Fang and Aqua Jet (t=196 and t=306).
- The result screens name Card of the Game: Mega Sharpedo ex for Dustin, Oricorio for the opponent (t=507-508).
- Eevee's attack is Find a Friend (t=52).

## Which review to rely on
On the actual game (damage, HP, Knock Outs, points, healing, Mega evolutions) the two reviews match, and both are reliable.

X gets more of the disputed facts right (5 to C's 3). It identifies:
- the opponent's turn-7 Copycat and turn-1 Professor's Research;
- the turn-12 draw;
- the result-screen statistics;
- the deck name.

C wrongly says the result screen and the deck name are unreadable.

C is better at tracking the opponent's Energy, which matters for working out what the opponent can do next:
- X says the turn-5 Lightning was left unspent. This contradicts the frames and X's own later Energy counts.
- X puts the turn-13 Energy on Shinx. It went on Luxray.

Neither review gets the order of turn 13 right.

Overall: use X for what was played and for the result screen, and C for where the Energy went. C has the edge on game-state tracking, because the Energy count decides what the opponent can attack with.
