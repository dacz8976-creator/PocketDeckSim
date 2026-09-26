# Card-text check: arch:raticate (h-raticate.txt)

Date: 2026-09-26. List: `rl/results/b2e_card_check_2026-09-26/decks/h-raticate.txt` (Team Rocket's Raticate ex / Alolan Ninetales ex, Energy: Water, 20 cards, 13 distinct).

How it was checked:
- Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root, plus the raw entry in `lib/deckgym-database.json` for the Trainer sub-type (card.py prints only "Trainer").
- Limitless text: `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched on 2026-09-26.
- Coverage flags: `rl/engine-2026-09-25/goldfish --deck <list> --panel decks/screen/opponents --games 0 --coverage <out>` in WSL (goldfish sha256 `318c82c8…dbe997`, matches `rl/engine-2026-09-25/README.md`). 0 games played. Raw output: `coverage_arch_raticate.json` next to this file.

Result in one line: 13 of 13 cards verified; no high-severity mismatch; one low (Poké Ball says "a random" in the engine, "1 random" on Limitless, same meaning); one notation-only difference (Ambush "20+"). Three coverage flags, one of them a false positive of the tool's text rule.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Verdict |
|---|---|---|---|---|---|
| 1 | Alolan Vulpix (A3 040) | HP / type / stage | 60 / Water / Basic | 60 / Water / Basic | match |
| | | weakness / retreat | Metal / 1 | Metal / 1 | match |
| | | attack | [W] Call Forth Cold, no damage: "Take a [W] Energy from your Energy Zone and attach it to this Pokémon." | [W] Call Forth Cold, no damage, same text | match |
| 2 | Alolan Ninetales ex (B2 029) | HP / type / stage | 150 / Water / Stage 1 from Alolan Vulpix | 150 / Water / Stage 1 from Alolan Vulpix | match |
| | | weakness / retreat | Metal / 2 | Metal / 2 | match |
| | | attack | [WW] Binding Snow 80: "During your opponent's next turn, they can't take any Energy from their Energy Zone to attach to their Active Pokémon." | [WW] Binding Snow 80, same text | match |
| 3 | Team Rocket's Rattata (B4a 058) | HP / type / stage | 40 / Colorless / Basic | 40 / Colorless / Basic | match |
| | | weakness / retreat | Fighting / 1 | Fighting / 1 | match |
| | | attack | [C] Ambush 20: "Flip a coin. If heads, this attack does 20 more damage." | [C] Ambush 20+, same text | match in meaning; Limitless prints "20+" (the plus marks the coin-flip bonus that the effect text describes), the engine stores base 20 and the effect. Notation only. |
| 4 | Team Rocket's Raticate ex (B4a 059) | HP / type / stage | 120 / Colorless / Stage 1 from Team Rocket's Rattata | 120 / Colorless / Stage 1 from Team Rocket's Rattata | match |
| | | weakness / retreat | Fighting / 0 | Fighting / 0 | match |
| | | ability | Thieving Incisors: "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may move a random Energy from your opponent's Active Pokémon to this Pokémon." | Thieving Incisors, same text | match |
| | | attack | [CC] Boost Dash 70, no effect | [CC] Boost Dash 70, no effect | match |
| 5 | Professor's Research (P-A 007) | Trainer type / text | Supporter: "Draw 2 cards." | Supporter, same text | match |
| 6 | Copycat (B1 225) | Trainer type / text | Supporter: "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | Supporter, same text | match |
| 7 | Cyrus (A2 150) | Trainer type / text | Supporter: "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | Supporter, same text | match |
| 8 | Sabrina (A1 225) | Trainer type / text | Supporter: "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | Supporter, same text | match |
| 9 | Poké Ball (P-A 005) | Trainer type / text | Item: "Put a random Basic Pokémon from your deck into your hand." | Item: "Put 1 random Basic Pokemon from your deck into your hand." | LOW mismatch: "a random" vs "1 random". Same meaning (one card). |
| 10 | Repel (A3a 064) | Trainer type / text | Item: "Switch out your opponent's Active Basic Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | Item, same text | match |
| 11 | Elegant Cape (B3b 065) | Trainer type / text | Tool: "The Stage 1 Pokémon this card is attached to gets +30 HP." | Pokémon Tool, same text | match ("Tool" is the engine's name for Pokémon Tool) |
| 12 | Soothing Shore (B4 154) | Trainer type / text | Stadium: "At the end of each player's turn, that player heals 20 damage from each of their Pokémon that has any [W] Energy attached." | Stadium, same text | match |
| 13 | Training Area (B2 153) | Trainer type / text | Stadium: "Attacks used by Stage 1 Pokémon in play (both yours and your opponent's) do +10 damage to the opponent's Active Pokémon." | Stadium, same text | match |

The ex rule ("When your Pokémon ex is Knocked Out, your opponent gets 2 points.") is printed on both ex cards on Limitless; the engine applies it as a game rule, not card text. Not counted as a difference.

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball (P-A 005) | effect text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | low (wording; same meaning) |
| Team Rocket's Rattata (B4a 058) | Ambush damage notation | 20 (base) + effect "does 20 more damage" on heads | "20+" | low (notation only; same meaning) |

No high-severity mismatch. No HP, type, stage, weakness, retreat, attack cost, damage or effect-meaning difference on any card.

## Coverage flags (goldfish --coverage, 0 games)

All 13 cards report `engine_status: Fully implemented`, `engine_complete: true`, `limitations: []`. So there are no "engine limitation" or "not implemented" flags. The tool's text-rule flags:

| Card | Flag class | What the tool flagged | Note |
|---|---|---|---|
| Copycat (B1 225) | unpriced text rule | "its effect" (reads the opponent's hand) | Genuine: k3 does not price the opponent's hand size, so the draw count is a fallback. |
| Alolan Ninetales ex (B2 029) | pays off on the opponent's turn | "attack Binding Snow" (the energy lock lasts through the opponent's next turn) | Genuine: k3 never searches the opponent's turn, so the lock's value is not priced. |
| Team Rocket's Raticate ex (B4a 059) | unpriced text rule | "ability Thieving Incisors" | False positive of the tool's rule: the text contains "opponent" and "hand", but the "hand" is your own ("play this Pokémon from your hand") and the target is the opponent's Active Pokémon, not their hand or deck. The engine implements the ability fully. Listed because the floor check takes this flag from the tool as is. |

No card flagged as "printed-damage estimator" (Ambush's coin flip maps to a priced mechanic, CoinFlipExtraDamage).

## Unverified

None. Every card's Limitless page loaded on the first try at its direct `/cards/<SET>/<NUMBER>` address.
