# Floor check: brew-06-pyukumuku-silvally-payback

**Verdict: fail.** 124 wins in 1920 games (6.46%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Pyukumuku as bench piece/passive ability: used on 2341 of 4071 opportunities (57.5%); Rocky Helmet as Trainer (played): used on 1439 of 1593 opportunities (90.3%); Silvally as attacker: used on 587 of 589 opportunities (99.7%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 4/240 = 2%
- t-blaziken: 8/240 = 3%
- t-hydreigon: 14/240 = 6%
- t-altaria: 15/240 = 6%
- t-suicune: 16/240 = 7%
- t-weezing: 16/240 = 7%
- t-lucario: 20/240 = 8%
- t-vespiquen: 31/240 = 13%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Pyukumuku (A3 054) | bench piece/passive ability (set for this deck) | ability Innards Out: pays off during the opponent's turn, which the search doesn't play out | 4071 | 2341 | 57.5% |
| Rocky Helmet (A2 148) | Trainer (played) (set for this deck) | its effect: pays off during the opponent's turn, which the search doesn't play out | 1593 | 1439 | 90.3% |
| Silvally (B4 144) | attacker (set for this deck) | Gold Breaker: ExtraDamageIfEx estimated at printed damage (k's damage estimate) | 589 | 587 | 99.7% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 965 | 0% / 0% / 16% | 0% / 0% / 11% | 2.50 | 76% | 0% | 1.38 | 3% |
| went second | 955 | 0% / 33% / 43% | 0% / 27% / 36% | 1.96 | 58% | 0% | 1.21 | 10% |

Main attackers for these measures (the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)): Silvally, Team Rocket's Mewtwo. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-06-pyukumuku-silvally-payback_coverage.json`. Per-game records: `brew-06-pyukumuku-silvally-payback_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 9 / 111 / 0
  - t-altaria, deck in seat 1: 114 / 6 / 0
  - t-blaziken, deck in seat 0: 6 / 114 / 0
  - t-blaziken, deck in seat 1: 118 / 2 / 0
  - t-hydreigon, deck in seat 0: 5 / 115 / 0
  - t-hydreigon, deck in seat 1: 111 / 9 / 0
  - t-lucario, deck in seat 0: 8 / 112 / 0
  - t-lucario, deck in seat 1: 107 / 12 / 1
  - t-sceptile, deck in seat 0: 2 / 118 / 0
  - t-sceptile, deck in seat 1: 118 / 2 / 0
  - t-suicune, deck in seat 0: 4 / 116 / 0
  - t-suicune, deck in seat 1: 108 / 12 / 0
  - t-vespiquen, deck in seat 0: 15 / 105 / 0
  - t-vespiquen, deck in seat 1: 104 / 16 / 0
  - t-weezing, deck in seat 0: 5 / 115 / 0
  - t-weezing, deck in seat 1: 109 / 11 / 0
