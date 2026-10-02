# Floor check: draft-B-tide-heal

**Verdict: fail.** 236 wins in 1920 games (12.29%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): none. A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-10-02/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-vespiquen: 16/240 = 7%
- t-suicune: 17/240 = 7%
- t-altaria: 25/240 = 10%
- t-weezing: 25/240 = 10%
- t-lucario: 34/240 = 14%
- t-blaziken: 37/240 = 15%
- t-sceptile: 37/240 = 15%
- t-hydreigon: 45/240 = 19%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| (none) | | | | | |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 923 | 0% / 23% / 29% | 0% / 23% / 29% | 1.91 | 61% | 0% | 1.61 | 11% |
| went second | 997 | 21% / 26% / 30% | 21% / 26% / 30% | 1.75 | 61% | 0% | 1.58 | 13% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Starmie. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-10-02/goldfish (sha256 cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66; the official release; `--games 0 --coverage`): `draft-B-tide-heal_coverage.json`. Per-game records: `draft-B-tide-heal_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 12 / 108 / 0
  - t-altaria, deck in seat 1: 107 / 13 / 0
  - t-blaziken, deck in seat 0: 18 / 102 / 0
  - t-blaziken, deck in seat 1: 101 / 19 / 0
  - t-hydreigon, deck in seat 0: 19 / 101 / 0
  - t-hydreigon, deck in seat 1: 94 / 26 / 0
  - t-lucario, deck in seat 0: 15 / 105 / 0
  - t-lucario, deck in seat 1: 101 / 19 / 0
  - t-sceptile, deck in seat 0: 21 / 99 / 0
  - t-sceptile, deck in seat 1: 104 / 16 / 0
  - t-suicune, deck in seat 0: 6 / 114 / 0
  - t-suicune, deck in seat 1: 109 / 11 / 0
  - t-vespiquen, deck in seat 0: 9 / 111 / 0
  - t-vespiquen, deck in seat 1: 113 / 7 / 0
  - t-weezing, deck in seat 0: 11 / 109 / 0
  - t-weezing, deck in seat 1: 106 / 14 / 0
