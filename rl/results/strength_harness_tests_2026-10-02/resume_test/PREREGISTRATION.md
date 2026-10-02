# Pre-registration: resume_test

Written 2026-10-02T19:52:41Z, **before any game was played**. The manifest (`manifest.json`, sha256 `b7ae49c126dababe355676c13dd75c0b38ae7f2eb62d8ea829d2e18c21acb0f9`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

Harness smoke test: kog3 against km3 on a handful of deals. Not a measurement.

## Pilots

- **Pilot under test (arm X):** `kog3`
- **Reference (arm ref, and the opponent in both arms):** `km3`
- Program: `/home/dacz8976/strength_build/strength` sha256 `fc07742a1374ecbb9d72e00a8c0d687d06e9c481f99cb236de4f2bf90997aca3`; engine: main-8626a35 engine tree 38af8b0cc4f3; repository commit: `None`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kog3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kog3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=126 digest=63f520e3318376ae`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24300000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 5 deals x 2 seats x 2 arms per pair; 9 pairs; **180 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| t-altaria | `decks/screen/opponents/t-altaria.txt` | c3a57b9c835b |
| t-hydreigon | `decks/screen/opponents/t-hydreigon.txt` | 18688bd9ab09 |
| draft-A-shark-tempo | `decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt` | 3f39092ba668 |

## Opponents

t-blaziken, t-lucario, t-suicune

## Held-out decks

Stage `dev`; held-out list `(none named yet)`, lock `on`. A development run refuses any held-out deck on either side.

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
