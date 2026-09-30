# Floor check: 03-wailord-indeedee-wall

**Verdict: clears the floor.** 1178 wins in 1920 games (61.35%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): none. A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-lucario: 127/240 = 53%
- t-vespiquen: 134/240 = 56%
- t-suicune: 146/240 = 61%
- t-altaria: 148/240 = 62%
- t-sceptile: 149/240 = 62%
- t-hydreigon: 154/240 = 64%
- t-blaziken: 160/240 = 67%
- t-weezing: 160/240 = 67%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| (none) | | | | | |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 908 | 0% / 0% / 0% | 0% / 0% / 0% | 1.41 | 48% | 0% | 1.46 | 60% |
| went second | 1012 | 0% / 0% / 21% | 0% / 0% / 21% | 1.38 | 47% | 0% | 1.36 | 62% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Wailord ex. Draws: 37.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `03-wailord-indeedee-wall_coverage.json`. Per-game records: `03-wailord-indeedee-wall_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 74 / 46 / 0
  - t-altaria, deck in seat 1: 46 / 74 / 0
  - t-blaziken, deck in seat 0: 75 / 45 / 0
  - t-blaziken, deck in seat 1: 35 / 85 / 0
  - t-hydreigon, deck in seat 0: 73 / 47 / 0
  - t-hydreigon, deck in seat 1: 39 / 81 / 0
  - t-lucario, deck in seat 0: 65 / 55 / 0
  - t-lucario, deck in seat 1: 58 / 62 / 0
  - t-sceptile, deck in seat 0: 74 / 46 / 0
  - t-sceptile, deck in seat 1: 45 / 75 / 0
  - t-suicune, deck in seat 0: 73 / 41 / 6
  - t-suicune, deck in seat 1: 37 / 73 / 10
  - t-vespiquen, deck in seat 0: 65 / 48 / 7
  - t-vespiquen, deck in seat 1: 42 / 69 / 9
  - t-weezing, deck in seat 0: 81 / 36 / 3
  - t-weezing, deck in seat 1: 39 / 79 / 2
