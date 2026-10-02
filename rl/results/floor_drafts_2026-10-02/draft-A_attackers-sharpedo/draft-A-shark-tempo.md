# Floor check: draft-A-shark-tempo

**Verdict: clears the floor.** 950 wins in 1920 games (49.48%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Alolan Ninetales ex as attacker: used on 3598 of 3903 opportunities (92.2%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-10-02/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-altaria: 95/240 = 40%
- t-sceptile: 105/240 = 44%
- t-weezing: 109/240 = 45%
- t-suicune: 114/240 = 48%
- t-lucario: 121/240 = 50%
- t-hydreigon: 122/240 = 51%
- t-vespiquen: 132/240 = 55%
- t-blaziken: 152/240 = 63%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Alolan Ninetales ex (B2 029) | attacker (default from the flag) | attack Binding Snow: pays off during the opponent's turn, which the search doesn't play out | 3903 | 3598 | 92.2% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 923 | 18% / 32% / 52% | 18% / 32% / 51% | 1.21 | 30% | 0% | 1.19 | 49% |
| went second | 997 | 24% / 40% / 50% | 23% / 39% / 49% | 1.22 | 38% | 0% | 1.23 | 50% |

Main attackers for these measures (set for this list in floor.py's ATTACKERS): Mega Sharpedo ex. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-10-02/goldfish (sha256 cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66; the official release; `--games 0 --coverage`): `draft-A-shark-tempo_coverage.json`. Per-game records: `draft-A-shark-tempo_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 48 / 72 / 0
  - t-altaria, deck in seat 1: 73 / 47 / 0
  - t-blaziken, deck in seat 0: 73 / 46 / 1
  - t-blaziken, deck in seat 1: 41 / 79 / 0
  - t-hydreigon, deck in seat 0: 60 / 60 / 0
  - t-hydreigon, deck in seat 1: 58 / 62 / 0
  - t-lucario, deck in seat 0: 58 / 62 / 0
  - t-lucario, deck in seat 1: 57 / 63 / 0
  - t-sceptile, deck in seat 0: 54 / 66 / 0
  - t-sceptile, deck in seat 1: 69 / 51 / 0
  - t-suicune, deck in seat 0: 57 / 63 / 0
  - t-suicune, deck in seat 1: 63 / 57 / 0
  - t-vespiquen, deck in seat 0: 69 / 51 / 0
  - t-vespiquen, deck in seat 1: 57 / 63 / 0
  - t-weezing, deck in seat 0: 60 / 60 / 0
  - t-weezing, deck in seat 1: 71 / 49 / 0
