# Card-text check: arch:whimsicott (Plan B2e held-out list)

**List:** `rl/results/b2e_card_check_2026-09-26/decks/h-whimsicott.txt` (Energy: Grass; 12 distinct cards, 20 cards total)
**Date:** 2026-09-26
**Engine text source:** `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`; trainer subtypes read from the same database's `trainer_card_type` field because `card.py` prints only "Trainer").
**Limitless source:** `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>`, fetched 2026-09-26 (all 12 direct fetches succeeded; no search fallback needed).
**Coverage tool:** `rl/engine-2026-09-25/goldfish --deck <list> --games 0 --panel decks/screen/opponents --coverage <out>` (sha256 `318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997`, the README's hash). Zero games played. Raw output: `coverage_arch_whimsicott.json` beside this file.

## Result in one line

**12 of 12 cards match Limitless. No mismatches. No unverified cards.** Three cards carry a coverage flag (see below); none is "not implemented" or has an engine limitation.

## Per-card table (engine vs Limitless)

Fields compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost / damage / effect, ability name and text, Trainer subtype and text. "Match" means identical beyond spelling and punctuation.

### Pokémon

| # | Card (id) | Field | Engine | Limitless | Verdict |
|---|---|---|---|---|---|
| 1 | Cottonee (B1 015) x2 | HP / type | 50 / Grass | 50 / Grass | match |
| | | Stage / evolves from | Basic (stage 0) / none | Basic / none | match |
| | | Weakness / retreat | Fire / 1 | Fire / 1 | match |
| | | Attack | [G] Razor Leaf 20, no effect | G Razor Leaf 20, no effect | match |
| | | Ability | none | none | match |
| 2 | Whimsicott ex (B1 016) x2 | HP / type | 140 / Grass | 140 / Grass | match |
| | | Stage / evolves from | Stage 1 / Cottonee | Stage 1 / Cottonee | match |
| | | Weakness / retreat | Fire / 1 | Fire / 1 | match |
| | | Attack | [GC] Grass Knot 40 — "This attack does 30 more damage for each Energy in your opponent's Active Pokémon's Retreat Cost." | GC Grass Knot "40+" — same effect text | match (Limitless prints the "+" suffix; the engine stores base 40 plus the effect; same meaning) |
| | | Ability | none | none | match |
| | | ex rule | not printed by card.py (ex status is carried by the name and the engine's ex flag) | "When your Pokémon ex is Knocked Out, your opponent gets 2 points." | not a card-text field; noted only |
| 3 | Spinarak (B1a 005) x2 | HP / type | 50 / Grass | 50 / Grass | match |
| | | Stage / evolves from | Basic / none | Basic / none | match |
| | | Weakness / retreat | Fire / 1 | Fire / 1 | match |
| | | Attack | [G] Sting 20, no effect | G Sting 20, no effect | match |
| | | Ability | none | none | match |
| 4 | Ariados (B1a 006) x2 | HP / type | 90 / Grass | 90 / Grass | match |
| | | Stage / evolves from | Stage 1 / Spinarak | Stage 1 / Spinarak | match |
| | | Weakness / retreat | Fire / 1 | Fire / 1 | match |
| | | Ability | Trap Territory: "Your opponent's Active Pokémon's Retreat Cost is 1 more." | Trap Territory: same text | match |
| | | Attack | [G] Pierce 30, no effect | G Pierce 30, no effect | match |
| 5 | Pheromosa (A3a 007) x1 | HP / type | 70 / Grass | 70 / Grass | match |
| | | Stage / evolves from | Basic / none | Basic / none | match |
| | | Weakness / retreat | Fire / 1 | Fire / 1 | match |
| | | Attack | [G] Jump Blues 20 — "This attack also does 20 damage to 1 of your opponent's Benched Pokémon." | G Jump Blues 20 — same text | match |
| | | Ability | none | none | match |

### Trainers

| # | Card (id) | Subtype (engine / Limitless) | Engine text | Limitless text | Verdict |
|---|---|---|---|---|---|
| 6 | Professor's Research (P-A 007) x2 | Supporter / Supporter | "Draw 2 cards." | "Draw 2 cards." | match |
| 7 | Cyrus (A2 150) x1 | Supporter / Supporter | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | same | match |
| 8 | Copycat (B1 225) x1 | Supporter / Supporter | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same | match |
| 9 | Quick-Grow Extract (B1a 067) x2 | Item / Item | "Choose 1 of your [G] Pokémon in play. Put a random [G] Pokémon from your deck that evolves from that Pokémon onto that Pokémon to evolve it. You can't use this card during your first turn or on a Pokémon that was put into play this turn." | same | match |
| 10 | Team Rocket's Goo-zooka (B4a 068) x2 | Item / Item | "Until the end of your opponent's next turn, your opponent's Active Pokémon's Retreat Cost is 1 more." | same | match |
| 11 | Leaf Cape (A3 147) x1 | Tool / Tool | "The [G] Pokémon this card is attached to gets +30 HP." | same | match |
| 12 | Fragrant Forest (B3 153) x2 | Stadium / Stadium | "Once during each player's turn, that player may put a random Basic [G] Pokémon from their deck into their hand." | same | match |

## Mismatches

None. (Every field on all 12 cards matches Limitless beyond spelling, punctuation and the "40+" damage notation.)

## Unverified

None. All 12 Limitless pages loaded on the first try and all 12 engine lookups resolved to exactly one printing.

## Coverage flags (goldfish `--coverage`, 0 games)

| Card (id) | Flag class | Tool's note | Plain meaning |
|---|---|---|---|
| Whimsicott ex (B1 016) | printed-damage estimator | "Grass Knot: ExtraDamagePerRetreatCost estimated at printed damage" | The game applies the +30 per retreat-cost Energy correctly, but the k3 bot's look-ahead values Grass Knot as a flat 40 when choosing moves. So the pilot under-rates its own main attack (and the Ariados / Goo-zooka synergy that pumps it). This is the deck's whole plan, so the bot's numbers for this list should be treated as untrusted. |
| Copycat (B1 225) | unpriced text rule (opponent's hand) | "its effect" | The card works in the game, but the bot has no price for "draw for each card in your opponent's hand", so it plays Copycat without weighing how many cards it would draw. |
| Team Rocket's Goo-zooka (B4a 068) | pays off on the opponent's turn | "its effect" | The retreat-cost increase lasts through the opponent's next turn; k3 never searches the opponent's turn, so it cannot see the trap value (only the immediate Grass Knot bonus, which it also does not price, see above). |

No card is flagged "engine limitation" or "not implemented". All 12 report `engine_status: Fully implemented`, `engine_complete: true`, `limitations: []`.

## Notes for the B2e comparison

- Card text is not a source of error for this list: the engine plays every card as printed.
- The three flags all sit on the deck's core plan (Whimsicott ex's scaling attack plus retreat-cost stacking from Ariados and Goo-zooka). Expect the pilot to under-perform the real Limitless cell on this archetype for bot reasons, not rules reasons.
- Ariados's Trap Territory is a passive ability; the coverage tool does not flag it, but its damage value flows only through Grass Knot, which the estimator prices at printed damage.
