# Floor check: 11-archaludon-haxorus-dragonair

**Verdict: untrusted.** 295 wins in 1920 games (15.36%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Archaludon as attacker: used on 424 of 429 opportunities (98.8%); Iris as Trainer (played): used on 233 of 3068 opportunities (7.6%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 28/240 = 12%
- t-blaziken: 30/240 = 12%
- t-suicune: 30/240 = 12%
- t-weezing: 31/240 = 13%
- t-hydreigon: 39/240 = 16%
- t-lucario: 44/240 = 18%
- t-vespiquen: 44/240 = 18%
- t-altaria: 49/240 = 20%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Archaludon (B4a 056) | attacker (default from the flag) | attack Protect Charge: pays off during the opponent's turn, which the search doesn't play out | 429 | 424 | 98.8% |
| Iris (B2b 067) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3068 | 233 | 7.6% — under 25% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 940 | 0% / 0% / 3% | 0% / 0% / 3% | 2.48 | 89% | 19% | 1.82 | 17% |
| went second | 980 | 0% / 2% / 8% | 0% / 2% / 8% | 2.39 | 86% | 17% | 1.78 | 14% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Archaludon. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `11-archaludon-haxorus-dragonair_coverage.json`. Per-game records: `11-archaludon-haxorus-dragonair_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 23 / 97 / 0
  - t-altaria, deck in seat 1: 94 / 26 / 0
  - t-blaziken, deck in seat 0: 13 / 107 / 0
  - t-blaziken, deck in seat 1: 103 / 17 / 0
  - t-hydreigon, deck in seat 0: 19 / 101 / 0
  - t-hydreigon, deck in seat 1: 100 / 20 / 0
  - t-lucario, deck in seat 0: 21 / 99 / 0
  - t-lucario, deck in seat 1: 97 / 23 / 0
  - t-sceptile, deck in seat 0: 15 / 105 / 0
  - t-sceptile, deck in seat 1: 107 / 13 / 0
  - t-suicune, deck in seat 0: 17 / 103 / 0
  - t-suicune, deck in seat 1: 107 / 13 / 0
  - t-vespiquen, deck in seat 0: 27 / 93 / 0
  - t-vespiquen, deck in seat 1: 103 / 17 / 0
  - t-weezing, deck in seat 0: 16 / 104 / 0
  - t-weezing, deck in seat 1: 105 / 15 / 0
