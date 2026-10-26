# Comparing Review C and Review X for ch_h2 (Dustin / Dacz8976 vs Zavs65)

Review C is `out_check/REVIEW_FINAL.md` plus `OPPONENT_FINAL.json`. Review X is `codex/REVIEW.md` v2, as amended by FINDINGS.json, COVERAGE.md and LEAD_ACCEPTANCE.json; X's v2 correction to the turn-9 order is already in REVIEW.md.

## What both reviews agree on (checked where it matters)
- The opponent went first and Dustin went second.
- Dustin's opening hand was Magikarp, Cabbie, Copycat, Poké Ball and Mega Gyarados ex.
- Energy Zones: Dustin's is Water and the opponent's is Lightning.
- The opponent scored both points with Furfrou's Double Headbutt (1 head each, 30 damage): Magikarp was Knocked Out in turn 3 and Feebas in turn 5.
- Turbo Shark did 50 to Furfrou after Fur Coat (turn 6) and 70 to Luxray (turn 14). Each time its effect attached a Water to the Benched Pokémon.
- Zzzap hit for 70 in turns 7, 9 and 11, and Volt Bolt hit for 140 in turn 13.
- Every heal agrees: Soothing Shore, Irida and Sylveon.
- Furfrou retreated in turn 7 and Oricorio in turn 13.
- Dustin conceded during turn 15. The score was 0–2, with 15 turns and 120 damage.
- Opponent Pokémon seen in both: Furfrou, Eevee to Sylveon, Oricorio, and Shinx to Luxray (via Rare Candy).

## Disagreements

| Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|
| 2 | Expert Splasher printed damage | "0+" | 10, +20 if both heads | The card reads "Expert Splasher 10+". Actual damage was 0 in both reviews. | t_0052, t_0060 | **X right** |
| 5 | Opponent's Energy | Lightning went on Oricorio | Lightning left unspent | Zone full and Oricorio bare at 190 s. Zone empty and Oricorio with 1 Lightning at 200 s. | t_0190, t_0200 | **C right** |
| 9 | When Zzzap hit (220→150) | 363–365 s | 369–371 s | Still 220 at 362/365 s (Shinx's Lightning landing at 365). Zzzap card at 369 s and 150 at 371 s. | t_0362, t_0365, t_0369, t_0371 | **X right** |
| 13 | Where the Lightning went | Luxray | Shinx, making 3, before Rare Candy | Shinx has 2 at 453–455 s. Luxray has 2 at 458.5 s and 3 at 459 s, when the Zone empties. | t_0453–t_0459, half t_0458.5 | **C right** |
| 13 | When the Lightning went on | After Oricorio retreated (~463 s) | Before Rare Candy (451–453 s) | After Rare Candy (454 s) and before the retreat. Luxray is still Benched and Oricorio still Active with 2 at 459 s. | t_0454, half t_0458.5, t_0459 | **both wrong** |
| 14 | Dustin's Zone after Turbo Shark | Water still in the Zone at 485 s | Zone emptied at 485 s | The big Water is still in the Zone at 483 and 485 s. The Bench Sharpedo has 4 Water. | t_0483, t_0485 | **C right** |

## Facts only C records (confirmed by the frames)
- Turn 15: at the concede menu (t_0498), Luxray has exactly 2 Lightning from Volkner, Volkner is in the discard, and the Zone Lightning is unattached. So no Volt Bolt was possible yet.

## Facts only X records (confirmed by the frames)
- Turn 1: Professor's Research was played and is in the opponent's discard at 60 s (t_0060).
- Turn 4: the first Carvanha is the Sharp Fang version (t_0190).
- Player names: Dacz8976 (owner) and Zavs65 (opponent) (e.g. t_0052).

## Which review to rely on
Both reviews get the parts that decide the game right: turn order, opening hand, every attack and its damage, both Knock Outs, the heals, the concede, and the 0–2 result. Review C is the better guide to board state:
- It correctly tracks the opponent's Energy in turn 5 and turn 13.
- It correctly says Dustin's turn-14 Energy stayed in the Zone.

X's turn-5 and turn-13 errors make its opponent Energy history wrong, and it gives a false "emptied Zone" detail in turn 14.

X does have the sharper text and timing details. It reads Expert Splasher correctly, gets the turn-9 Zzzap timing right, and records Professor's Research, which C missed. But those don't change any game state.

For working out what happened and why, a player can rely on C more. Its main faults are a misread "0+" and some timestamps that are off by a few seconds.
