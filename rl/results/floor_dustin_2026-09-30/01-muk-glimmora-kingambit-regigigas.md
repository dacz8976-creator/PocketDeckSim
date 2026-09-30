# Floor check: 01-muk-glimmora-kingambit-regigigas

**Verdict: fail.** 307 wins in 1920 games (15.99%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Kingambit as attacker: used on 775 of 776 opportunities (99.9%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-suicune: 23/240 = 10%
- t-blaziken: 25/240 = 10%
- t-sceptile: 25/240 = 10%
- t-lucario: 29/240 = 12%
- t-weezing: 29/240 = 12%
- t-hydreigon: 51/240 = 21%
- t-vespiquen: 55/240 = 23%
- t-altaria: 70/240 = 29%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Kingambit (B3a 043) | attacker (default from the flag) | Overlord's Blade: ExtraDamagePerOwnKnockoutThisGame estimated at printed damage (k's damage estimate) | 776 | 775 | 99.9% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 958 | 0% / 0% / 7% | 0% / 0% / 7% | 2.25 | 75% | 14% | 1.72 | 16% |
| went second | 962 | 0% / 6% / 14% | 0% / 6% / 14% | 2.22 | 73% | 14% | 1.73 | 16% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Regigigas. Draws: 2.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `01-muk-glimmora-kingambit-regigigas_coverage.json`. Per-game records: `01-muk-glimmora-kingambit-regigigas_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 39 / 81 / 0
  - t-altaria, deck in seat 1: 89 / 31 / 0
  - t-blaziken, deck in seat 0: 8 / 111 / 1
  - t-blaziken, deck in seat 1: 103 / 17 / 0
  - t-hydreigon, deck in seat 0: 21 / 99 / 0
  - t-hydreigon, deck in seat 1: 90 / 30 / 0
  - t-lucario, deck in seat 0: 16 / 104 / 0
  - t-lucario, deck in seat 1: 107 / 13 / 0
  - t-sceptile, deck in seat 0: 13 / 107 / 0
  - t-sceptile, deck in seat 1: 108 / 12 / 0
  - t-suicune, deck in seat 0: 12 / 108 / 0
  - t-suicune, deck in seat 1: 109 / 11 / 0
  - t-vespiquen, deck in seat 0: 28 / 92 / 0
  - t-vespiquen, deck in seat 1: 93 / 27 / 0
  - t-weezing, deck in seat 0: 16 / 104 / 0
  - t-weezing, deck in seat 1: 106 / 13 / 1
