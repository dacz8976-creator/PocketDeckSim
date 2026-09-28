# Floor check: brew-07-hoopa-darkrai-sableye

**Verdict: clears the floor.** 1177 wins in 1920 games (61.30%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Mega Sableye ex as attacker: used on 1089 of 1202 opportunities (90.6%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 88/240 = 37%
- t-vespiquen: 119/240 = 50%
- t-suicune: 142/240 = 59%
- t-blaziken: 143/240 = 60%
- t-lucario: 154/240 = 64%
- t-hydreigon: 167/240 = 70%
- t-altaria: 181/240 = 75%
- t-weezing: 183/240 = 76%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Mega Sableye ex (B3b 041) | attacker (default from the flag) | Cursed Jewel: DamageAndCardEffect estimated at printed damage (k's damage estimate); attack Cursed Jewel: pays off during the opponent's turn, which the search doesn't play out | 1202 | 1089 | 90.6% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 934 | 63% / 74% / 82% | 63% / 74% / 82% | 0.45 | 10% | 0% | 0.80 | 56% |
| went second | 986 | 72% / 79% / 86% | 72% / 79% / 85% | 0.38 | 11% | 0% | 0.77 | 67% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Hoopa ex. Draws: 7.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-07-hoopa-darkrai-sableye_coverage.json`. Per-game records: `brew-07-hoopa-darkrai-sableye_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 86 / 32 / 2
  - t-altaria, deck in seat 1: 25 / 95 / 0
  - t-blaziken, deck in seat 0: 73 / 47 / 0
  - t-blaziken, deck in seat 1: 50 / 70 / 0
  - t-hydreigon, deck in seat 0: 79 / 40 / 1
  - t-hydreigon, deck in seat 1: 32 / 88 / 0
  - t-lucario, deck in seat 0: 73 / 46 / 1
  - t-lucario, deck in seat 1: 38 / 81 / 1
  - t-sceptile, deck in seat 0: 46 / 74 / 0
  - t-sceptile, deck in seat 1: 78 / 42 / 0
  - t-suicune, deck in seat 0: 64 / 56 / 0
  - t-suicune, deck in seat 1: 41 / 78 / 1
  - t-vespiquen, deck in seat 0: 56 / 63 / 1
  - t-vespiquen, deck in seat 1: 57 / 63 / 0
  - t-weezing, deck in seat 0: 93 / 27 / 0
  - t-weezing, deck in seat 1: 30 / 90 / 0
