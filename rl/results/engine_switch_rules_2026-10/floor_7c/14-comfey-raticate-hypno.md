# Floor check: 14-comfey-raticate-hypno

**Verdict: untrusted.** 321 wins in 1920 games (16.72%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Team Rocket's Goo-zooka as Trainer (played): used on 185 of 4473 opportunities (4.1%); Team Rocket's Hypno as attacker: used on 1234 of 1361 opportunities (90.7%); Team Rocket's Researcher as Trainer (played): used on 1040 of 1294 opportunities (80.4%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: ../../../../../../../home/dacz8976/engine-rules-5a18d31/engine/target/release/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-suicune: 16/240 = 7%
- t-sceptile: 19/240 = 8%
- t-weezing: 27/240 = 11%
- t-hydreigon: 32/240 = 13%
- t-blaziken: 42/240 = 18%
- t-lucario: 48/240 = 20%
- t-vespiquen: 66/240 = 28%
- t-altaria: 71/240 = 30%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Team Rocket's Goo-zooka (B4a 068) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 4473 | 185 | 4.1% — under 25% |
| Team Rocket's Hypno (B4a 028) | attacker (default from the flag) | Entrap: SwitchInOpponentBenchedThenDamage estimated at printed damage (k's damage estimate) | 1361 | 1234 | 90.7% |
| Team Rocket's Researcher (B4a 069) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | engine: Implemented with unverified rule boundaries; Unverified Pokémon TCG Pocket boundary: random Pokémon transferred by this effect are not capped at a 10-card hand; this inherits the engine's existing random-search transfer policy., Unverified Pokémon TCG Pocket boundary: the deck is shuffled exactly once after resolution, including zero heads or no eligible Pokémon; this inherits the engine's hidden-zone normalization policy rather than printed card text. | 1294 | 1040 | 80.4% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 933 | 18% / 46% / 65% | 18% / 46% / 65% | 1.17 | 24% | 0% | 1.46 | 17% |
| went second | 987 | 37% / 50% / 63% | 36% / 50% / 62% | 1.17 | 27% | 0% | 1.46 | 16% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Team Rocket's Raticate ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-30/goldfish (sha256 8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073; the official release; `--games 0 --coverage`): `14-comfey-raticate-hypno_coverage.json`. Per-game records: `14-comfey-raticate-hypno_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 37 / 83 / 0
  - t-altaria, deck in seat 1: 86 / 34 / 0
  - t-blaziken, deck in seat 0: 22 / 98 / 0
  - t-blaziken, deck in seat 1: 100 / 20 / 0
  - t-hydreigon, deck in seat 0: 18 / 102 / 0
  - t-hydreigon, deck in seat 1: 106 / 14 / 0
  - t-lucario, deck in seat 0: 22 / 98 / 0
  - t-lucario, deck in seat 1: 94 / 26 / 0
  - t-sceptile, deck in seat 0: 9 / 111 / 0
  - t-sceptile, deck in seat 1: 110 / 10 / 0
  - t-suicune, deck in seat 0: 8 / 112 / 0
  - t-suicune, deck in seat 1: 112 / 8 / 0
  - t-vespiquen, deck in seat 0: 33 / 87 / 0
  - t-vespiquen, deck in seat 1: 87 / 33 / 0
  - t-weezing, deck in seat 0: 12 / 108 / 0
  - t-weezing, deck in seat 1: 105 / 15 / 0
