# Exam v2, part 3: labels

48 points labelled out of the 48 in positions.json. All of them are written to labels.json, and none were left unlabelled. The key is his recorded move on every point. Section 3 (segments, scope, validation) is left to the assembly.

## Counts by answer kind
- prepare: 32
- attack now: 14
- sacrifice: 2
- abandon: 0

## Counts by deck (points: prepare / attack now / sacrifice)
- v2deck_4fa967805c: 9 (5 / 4 / 0)
- v2deck_693850eaa5: 5 (2 / 2 / 1)
- v2deck_f5671a4e7f: 2 (2 / 0 / 0)
- v2deck_4af97d2795: 5 (4 / 1 / 0)
- v2deck_ba2eca5816: 9 (7 / 2 / 0)
- v2deck_6328cc45fe: 8 (5 / 2 / 1)
- v2deck_589bb9927a: 10 (7 / 3 / 0)

## Accepted alternatives (5 points)
- LAD-20261021_225620000_SR-t3: the mirror order (hand Mega Sharpedo ex on the benched Carvanha, Wallace on the Active one).
- LAD-20261022_000850000_SR-t8: Wallace on the other Carvanha (idx 3), with the hand Mega Sharpedo ex on idx 1.
- LAD-20261022_004518000_SR-t8: the Water goes to the benched Mega Sharpedo ex instead of the already-charged Wailmer, with the same Wave Splash KO.
- LAD-20261022_235420000_SR-t4: Rare Candy Flygon ex goes on the other, identical, Trapinch.
- LAD-20261023_005124000_SR-t8: the zone Grass also goes on Buzzwole ex after Lusamine.

## Question for Dustin (1 of the 6 allowed)
- LAD-20261023_010556000_SR-t8: "On turn 8 vs Hitmonlee you put the Water on the damaged Oricorio so Soothing Shore heals it. Would Water on the damaged benched Wartortle (Mega Blastoise line, also healed by Shore) be just as good?" Until he answers, the Wartortle line is pending and doesn't count.

## Deck kinds (the 5 decks in DECK_KINDS_FOR.txt)
- v2deck_4af97d2795: evolution and setup, Bench preparation, control and combinations
- v2deck_693850eaa5: evolution and setup, Bench preparation, control and combinations
- v2deck_f5671a4e7f: evolution and setup, Bench preparation, control and combinations
- v2deck_ba2eca5816: evolution and setup, Bench preparation, control and combinations
- v2deck_6328cc45fe: control and combinations, Bench preparation, sacrifice and recovery

## Notes
- I could check each alternative's first action against legal.jsonl, but not its later steps, because I had no legal-moves tool. Later steps follow the labels in the legal lists and his recorded moves. The assembly's validation should still replay them.
- Some lines are just his own actions in a different order, with no change to the outcome. I didn't list those, since a line is a set of actions.
- On many points the first segment stops at a chance action (Poké Ball, Research, Copycat, Wallace, Fragrant Forest). There, alternatives that differ only after that action would not change matching, so I didn't list any.
