# Floor check: brew-08-entei-rainbow-cave

**Verdict: clears the floor.** 1040 wins in 1920 games (54.17%) against the 8 lists in decks/screen/opponents. Bar 20% with the screen's own noise ±1.79 points at this n: 349 wins or fewer fail, 350-418 are borderline, 419 or more clear the floor.
Flagged cards (the bot is known not to price them fully): none. A share under 25% of at least 20 opportunities is a flag for a person to look at.
Not a ranking: no average across decks is used for anything else.

- Engine: rl/engine-2026-09-28/deckgym (the manifest's available release). Pilots: kog3 on the deck, kog3 on the panel. 240 games per matchup, seeds 7100 + 1,000 x opponent (seat 0) and +500 (seat 1), --seed-stream.

## Worst matchups (each line ±6 points at 240 games)

- t-blaziken: 86/240 = 36%
- t-altaria: 99/240 = 41%
- t-suicune: 103/240 = 43%
- t-lucario: 115/240 = 48%
- t-weezing: 124/240 = 52%
- t-hydreigon: 156/240 = 65%
- t-sceptile: 157/240 = 65%
- t-vespiquen: 200/240 = 83%

## Coverage flag: cards the bot may not play as a strong player would

| card | role (source) | why flagged | opportunities | used | share |
|---|---|---|---|---|---|
| (none) | | | | | |

Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong role is set per deck in floor.py's ROLES.

## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)

| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn (turns 2-4) | won |
|---|---|---|---|---|---|---|---|---|
| went first | 933 | 38% / 92% / 99% | 38% / 92% / 99% | 0.06 | 1% | 0% | 1.40 | 50% |
| went second | 987 | 92% / 98% / 99% | 92% / 98% / 99% | 0.07 | 1% | 0% | 1.36 | 58% |

Main attackers for these measures (fallback: the Pokemon with the highest printed damage (no A1 entry for this list)): Entei ex. Draws: 1.

## For a second reader

- Coverage from rl/engine-2026-09-28/goldfish (sha256 f3ebb69b061c884a261dc7cf120352ff8112eebd0fdd705dfd9c841f72a46f09; the official release; `--games 0 --coverage`): `brew-08-entei-rainbow-cave_coverage.json`. Per-game records: `brew-08-entei-rainbow-cave_games.jsonl` (each game's 'flagged' field holds every flagged card's [opportunities, used] under its role; they sum to the table above).
- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run with the same pilots, seeds and games must print the same:
  - t-altaria, deck in seat 0: 50 / 70 / 0
  - t-altaria, deck in seat 1: 71 / 49 / 0
  - t-blaziken, deck in seat 0: 51 / 69 / 0
  - t-blaziken, deck in seat 1: 84 / 35 / 1
  - t-hydreigon, deck in seat 0: 83 / 37 / 0
  - t-hydreigon, deck in seat 1: 47 / 73 / 0
  - t-lucario, deck in seat 0: 52 / 68 / 0
  - t-lucario, deck in seat 1: 57 / 63 / 0
  - t-sceptile, deck in seat 0: 78 / 42 / 0
  - t-sceptile, deck in seat 1: 41 / 79 / 0
  - t-suicune, deck in seat 0: 53 / 67 / 0
  - t-suicune, deck in seat 1: 70 / 50 / 0
  - t-vespiquen, deck in seat 0: 100 / 20 / 0
  - t-vespiquen, deck in seat 1: 20 / 100 / 0
  - t-weezing, deck in seat 0: 64 / 56 / 0
  - t-weezing, deck in seat 1: 60 / 60 / 0

## If you play it on the ladder: what to note (Dustin, Sept 28)

Dustin, about 7:30 pm Central (via the Fable session, verbatim): "Play the one you'll enjoy twenty games of ... if it's a coin flip between 07 and 08, 08 is the better evidence ... it's an unchanged real Limitless list, so it's the first deck you'd play that has both a screen number and a real cell." And: "the A1 prediction — 07 and 08 fastest to set up, 10 slowest — gets its first real test from whichever you play, so note setup speed when you log."

For each game, note three things beside the result:
- whether you went first or second;
- **the turn you first attacked with Entei ex**, counting your own turns (your first turn is 1), or "never";
- **the opponent's points at that moment** (0, 1, 2...).

The simulator's numbers to compare, from the table above:
- went first: Entei ex attacked by your turn 2 in 38% of games, turn 3 in 92%, turn 4 in 99%;
- went second: 92% by turn 2, 98% by turn 3;
- the opponent had 0.06 points on average when it did.

Twenty games is enough to see whether the real setup is roughly that fast, not to measure it exactly.

In the Ladder Log, put them in the game's Note box, for example `2nd | Entei T2 | opp 0 pts` (the log has no separate boxes for these, and none are needed).

## Your first nine ladder games with it (Sept 28 evening; from the written video reviews)

All nine were brew 08 (Dustin, Sept 28). They are filed under "Brew 8" in the Ladder Log; the video reviewer had first logged them as "Entei ex (video-visible core)". The setup items were taken from each game's REVIEW.md (`Battle Logs/Recording_QA/`), counting your own turns.

**Running record:** this section is the first nine games only, as written up on Sept 28. Brew 08's ladder record as the Ladder Log grows (7-3 with the tenth game, filed Sept 28 at 23:43 CDT) is kept current in `decks/screen/panel_ladder_2026-09-26/brew_scorecard.md`.

| Opponent | Went | First Entei ex attack | Opp. points then | Result |
|---|---|---|---|---|
| ユアンジュナ (Mega Rayquaza) | 2nd | turn 2 | 0 | Win (concession) |
| Pipelayer69 (Hitmonchan ex) | 2nd | never (conceded first) | 0 | Win (concession) |
| Belial (Dragonite) | 1st | turn 3 | 0 | Loss 2-3 |
| かえぴ (Riolu / Sawk) | 1st | turn 2 | 0 | Win (concession) |
| NINTENDO DS (Snorlax) | 2nd | turn 2 | 0 | Win (concession) |
| ぽて (Mega Diancie / Gardevoir) | 2nd | turn 2 | 0 | Loss 0-3 |
| Maru (Raticate ex) | 2nd | turn 2 | 0 | Win (concession) |
| JayLaPi (Mega Audino) | 1st | turn 2 | 0 | Win (concession) |
| PsyckoHead (Mega Lucario) | 2nd (inferred) | turn 2 (inferred) | 0 | Loss 2-3 |

- **Against the simulator's numbers above:** no sign the real deck sets up slower than predicted.
  - Going second, Entei attacked by turn 2 in 5 of 5 games that got that far (sim: 92%).
  - Going first, it attacked by turn 2 in 2 of 3 (sim: 38%) and by turn 3 in 3 of 3 (sim: 92%).
  - The opponent had 0 points every time (sim: 0.06 on average).
- **What nine games can't do:** measure a rate. 2 of 3 fits anything from about 10% to 99%.
- **Win rate: 6-3 (67%).** A concession is a win: the opponent gives up because they can't win or are about to lose, which is common on the ladder. The floor's 54.2% is against the sim's eight-list panel, not ladder opponents. Nine games can't separate 67% from 54% (roughly ±30 points at this size), so it's consistent, nothing more yet.
- **The A1 prediction** (07 and 08 fastest, 10 slowest) needs games with 07 or 10 to be tested.
