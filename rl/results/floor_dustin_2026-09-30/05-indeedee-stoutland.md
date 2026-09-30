# Floor check: 05-indeedee-stoutland

**Verdict: clears the floor.** 578 wins in 1920 games (30.10%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Cheren as Trainer (played): used on 433 of 2152 opportunities (20.1%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 44/240 = 18%
- t-blaziken: 47/240 = 20%
- t-weezing: 52/240 = 22%
- t-hydreigon: 70/240 = 29%
- t-altaria: 73/240 = 30%
- t-vespiquen: 77/240 = 32%
- t-suicune: 106/240 = 44%
- t-lucario: 109/240 = 45%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Cheren (B3 151) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | its effect: pays off during the opponent's turn, which the search doesn't play out | 2152 | 433 | 20.1% — under 25% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 934 | 0% / 14% / 25% | 0% / 14% / 25% | 1.89 | 48% | 49% | 1.41 | 30% |
| went second | 986 | 9% / 17% / 31% | 9% / 17% / 31% | 1.99 | 53% | 44% | 1.43 | 30% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Stoutland. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `05-indeedee-stoutland_coverage.json`. Per-game records: `05-indeedee-stoutland_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 31 / 89 / 0
  - t-altaria, deck in seat 1: 78 / 42 / 0
  - t-blaziken, deck in seat 0: 20 / 100 / 0
  - t-blaziken, deck in seat 1: 93 / 27 / 0
  - t-hydreigon, deck in seat 0: 29 / 91 / 0
  - t-hydreigon, deck in seat 1: 79 / 41 / 0
  - t-lucario, deck in seat 0: 50 / 70 / 0
  - t-lucario, deck in seat 1: 61 / 59 / 0
  - t-sceptile, deck in seat 0: 26 / 94 / 0
  - t-sceptile, deck in seat 1: 102 / 18 / 0
  - t-suicune, deck in seat 0: 52 / 68 / 0
  - t-suicune, deck in seat 1: 66 / 54 / 0
  - t-vespiquen, deck in seat 0: 40 / 80 / 0
  - t-vespiquen, deck in seat 1: 83 / 37 / 0
  - t-weezing, deck in seat 0: 29 / 91 / 0
  - t-weezing, deck in seat 1: 97 / 23 / 0
