# Card-text check: h-garchomp.txt (arch:garchomp)

Date: 2026-09-26. Deck file: `rl/results/b2e_card_check_2026-09-26/decks/h-garchomp.txt` (Energy: Water, Fighting; 20 cards, 16 distinct).

Method: engine text from `python lib/card.py "<SET> <NUMBER>"` (database `lib/deckgym-database.json`; letter key from `lib/card.py` line 14: G Grass, R Fire, W Water, L Lightning, P Psychic, F Fighting, D Dark, M Metal, C Colorless, `[-]` = no energy cost). Limitless text from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched today. Trainer subtype for the engine comes from the database's `trainer_card_type` field (card.py prints only "Trainer"). Coverage flags from `rl/engine-2026-09-25/goldfish --deck <file> --panel decks/screen/opponents --games 0 --coverage rl/results/b2e_card_check_2026-09-26/coverage_arch_garchomp.json` (0 games played; the tool has no `--help`, flags read from `engine/examples/goldfish.rs`).

## Result

- Cards checked: 16 of 16. Unverified: none.
- Mismatches: 1, low severity (Poké Ball wording: engine "Put a random Basic Pokémon", Limitless "Put 1 random Basic Pokemon"; same meaning).
- Coverage flags: 3 cards flagged (Garchomp, Happiny, Copycat). All 16 cards report "Fully implemented", no engine limitations, nothing "not implemented".

## Pokémon

| Card | Field | Engine | Limitless | Verdict |
|---|---|---|---|---|
| Gible A2 121 | HP / type / stage | 60 / Dragon / Basic | 60 / Dragon / Basic | match |
| | Weakness / retreat | none / 1 | none / 1 | match |
| | Attack Gnaw | [C] 20, no effect | 1 Colorless, 20, no effect | match |
| Gible B4a 052 | HP / type / stage | 60 / Dragon / Basic | 60 / Dragon / Basic | match |
| | Weakness / retreat | none / 1 | none / 1 | match |
| | Attack Take Down | [C] 30 — "This Pokémon also does 10 damage to itself." | 1 Colorless, 30 — "This Pokémon also does 10 damage to itself." | match |
| Garchomp B4a 054 | HP / type / stage | 150 / Dragon / Stage 2 from Gabite | 150 / Dragon / Stage 2, evolves from Gabite | match |
| | Weakness / retreat | none / 1 | none / 1 | match |
| | Ability Mach Stealth | "If your opponent's Pokémon is Knocked Out by damage from this Pokémon's attacks, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon." | identical text | match |
| | Attack Land Crush | [WFC] 120 (database: Water, Fighting, Colorless) | "WFC Land Crush 120" (page letters W F C) | match. Note: a first summarised fetch expanded F as "Fire"; the page itself shows the letter F, and the deck's energy line (Water, Fighting) agrees with the engine. |
| Happiny B4a 063 | HP / type / stage | 30 / Colorless / Basic | 30 / Colorless / Basic | match |
| | Weakness / retreat | none / 0 | none / 0 | match |
| | Attack Chubby Cheer | [-] 10 — "During your next turn, attacks used by your Pokémon do +20 damage to your opponent's Active Pokémon." | cost 0, 10 — identical text | match |
| Mantyke A4a 023 | HP / type / stage | 30 / Water / Basic | 30 / Water / Basic | match |
| | Weakness / retreat | none / 0 | none / 0 | match |
| | Attack Splashy Toss | [-] no damage — "Take a [W] Energy from your Energy Zone and attach it to 1 of your Benched Basic Pokémon." | "0 Splashy Toss", no damage, identical text | match. Note: a first summarised fetch reported a 1-Water cost; a targeted re-fetch confirms the page shows cost 0 (the [W] is inside the effect text). |
| Cleffa A4 077 | HP / type / stage | 30 / Psychic / Basic | 30 / Psychic / Basic | match |
| | Weakness / retreat | none / 0 | none / 0 | match |
| | Attack Twinkly Call | [-] no damage — "Put a random Pokémon from your deck into your hand." | "0 Twinkly Call" (attack, cost 0, no damage), identical text | match. Note: a first summarised fetch called it an Ability; a targeted re-fetch confirms the page labels it a 0-cost attack, as the engine does. |

## Trainers

| Card | Engine subtype / text | Limitless subtype / text | Verdict |
|---|---|---|---|
| Professor's Research P-A 007 | Supporter — "Draw 2 cards." | Supporter — "Draw 2 cards." | match |
| Cynthia A2 152 | Supporter — "During this turn, attacks used by your Garchomp or Togekiss do +50 damage to your opponent's Active Pokémon." | Supporter — identical | match |
| Cyrus A2 150 | Supporter — "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | Supporter — identical | match |
| Lisia B1 226 | Supporter — "Put 2 random Basic Pokémon with 50 HP or less from your deck into your hand." | Supporter — identical | match |
| Copycat B1 225 | Supporter — "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | Supporter — identical | match |
| Wally B4 153 | Supporter — "Take a [C] Energy from your Energy Zone and attach it to 1 of your Stage 2 Pokémon." | Supporter — identical | match |
| Rare Candy A3 144 | Item — "Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn." | Item — identical | match |
| Poké Ball P-A 005 | Item — "Put a random Basic Pokémon from your deck into your hand." | Item — "Put 1 random Basic Pokemon from your deck into your hand." | LOW mismatch: wording only ("a" vs "1"), same meaning |
| Protective Poncho B2 147 | Tool — "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." | Tool — identical | match |
| Rainbow Cave B4 155 | Stadium — "Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced." | Stadium — identical | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card | Flag class | Detail from the tool |
|---|---|---|
| Garchomp B4a 054 | pays off on the opponent's turn | `ability Mach Stealth` (k3 never searches the opponent's turn, so the damage/effect prevention is not priced) |
| Happiny B4a 063 | printed-damage estimator | `Chubby Cheer: IncreasedDamageNextTurn estimated at printed damage` (the +20 next turn is not priced) |
| Copycat B1 225 | unpriced text rule | `its effect` (draws by the opponent's hand size; k3 prices it with a fallback) |

All 16 cards: `engine_status` "Fully implemented", `engine_complete` true, `limitations` empty. No "engine limitation" or "not implemented" flags.

Per the goldfish doc header, the bot's numbers for a list with flagged cards are marked untrusted on its page; this list has three flagged cards.
