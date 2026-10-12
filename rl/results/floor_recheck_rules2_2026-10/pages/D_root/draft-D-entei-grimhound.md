> Games: step 7c's replays on the new engine, equal to Oct 2's, and no game was played for this page (the coordinator, Oct 11: draft D has no expected change, and the Victini caveat is text). Engine lines, Victini's row's caveat and the coverage file are the new engine's.

# Floor check: draft-D-entei-grimhound

**Verdict: clears the floor.** 693 wins in 1920 games (36.09%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Victini as attacker: used on 898 of 1070 opportunities (83.9%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-10-12/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-suicune: 53/240 = 22%
- t-weezing: 53/240 = 22%
- t-blaziken: 63/240 = 26%
- t-hydreigon: 77/240 = 32%
- t-altaria: 80/240 = 33%
- t-lucario: 98/240 = 41%
- t-sceptile: 116/240 = 48%
- t-vespiquen: 153/240 = 64%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Victini (B3 025) | attacker (default from the flag) | engine: Implemented with unverified rule boundaries; Victory Star supports printed attack-effect coin batches. The gate coins come first and are never offered for a reroll: Confusion (rules/04 §9, seen in Pocket Sept 29) and a block coin ("if the Defending Pokémon tries to use an attack, your opponent flips a coin"; Victory Star covers only "coins for an attack of 1 of your [R] Pokémon", TEXT_AUDIT.md A1). After their heads the attack's own coins are offered, with no second gate coin. A pending Will goes to a block coin when there is one (flipped for the effect of an attack), otherwise to the attack's own first coin (Recording_QA 210403), and a reroll is a fresh batch it does not touch (203626)., Still open, decided by no card text: which of the Confusion coin and a block coin comes first when both apply (nothing visible depends on it). The block coin's not being offered rests on the plain reading of Victory Star's text; a recording of shot row victory-star-block-coin would confirm it. | 1070 | 898 | 83.9% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 962 | 1% / 6% / 23% | 1% / 6% / 23% | 2.28 | 62% | 0% | 2.14 | 35% |
| went second | 958 | 3% / 16% / 34% | 3% / 16% / 34% | 2.15 | 56% | 0% | 2.01 | 37% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Mega Houndoom ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-10-12/goldfish (sha256 d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84; the official release; `--games 0 --coverage`): `draft-D-entei-grimhound_coverage.json`. Per-game records: `draft-D-entei-grimhound_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 36 / 84 / 0
  - t-altaria, deck in seat 1: 76 / 44 / 0
  - t-blaziken, deck in seat 0: 29 / 91 / 0
  - t-blaziken, deck in seat 1: 86 / 34 / 0
  - t-hydreigon, deck in seat 0: 35 / 85 / 0
  - t-hydreigon, deck in seat 1: 78 / 42 / 0
  - t-lucario, deck in seat 0: 53 / 67 / 0
  - t-lucario, deck in seat 1: 75 / 45 / 0
  - t-sceptile, deck in seat 0: 63 / 57 / 0
  - t-sceptile, deck in seat 1: 67 / 53 / 0
  - t-suicune, deck in seat 0: 27 / 93 / 0
  - t-suicune, deck in seat 1: 94 / 26 / 0
  - t-vespiquen, deck in seat 0: 74 / 46 / 0
  - t-vespiquen, deck in seat 1: 41 / 79 / 0
  - t-weezing, deck in seat 0: 31 / 89 / 0
  - t-weezing, deck in seat 1: 98 / 22 / 0
