# Floor check: 12-ariados-whimsicott-ogerpon

**Verdict: clears the floor.** 602 wins in 1920 games (31.35%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Team Rocket's Goo-zooka as Trainer (played): used on 1858 of 5380 opportunities (34.5%); Whimsicott ex as attacker: used on 2151 of 2187 opportunities (98.4%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-blaziken: 37/240 = 15%
- t-lucario: 56/240 = 23%
- t-sceptile: 63/240 = 26%
- t-vespiquen: 66/240 = 28%
- t-suicune: 71/240 = 30%
- t-hydreigon: 75/240 = 31%
- t-altaria: 112/240 = 47%
- t-weezing: 122/240 = 51%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Team Rocket's Goo-zooka (B4a 068) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 5380 | 1858 | 34.5% |
| Whimsicott ex (B1 016) | attacker (default from the flag) | Grass Knot: ExtraDamagePerRetreatCost estimated at printed damage (k's damage estimate) | 2187 | 2151 | 98.4% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 923 | 0% / 26% / 35% | 0% / 26% / 35% | 1.68 | 58% | 0% | 1.00 | 26% |
| went second | 997 | 28% / 41% / 47% | 28% / 40% / 47% | 1.32 | 50% | 0% | 1.00 | 36% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Teal Mask Ogerpon ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `12-ariados-whimsicott-ogerpon_coverage.json`. Per-game records: `12-ariados-whimsicott-ogerpon_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 60 / 60 / 0
  - t-altaria, deck in seat 1: 68 / 52 / 0
  - t-blaziken, deck in seat 0: 19 / 101 / 0
  - t-blaziken, deck in seat 1: 102 / 18 / 0
  - t-hydreigon, deck in seat 0: 37 / 83 / 0
  - t-hydreigon, deck in seat 1: 82 / 38 / 0
  - t-lucario, deck in seat 0: 31 / 89 / 0
  - t-lucario, deck in seat 1: 95 / 25 / 0
  - t-sceptile, deck in seat 0: 28 / 92 / 0
  - t-sceptile, deck in seat 1: 85 / 35 / 0
  - t-suicune, deck in seat 0: 36 / 84 / 0
  - t-suicune, deck in seat 1: 85 / 35 / 0
  - t-vespiquen, deck in seat 0: 27 / 93 / 0
  - t-vespiquen, deck in seat 1: 81 / 39 / 0
  - t-weezing, deck in seat 0: 61 / 59 / 0
  - t-weezing, deck in seat 1: 59 / 61 / 0
