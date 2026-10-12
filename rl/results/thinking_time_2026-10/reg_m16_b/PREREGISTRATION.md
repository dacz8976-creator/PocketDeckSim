# Pre-registration: kx3_think_m16_b

Written 2026-10-11T21:28:20Z, **before any game was played**. The manifest (`manifest.json`, sha256 `61e61f3e0a7fe0959fbd53651f6a72fe27e0239774103ca7039d1df2b2989002`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

THE THINKING-TIME TEST, setting m16, slice b (coordinator, Oct 11; PLAN.md in rl/results/thinking_time_2026-10/). How much of the combined candidate's gain over the frozen kx3 does kx3 with `_tools _zs3` and no close-call extension (16 play-outs) keep, on the development decks without Wailord (Dustin, Oct 10)? This slice: 01-muk-glimmora-kingambit-regigigas, 05-indeedee-stoutland, draft-A-shark-tempo, seed_base 24440000000 (each key gets the development run's own seed). PRIMARY and the reading are fixed in PLAN.md before any game.

## Pilots

- **Pilot under test (arm X):** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3` (kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3 from claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219: the combined candidate's code (_tools _zs3) with no _m (no extension); the same program as the combined run (the suffixes are the pilot code's parameters))
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it must equal the pinned km3 (self-check 81b572198c04d5d1) and replay the development run's ref games)
- Program: `/home/dacz8976/kxc/172cbe9c/strength` sha256 `f5a6ae95051c0c673d45a6a8be9d6d840827a97bbb2feaaa0fccb4cbb8076b58`; engine: claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 engine tree 69a5a4419da2 (kx3 with the Tool rule, the skip bar and close calls as fixed after the laptop's reviews; ties join a running extension but never start one), built on the laptop Oct 8 with rl/strength/build.sh (main's harness source bf9c5d6814007f1f); gate 1 here: km3 240/240 v the official program, km3 81b572198c04d5d1, the lab form kx3_r2_c3_lab_tools_zs3_m64 8c1244aec5c8419d as in the cloud's gate 1, suite passed with 0 failed; at 54209409 the same build steps gave the frozen code 31d638dbc818b0fa and the Tool code c426e4c860e836ed (the code with every new suffix off is unchanged); KX_EXTRA_LISTS unset; repository commit: `1b11c13cad709ebc4cd0185b97b1a1a78792c182`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3 games=12 seat0_wins=7 seat1_wins=5 ties=0 turns=136 digest=480a2a2240c3c90a`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24440000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 5 deals x 2 seats x 2 arms per pair; 24 pairs; **480 games in all**.
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
