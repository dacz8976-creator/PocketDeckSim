# Floor check: draft-C-meowstic-hatterene-v2

**Verdict: borderline.** 366 wins in 1920 games (19.06%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Hatterene as attacker: used on 2302 of 2376 opportunities (96.9%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-10-02/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-suicune: 7/240 = 3%
- t-hydreigon: 15/240 = 6%
- t-weezing: 22/240 = 9%
- t-sceptile: 24/240 = 10%
- t-vespiquen: 26/240 = 11%
- t-blaziken: 55/240 = 23%
- t-altaria: 101/240 = 42%
- t-lucario: 116/240 = 48%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Hatterene (B3 071) | attacker (default from the flag) | Mental Crush: ExtraDamageIfDefenderStatus estimated at printed damage (k's damage estimate) | 2376 | 2302 | 96.9% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 936 | 0% / 16% / 36% | 0% / 16% / 36% | 1.60 | 39% | 48% | 1.86 | 21% |
| went second | 984 | 2% / 19% / 35% | 2% / 19% / 35% | 1.75 | 46% | 40% | 1.95 | 18% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Hatterene. Draws: 4.

## For a second reader

- Coverage from rl/engine-2026-10-02/goldfish (sha256 cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66; the official release; `--games 0 --coverage`): `draft-C-meowstic-hatterene-v2_coverage.json`. Per-game records: `draft-C-meowstic-hatterene-v2_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 52 / 68 / 0
  - t-altaria, deck in seat 1: 71 / 49 / 0
  - t-blaziken, deck in seat 0: 30 / 87 / 3
  - t-blaziken, deck in seat 1: 94 / 25 / 1
  - t-hydreigon, deck in seat 0: 4 / 116 / 0
  - t-hydreigon, deck in seat 1: 109 / 11 / 0
  - t-lucario, deck in seat 0: 60 / 60 / 0
  - t-lucario, deck in seat 1: 64 / 56 / 0
  - t-sceptile, deck in seat 0: 10 / 110 / 0
  - t-sceptile, deck in seat 1: 106 / 14 / 0
  - t-suicune, deck in seat 0: 4 / 116 / 0
  - t-suicune, deck in seat 1: 117 / 3 / 0
  - t-vespiquen, deck in seat 0: 15 / 105 / 0
  - t-vespiquen, deck in seat 1: 109 / 11 / 0
  - t-weezing, deck in seat 0: 12 / 108 / 0
  - t-weezing, deck in seat 1: 110 / 10 / 0
