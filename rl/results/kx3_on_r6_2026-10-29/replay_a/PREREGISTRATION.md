# Pre-registration: kx3_replay_r6_2026_10_29_a

Written 2026-10-29T06:50:11Z, **before any game was played**. The manifest (`manifest.json`, sha256 `d2e44e11e247fa8e72924f82426e8c3c75567b9d7800b854cabc0fed60c642e2`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

THE SLOW REPORT'S R6 RE-PIN CHECK (rl/results/kx3_on_r6_2026-10-29/SPEC.md): do the frozen kx3's development-run games replay exactly on R6's engine? SPEC.md section 3 found no R6 change that can act in these games and names no row, so any changed game is a stop. This registration: 09-mega-manectric-heliolisk, 06-mega-blaziken-tournament-list, 10-xatu-oricorio-tr-weezing v the 8 panel lists, deals 0-1, seed_base 24400000000 (each key the development run's own seed).

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 (d513e37b's files, on main-affe56e): kx3 from claude/playout-pilot@d513e37b (frozen Oct 4-5), its six engine files byte for byte on R6's engine, whose km3 player files changed (fuel_credit.rs, value_functions.rs, public_pricing_player.rs, weighted_random_player.rs))
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; its self-check is the pinned km3's (81b572198c04d5d1))
- Program: `/home/dacz8976/kx_r4/strength` sha256 `23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378`; engine: laptop/kx3-on-r6-2026-10-29 e3ddc0149bb9d35fda1becbb17ab5f71d9461609 engine tree cd970db60aa5df7e9db9d7479e88f87190dab2c3 (the frozen kx3's six engine files, d513e37b's blobs, laid onto R6's release commit S affe56e88985e2997a66beb85efaca0c487617bd: main ffe97adb, the card-support refusal and the tests-only fold), built on the laptop 2026-10-29T04:13:47Z with rl/strength/build.sh (harness c4f7da21, STRENGTH_JOBS=2); self-checks measured on this program in the R6 night: km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa, equal to the slow-report pin's; repository commit: `b3de3e2841f9bc0a655d440d523c39ee2b38c277`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24400000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 2 deals x 2 seats x 2 arms per pair; 24 pairs; **192 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| 09-mega-manectric-heliolisk | `decks/dustin/09-mega-manectric-heliolisk.txt` | 48ca6b6c6aee |
| 06-mega-blaziken-tournament-list | `decks/dustin/06-mega-blaziken-tournament-list.txt` | 69c521a33339 |
| 10-xatu-oricorio-tr-weezing | `decks/dustin/10-xatu-oricorio-tr-weezing.txt` | a9cf8f1998a5 |

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
