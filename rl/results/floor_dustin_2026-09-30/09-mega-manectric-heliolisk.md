# Floor check: 09-mega-manectric-heliolisk

**Verdict: clears the floor.** 1124 wins in 1920 games (58.54%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): none. A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-lucario: 110/240 = 46%
- t-sceptile: 114/240 = 48%
- t-weezing: 116/240 = 48%
- t-blaziken: 140/240 = 58%
- t-suicune: 154/240 = 64%
- t-altaria: 155/240 = 65%
- t-hydreigon: 155/240 = 65%
- t-vespiquen: 180/240 = 75%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| (none) | | | | | |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 908 | 0% / 17% / 42% | 0% / 17% / 41% | 1.28 | 40% | 0% | 0.83 | 56% |
| went second | 1012 | 25% / 44% / 59% | 25% / 43% / 59% | 1.06 | 34% | 0% | 0.81 | 61% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Mega Manectric ex. Draws: 2.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `09-mega-manectric-heliolisk_coverage.json`. Per-game records: `09-mega-manectric-heliolisk_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 77 / 43 / 0
  - t-altaria, deck in seat 1: 42 / 78 / 0
  - t-blaziken, deck in seat 0: 70 / 50 / 0
  - t-blaziken, deck in seat 1: 50 / 70 / 0
  - t-hydreigon, deck in seat 0: 81 / 39 / 0
  - t-hydreigon, deck in seat 1: 46 / 74 / 0
  - t-lucario, deck in seat 0: 49 / 71 / 0
  - t-lucario, deck in seat 1: 59 / 61 / 0
  - t-sceptile, deck in seat 0: 60 / 60 / 0
  - t-sceptile, deck in seat 1: 66 / 54 / 0
  - t-suicune, deck in seat 0: 71 / 49 / 0
  - t-suicune, deck in seat 1: 37 / 83 / 0
  - t-vespiquen, deck in seat 0: 93 / 27 / 0
  - t-vespiquen, deck in seat 1: 33 / 87 / 0
  - t-weezing, deck in seat 0: 62 / 56 / 2
  - t-weezing, deck in seat 1: 66 / 54 / 0
