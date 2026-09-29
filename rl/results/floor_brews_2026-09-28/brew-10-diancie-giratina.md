# Floor check: brew-10-diancie-giratina

**Verdict: clears the floor.** 779 wins in 1920 games (40.57%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): none. A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-weezing: 49/240 = 20%
- t-suicune: 65/240 = 27%
- t-blaziken: 85/240 = 35%
- t-vespiquen: 103/240 = 43%
- t-altaria: 107/240 = 45%
- t-hydreigon: 115/240 = 48%
- t-lucario: 125/240 = 52%
- t-sceptile: 130/240 = 54%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| (none) | | | | | |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 936 | 0% / 39% / 66% | 0% / 39% / 65% | 1.03 | 29% | 0% | 1.16 | 41% |
| went second | 984 | 0% / 56% / 65% | 0% / 53% / 62% | 1.08 | 36% | 0% | 1.05 | 40% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Giratina ex. Draws: 5.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-10-diancie-giratina_coverage.json`. Per-game records: `brew-10-diancie-giratina_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 48 / 70 / 2
  - t-altaria, deck in seat 1: 61 / 59 / 0
  - t-blaziken, deck in seat 0: 44 / 76 / 0
  - t-blaziken, deck in seat 1: 78 / 41 / 1
  - t-hydreigon, deck in seat 0: 62 / 58 / 0
  - t-hydreigon, deck in seat 1: 67 / 53 / 0
  - t-lucario, deck in seat 0: 54 / 66 / 0
  - t-lucario, deck in seat 1: 49 / 71 / 0
  - t-sceptile, deck in seat 0: 66 / 53 / 1
  - t-sceptile, deck in seat 1: 56 / 64 / 0
  - t-suicune, deck in seat 0: 28 / 92 / 0
  - t-suicune, deck in seat 1: 83 / 37 / 0
  - t-vespiquen, deck in seat 0: 52 / 68 / 0
  - t-vespiquen, deck in seat 1: 68 / 51 / 1
  - t-weezing, deck in seat 0: 22 / 98 / 0
  - t-weezing, deck in seat 1: 93 / 27 / 0
