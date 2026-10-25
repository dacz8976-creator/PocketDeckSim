# Exam v2, part 5: labels

There are 51 points, all labelled. Each `his_move` is copied exactly. Every point's `acceptable` list is empty; the five alternatives I wasn't sure of are under `pending_alternatives`, waiting for Dustin's answer. Every pending line starts with an action in that point's `legal.jsonl` list.

## Counts by answer kind
| deck | prepare | sacrifice | attack now | abandon | total |
|---|---|---|---|---|---|
| v2deck_2c68a379f5 (Haxorus, Fighting/Metal) | 10 | 1 | 3 | 0 | 14 |
| v2deck_7907f1e146 (Mega Sharpedo/Gyarados, Water) | 13 | 2 | 14 | 0 | 29 |
| v2deck_a75894a903 (Dedenne ex Tools, Lightning) | 5 | 0 | 1 | 0 | 6 |
| v2deck_bac3c8a158 (Darkrai/Hoopa, Darkness) | 2 | 0 | 0 | 0 | 2 |
| **all** | **30** | **3** | **18** | **0** | **51** |

## Deck kinds
- v2deck_2c68a379f5: evolution and setup, Bench preparation, sacrifice and recovery, control and combinations
- v2deck_7907f1e146: fast pressure, evolution and setup, Bench preparation
- v2deck_a75894a903: Bench preparation, control and combinations, sacrifice and recovery
- v2deck_bac3c8a158: control and combinations, Bench preparation

## Questions for Dustin (5 of the 6 allowed)
1. **LAD-20261024_143157000_SR-t4**: You retreated the 30-HP Axew to Goomy (discarding its Fighting), attached Fighting to the benched Axew and Rare Candied it to Haxorus. Would keeping Axew Active, attaching the Fighting to it and Rare Candying it into Haxorus in the Active Spot (Haxorus at 110 HP with 2 Energy) also be acceptable?
2. **LAD-20261024_165202000_SR-t9**: You healed Dedenne ex twice, retreated it to Oricorio and passed. Dede-Circuit would have done 160 to the 60-HP Hydreigon (a 1-point KO; Rocky Helmet leaves Dedenne at 30). Is healing and attacking also acceptable, or was keeping Dedenne off the Active Spot clearly right?
3. **LAD-20261024_175606000_SR-t1**: Elegant Cape on the lone Carvanha, then Copycat shuffled away Mega Sharpedo ex and Mega Gyarados ex for 2 cards. Would keeping your hand (Cape only, then pass), so the Sharpedo evolution is certain next turn, also be acceptable?
4. **LAD-20261024_181948000_SR-t8**: You evolved Carvanha into Mega Sharpedo and Turbo Sharked Zapdos ex (140 to 70). Instead you could attach the Water to the benched 3-Energy Gyarados, switch it in with the free-retreat Sharpedo and Mega Blast the 140-HP Zapdos ex for a 2-point KO. Is that also acceptable, or was there a reason to prefer Turbo Shark?
5. **LAD-20261024_182453000_SR-t8**: Against Safeguard Oricorio you swapped Sharpedos and ended without attacking. Should you still attack with Turbo Shark for its free Bench Water (it does 0 damage)? The same choice comes up at t10 and t12. Those two points have no pending alternative, so his answer here should be applied to them too.

## Anything not labelled
Nothing. Notes:
- I didn't use or open any `UNCERTAINTIES.json` or `LADDER_ENTRY.json`; I labelled from the reviews, positions, legal lists, decks and card text only.
- Pending lines are written in the engine's labels but only their first action was checked against `legal.jsonl`. Their later steps (for example `Evolve:Haxorus@0` after Rare Candy, and `Attack:Mega Blaster` after `Retreat:1`) still need the legal-moves check during assembly.
- 181948-t8's KO line assumes Zapdos ex's listed 140 HP (120 + Giant Cape) and Mega Blaster's printed 140 with no reduction on the board.
