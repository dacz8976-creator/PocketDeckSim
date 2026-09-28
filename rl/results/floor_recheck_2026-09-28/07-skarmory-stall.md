# Floor check: 07-skarmory-stall

**Verdict: clears the floor.** 903 wins in 1920 games (47.03%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Jasmine as Trainer (played): used on 53 of 3961 opportunities (1.3%); Metal Core Barrier as Trainer (played): used on 2422 of 3066 opportunities (79.0%); Skarmory ex as attacker: used on 7687 of 7687 opportunities (100.0%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-blaziken: 54/240 = 22%
- t-lucario: 63/240 = 26%
- t-sceptile: 69/240 = 29%
- t-vespiquen: 110/240 = 46%
- t-weezing: 138/240 = 58%
- t-altaria: 143/240 = 60%
- t-hydreigon: 155/240 = 65%
- t-suicune: 171/240 = 71%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Jasmine (A4 160) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3961 | 53 | 1.3% — under 25% |
| Metal Core Barrier (B2 148) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3066 | 2422 | 79.0% |
| Skarmory ex (A4 124) | attacker (default from the flag) | attack Steel Wing: pays off during the opponent's turn, which the search doesn't play out | 7687 | 7687 | 100.0% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 935 | 0% / 59% / 84% | 0% / 59% / 84% | 0.44 | 8% | 0% | 0.82 | 42% |
| went second | 985 | 62% / 87% / 92% | 62% / 87% / 92% | 0.26 | 5% | 0% | 0.70 | 52% |

Main attackers for these measures (the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)): Skarmory ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `07-skarmory-stall_coverage.json`. Per-game records: `07-skarmory-stall_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 77 / 43 / 0
  - t-altaria, deck in seat 1: 54 / 66 / 0
  - t-blaziken, deck in seat 0: 27 / 93 / 0
  - t-blaziken, deck in seat 1: 93 / 27 / 0
  - t-hydreigon, deck in seat 0: 78 / 42 / 0
  - t-hydreigon, deck in seat 1: 43 / 77 / 0
  - t-lucario, deck in seat 0: 33 / 87 / 0
  - t-lucario, deck in seat 1: 90 / 30 / 0
  - t-sceptile, deck in seat 0: 34 / 86 / 0
  - t-sceptile, deck in seat 1: 85 / 35 / 0
  - t-suicune, deck in seat 0: 87 / 33 / 0
  - t-suicune, deck in seat 1: 36 / 84 / 0
  - t-vespiquen, deck in seat 0: 43 / 77 / 0
  - t-vespiquen, deck in seat 1: 53 / 67 / 0
  - t-weezing, deck in seat 0: 61 / 59 / 0
  - t-weezing, deck in seat 1: 43 / 77 / 0
