# Card-text check: dustin:raticate (decks/dustin/13-a-ninetales-raticate.txt)

Date: 2026-09-26. Plan B2e, held-out archetype "Team Rocket's Raticate ex Alolan Ninetales ex".

Sources:
- Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`), plus the raw database entry for trainer subtype and retreat-cost list.
- Limitless text: `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>`, fetched with WebFetch on 2026-09-26 (the fetch tool extracts the page with a small model; every field was read back and compared by hand).
- Coverage flags: `rl/engine-2026-09-25/goldfish --deck <file> --panel decks/screen/opponents --games 0 --coverage coverage_dustin_raticate.json` (goldfish sha256 `318c82c8...dbe997`, matches the README). `--games 0` iterates zero games per panel deck, so nothing was played. Raw output: `coverage_dustin_raticate.json` in this folder. Script: scratchpad `b2e/coverage_dustin_raticate.sh`.

Deck file (Energy: Water, 20 cards, 14 distinct):

```
2 Alolan Vulpix B2 028
2 Alolan Ninetales ex B2 029
2 Team Rocket's Rattata B4a 058
2 Team Rocket's Raticate ex B4a 059
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Elegant Cape B3b 065
2 Professor's Research P-A 007
1 Sabrina A1 225
1 Cyrus A2 150
1 Ilima A3 149
1 Copycat B1 225
1 Sightseer B2 150
1 Soothing Shore B4 154
```

## Summary

- 14 distinct cards checked, 14 verified against Limitless.
- Mismatches: 1, low severity (Poké Ball wording "a random" vs "1 random"; same meaning). No high-severity mismatch: every HP, type, stage, evolves-from, weakness, retreat cost, attack cost, damage, effect, ability and Trainer type matches.
- Coverage flags (bot side): 3 cards flagged, none "engine limitation" or "not implemented" (all 14 are "Fully implemented", empty limitations, no printed-damage estimator fallback).
  - Copycat B1 225: unpriced text rule (its effect).
  - Alolan Ninetales ex B2 029: pays off on the opponent's turn (attack Binding Snow).
  - Team Rocket's Raticate ex B4a 059: unpriced text rule (ability Thieving Incisors). Note: the tool's rule is a substring test ("opponent" plus "hand" or "deck"); the ability text says "from your hand" and "opponent's Active Pokémon", so this is a heuristic hit, not a real hand/deck-of-opponent effect. Reported as the tool reports it.

## Pokémon

| Card | Field | Engine | Limitless | Result |
|---|---|---|---|---|
| Alolan Vulpix B2 028 | Type / Stage | Water, Basic | Water, Basic | match |
| | HP / Weakness / Retreat | 60 / Metal / 1 | 60 / Metal / 1 | match |
| | Attack: Gnaw | [W] 20, no effect | W, 20, no effect | match |
| | Ability | none | none | match |
| Alolan Ninetales ex B2 029 | Type / Stage | Water, Stage 1 from Alolan Vulpix | Water, Stage 1, evolves from Alolan Vulpix | match |
| | HP / Weakness / Retreat | 150 / Metal / 2 | 150 / Metal / 2 | match |
| | Attack: Binding Snow | [WW] 80 — "During your opponent's next turn, they can't take any Energy from their Energy Zone to attach to their Active Pokémon." | WW, 80 — "During your opponent's next turn, they can't take any Energy from their Energy Zone to attach to their Active Pokémon." | match |
| | Ability | none | none (ex rule box only) | match |
| Team Rocket's Rattata B4a 058 | Type / Stage | Colorless, Basic | Colorless, Basic | match |
| | HP / Weakness / Retreat | 40 / Fighting / 1 | 40 / Fighting / 1 | match |
| | Attack: Ambush | [C] 20 — "Flip a coin. If heads, this attack does 20 more damage." | C, 20+ — "Flip a coin. If heads, this attack does 20 more damage." | match (the "+" is print notation; the effect text carries it) |
| | Ability | none | none | match |
| Team Rocket's Raticate ex B4a 059 | Type / Stage | Colorless, Stage 1 from Team Rocket's Rattata | Colorless, Stage 1, evolves from Team Rocket's Rattata | match |
| | HP / Weakness / Retreat | 120 / Fighting / 0 | 120 / Fighting / 0 | match |
| | Ability: Thieving Incisors | "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may move a random Energy from your opponent's Active Pokémon to this Pokémon." | same text | match |
| | Attack: Boost Dash | [CC] 70, no effect | CC, 70, no effect | match |

## Trainers

| Card | Field | Engine | Limitless | Result |
|---|---|---|---|---|
| Poké Ball P-A 005 | Trainer type | Item | Item | match |
| | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | LOW: "a random" vs "1 random" (same meaning) |
| Field Blower B3 147 | Trainer type | Item | Item | match |
| | Text | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | same | match |
| Elegant Cape B3b 065 | Trainer type | Tool | Tool | match |
| | Text | "The Stage 1 Pokémon this card is attached to gets +30 HP." | same | match |
| Professor's Research P-A 007 | Trainer type | Supporter | Supporter | match |
| | Text | "Draw 2 cards." | same | match |
| Sabrina A1 225 | Trainer type | Supporter | Supporter | match |
| | Text | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | same | match |
| Cyrus A2 150 | Trainer type | Supporter | Supporter | match |
| | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | same | match |
| Ilima A3 149 | Trainer type | Supporter | Supporter | match |
| | Text | "Put 1 of your [C] Pokémon that has damage on it into your hand." | same | match |
| Copycat B1 225 | Trainer type | Supporter | Supporter | match |
| | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same | match |
| Sightseer B2 150 | Trainer type | Supporter | Supporter | match |
| | Text | "Look at the top 4 cards of your deck. Put all Stage 1 Pokémon you find there into your hand. Shuffle the other cards back into your deck." | same | match |
| Soothing Shore B4 154 | Trainer type | Stadium | Stadium | match |
| | Text | "At the end of each player's turn, that player heals 20 damage from each of their Pokémon that has any [W] Energy attached." | same | match |

## Coverage flags (goldfish --coverage)

| Card | engine_status | limitations | unpriced text rule | printed-damage estimator | pays off on opponent's turn |
|---|---|---|---|---|---|
| Alolan Vulpix B2 028 | Fully implemented | none | - | - | - |
| Alolan Ninetales ex B2 029 | Fully implemented | none | - | - | attack Binding Snow |
| Team Rocket's Rattata B4a 058 | Fully implemented | none | - | - | - |
| Team Rocket's Raticate ex B4a 059 | Fully implemented | none | ability Thieving Incisors (substring hit, see note above) | - | - |
| Poké Ball P-A 005 | Fully implemented | none | - | - | - |
| Field Blower B3 147 | Fully implemented | none | - | - | - |
| Elegant Cape B3b 065 | Fully implemented | none | - | - | - |
| Professor's Research P-A 007 | Fully implemented | none | - | - | - |
| Sabrina A1 225 | Fully implemented | none | - | - | - |
| Cyrus A2 150 | Fully implemented | none | - | - | - |
| Ilima A3 149 | Fully implemented | none | - | - | - |
| Copycat B1 225 | Fully implemented | none | its effect | - | - |
| Sightseer B2 150 | Fully implemented | none | - | - | - |
| Soothing Shore B4 154 | Fully implemented | none | - | - | - |

What the flag classes mean (from `engine/examples/goldfish.rs`): "unpriced text rule" = the effect text names the opponent's hand or deck, which the k3 pilot's pricing does not value; "printed-damage estimator" = an attack whose damage effect the pilot's estimator prices at the printed number (none here); "pays off on the opponent's turn" = an effect whose value lands during the opponent's turn, which k3 never searches; "engine limitation" = a non-empty `limitations` list (none here); "not implemented" = engine_status other than fully implemented (none here).

## Unverified

None. All 14 cards fetched from Limitless on the first try at the exact-id URL.
