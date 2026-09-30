# Floor check: brew-09-sableye-obstagoon

**Verdict: clears the floor.** 835 wins in 1920 games (43.49%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Galarian Obstagoon as attacker: used on 1033 of 1048 opportunities (98.6%); Mega Sableye ex as attacker: used on 4326 of 4499 opportunities (96.2%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-30/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-sceptile: 76/240 = 32%
- t-weezing: 76/240 = 32%
- t-suicune: 82/240 = 34%
- t-vespiquen: 93/240 = 39%
- t-lucario: 100/240 = 42%
- t-altaria: 131/240 = 55%
- t-blaziken: 137/240 = 57%
- t-hydreigon: 140/240 = 58%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Galarian Obstagoon (B2 100) | attacker (default from the flag) | Merciless Strike: ExtraDamageIfHurt estimated at printed damage (k's damage estimate) | 1048 | 1033 | 98.6% |
| Mega Sableye ex (B3b 041) | attacker (default from the flag) | Cursed Jewel: DamageAndCardEffect estimated at printed damage (k's damage estimate); attack Cursed Jewel: pays off during the opponent's turn, which the search doesn't play out | 4499 | 4326 | 96.2% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 934 | 0% / 53% / 68% | 0% / 52% / 67% | 0.79 | 10% | 44% | 1.23 | 37% |
| went second | 986 | 46% / 73% / 83% | 46% / 73% / 83% | 0.56 | 7% | 44% | 1.20 | 50% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Mega Sableye ex. Draws: 34.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `brew-09-sableye-obstagoon_coverage.json`. Per-game records: `brew-09-sableye-obstagoon_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 65 / 54 / 1
  - t-altaria, deck in seat 1: 53 / 66 / 1
  - t-blaziken, deck in seat 0: 70 / 48 / 2
  - t-blaziken, deck in seat 1: 51 / 67 / 2
  - t-hydreigon, deck in seat 0: 67 / 52 / 1
  - t-hydreigon, deck in seat 1: 46 / 73 / 1
  - t-lucario, deck in seat 0: 50 / 67 / 3
  - t-lucario, deck in seat 1: 67 / 50 / 3
  - t-sceptile, deck in seat 0: 38 / 81 / 1
  - t-sceptile, deck in seat 1: 82 / 38 / 0
  - t-suicune, deck in seat 0: 40 / 75 / 5
  - t-suicune, deck in seat 1: 72 / 42 / 6
  - t-vespiquen, deck in seat 0: 44 / 75 / 1
  - t-vespiquen, deck in seat 1: 68 / 49 / 3
  - t-weezing, deck in seat 0: 35 / 83 / 2
  - t-weezing, deck in seat 1: 77 / 41 / 2
