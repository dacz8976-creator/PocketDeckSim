# Floor check: 06-mega-blaziken-tournament-list

**Verdict: clears the floor.** 1110 wins in 1920 games (57.81%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Rocky Helmet as Trainer (played): used on 1270 of 1859 opportunities (68.3%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-altaria: 95/240 = 40%
- t-weezing: 116/240 = 48%
- t-lucario: 122/240 = 51%
- t-blaziken: 133/240 = 55%
- t-hydreigon: 142/240 = 59%
- t-suicune: 150/240 = 62%
- t-sceptile: 163/240 = 68%
- t-vespiquen: 189/240 = 79%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Rocky Helmet (A2 148) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 1859 | 1270 | 68.3% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 908 | 0% / 27% / 56% | 0% / 23% / 55% | 1.40 | 25% | 56% | 1.44 | 56% |
| went second | 1012 | 15% / 38% / 60% | 13% / 37% / 59% | 1.32 | 30% | 51% | 1.30 | 60% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Mega Blaziken ex. Draws: 3.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `06-mega-blaziken-tournament-list_coverage.json`. Per-game records: `06-mega-blaziken-tournament-list_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 47 / 73 / 0
  - t-altaria, deck in seat 1: 72 / 48 / 0
  - t-blaziken, deck in seat 0: 68 / 52 / 0
  - t-blaziken, deck in seat 1: 55 / 65 / 0
  - t-hydreigon, deck in seat 0: 75 / 45 / 0
  - t-hydreigon, deck in seat 1: 52 / 67 / 1
  - t-lucario, deck in seat 0: 62 / 58 / 0
  - t-lucario, deck in seat 1: 60 / 60 / 0
  - t-sceptile, deck in seat 0: 81 / 39 / 0
  - t-sceptile, deck in seat 1: 38 / 82 / 0
  - t-suicune, deck in seat 0: 73 / 47 / 0
  - t-suicune, deck in seat 1: 43 / 77 / 0
  - t-vespiquen, deck in seat 0: 97 / 22 / 1
  - t-vespiquen, deck in seat 1: 28 / 92 / 0
  - t-weezing, deck in seat 0: 54 / 65 / 1
  - t-weezing, deck in seat 1: 58 / 62 / 0
