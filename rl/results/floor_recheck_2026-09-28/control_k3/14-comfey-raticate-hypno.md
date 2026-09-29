# Floor check: 14-comfey-raticate-hypno

**Verdict: control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not kog3 on both): untrusted.** 196 wins in 1920 games (10.21%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Copycat as Trainer (played): used on 572 of 1508 opportunities (37.9%); Team Rocket's Goo-zooka as Trainer (played): used on 66 of 4486 opportunities (1.5%); Team Rocket's Hypno as attacker: used on 1099 of 1161 opportunities (94.7%); Team Rocket's Raticate ex as activated ability: used on 49 of 1622 opportunities (3.0%); Team Rocket's Researcher as Trainer (played): used on 1110 of 1303 opportunities (85.2%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: k3 on the deck, k3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-weezing: 3/240 = 1%
- t-sceptile: 8/240 = 3%
- t-suicune: 8/240 = 3%
- t-vespiquen: 22/240 = 9%
- t-hydreigon: 27/240 = 11%
- t-blaziken: 33/240 = 14%
- t-lucario: 34/240 = 14%
- t-altaria: 61/240 = 25%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Copycat (B1 225) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | its effect: text the pilot leaves unpriced (opponent's hand or deck) | 1508 | 572 | 37.9% |
| Team Rocket's Goo-zooka (B4a 068) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 4486 | 66 | 1.5% — under 25% |
| Team Rocket's Hypno (B4a 028) | attacker (default from the flag) | Entrap: SwitchInOpponentBenchedThenDamage estimated at printed damage (k's damage estimate) | 1161 | 1099 | 94.7% |
| Team Rocket's Raticate ex (B4a 059) | activated ability (default from the flag) | ability Thieving Incisors: text the pilot leaves unpriced (opponent's hand or deck) | 1622 | 49 | 3.0% — under 25% |
| Team Rocket's Researcher (B4a 069) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | engine: Implemented with unverified rule boundaries; Unverified Pokémon TCG Pocket boundary: random Pokémon transferred by this effect are not capped at a 10-card hand; this inherits the engine's existing random-search transfer policy., Unverified Pokémon TCG Pocket boundary: the deck is shuffled exactly once after resolution, including zero heads or no eligible Pokémon; this inherits the engine's hidden-zone normalization policy rather than printed card text. | 1303 | 1110 | 85.2% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 933 | 0% / 23% / 39% | 0% / 23% / 39% | 1.87 | 42% | 0% | 1.56 | 9% |
| went second | 987 | 14% / 28% / 46% | 14% / 28% / 46% | 1.69 | 43% | 0% | 1.53 | 11% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Team Rocket's Raticate ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `14-comfey-raticate-hypno_coverage.json`. Per-game records: `14-comfey-raticate-hypno_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 29 / 91 / 0
  - t-altaria, deck in seat 1: 88 / 32 / 0
  - t-blaziken, deck in seat 0: 21 / 99 / 0
  - t-blaziken, deck in seat 1: 108 / 12 / 0
  - t-hydreigon, deck in seat 0: 12 / 108 / 0
  - t-hydreigon, deck in seat 1: 105 / 15 / 0
  - t-lucario, deck in seat 0: 14 / 106 / 0
  - t-lucario, deck in seat 1: 100 / 20 / 0
  - t-sceptile, deck in seat 0: 6 / 114 / 0
  - t-sceptile, deck in seat 1: 118 / 2 / 0
  - t-suicune, deck in seat 0: 4 / 116 / 0
  - t-suicune, deck in seat 1: 116 / 4 / 0
  - t-vespiquen, deck in seat 0: 11 / 109 / 0
  - t-vespiquen, deck in seat 1: 109 / 11 / 0
  - t-weezing, deck in seat 0: 0 / 120 / 0
  - t-weezing, deck in seat 1: 117 / 3 / 0
