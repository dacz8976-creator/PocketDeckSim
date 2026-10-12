# Pre-registration: kx3_combined_v_frozen

Written 2026-10-08T03:27:37Z, **before any game was played**. The manifest (`manifest.json`, sha256 `16fe75ad9e7c30a776202a2023d6f2b6b1e92be0189ab90928bec4029dd27c9a`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

THE COMBINED CANDIDATE against the frozen kx3 (coordinator, Oct 7; Dustin chose the full run, Oct 7; rl/RUN5.md). Does kx3 with `_tools _zs3 _m64` together play Dustin's 7 development decks better or worse than the frozen kx3 (d513e37b, the development run's pilot)? `_tools`: the Tool rule in the play-outs and the within-noise Tool tie-break at kx3's own decision (gate 3: +0.2 +- 1.5 against the rule off). `_zs3`: a switch away from km3's attack to a line that attacks this turn in fewer than half of its play-outs needs a lead of 3 standard errors, not 2. `_m64`: where the best moves are within the bar the decision will use after 16 play-outs, the best, the close moves and km3's move play on to 64 on the same worlds, and the decision is made once, at the end (claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219; README rl/results/playout_close_calls_2026-10-07/README.md, the fix round). km3 is untouched. The manifest lists the seven development decks in the development run's order with its seed_base, so every deal is that run's (strength_2026-10-03_kx3_dev) and the frozen arm is that run's X arm, already played; this run plays the candidate (arm X) and km3 (arm ref) on all 7 decks: 1120 games = 560 kx3 games + 560 km3 games. Build check: every reference game here must replay the development run's game for game, or the pairing is void. PRIMARY: candidate - frozen in game score (win 1, tie 1/2, loss 0) on the same (deck, opponent, deal, seat), mean +- 1.96 sd/sqrt(n) over the 560 pairs, read by pair_combined.py in this folder; also every deck weighted equally, per group (fast 09, 06, 10; setup 03, 01, 05; draft A in the middle) and per deck, with pace (turns per game, first-attack own turn). READING, fixed now: if the pooled interval is entirely above zero, the candidate is recommended as the next frozen candidate (Dustin's word), and the held-out exam re-run decides; otherwise the frozen kx3 stays. A deck whose interval is entirely below zero is REPORTED, not a veto. Also reported, per arm: km3-attack skip turns per game (the deck's own turns where km3 proposed an attack, kx3 played something else and no attack followed that turn; trainer_habits scripted --attack-scan on the candidate arm, the existing scan for the frozen arm), the share of games with one or more, and the win rate of games with v without. Time is quoted for kx3 games only. A halfway look (the first 280 kx3 games' pairs, whatever decks they are) is shown to Dustin for information only; nothing is decided on it.

## Pilots

- **Pilot under test (arm X):** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` (kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64 from claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219: the development run's kx3 (REALISTIC, the pool's 8 meta lists, 16 play-outs, cap 12, z 2) plus the Tool rule (gate 3), the skip bar and close calls as fixed after the laptop's review; gates 1-2 in the cloud (rl/results/playout_close_calls_2026-10-07/README.md), gate 1 on the laptop)
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it must equal the pinned km3 (self-check 81b572198c04d5d1) and replay the development run's ref games)
- Program: `/home/dacz8976/kxc/172cbe9c/strength` sha256 `f5a6ae95051c0c673d45a6a8be9d6d840827a97bbb2feaaa0fccb4cbb8076b58`; engine: claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 engine tree 69a5a4419da2 (kx3 with the Tool rule, the skip bar and close calls as fixed after the laptop's reviews; ties join a running extension but never start one), built on the laptop Oct 8 with rl/strength/build.sh (main's harness source bf9c5d6814007f1f); gate 1 here: km3 240/240 v the official program, km3 81b572198c04d5d1, the lab form kx3_r2_c3_lab_tools_zs3_m64 8c1244aec5c8419d as in the cloud's gate 1, suite passed with 0 failed; at 54209409 the same build steps gave the frozen code 31d638dbc818b0fa and the Tool code c426e4c860e836ed (the code with every new suffix off is unchanged); KX_EXTRA_LISTS unset; repository commit: `2bfb1b7391797f5799312703b347f39ae8545a56`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=132 digest=724e581a9c51711f`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24400000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 5 deals x 2 seats x 2 arms per pair; 56 pairs; **1120 games in all**.
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
