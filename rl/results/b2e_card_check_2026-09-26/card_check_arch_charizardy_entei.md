# Card-text check: arch:charizardy_entei (held-out list, Plan B2e)

**Deck file:** `rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt` (Energy: Fire, 20 cards, 13 distinct)
**Engine text source:** `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`); trainer subtypes read from the same database (`trainer_card_type`), since `card.py` prints only "Trainer".
**Limitless source:** `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` (numbers without leading zeros), fetched Sept 26, 2026.
**Coverage tool:** `rl/engine-2026-09-25/goldfish` (sha256 `318c82c8…be997`, matches the README) run with `--games 0 --coverage`, panel `decks/screen/opponents`; 0 games played. Output: `coverage_arch_charizardy_entei.json` in this folder.

## Summary

- 13 of 13 distinct cards verified against Limitless.
- **0 high-severity mismatches.** Every HP, type, stage, evolves-from, weakness, retreat cost, attack cost, attack damage, attack effect, ability name/text, trainer subtype and trainer text agrees.
- **1 low-severity wording mismatch:** Poké Ball (P-A 005) — engine "Put **a** random Basic Pokémon…", Limitless "Put **1** random Basic Pokémon…". Same meaning.
- **Coverage flags:** 1 card flagged — Copycat (B1 225), *unpriced text rule* (its effect reads the opponent's hand; k3 prices it with a fallback). No card is flagged for the printed-damage estimator, for paying off on the opponent's turn, for an engine limitation, or as not implemented. All 13 report "Fully implemented".
- **Unverified:** none.

## Per-card table

Columns compare the engine's database text with the Limitless card page. "same" means identical apart from spelling/punctuation/accents.

| # | Card (id) | Count | Field | Engine | Limitless | Result |
|---|---|---|---|---|---|---|
| 1 | Charmander (B2b 007) | 2 | Type / Stage | Fire / Basic (stage 0) | Fire / Basic | same |
| | | | HP / Weakness / Retreat | 70 / Water / 1 | 70 / Water / 1 | same |
| | | | Attack | [RC] Flame Tail 30, no effect | RC Flame Tail 30, no effect | same |
| | | | Ability | none | none | same |
| 2 | Charmeleon (B2b 008) | 2 | Type / Stage | Fire / Stage 1 from Charmander | Fire / Stage 1, evolves from Charmander | same |
| | | | HP / Weakness / Retreat | 80 / Water / 2 | 80 / Water / 2 | same |
| | | | Ability | Ignition: "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may take a [R] Energy from your Energy Zone and attach it to your Active [R] Pokémon." | Ignition: identical text | same |
| | | | Attack | [RR] Slash 40, no effect | RR Slash 40, no effect | same |
| 3 | Mega Charizard Y ex (B1a 014) | 1 | Type / Stage | Fire / Stage 2 from Charmeleon | Fire / Stage 2, evolves from Charmeleon | same |
| | | | HP / Weakness / Retreat | 220 / Water / 2 | 220 / Water / 2 | same |
| | | | Attack | [RRRC] Crimson Dive 250 — "This Pokémon also does 50 damage to itself." | RRRC Crimson Dive 250 — identical effect | same |
| | | | Ability | none | none | same |
| | | | Rule box | (not card text in the database) | "When your Mega Evolution Pokémon ex is Knocked Out, your opponent gets 3 points." | rules text, not compared here (see note) |
| 4 | Entei ex (A4a 010) | 2 | Type / Stage | Fire / Basic (stage 0) | Fire / Basic | same |
| | | | HP / Weakness / Retreat | 140 / Water / 2 | 140 / Water / 2 | same |
| | | | Ability | Legendary Pulse: "At the end of your turn, if this Pokémon is in the Active Spot, draw a card." | Legendary Pulse: identical text | same |
| | | | Attack | [RR] Blazing Beatdown 60 — "If this Pokémon has at least 2 extra [R] Energy attached, this attack does 60 more damage." | RR Blazing Beatdown 60+ — identical effect | same |
| | | | Rule box | (not card text in the database) | "When your Pokémon ex is Knocked Out, your opponent gets 2 points." | rules text, not compared here |
| 5 | Professor's Research (P-A 007) | 2 | Trainer type | Supporter | Supporter | same |
| | | | Text | "Draw 2 cards." | "Draw 2 cards." | same |
| 6 | Copycat (B1 225) | 2 | Trainer type | Supporter | Supporter | same |
| | | | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | identical | same |
| 7 | Wally (B4 153) | 1 | Trainer type | Supporter | Supporter | same |
| | | | Text | "Take a [C] Energy from your Energy Zone and attach it to 1 of your Stage 2 Pokémon." | identical | same |
| 8 | Pokémon Center Lady (A2b 070) | 1 | Trainer type | Supporter | Supporter | same |
| | | | Text | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | identical | same |
| 9 | Flame Patch (B1 217) | 2 | Trainer type | Item | Item | same |
| | | | Text | "Attach a [R] Energy from your discard pile to your Active [R] Pokémon." | identical | same |
| 10 | Poké Ball (P-A 005) | 2 | Trainer type | Item | Item | same |
| | | | Text | "Put **a** random Basic Pokémon from your deck into your hand." | "Put **1** random Basic Pokémon from your deck into your hand." | **low mismatch** (wording; same meaning) |
| 11 | Lucky Ice Pop (B2 145) | 1 | Trainer type | Item | Item | same |
| | | | Text | "Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile." | identical | same |
| 12 | Giant Cape (A2 147) | 1 | Trainer type | Tool | Tool | same |
| | | | Text | "The Pokémon this card is attached to gets +20 HP." | identical | same |
| 13 | Rainbow Cave (B4 155) | 1 | Trainer type | Stadium | Stadium | same |
| | | | Text | "Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced." | identical | same |

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball (P-A 005) | Trainer text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokémon from your deck into your hand." | low (wording only) |

## Coverage flags (goldfish `--coverage`, 0 games)

| Card | unpriced text rule | printed-damage estimator | pays off on opponent's turn | engine limitation | not implemented |
|---|---|---|---|---|---|
| Copycat (B1 225) | **yes** — "its effect" (reads the opponent's hand) | – | – | – | – |
| all other 12 cards | – | – | – | – | – |

Every card's `engine_status` is "Fully implemented" with `engine_complete: true` and an empty `limitations` list.

## Notes

- The ex and Mega ex rule boxes ("opponent gets 2/3 points") are printed on the Limitless page but are game rules, not the card's own text, and the database does not store them; they were not counted as mismatches. The engine applies them by name: `engine/src/models/card.rs` lines 197-208 treat a Pokémon whose name starts with "Mega " as worth 3 points on KO, an ex as 2, anything else as 1. So Mega Charizard Y ex (3) and Entei ex (2) get the printed values.
- Limitless renders "Pokémon" as "Pokemon" in places; treated as spelling.
- `goldfish` has no `--help` (it panics asking for `--deck`); its flags were read from `engine/examples/goldfish.rs`. It requires a panel directory to exist even with `--games 0`, so the screen opponents folder was passed; with 0 games the per-opponent loop is empty and nothing is played.
