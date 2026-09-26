# Card-text check: dustin:charizardy_entei (brew-08-entei-rainbow-cave.txt)

Date: 2026-09-26. Plan B2e, held-out archetype 6 ("Mega Charizard Y ex Entei ex"; the brew's base).

Deck file: `decks/brews/brew-08-entei-rainbow-cave.txt` (Energy: Fire; 20 cards, 13 distinct).

**Sources.** Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`);
Trainer subtype read from the same database's `trainer_card_type` field, since card.py prints only "Trainer".
Real text: the Limitless Pocket card database, `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>`, fetched 2026-09-26.
Coverage: `rl/engine-2026-09-25/goldfish --deck <file> --panel decks/screen/opponents --games 0 --coverage brew08_coverage.json`,
run in WSL with cwd `engine/` (the same invocation `decks/screen/floor.py` uses); goldfish sha256
`318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997` = the official release's. Zero games were played.
Raw output: `brew08_coverage.json` in this folder.

## Summary

- 13 of 13 distinct cards verified against Limitless.
- 0 high-severity mismatches. 1 low (wording only): Poké Ball, engine "a random Basic Pokémon" vs Limitless "1 random Basic Pokemon".
- Coverage flags: 1 card, Copycat (unpriced text rule: its text names the opponent's hand and deck). Every card is
  "Fully implemented" with no engine limitation, no printed-damage estimator flag and no opponent's-turn payoff.
- Nothing unverified.

## Per-card table

| # | Card | Id | Field | Engine (lib/card.py) | Limitless | Result |
|---|---|---|---|---|---|---|
| 2 | Entei ex | A4a 010 | type / stage | Fire, Basic (Stage 0), no evolves-from | Fire, Basic, ex | match |
| | | | HP | 140 | 140 | match |
| | | | weakness | Water | Water | match |
| | | | retreat | 2 (Colorless, Colorless) | 2 | match |
| | | | ability | Legendary Pulse: "At the end of your turn, if this Pokémon is in the Active Spot, draw a card." | Legendary Pulse: same text | match |
| | | | attack | [RR] Blazing Beatdown 60 — "If this Pokémon has at least 2 extra [R] Energy attached, this attack does 60 more damage." | RR, 60+, same effect text | match (60+ is the printed base; the effect adds 60) |
| 2 | Professor's Research | P-A 007 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Draw 2 cards." | "Draw 2 cards." | match |
| 2 | Copycat | B1 225 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same | match |
| 1 | Pokémon Center Lady | A2b 070 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | same | match |
| 1 | Sabrina | A1 225 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | same | match |
| 1 | Cyrus | A2 150 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | same | match |
| 2 | Lucky Ice Pop | B2 145 | Trainer type | Item | Trainer - Item | match |
| | | | text | "Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile." | same | match |
| 2 | Flame Patch | B1 217 | Trainer type | Item | Trainer - Item | match |
| | | | text | "Attach a [R] Energy from your discard pile to your Active [R] Pokémon." | same | match |
| 1 | Repel | A3a 064 | Trainer type | Item | Trainer - Item | match |
| | | | text | "Switch out your opponent's Active Basic Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | same | match |
| 1 | Poké Ball | P-A 005 | Trainer type | Item | Trainer - Item | match |
| | | | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | **low**: "a random" vs "1 random" (wording; same meaning) |
| 2 | Giant Cape | A2 147 | Trainer type | Tool | Trainer - Tool | match |
| | | | text | "The Pokémon this card is attached to gets +20 HP." | same | match |
| 2 | Rainbow Cave | B4 155 | Trainer type | Stadium | Trainer - Stadium | match |
| | | | text | "Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced." | same | match |
| 1 | Starting Plains | B2 154 | Trainer type | Stadium | Trainer - Stadium | match |
| | | | text | "Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP." | same | match |

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball (P-A 005) | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | low (wording) |

## Coverage flags (goldfish --coverage, official release)

| Card | Id | Flag class | Detail |
|---|---|---|---|
| Copycat | B1 225 | unpriced text rule | `unpriced_text_rule: ["its effect"]` — the text names the opponent's hand and deck, which k3 leaves unpriced |

All 13 cards: `engine_status` "Fully implemented", `engine_complete` true, `limitations` empty,
`estimator_printed_damage` empty, `pays_off_on_opponent_turn` empty. Cards with no flag: Entei ex, Professor's Research,
Pokémon Center Lady, Sabrina, Cyrus, Lucky Ice Pop, Flame Patch, Repel, Poké Ball, Giant Cape, Rainbow Cave, Starting Plains.

## Unverified

None.

## Notes for a second reader

- The first goldfish attempt used a positional deck path and `--help`; the tool has neither (it panicked with
  `--deck <list.txt>`). The script was corrected to floor.py's form. Script: scratchpad `b2e/coverage_brew08.sh`.
- Limitless renders "Pokemon" without the accent on Poké Ball; that is spelling and not counted.
- Nothing in the repo outside this folder was modified.
