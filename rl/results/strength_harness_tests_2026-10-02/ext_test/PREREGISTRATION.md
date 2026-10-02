# Pre-registration: ext_test

Written 2026-10-02T19:53:26Z, **before any game was played**. The manifest (`manifest.json`, sha256 `3ebcee893d5a47936b15dbe0ba59d9840fb4ed36235ef7e2b97084882fb5b502`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

Protocol test: the example external pilot (prefers an attack) against km3.

## Pilots

- **Pilot under test (arm X):** `ext:python3 rl/strength/ext_pilot_example.py attack`
- **Reference (arm ref, and the opponent in both arms):** `km3`
- Program: `None` sha256 `None`; engine: None; repository commit: `None`
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24300000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 3 deals x 2 seats x 2 arms per pair; 1 pairs; **12 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| t-altaria | `decks/screen/opponents/t-altaria.txt` | c3a57b9c835b |

## Opponents

t-blaziken

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
