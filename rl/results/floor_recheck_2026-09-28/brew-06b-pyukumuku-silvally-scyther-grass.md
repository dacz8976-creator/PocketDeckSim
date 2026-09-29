# Floor check: brew-06b-pyukumuku-silvally-scyther-grass

**Verdict: fail.** 259 wins in 1920 games (13.49%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Pyukumuku as bench piece/passive ability: used on 2195 of 3303 opportunities (66.5%); Rocky Helmet as Trainer (played): used on 1293 of 2071 opportunities (62.4%); Silvally as attacker: used on 591 of 598 opportunities (98.8%); Team Rocket's Scyther as attacker: used on 178 of 184 opportunities (96.7%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 5/240 = 2%
- t-blaziken: 16/240 = 7%
- t-lucario: 26/240 = 11%
- t-suicune: 27/240 = 11%
- t-hydreigon: 30/240 = 12%
- t-altaria: 49/240 = 20%
- t-vespiquen: 53/240 = 22%
- t-weezing: 53/240 = 22%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Pyukumuku (A3 054) | bench piece/passive ability (set for this deck) | ability Innards Out: pays off during the opponent's turn, which the search doesn't play out | 3303 | 2195 | 66.5% |
| Rocky Helmet (A2 148) | Trainer (played) (set for this deck) | its effect: pays off during the opponent's turn, which the search doesn't play out | 2071 | 1293 | 62.4% |
| Silvally (B4 144) | attacker (set for this deck) | Gold Breaker: ExtraDamageIfEx estimated at printed damage (k's damage estimate) | 598 | 591 | 98.8% |
| Team Rocket's Scyther (P-B 088) | attacker (set for this deck) | Second Strike: ExtraDamageIfHurt estimated at printed damage (k's damage estimate) | 184 | 178 | 96.7% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 965 | 0% / 3% / 9% | 0% / 3% / 9% | 2.71 | 83% | 0% | 1.37 | 11% |
| went second | 955 | 5% / 23% / 31% | 5% / 23% / 31% | 2.13 | 63% | 0% | 1.32 | 16% |

Main attackers for these measures (the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)): Silvally, Team Rocket's Scyther. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-06b-pyukumuku-silvally-scyther-grass_coverage.json`. Per-game records: `brew-06b-pyukumuku-silvally-scyther-grass_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 21 / 99 / 0
  - t-altaria, deck in seat 1: 92 / 28 / 0
  - t-blaziken, deck in seat 0: 7 / 113 / 0
  - t-blaziken, deck in seat 1: 111 / 9 / 0
  - t-hydreigon, deck in seat 0: 15 / 105 / 0
  - t-hydreigon, deck in seat 1: 105 / 15 / 0
  - t-lucario, deck in seat 0: 9 / 111 / 0
  - t-lucario, deck in seat 1: 103 / 17 / 0
  - t-sceptile, deck in seat 0: 3 / 117 / 0
  - t-sceptile, deck in seat 1: 118 / 2 / 0
  - t-suicune, deck in seat 0: 13 / 107 / 0
  - t-suicune, deck in seat 1: 106 / 14 / 0
  - t-vespiquen, deck in seat 0: 23 / 97 / 0
  - t-vespiquen, deck in seat 1: 90 / 30 / 0
  - t-weezing, deck in seat 0: 21 / 99 / 0
  - t-weezing, deck in seat 1: 88 / 32 / 0
