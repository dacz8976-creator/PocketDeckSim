# Pre-registration: repro_check

Written 2026-10-06T01:48:28Z, **before any game was played**. The manifest (`manifest.json`, sha256 `0b7edc924f85468ded2d6b66f2cf9d16ce89f654eb45c32357d1586ba5ac7187`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

scratch: does this build's kx3_r16_c12_z2_real_t0_poolmeta replay the development run's kx3 games?

## Pilots

- **Pilot under test (arm X):** `kx3_r16_c12_z2_real_t0_poolmeta`
- **Reference (arm ref, and the opponent in both arms):** `km3`
- Program: `None` sha256 `None`; engine: None; repository commit: `14773e518c2c34db156a4bdb237e578193f3b3a3`
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24400000000 + p x 10000 + i`; each deal is played with the deck in seats [0]. 1 deals x 1 seats x 2 arms per pair; 56 pairs; **112 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| 09-mega-manectric-heliolisk | `decks/dustin/09-mega-manectric-heliolisk.txt` | 48ca6b6c6aee |
| 06-mega-blaziken-tournament-list | `decks/dustin/06-mega-blaziken-tournament-list.txt` | 69c521a33339 |
| 10-xatu-oricorio-tr-weezing | `decks/dustin/10-xatu-oricorio-tr-weezing.txt` | a9cf8f1998a5 |
| 03-wailord-indeedee-wall | `decks/dustin/03-wailord-indeedee-wall.txt` | 7d367c7ce81b |
| 01-muk-glimmora-kingambit-regigigas | `decks/dustin/01-muk-glimmora-kingambit-regigigas.txt` | 49d135c6e09e |
| 05-indeedee-stoutland | `decks/dustin/05-indeedee-stoutland.txt` | 0524e3595c49 |
| draft-A-shark-tempo | `decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt` | 3f39092ba668 |

## Opponents

t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing

## Held-out decks

Stage `dev`; held-out list `['02-arceus-crobat', '04-absol-hoopa-darkrai', '07-skarmory-stall', '08-garchomp-toolbox', '11-archaludon-haxorus-dragonair', '12-ariados-whimsicott-ogerpon', '13-a-ninetales-raticate', '14-comfey-raticate-hypno', '15-jolteon-oricorio-raticate', 'draft-C-meowstic-hatterene-v2', 'draft-D-entei-grimhound']`, lock `on`. A development run refuses any held-out deck on either side.

## Analysis plan (fixed now)

- Score of a game for the deck: win 1, tie 0.5, loss 0. **Paired difference** `d = score(arm X) - score(arm ref)` on each (deck, opponent, deal, seat).
- Reported per (deck, opponent) pair, per deck pooled over its opponents, and pooled over everything: the mean of `d` with the interval **mean ± 1.96·sd/√n** (sample sd, n = paired games). A second pooled figure weights every deck equally.
- Also reported: the same split by who went first (the first player is identical in both arms), win rates per arm, wall time and decisions per game for each pilot, cost per game when an external pilot reports it, and how many more deals would narrow the pooled interval to ±3 and ±5 points at the sd reached.
- Intended-line rates from `rl/strength/intended_lines.json` (sha256 `80778f3c4a58`): per game and per use, per arm, with the paired difference where it is per game.
- No pass/fail threshold is set by this document. A slow pilot is reported with its time and cost, not rejected.

## Run

```
strength run --manifest manifest.json --out .   # add --max-games N or --stop-after-min M to stop early; run it again to resume
python3 strength_report.py --dir .
```
