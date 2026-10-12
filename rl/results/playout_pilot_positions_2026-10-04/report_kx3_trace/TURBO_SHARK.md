# Turbo Shark turns: km3's scores, step by step along his line

Each row replays his own line from the position and, at every step, asks km3 (on a fresh game from the same state, 12 seeds) what it would play and how its search scores his action against its own best at that step. Scores are the search's root values (the same print as the Step 8c dump), averaged over 12 seeds; a gap of 0 means his action was km3's top-scoring candidate. The last step of each block is the Bench Energy target of Turbo Shark: every legal target and its root score.

## A-132311-t03: game 132311, his turn 2 (game turn 3)

His line: Evolve:Mega Sharpedo ex@0 → Attach:1Water@0 zone → Attack:Turbo Shark → Attach:1Water@1 fx. Draw Irida. Opp Furfrou's Fur Coat takes 20 off attacks. The Bench holds only one Water Pokémon, so Turbo Shark has no real target choice here.

| step | his action | km3 picks (12 seeds) | km3 score for his action | km3 best at this step | gap |
|---|---|---|---|---|---|
| 0 | Evolve:Mega Sharpedo ex@0 | Evolve:Mega Sharpedo ex@0 ×3 | (only legal action) | | |
| 1 | Attach:1Water@0 zone | Attach:1Water@0 zone ×3 | (only legal action) | | |
| 2 | Attack:Turbo Shark | Attack:Turbo Shark ×3 | (only legal action) | | |

There is no Bench target choice here (only one Water Pokémon on the Bench, so the engine places the Energy without asking).

## A-115323-t05b: game 115323, his turn 3 (game turn 5) (mid-turn position)

His line: Place:Alolan Vulpix@3 → Evolve:Mega Sharpedo ex@1 → Retreat:1 → Attach:1Water@0 zone → Attack:Turbo Shark → Attach:1Water@3 fx. MID-TURN position: turn 5 after the second Carvanha was benched and Copycat drew Sharpedo, Vulpix, Cyrus. Turbo Shark's Bench target: Lapras (0 Energy after the retreat), the second Carvanha, or Vulpix (his pick).

| step | his action | km3 picks (12 seeds) | km3 score for his action | km3 best at this step | gap |
|---|---|---|---|---|---|
| 0 | Place:Alolan Vulpix@3 | Evolve:Mega Sharpedo ex@1 ×2, EndTurn ×1 | (only legal action) | | |
| 1 | Evolve:Mega Sharpedo ex@1 | Evolve:Mega Sharpedo ex@1 ×2, EndTurn ×1 | (only legal action) | | |
| 2 | Retreat:1 | Retreat:1 ×3 | (only legal action) | | |
| 3 | Attach:1Water@0 zone | Attach:1Water@0 zone ×3 | (only legal action) | | |
| 4 | Attack:Turbo Shark | Attack:Turbo Shark ×3 | (only legal action) | | |

Bench target after Turbo Shark (step 5); km3 picks: Attach:1Water@3 fx ×3. His pick: ['Attach:1Water@3 fx']

| target (slot) | km3 root score (mean of 12 seeds) | min | max |
|---|---|---|---|

## A-115323-t07: game 115323, his turn 4 (game turn 7)

His line: Attach:1Water@1 zone → Attack:Turbo Shark → Attach:1Water@1 fx. Draw Irida (shuffled away by Copycat on T5, drawn again). Opp Penny'd the damaged Snorlax back to hand on T6. Turbo Shark's Bench target: Lapras (his pick), Carvanha or Vulpix.

| step | his action | km3 picks (12 seeds) | km3 score for his action | km3 best at this step | gap |
|---|---|---|---|---|---|
| 0 | Attach:1Water@1 zone | Attach:1Water@1 zone ×3 | (only legal action) | | |
| 1 | Attack:Turbo Shark | Play:Irida ×3 | (only legal action) | | |

Bench target after Turbo Shark (step 2); km3 picks: Attach:1Water@2 fx ×3. His pick: ['Attach:1Water@1 fx']

| target (slot) | km3 root score (mean of 12 seeds) | min | max |
|---|---|---|---|

## A-115323-t11: game 115323, his turn 6 (game turn 11)

His line: Place:Alolan Vulpix@3 → Attach:1Water@3 zone → Attack:Turbo Shark → Attach:1Water@3 fx. Head Smash (130 + Arena's 20 only against ex) KO'd the 80-HP Lapras; the Mega Sharpedo ex was promoted at 220 HP. Draw Vulpix: bench it, give it the turn's Water, Turbo Shark (70) hits Rampardos 100 -> 30 and sends the second Water to the new Vulpix.

| step | his action | km3 picks (12 seeds) | km3 score for his action | km3 best at this step | gap |
|---|---|---|---|---|---|
| 0 | Place:Alolan Vulpix@3 | Place:Alolan Vulpix@3 ×3 | (only legal action) | | |
| 1 | Attach:1Water@3 zone | Attach:1Water@3 zone ×3 | (only legal action) | | |
| 2 | Attack:Turbo Shark | Attack:Turbo Shark ×3 | (only legal action) | | |

Bench target after Turbo Shark (step 3); km3 picks: Attach:1Water@1 fx ×3. His pick: ['Attach:1Water@3 fx']

| target (slot) | km3 root score (mean of 12 seeds) | min | max |
|---|---|---|---|

## A-132311-t07b: game 132311, his turn 4 (game turn 7) (mid-turn position)

His line: Place:Alolan Vulpix@2 → Attach:1Water@2 zone → Retreat:1 → Attack:Turbo Shark → Attach:1Water@2 fx. MID-TURN position: turn 7 after Research and Poké Ball. Turbo Shark's Bench target: the damaged Mega (2 Water) or the new Vulpix (1 Water, his pick).

| step | his action | km3 picks (12 seeds) | km3 score for his action | km3 best at this step | gap |
|---|---|---|---|---|---|
| 0 | Place:Alolan Vulpix@2 | Retreat:1 ×3 | (only legal action) | | |
| 1 | Attach:1Water@2 zone | Retreat:1 ×3 | (only legal action) | | |
| 2 | Retreat:1 | Retreat:1 ×3 | (only legal action) | | |
| 3 | Attack:Turbo Shark | Place:Alolan Vulpix@3 ×3 | (only legal action) | | |

Bench target after Turbo Shark (step 4); km3 picks: Attach:1Water@2 fx ×3. His pick: ['Attach:1Water@2 fx']

| target (slot) | km3 root score (mean of 12 seeds) | min | max |
|---|---|---|---|
