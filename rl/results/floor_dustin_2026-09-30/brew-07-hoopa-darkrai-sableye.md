# Floor check: brew-07-hoopa-darkrai-sableye

**Verdict: clears the floor.** 1168 wins in 1920 games (60.83%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Mega Sableye ex as attacker: used on 1088 of 1195 opportunities (91.0%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 88/240 = 37%
- t-vespiquen: 119/240 = 50%
- t-lucario: 140/240 = 58%
- t-suicune: 142/240 = 59%
- t-blaziken: 143/240 = 60%
- t-hydreigon: 167/240 = 70%
- t-weezing: 183/240 = 76%
- t-altaria: 186/240 = 78%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Mega Sableye ex (B3b 041) | attacker (default from the flag) | Cursed Jewel: DamageAndCardEffect estimated at printed damage (k's damage estimate); attack Cursed Jewel: pays off during the opponent's turn, which the search doesn't play out | 1195 | 1088 | 91.0% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 934 | 63% / 73% / 82% | 62% / 73% / 82% | 0.46 | 11% | 0% | 0.80 | 55% |
| went second | 986 | 72% / 79% / 86% | 72% / 79% / 85% | 0.39 | 11% | 0% | 0.75 | 67% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Hoopa ex. Draws: 10.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `brew-07-hoopa-darkrai-sableye_coverage.json`. Per-game records: `brew-07-hoopa-darkrai-sableye_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 89 / 28 / 3
  - t-altaria, deck in seat 1: 23 / 97 / 0
  - t-blaziken, deck in seat 0: 73 / 47 / 0
  - t-blaziken, deck in seat 1: 50 / 70 / 0
  - t-hydreigon, deck in seat 0: 79 / 40 / 1
  - t-hydreigon, deck in seat 1: 32 / 88 / 0
  - t-lucario, deck in seat 0: 64 / 55 / 1
  - t-lucario, deck in seat 1: 41 / 76 / 3
  - t-sceptile, deck in seat 0: 46 / 74 / 0
  - t-sceptile, deck in seat 1: 78 / 42 / 0
  - t-suicune, deck in seat 0: 64 / 56 / 0
  - t-suicune, deck in seat 1: 41 / 78 / 1
  - t-vespiquen, deck in seat 0: 56 / 63 / 1
  - t-vespiquen, deck in seat 1: 57 / 63 / 0
  - t-weezing, deck in seat 0: 93 / 27 / 0
  - t-weezing, deck in seat 1: 30 / 90 / 0
