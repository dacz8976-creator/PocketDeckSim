# Exam v2, part 1 labels

I labelled all 54 points in positions.json using section 2 of ADJUDICATION_RULES.md. The data is in `labels.json`. None of these games was split into clips, so each game has one review and one global turn count.

## Counts by answer kind

| Answer kind | Points |
|---|---|
| prepare | 29 |
| attack now | 22 |
| sacrifice | 3 |
| abandon | 0 |
| **total** | **54** |

## Counts by deck

| Deck | Points | prepare | attack now | sacrifice |
|---|---|---|---|---|
| v2deck_06ee642b71 (Hoopa / Darkrai / Mega Sableye / Weezing) | 21 | 11 | 8 | 2 |
| v2deck_d5e2757125 (Muk it up: Glimmora / Muk ex / Weezing) | 7 | 3 | 4 | 0 |
| v2deck_5469f7747f (Muk ex / Dustox with Rare Candy) | 6 | 5 | 0 | 1 |
| v2deck_9633a01781 (Dragonite / Hisuian Goodra) | 6 | 4 | 2 | 0 |
| v2deck_9d2c3c7ccf (Hoopa / Glimmora / Claydol x2) | 4 | 1 | 3 | 0 |
| v2deck_5c3566c961 (Glimmora / Kingambit / Muk) | 3 | 2 | 1 | 0 |
| v2deck_b1999cc10f (Hoopa / Darkrai / Mega Sableye, Center Lady) | 3 | 2 | 1 | 0 |
| v2deck_03c584b95c (Hoopa x2 / Glimmora / Nihilego) | 2 | 0 | 2 | 0 |
| v2deck_0a80817331 (Muk ex / Dustox with Cascoon) | 2 | 1 | 1 | 0 |

All 9 decks in DECK_KINDS_FOR.txt have deck_kinds, each with a one-line reason.

## Acceptable alternatives (count now)

Five points have accepted alternatives (six lines in all). The other 49 have none.

- LAD-20261017_150509000_SR-t4: the same turn, but also bench the second Baltoy so the second Claydol has somewhere to go.
- LAD-20261017_150509000_SR-t8: the same retreat into Claydol, plus benching Baltoy.
- LAD-20261019_224222000_SR-t13: the attack wins wherever the Energy goes, so two lines are listed: attach to the Active Pokémon, or don't attach at all.
- LAD-20261020_033156000_SR-t2: play Needle first, then Copycat instead of Research (the opponent has 5 cards, so Copycat draws 5 instead of 2).
- LAD-20261020_034501000_SR-t3: evolve the lone Grimer into Alolan Muk ex (160 HP) before attaching. He attached and ended without evolving.

## Questions for Dustin (3 of the 6 allowed)

Each of these alternatives is held as pending and doesn't count until he answers.

1. **LAD-20261019_221218000_SR-t5**: At 221218 global turn 5, Mega Sableye ex was Active with 1 Energy. Would attaching a second Energy and attacking with Cursed Jewel (80) have been as good as retreating into Hoopa ex for Shadow Bullet, or did you want the 3-point Mega off the Active Spot?
2. **LAD-20261019_224222000_SR-t5**: At 224222 global turn 5, was Cyrus (pulling the 80-HP Darkrai, with 1 of the 3 Energy it needs, into the Active Spot) better than leaving the 20-HP Espeon Active, where your next Nightmare Aura would knock it out? Your sleeping Hoopa ex was lost either way.
3. **LAD-20261020_034756000_SR-t6**: At 034756 global turn 6, Dustox (60 HP, 1 Energy) faced a Poisoned and Confused Butterfree at 120. Would attaching to Dustox and attacking with Cutting Wind for 60 have been as good as putting the Energy on the benched Grimer for Muk ex?

## Notes and anything I couldn't label

- Every point is labelled; nothing was skipped.
- For each line, I checked that the first action is in that point's legal list in legal.jsonl. I did not run any tool, so the step-by-step legality check is left to the assembly.
- Lines that start with a chance action (Professor's Research, Poké Ball, Copycat, the Fragrant Forest Stadium, Variety Powder) include the actions after it as he recorded them. The first-segment cut is section 3 and is done later by the assembly.
- At 221218 t5, the pending Cursed Jewel line leaves out Field Blower. That card only came from Copycat's hidden draw.
- I kept close calls out of the key where I judged his move clearly fit his plan better. One example is 151306 t6, where he put the Energy on Pawniard for Kingambit instead of using a 20-damage Hang Down.
- I used "sacrifice" where the Active Pokémon couldn't be saved and the turn's resources went to the next attacker instead: 224222 t5, 000238 t3 and 034756 t6.
