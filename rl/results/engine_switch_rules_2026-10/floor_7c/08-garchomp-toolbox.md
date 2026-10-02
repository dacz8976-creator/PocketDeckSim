# Floor check: 08-garchomp-toolbox

**Verdict: clears the floor.** 500 wins in 1920 games (26.04%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Garchomp as bench piece/passive ability: used on 1417 of 1541 opportunities (92.0%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: ../../../../../../../home/dacz8976/engine-rules-5a18d31/engine/target/release/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-weezing: 30/240 = 12%
- t-blaziken: 42/240 = 18%
- t-hydreigon: 44/240 = 18%
- t-sceptile: 56/240 = 23%
- t-suicune: 57/240 = 24%
- t-lucario: 80/240 = 33%
- t-altaria: 95/240 = 40%
- t-vespiquen: 96/240 = 40%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Garchomp (B4a 054) | bench piece/passive ability (default from the flag) | ability Mach Stealth: pays off during the opponent's turn, which the search doesn't play out | 1541 | 1417 | 92.0% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 929 | 0% / 15% / 37% | 0% / 15% / 37% | 1.91 | 49% | 34% | 2.12 | 25% |
| went second | 991 | 0% / 21% / 36% | 0% / 21% / 36% | 1.91 | 51% | 38% | 2.01 | 27% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Garchomp. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `08-garchomp-toolbox_coverage.json`. Per-game records: `08-garchomp-toolbox_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 45 / 75 / 0
  - t-altaria, deck in seat 1: 70 / 50 / 0
  - t-blaziken, deck in seat 0: 22 / 98 / 0
  - t-blaziken, deck in seat 1: 99 / 20 / 1
  - t-hydreigon, deck in seat 0: 22 / 98 / 0
  - t-hydreigon, deck in seat 1: 98 / 22 / 0
  - t-lucario, deck in seat 0: 33 / 87 / 0
  - t-lucario, deck in seat 1: 73 / 47 / 0
  - t-sceptile, deck in seat 0: 31 / 89 / 0
  - t-sceptile, deck in seat 1: 95 / 25 / 0
  - t-suicune, deck in seat 0: 26 / 94 / 0
  - t-suicune, deck in seat 1: 89 / 31 / 0
  - t-vespiquen, deck in seat 0: 52 / 68 / 0
  - t-vespiquen, deck in seat 1: 76 / 44 / 0
  - t-weezing, deck in seat 0: 17 / 103 / 0
  - t-weezing, deck in seat 1: 107 / 13 / 0
