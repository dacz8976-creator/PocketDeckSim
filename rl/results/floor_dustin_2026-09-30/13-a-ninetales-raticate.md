# Floor check: 13-a-ninetales-raticate

**Verdict: clears the floor.** 1068 wins in 1920 games (55.62%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Alolan Ninetales ex as attacker: used on 4251 of 4369 opportunities (97.3%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-altaria: 94/240 = 39%
- t-hydreigon: 110/240 = 46%
- t-weezing: 122/240 = 51%
- t-sceptile: 124/240 = 52%
- t-vespiquen: 139/240 = 58%
- t-lucario: 144/240 = 60%
- t-suicune: 163/240 = 68%
- t-blaziken: 172/240 = 72%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Alolan Ninetales ex (B2 029) | attacker (default from the flag) | attack Binding Snow: pays off during the opponent's turn, which the search doesn't play out | 4369 | 4251 | 97.3% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 908 | 0% / 45% / 67% | 0% / 45% / 67% | 0.87 | 23% | 0% | 0.93 | 57% |
| went second | 1012 | 24% / 46% / 62% | 24% / 46% / 62% | 1.06 | 30% | 0% | 1.06 | 55% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Alolan Ninetales ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `13-a-ninetales-raticate_coverage.json`. Per-game records: `13-a-ninetales-raticate_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 41 / 79 / 0
  - t-altaria, deck in seat 1: 67 / 53 / 0
  - t-blaziken, deck in seat 0: 81 / 39 / 0
  - t-blaziken, deck in seat 1: 29 / 91 / 0
  - t-hydreigon, deck in seat 0: 54 / 66 / 0
  - t-hydreigon, deck in seat 1: 64 / 56 / 0
  - t-lucario, deck in seat 0: 76 / 44 / 0
  - t-lucario, deck in seat 1: 52 / 68 / 0
  - t-sceptile, deck in seat 0: 62 / 58 / 0
  - t-sceptile, deck in seat 1: 58 / 62 / 0
  - t-suicune, deck in seat 0: 87 / 33 / 0
  - t-suicune, deck in seat 1: 44 / 76 / 0
  - t-vespiquen, deck in seat 0: 70 / 50 / 0
  - t-vespiquen, deck in seat 1: 51 / 69 / 0
  - t-weezing, deck in seat 0: 68 / 52 / 0
  - t-weezing, deck in seat 1: 66 / 54 / 0
