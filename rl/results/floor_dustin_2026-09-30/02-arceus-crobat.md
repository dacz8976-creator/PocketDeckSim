# Floor check: 02-arceus-crobat

**Verdict: clears the floor.** 579 wins in 1920 games (30.16%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Lucky Egg as Trainer (played): used on 1192 of 2137 opportunities (55.8%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-suicune: 45/240 = 19%
- t-lucario: 46/240 = 19%
- t-weezing: 64/240 = 27%
- t-sceptile: 67/240 = 28%
- t-hydreigon: 70/240 = 29%
- t-vespiquen: 82/240 = 34%
- t-blaziken: 87/240 = 36%
- t-altaria: 118/240 = 49%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Lucky Egg (B3 148) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 2137 | 1192 | 55.8% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 936 | 0% / 0% / 14% | 0% / 0% / 14% | 2.06 | 56% | 47% | 1.59 | 29% |
| went second | 984 | 0% / 25% / 46% | 0% / 25% / 46% | 1.61 | 36% | 44% | 1.53 | 31% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Arceus ex. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `02-arceus-crobat_coverage.json`. Per-game records: `02-arceus-crobat_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 60 / 60 / 0
  - t-altaria, deck in seat 1: 62 / 58 / 0
  - t-blaziken, deck in seat 0: 50 / 70 / 0
  - t-blaziken, deck in seat 1: 82 / 37 / 1
  - t-hydreigon, deck in seat 0: 35 / 85 / 0
  - t-hydreigon, deck in seat 1: 85 / 35 / 0
  - t-lucario, deck in seat 0: 20 / 100 / 0
  - t-lucario, deck in seat 1: 94 / 26 / 0
  - t-sceptile, deck in seat 0: 35 / 85 / 0
  - t-sceptile, deck in seat 1: 88 / 32 / 0
  - t-suicune, deck in seat 0: 20 / 100 / 0
  - t-suicune, deck in seat 1: 95 / 25 / 0
  - t-vespiquen, deck in seat 0: 34 / 86 / 0
  - t-vespiquen, deck in seat 1: 72 / 48 / 0
  - t-weezing, deck in seat 0: 33 / 87 / 0
  - t-weezing, deck in seat 1: 89 / 31 / 0
