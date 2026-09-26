# Card-text check: dustin:garchomp (decks/dustin/08-garchomp-toolbox.txt)

Date: 2026-09-26. Plan B2e held-out archetype "Garchomp".

How it was done:
- Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`), plus a read-only
  script that printed the raw database fields (`trainer_card_type`, `energy_required`, `fixed_damage`) because card.py does not print
  the Trainer subtype (script: scratchpad `b2e/garchomp_trainer_types.py`).
- Limitless text: `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` (numbers without leading zeros), one fetch per card, with a
  second verbatim fetch where the first summary was ambiguous (Garchomp cost letters, Munchlax and Gabite damage lines, Poké Ball wording).
- Coverage: `rl/engine-2026-09-25/goldfish --deck <list> --panel decks/screen/opponents --games 0 --coverage <out>` in WSL
  (goldfish sha256 `318c82c8...dbe997`, the manifest's hash). `--games 0` runs the per-opponent loop over zero games, so no game was
  played; the coverage file is written before that loop anyway. Output: `coverage_dustin_garchomp.json` in this folder.
  Script: scratchpad `b2e/garchomp_coverage.sh`.

Deck line: `Energy: Water, Fighting`. 15 distinct cards, 20 cards total.

## Per-card table

Legend: "same" means every compared field matched beyond spelling/punctuation. Costs use the engine's letters (W Water, F Fighting, C Colorless).

| # | Card (id) | Field | Engine (card.py / database) | Limitless | Result |
|---|---|---|---|---|---|
| 1 | Celebi (B3 004) x1 | type / stage / HP / weak / retreat | Grass, Basic, HP 70, weak Fire, retreat 1 | Grass, Basic, HP 70, weak Fire, retreat 1 | same |
| | | ability | Time Recall: "Each of your evolved Pokémon can use any attack from its previous Evolutions. (You still need the necessary Energy to use each attack.)" | identical | same |
| | | attack | [CC] Smack 30, no effect | CC Smack 30, no effect | same |
| 2 | Gible (A2 121) x2 | type / stage / HP / weak / retreat | Dragon, Basic, HP 60, weak none, retreat 1 | Dragon, Basic, HP 60, weak none, retreat 1 | same |
| | | attack | [C] Gnaw 20, no effect | C Gnaw 20, no effect | same |
| 3 | Gabite (B4a 053) x2 | type / stage / HP / weak / retreat | Dragon, Stage 1 from Gible, HP 80, weak none, retreat 1 | Dragon, Stage 1 evolves from Gible, HP 80, weak none, retreat 1 | same |
| | | attack | [WF] Linear Attack, printed damage none (fixed_damage 0), effect "This attack does 50 damage to 1 of your opponent's Pokémon." | "WF Linear Attack" with no number after the name; effect identical (verified verbatim: the only 50 is inside the effect sentence) | same |
| 4 | Garchomp (B4a 054) x2 | type / stage / HP / weak / retreat | Dragon, Stage 2 from Gabite, HP 150, weak none, retreat 1 | Dragon, Stage 2 evolves from Gabite, HP 150, weak none, retreat 1 | same |
| | | ability | Mach Stealth: "If your opponent's Pokémon is Knocked Out by damage from this Pokémon's attacks, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon." | identical | same |
| | | attack | [WFC] Land Crush 120, no effect (database cost: Water, Fighting, Colorless) | "WFC" Land Crush 120 (page uses the letters W, F, C; second fetch confirmed F = Fighting, 3 energy total) | same |
| 5 | Munchlax (B3b 054) x1 | type / stage / HP / weak / retreat | Colorless, Basic, HP 50, weak none, retreat 2 | Colorless, Basic, HP 50, weak none, retreat 2 | same |
| | | attack | [-] (no energy) Hungrily Draw 10, effect "Draw a card." | "0 Hungrily Draw 10" / "Draw a card." (verbatim fetch: the 10 is the number at the end of the attack-name line) | same |
| 6 | Poké Ball (P-A 005) x2 | trainer type | Item | Item | same |
| | | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." (two fetches, one asked for character-exact text, both gave "1 random") | LOW: wording only, "a" vs "1"; same meaning |
| 7 | Pokémon Flute (A1a 064) x1 | trainer type | Item | Item | same |
| | | text | "Put a Basic Pokémon from your opponent's discard pile onto their Bench." | identical | same |
| 8 | Lucky Ice Pop (B2 145) x1 | trainer type | Item | Item | same |
| | | text | "Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile." | identical | same |
| 9 | Small Balloon (B3b 064) x1 | trainer type | Tool | Tool | same |
| | | text | "The Retreat Cost of the Basic Pokémon this card is attached to is 1 less." | identical | same |
| 10 | Professor's Research (P-A 007) x2 | trainer type | Supporter | Supporter | same |
| | | text | "Draw 2 cards." | identical | same |
| 11 | Cynthia (A2 152) x1 | trainer type | Supporter | Supporter | same |
| | | text | "During this turn, attacks used by your Garchomp or Togekiss do +50 damage to your opponent's Active Pokémon." | identical | same |
| 12 | Copycat (B1 225) x1 | trainer type | Supporter | Supporter | same |
| | | text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | identical | same |
| 13 | Wally (B4 153) x1 | trainer type | Supporter | Supporter | same |
| | | text | "Take a [C] Energy from your Energy Zone and attach it to 1 of your Stage 2 Pokémon." | identical | same |
| 14 | Mesagoza (B2a 093) x1 | trainer type | Stadium | Stadium | same |
| | | text | "Once during each player's turn, that player may flip a coin. If heads, that player puts a random Pokémon from their deck into their hand." | identical | same |
| 15 | Rainbow Cave (B4 155) x1 | trainer type | Stadium | Stadium | same |
| | | text | "Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced." | identical | same |

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball (P-A 005) | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | low (wording; "a" vs "1", same meaning) |

No high-severity mismatch: every HP, type, stage, evolves-from, weakness, retreat cost, attack cost, damage, effect, ability and Trainer
subtype matched. In particular Garchomp's Land Crush cost is Water + Fighting + Colorless on both sides (the deck's energy line is
Water, Fighting), and Gabite's Linear Attack has no printed damage on either side (the 50 lives in the effect).

## Coverage flags (goldfish --coverage, k3's fallbacks)

Every card: engine_status "Fully implemented", engine_complete true, limitations [] (so no "engine limitation" and no "not implemented" flags).

| Card | Flag class | Detail |
|---|---|---|
| Copycat (B1 225) | unpriced text rule | its effect (text names the opponent's hand: k3 prices this with a fallback) |
| Garchomp (B4a 054) | pays off on the opponent's turn | ability Mach Stealth (protection during the opponent's next turn; k3 never searches that turn) |

No card was flagged printed-damage estimator. Linear Attack's text ("does 50 damage to 1 of your opponent's Pokémon") does count as
damage-changing in goldfish's check, but its effect is mapped to a mechanic in the estimator's priced list, so it is not flagged.
Land Crush, Smack, Gnaw and Hungrily Draw have no effect on their own damage.

## Unverified

None. All 15 cards had an engine record and a Limitless page at the expected set/number, with matching names.
