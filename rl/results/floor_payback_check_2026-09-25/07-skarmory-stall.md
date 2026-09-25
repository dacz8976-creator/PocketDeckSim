# Floor check: 07-skarmory-stall

**Verdict: clears the floor.** 908 wins in 1920 games (47.29%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Jasmine as Trainer (played): used on 50 of 3968 opportunities (1.3%); Metal Core Barrier as Trainer (played): used on 2430 of 3054 opportunities (79.6%); Skarmory ex as attacker: used on 7681 of 7681 opportunities (100.0%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-25/deckgym (the manifest's available release). Pilots: kp3 on the deck, kp3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-blaziken: 55/240 = 23%
- t-lucario: 63/240 = 26%
- t-sceptile: 69/240 = 29%
- t-vespiquen: 110/240 = 46%
- t-weezing: 140/240 = 58%
- t-altaria: 147/240 = 61%
- t-hydreigon: 155/240 = 65%
- t-suicune: 169/240 = 70%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Jasmine (A4 160) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3968 | 50 | 1.3% — under 25% |
| Metal Core Barrier (B2 148) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3054 | 2430 | 79.6% |
| Skarmory ex (A4 124) | attacker (default from the flag) | attack Steel Wing: pays off during the opponent's turn, which the search doesn't play out | 7681 | 7681 | 100.0% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 935 | 0% / 59% / 85% | 0% / 59% / 85% | 0.44 | 8% | 0% | 0.83 | 42% |
| went second | 985 | 62% / 87% / 92% | 62% / 87% / 92% | 0.25 | 5% | 0% | 0.71 | 52% |

Main attackers for these measures (the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)): Skarmory ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-25/goldfish (sha256 318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997; the official release; `--games 0 --coverage`): `07-skarmory-stall_coverage.json`. Per-game records: `07-skarmory-stall_games.jsonl`.
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 78 / 42 / 0
  - t-altaria, deck in seat 1: 51 / 69 / 0
  - t-blaziken, deck in seat 0: 29 / 91 / 0
  - t-blaziken, deck in seat 1: 94 / 26 / 0
  - t-hydreigon, deck in seat 0: 78 / 42 / 0
  - t-hydreigon, deck in seat 1: 43 / 77 / 0
  - t-lucario, deck in seat 0: 33 / 87 / 0
  - t-lucario, deck in seat 1: 90 / 30 / 0
  - t-sceptile, deck in seat 0: 34 / 86 / 0
  - t-sceptile, deck in seat 1: 85 / 35 / 0
  - t-suicune, deck in seat 0: 86 / 34 / 0
  - t-suicune, deck in seat 1: 37 / 83 / 0
  - t-vespiquen, deck in seat 0: 43 / 77 / 0
  - t-vespiquen, deck in seat 1: 53 / 67 / 0
  - t-weezing, deck in seat 0: 62 / 58 / 0
  - t-weezing, deck in seat 1: 42 / 78 / 0
