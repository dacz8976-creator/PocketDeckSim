# Floor check: 15-jolteon-oricorio-raticate

**Verdict: clears the floor.** 698 wins in 1920 games (36.35%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Team Rocket's Goo-zooka as Trainer (played): used on 175 of 4590 opportunities (3.8%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-lucario: 66/240 = 28%
- t-sceptile: 71/240 = 30%
- t-altaria: 89/240 = 37%
- t-weezing: 92/240 = 38%
- t-blaziken: 93/240 = 39%
- t-hydreigon: 95/240 = 40%
- t-vespiquen: 95/240 = 40%
- t-suicune: 97/240 = 40%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Team Rocket's Goo-zooka (B4a 068) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 4590 | 175 | 3.8% — under 25% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 924 | 0% / 29% / 44% | 0% / 29% / 44% | 1.39 | 34% | 0% | 1.02 | 36% |
| went second | 996 | 27% / 42% / 56% | 27% / 42% / 56% | 1.28 | 31% | 0% | 1.00 | 37% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Jolteon ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `15-jolteon-oricorio-raticate_coverage.json`. Per-game records: `15-jolteon-oricorio-raticate_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 42 / 78 / 0
  - t-altaria, deck in seat 1: 73 / 47 / 0
  - t-blaziken, deck in seat 0: 46 / 74 / 0
  - t-blaziken, deck in seat 1: 73 / 47 / 0
  - t-hydreigon, deck in seat 0: 46 / 74 / 0
  - t-hydreigon, deck in seat 1: 71 / 49 / 0
  - t-lucario, deck in seat 0: 29 / 91 / 0
  - t-lucario, deck in seat 1: 83 / 37 / 0
  - t-sceptile, deck in seat 0: 38 / 82 / 0
  - t-sceptile, deck in seat 1: 87 / 33 / 0
  - t-suicune, deck in seat 0: 49 / 71 / 0
  - t-suicune, deck in seat 1: 72 / 48 / 0
  - t-vespiquen, deck in seat 0: 54 / 66 / 0
  - t-vespiquen, deck in seat 1: 79 / 41 / 0
  - t-weezing, deck in seat 0: 45 / 75 / 0
  - t-weezing, deck in seat 1: 73 / 47 / 0
