# Floor check: 04-absol-hoopa-darkrai

**Verdict: clears the floor.** 627 wins in 1920 games (32.66%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Absol as attacker: used on 659 of 855 opportunities (77.1%); Happiny as attacker: used on 316 of 824 opportunities (38.3%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 42/240 = 18%
- t-suicune: 47/240 = 20%
- t-vespiquen: 59/240 = 25%
- t-weezing: 76/240 = 32%
- t-blaziken: 84/240 = 35%
- t-hydreigon: 90/240 = 38%
- t-lucario: 104/240 = 43%
- t-altaria: 125/240 = 52%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Absol (B4 100) | attacker (default from the flag) | Enhanced Blade: ExtraDamageIfToolAttached estimated at printed damage (k's damage estimate) | 855 | 659 | 77.1% |
| Happiny (B4a 063) | attacker (default from the flag) | Chubby Cheer: IncreasedDamageNextTurn estimated at printed damage (k's damage estimate) | 824 | 316 | 38.3% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 939 | 63% / 77% / 84% | 63% / 76% / 84% | 0.53 | 9% | 0% | 1.05 | 28% |
| went second | 981 | 69% / 78% / 85% | 68% / 78% / 85% | 0.53 | 12% | 0% | 0.91 | 37% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Hoopa ex. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `04-absol-hoopa-darkrai_coverage.json`. Per-game records: `04-absol-hoopa-darkrai_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 67 / 53 / 0
  - t-altaria, deck in seat 1: 62 / 58 / 0
  - t-blaziken, deck in seat 0: 40 / 80 / 0
  - t-blaziken, deck in seat 1: 76 / 44 / 0
  - t-hydreigon, deck in seat 0: 43 / 77 / 0
  - t-hydreigon, deck in seat 1: 73 / 47 / 0
  - t-lucario, deck in seat 0: 44 / 76 / 0
  - t-lucario, deck in seat 1: 60 / 60 / 0
  - t-sceptile, deck in seat 0: 23 / 97 / 0
  - t-sceptile, deck in seat 1: 101 / 19 / 0
  - t-suicune, deck in seat 0: 26 / 94 / 0
  - t-suicune, deck in seat 1: 99 / 21 / 0
  - t-vespiquen, deck in seat 0: 29 / 91 / 0
  - t-vespiquen, deck in seat 1: 90 / 30 / 0
  - t-weezing, deck in seat 0: 39 / 81 / 0
  - t-weezing, deck in seat 1: 82 / 37 / 1
