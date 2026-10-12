# Pre-registration: kx3_replay_rules2_b

Written 2026-10-12T18:34:05Z, **before any game was played**. The manifest (`manifest.json`, sha256 `977afc71e565b14e14087f860847971b768ae122c8840336aaa5a90d7136a766`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

STEP 4's kx3 REPLAY CHECK after rules switch 2 (rl/results/kx3_on_rules2_2026-10/SPEC.md section 4): do the frozen kx3's development-run games replay exactly on the new engine, except deck 10 against t-weezing, where each changed game must show Will's new rule acting? This registration: 01-muk-glimmora-kingambit-regigigas, 05-indeedee-stoutland, draft-A-shark-tempo v the 8 panel lists, deals 0-1, seed_base 24440000000 (each key the development run's own seed).

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 from claude/playout-pilot@d513e37b (frozen Oct 4-5), its players byte for byte on main-c045ede's engine)
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; its self-check is the pinned km3's (81b572198c04d5d1))
- Program: `/home/dacz8976/kx_r2/strength` sha256 `76df495bef0b057fd28b4991dce76d3e3e1772667694161c945f17364f9c4e08`; engine: laptop/kx3-on-rules2 cd20a97a2e76897fae9883389cee4bf7ce5b3d97 engine tree 4ebb30a94173: the frozen kx3's players (d513e37b) on main-c045ede's engine (rules switch 2), built on the laptop Oct 12 with rl/strength/build.sh (harness bf9c5d68); self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa, equal to the slow-report pin's; repository commit: `e12342cd17f3c154cf8f4a1ca8a74c670552ebec`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24440000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 2 deals x 2 seats x 2 arms per pair; 24 pairs; **192 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
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
