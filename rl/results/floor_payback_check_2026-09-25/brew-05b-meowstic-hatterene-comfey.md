# Floor check: brew-05b-meowstic-hatterene-comfey

**Verdict: clears the floor.** 597 wins in 1920 games (31.09%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Hatterene as attacker: used on 2463 of 2543 opportunities (96.9%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-25/deckgym (the manifest's available release). Pilots: kp3 on the deck, kp3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-hydreigon: 31/240 = 13%
- t-weezing: 48/240 = 20%
- t-vespiquen: 52/240 = 22%
- t-suicune: 53/240 = 22%
- t-sceptile: 54/240 = 22%
- t-blaziken: 94/240 = 39%
- t-altaria: 125/240 = 52%
- t-lucario: 140/240 = 58%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Hatterene (B3 071) | attacker (default from the flag) | Mental Crush: ExtraDamageIfDefenderStatus estimated at printed damage (k's damage estimate) | 2543 | 2463 | 96.9% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 923 | 0% / 18% / 41% | 0% / 18% / 41% | 1.54 | 36% | 51% | 1.32 | 32% |
| went second | 997 | 3% / 24% / 41% | 3% / 24% / 41% | 1.64 | 41% | 45% | 1.28 | 30% |

Main attackers for these measures (the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)): Hatterene. Draws: 2.

## For a second reader

- Coverage from rl/engine-2026-09-25/goldfish (sha256 318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997; the official release; `--games 0 --coverage`): `brew-05b-meowstic-hatterene-comfey_coverage.json`. Per-game records: `brew-05b-meowstic-hatterene-comfey_games.jsonl`.
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 65 / 55 / 0
  - t-altaria, deck in seat 1: 60 / 60 / 0
  - t-blaziken, deck in seat 0: 49 / 71 / 0
  - t-blaziken, deck in seat 1: 73 / 45 / 2
  - t-hydreigon, deck in seat 0: 15 / 105 / 0
  - t-hydreigon, deck in seat 1: 104 / 16 / 0
  - t-lucario, deck in seat 0: 63 / 57 / 0
  - t-lucario, deck in seat 1: 43 / 77 / 0
  - t-sceptile, deck in seat 0: 22 / 98 / 0
  - t-sceptile, deck in seat 1: 88 / 32 / 0
  - t-suicune, deck in seat 0: 28 / 92 / 0
  - t-suicune, deck in seat 1: 95 / 25 / 0
  - t-vespiquen, deck in seat 0: 24 / 96 / 0
  - t-vespiquen, deck in seat 1: 92 / 28 / 0
  - t-weezing, deck in seat 0: 25 / 95 / 0
  - t-weezing, deck in seat 1: 97 / 23 / 0
