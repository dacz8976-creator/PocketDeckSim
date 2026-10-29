# Floor check: 12-ariados-whimsicott-ogerpon

**Verdict: clears the floor.** 635 wins in 1920 games (33.07%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Team Rocket's Goo-zooka as Trainer (played): used on 1827 of 5408 opportunities (33.8%); Whimsicott ex as attacker: used on 2134 of 2164 opportunities (98.6%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: ../pincand_work/programs/R/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-blaziken: 42/240 = 18%
- t-lucario: 58/240 = 24%
- t-sceptile: 66/240 = 28%
- t-vespiquen: 76/240 = 32%
- t-suicune: 77/240 = 32%
- t-hydreigon: 81/240 = 34%
- t-altaria: 113/240 = 47%
- t-weezing: 122/240 = 51%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Team Rocket's Goo-zooka (B4a 068) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 5408 | 1827 | 33.8% |
| Whimsicott ex (B1 016) | attacker (default from the flag) | Grass Knot: ExtraDamagePerRetreatCost estimated at printed damage (k's damage estimate) | 2164 | 2134 | 98.6% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 923 | 0% / 26% / 35% | 0% / 26% / 35% | 1.64 | 58% | 0% | 1.00 | 27% |
| went second | 997 | 28% / 41% / 46% | 28% / 40% / 46% | 1.28 | 50% | 0% | 1.00 | 38% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Teal Mask Ogerpon ex. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-10-21/goldfish (sha256 db52d3de65ca2577aa39af7539635a1473d4f876842bd711131a3b2c7d797f31; the official release; `--games 0 --coverage`): `12-ariados-whimsicott-ogerpon_coverage.json`. Per-game records: `12-ariados-whimsicott-ogerpon_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 62 / 58 / 0
  - t-altaria, deck in seat 1: 69 / 51 / 0
  - t-blaziken, deck in seat 0: 21 / 98 / 1
  - t-blaziken, deck in seat 1: 99 / 21 / 0
  - t-hydreigon, deck in seat 0: 39 / 81 / 0
  - t-hydreigon, deck in seat 1: 78 / 42 / 0
  - t-lucario, deck in seat 0: 32 / 88 / 0
  - t-lucario, deck in seat 1: 94 / 26 / 0
  - t-sceptile, deck in seat 0: 29 / 91 / 0
  - t-sceptile, deck in seat 1: 83 / 37 / 0
  - t-suicune, deck in seat 0: 38 / 82 / 0
  - t-suicune, deck in seat 1: 81 / 39 / 0
  - t-vespiquen, deck in seat 0: 32 / 88 / 0
  - t-vespiquen, deck in seat 1: 76 / 44 / 0
  - t-weezing, deck in seat 0: 60 / 60 / 0
  - t-weezing, deck in seat 1: 58 / 62 / 0
