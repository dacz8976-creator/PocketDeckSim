# Card-text check: dustin:manectric (Plan B2e)

- List: `decks/dustin/09-mega-manectric-heliolisk.txt` (Energy: Lightning; 20 cards, 13 distinct)
- Limitless archetype: "Mega Manectric ex Heliolisk"
- Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root, plus the raw entry in `lib/deckgym-database.json` (for the Trainer subtype, which `card.py` does not print)
- Limitless text: `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched Sept 26, 2026
- Coverage: `rl/engine-2026-09-25/goldfish --deck <list> --panel decks/screen/opponents --games 0 --coverage` (sha256 `318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997`, the official release; 0 games played). Output: `card_check_dustin_manectric_coverage.json` beside this file.

## Verdict

- **Cards checked: 13 of 13.** Every card was verified against its Limitless page.
- **High-severity mismatches: 0.** HP, type, stage, evolves-from, weakness, retreat cost, attack cost, attack damage, attack effect text, and Trainer subtype/text all agree.
- **Low-severity mismatches: 1.** Poké Ball: engine "Put **a** random Basic Pokémon…" vs Limitless "Put **1** random Basic Pokemon…" (same meaning).
- **Coverage flags: 1.** Copycat (B1 225) trips the *unpriced text rule* (its text refers to the opponent's hand, which k3 does not price). Every card is "Fully implemented" with no named limitation; no printed-damage estimator fallback; nothing pays off on the opponent's turn.
- Mega ex rule: Limitless prints "When your Mega Evolution Pokémon ex is Knocked Out, your opponent gets 3 points" on Mega Manectric ex. The engine does not store this as card text; it applies it by name (`engine/src/models/card.rs` lines 196-209: a Pokémon whose name starts with "Mega " is worth 3 points). Not a mismatch.
- Unverified: none.

## Per-card table

### Pokémon

| Card (id) | Field | Engine | Limitless | Match |
|---|---|---|---|---|
| Helioptile (B1a 028) | Type / Stage / Evolves from | Lightning / Basic (stage 0) / — | Lightning / Basic / — | yes |
| | HP / Weakness / Retreat | 60 / Fighting / 1 | 60 / Fighting / 1 | yes |
| | Ability | none | none | yes |
| | Attack: Thunder Shock | [L] 10 — "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed." | 1 Lightning, 10 — same text | yes |
| Heliolisk (B4 061) | Type / Stage / Evolves from | Lightning / Stage 1 / Helioptile | Lightning / Stage 1 / Helioptile | yes |
| | HP / Weakness / Retreat | 80 / Fighting / 1 | 80 / Fighting / 1 | yes |
| | Ability | none | none | yes |
| | Attack: Electrispark | [L] 40 — "This attack also does 10 damage to each of your opponent's Benched Pokémon." | 1 Lightning, 40 — same text | yes |
| Electrike (B2b 026) | Type / Stage / Evolves from | Lightning / Basic (stage 0) / — | Lightning / Basic / — | yes |
| | HP / Weakness / Retreat | 60 / Fighting / 1 | 60 / Fighting / 1 | yes |
| | Ability | none | none | yes |
| | Attack: Quick Attack | [L] 10 — "Flip a coin. If heads, this attack does 30 more damage." | L, 10+ — same text | yes |
| Mega Manectric ex (B2b 027) | Type / Stage / Evolves from | Lightning / Stage 1 / Electrike | Lightning / Stage 1 / Electrike | yes |
| | HP / Weakness / Retreat | 180 / Fighting / 0 | 180 / Fighting / 0 | yes |
| | Ability | none | none (Mega ex rule box only: 3 points when KO'd; engine applies it by the "Mega " name rule) | yes |
| | Attack: Lightning Accelerator | [LL] 80 — "This attack does 30 more damage for each point you have gotten." | 2 Lightning, 80+ — same text | yes |

### Trainers

| Card (id) | Field | Engine | Limitless | Match |
|---|---|---|---|---|
| Poké Ball (P-A 005) | Trainer type | Item | Item | yes |
| | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | **low: "a" vs "1", same meaning** |
| Clemont's Backpack (B1a 066) | Trainer type | Item | Item | yes |
| | Text | "During this turn, attacks used by your Magneton or Heliolisk do +20 damage to your opponent's Pokémon." | same | yes |
| Field Blower (B3 147) | Trainer type | Item | Item | yes |
| | Text | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | same | yes |
| Elegant Cape (B3b 065) | Trainer type | Tool | Tool | yes |
| | Text | "The Stage 1 Pokémon this card is attached to gets +30 HP." | same | yes |
| Professor's Research (P-A 007) | Trainer type | Supporter | Supporter | yes |
| | Text | "Draw 2 cards." | same | yes |
| Cyrus (A2 150) | Trainer type | Supporter | Supporter | yes |
| | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | same | yes |
| Clemont (B1a 068) | Trainer type | Supporter | Supporter | yes |
| | Text | "Put 2 random cards from among Magneton, Heliolisk, and Clemont's Backpack from your deck into your hand." | same | yes |
| Copycat (B1 225) | Trainer type | Supporter | Supporter | yes |
| | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same | yes |
| Training Area (B2 153) | Trainer type | Stadium | Stadium | yes |
| | Text | "Attacks used by Stage 1 Pokémon in play (both yours and your opponent's) do +10 damage to the opponent's Active Pokémon." | same | yes |

## Coverage flags (goldfish `--coverage`, official release)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn | Flag class |
|---|---|---|---|---|---|---|
| Helioptile (B1a 028) | Fully implemented | none | — | — | — | clean |
| Heliolisk (B4 061) | Fully implemented | none | — | — | — | clean |
| Electrike (B2b 026) | Fully implemented | none | — | — | — | clean |
| Mega Manectric ex (B2b 027) | Fully implemented | none | — | — | — | clean |
| Poké Ball (P-A 005) | Fully implemented | none | — | — | — | clean |
| Clemont's Backpack (B1a 066) | Fully implemented | none | — | — | — | clean |
| Field Blower (B3 147) | Fully implemented | none | — | — | — | clean |
| Elegant Cape (B3b 065) | Fully implemented | none | — | — | — | clean |
| Professor's Research (P-A 007) | Fully implemented | none | — | — | — | clean |
| Cyrus (A2 150) | Fully implemented | none | — | — | — | clean |
| Clemont (B1a 068) | Fully implemented | none | — | — | — | clean |
| Copycat (B1 225) | Fully implemented | none | **its effect** | — | — | **unpriced text rule** |
| Training Area (B2 153) | Fully implemented | none | — | — | — | clean |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck; k3 leaves it unpriced), printed-damage estimator (attack damage effect not in the estimator's priced list), pays off on the opponent's turn, engine limitation (named limitation), not implemented (engine status incomplete). Only the first class fires here, on Copycat.

## Notes

- Limitless renders coin-flip and scaling attacks as "10+" / "80+"; the engine stores the base as `fixed_damage` and the effect text. That is a display convention, not a difference.
- The engine's `retreat_cost` is a list of Colorless symbols (`["Colorless"]` = 1; `[]` = 0), which matches Limitless's numeric retreat cost for all four Pokémon.
- The panel directory was passed only so the tool would not look for a `../decks/research` folder; with `--games 0` it opens no game.
