# Floor check: 10-xatu-oricorio-tr-weezing

**Verdict: fail.** 324 wins in 1920 games (16.88%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Poison Barb as Trainer (played): used on 2513 of 3686 opportunities (68.2%); Xatu as attacker: used on 981 of 1050 opportunities (93.4%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-weezing: 8/240 = 3%
- t-suicune: 13/240 = 5%
- t-vespiquen: 29/240 = 12%
- t-hydreigon: 33/240 = 14%
- t-sceptile: 38/240 = 16%
- t-blaziken: 54/240 = 22%
- t-altaria: 56/240 = 23%
- t-lucario: 93/240 = 39%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Poison Barb (A3 146) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3686 | 2513 | 68.2% |
| Xatu (A4 082) | attacker (default from the flag) | Life Drain: CoinFlipSetOpponentActiveRemainingHp estimated at printed damage (k's damage estimate) | 1050 | 981 | 93.4% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 924 | 0% / 0% / 0% | 0% / 0% / 0% | 2.76 | 100% | 0% | 1.01 | 14% |
| went second | 996 | 0% / 0% / 0% | 0% / 0% / 0% | 2.63 | 100% | 0% | 0.91 | 20% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Team Rocket's Weezing ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `10-xatu-oricorio-tr-weezing_coverage.json`. Per-game records: `10-xatu-oricorio-tr-weezing_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 35 / 85 / 0
  - t-altaria, deck in seat 1: 99 / 21 / 0
  - t-blaziken, deck in seat 0: 29 / 91 / 0
  - t-blaziken, deck in seat 1: 95 / 25 / 0
  - t-hydreigon, deck in seat 0: 18 / 102 / 0
  - t-hydreigon, deck in seat 1: 105 / 15 / 0
  - t-lucario, deck in seat 0: 45 / 75 / 0
  - t-lucario, deck in seat 1: 72 / 48 / 0
  - t-sceptile, deck in seat 0: 17 / 103 / 0
  - t-sceptile, deck in seat 1: 99 / 21 / 0
  - t-suicune, deck in seat 0: 8 / 112 / 0
  - t-suicune, deck in seat 1: 115 / 5 / 0
  - t-vespiquen, deck in seat 0: 13 / 107 / 0
  - t-vespiquen, deck in seat 1: 104 / 16 / 0
  - t-weezing, deck in seat 0: 2 / 118 / 0
  - t-weezing, deck in seat 1: 114 / 6 / 0
