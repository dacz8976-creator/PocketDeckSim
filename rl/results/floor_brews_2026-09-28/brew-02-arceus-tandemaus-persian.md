# Floor check: brew-02-arceus-tandemaus-persian

**Verdict: fail.** 273 wins in 1920 games (14.22%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Maushold as attacker: used on 2185 of 2305 opportunities (94.8%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-weezing: 12/240 = 5%
- t-suicune: 15/240 = 6%
- t-lucario: 26/240 = 11%
- t-hydreigon: 30/240 = 12%
- t-vespiquen: 32/240 = 13%
- t-blaziken: 42/240 = 18%
- t-sceptile: 47/240 = 20%
- t-altaria: 69/240 = 29%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Maushold (B2 143) | attacker (default from the flag) | Family Beatdown: CoinFlipPerPokemonInPlay estimated at printed damage (k's damage estimate) | 2305 | 2185 | 94.8% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 966 | 0% / 0% / 13% | 0% / 0% / 13% | 2.53 | 75% | 0% | 1.54 | 10% |
| went second | 954 | 0% / 26% / 31% | 0% / 26% / 31% | 1.96 | 56% | 0% | 1.63 | 18% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Arceus ex. Draws: 2.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-02-arceus-tandemaus-persian_coverage.json`. Per-game records: `brew-02-arceus-tandemaus-persian_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 31 / 89 / 0
  - t-altaria, deck in seat 1: 82 / 38 / 0
  - t-blaziken, deck in seat 0: 15 / 104 / 1
  - t-blaziken, deck in seat 1: 92 / 27 / 1
  - t-hydreigon, deck in seat 0: 18 / 102 / 0
  - t-hydreigon, deck in seat 1: 108 / 12 / 0
  - t-lucario, deck in seat 0: 12 / 108 / 0
  - t-lucario, deck in seat 1: 106 / 14 / 0
  - t-sceptile, deck in seat 0: 21 / 99 / 0
  - t-sceptile, deck in seat 1: 94 / 26 / 0
  - t-suicune, deck in seat 0: 9 / 111 / 0
  - t-suicune, deck in seat 1: 114 / 6 / 0
  - t-vespiquen, deck in seat 0: 15 / 105 / 0
  - t-vespiquen, deck in seat 1: 103 / 17 / 0
  - t-weezing, deck in seat 0: 6 / 114 / 0
  - t-weezing, deck in seat 1: 114 / 6 / 0
