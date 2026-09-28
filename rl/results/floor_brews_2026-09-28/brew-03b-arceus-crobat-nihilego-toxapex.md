# Floor check: brew-03b-arceus-crobat-nihilego-toxapex

**Verdict: borderline.** 397 wins in 1920 games (20.68%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Mareanie as attacker: used on 111 of 124 opportunities (89.5%); Team Rocket's Goo-zooka as Trainer (played): used on 95 of 4445 opportunities (2.1%); Toxapex as attacker: used on 426 of 493 opportunities (86.4%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-lucario: 31/240 = 13%
- t-suicune: 35/240 = 15%
- t-weezing: 36/240 = 15%
- t-hydreigon: 45/240 = 19%
- t-vespiquen: 48/240 = 20%
- t-sceptile: 53/240 = 22%
- t-blaziken: 66/240 = 28%
- t-altaria: 83/240 = 35%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Mareanie (B3b 046) | attacker (default from the flag) | Venoshock: ExtraDamageIfDefenderStatus estimated at printed damage (k's damage estimate) | 124 | 111 | 89.5% |
| Team Rocket's Goo-zooka (B4a 068) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 4445 | 95 | 2.1% — under 25% |
| Toxapex (B3b 047) | attacker (default from the flag) | Severe Poison: InflictPoisonWithCustomCheckupDamage estimated at printed damage (k's damage estimate) | 493 | 426 | 86.4% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 965 | 0% / 0% / 16% | 0% / 0% / 16% | 2.40 | 67% | 32% | 2.24 | 18% |
| went second | 955 | 0% / 24% / 35% | 0% / 24% / 35% | 1.89 | 51% | 43% | 2.15 | 23% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Arceus ex. Draws: 5.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-03b-arceus-crobat-nihilego-toxapex_coverage.json`. Per-game records: `brew-03b-arceus-crobat-nihilego-toxapex_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 40 / 80 / 0
  - t-altaria, deck in seat 1: 77 / 43 / 0
  - t-blaziken, deck in seat 0: 37 / 81 / 2
  - t-blaziken, deck in seat 1: 88 / 29 / 3
  - t-hydreigon, deck in seat 0: 19 / 101 / 0
  - t-hydreigon, deck in seat 1: 94 / 26 / 0
  - t-lucario, deck in seat 0: 12 / 108 / 0
  - t-lucario, deck in seat 1: 101 / 19 / 0
  - t-sceptile, deck in seat 0: 26 / 94 / 0
  - t-sceptile, deck in seat 1: 93 / 27 / 0
  - t-suicune, deck in seat 0: 16 / 104 / 0
  - t-suicune, deck in seat 1: 101 / 19 / 0
  - t-vespiquen, deck in seat 0: 27 / 93 / 0
  - t-vespiquen, deck in seat 1: 99 / 21 / 0
  - t-weezing, deck in seat 0: 21 / 99 / 0
  - t-weezing, deck in seat 1: 105 / 15 / 0
