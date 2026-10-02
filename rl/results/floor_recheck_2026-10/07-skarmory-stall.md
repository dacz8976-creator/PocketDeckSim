# Floor check: 07-skarmory-stall

**Verdict: clears the floor.** 1098 wins in 1920 games (57.19%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): Jasmine as Trainer (played): used on 1786 of 3299 opportunities (54.1%); Metal Core Barrier as Trainer (played): used on 2419 of 3667 opportunities (66.0%); Skarmory ex as attacker: used on 8397 of 8398 opportunities (100.0%). A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-10-02/deckgym (the manifest's available release). Pilots: km3 on the deck, km3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-blaziken: 63/240 = 26%
- t-lucario: 78/240 = 32%
- t-sceptile: 97/240 = 40%
- t-vespiquen: 150/240 = 62%
- t-altaria: 151/240 = 63%
- t-weezing: 157/240 = 65%
- t-hydreigon: 184/240 = 77%
- t-suicune: 218/240 = 91%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| Jasmine (A4 160) | Trainer (played) (default from the flag; a Supporter: turns with another Supporter played left out) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3299 | 1786 | 54.1% |
| Metal Core Barrier (B2 148) | Trainer (played) (default from the flag) | its effect: pays off during the opponent's turn, which the search doesn't play out | 3667 | 2419 | 66.0% |
| Skarmory ex (A4 124) | attacker (default from the flag) | attack Steel Wing: pays off during the opponent's turn, which the search doesn't play out | 8398 | 8397 | 100.0% |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 935 | 0% / 59% / 87% | 0% / 59% / 87% | 0.31 | 4% | 0% | 0.69 | 53% |
| went second | 985 | 62% / 87% / 93% | 62% / 87% / 93% | 0.22 | 5% | 0% | 0.60 | 61% |

Main attackers for these measures (the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)): Skarmory ex. Draws: 0.

## For a second reader

- Coverage from rl/engine-2026-10-02/goldfish (sha256 cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66; the official release; `--games 0 --coverage`): `07-skarmory-stall_coverage.json`. Per-game records: `07-skarmory-stall_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 75 / 45 / 0
  - t-altaria, deck in seat 1: 44 / 76 / 0
  - t-blaziken, deck in seat 0: 30 / 90 / 0
  - t-blaziken, deck in seat 1: 87 / 33 / 0
  - t-hydreigon, deck in seat 0: 94 / 26 / 0
  - t-hydreigon, deck in seat 1: 30 / 90 / 0
  - t-lucario, deck in seat 0: 41 / 79 / 0
  - t-lucario, deck in seat 1: 83 / 37 / 0
  - t-sceptile, deck in seat 0: 48 / 72 / 0
  - t-sceptile, deck in seat 1: 71 / 49 / 0
  - t-suicune, deck in seat 0: 109 / 11 / 0
  - t-suicune, deck in seat 1: 11 / 109 / 0
  - t-vespiquen, deck in seat 0: 69 / 51 / 0
  - t-vespiquen, deck in seat 1: 39 / 81 / 0
  - t-weezing, deck in seat 0: 73 / 47 / 0
  - t-weezing, deck in seat 1: 36 / 84 / 0
