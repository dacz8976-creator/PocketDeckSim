# Pre-registration: kx3_tools_gate3

Written 2026-10-06T18:18:06Z, **before any game was played**. The manifest (`manifest.json`, sha256 `23e7919db085a842a232b83046a69f0e746beec84541f954b476654dc4027168`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

GATE 3 of the Tool rule (Fable via Dustin, Oct 5 and Oct 6, amended; rl/results/playout_tool_rule_2026-10-06/README.md): a first paired cut. Does kx3 with the Tool rule play development decks 01, 10, 06, 05 and 03 better or worse than kx3 without it? With `_tools` the rule works in two places: (1) in the play-outs, on both sides, a Tool is attached only where its printed effect can apply (where no placement has an effect, km3's choice stands); (2) at kx3's own decision, a within-noise tie-break: every placement stays in the pool and is played out; only when no move clears the z bar, and km3's proposed placement has no printed effect now while another placement has one, kx3 plays the placement with an effect that km3 prefers (trace: 'tie-break: Tool effect'), unless km3's placement leads it beyond the noise. km3 itself is untouched. The pilot is the development run's kx3 (REALISTIC, the pool's 8 meta lists, 16 play-outs, cap 12, z 2) plus the rule. ONLY DECKS 01, 10, 06, 05 AND 03 ARE PLAYED (--only-deck, 800 games: 400 kx3, 400 km3). The manifest lists the seven development decks in the development run's order, with its seed_base, so every deal is that run's (strength_2026-10-03_kx3_dev) and the rule-off arm is that run's X arm, already played. Build check: every reference game here (km3 v km3) must replay the development run's game for game, or the pairing is void. Primary: rule on - rule off in game score (win 1, tie 1/2, loss 0) on the same (deck, opponent, deal, seat), mean +- 1.96 sd/sqrt(n), per deck and pooled, read by pair_with_dev.py in this folder (byte copy of claude/playout-pilot 11b4836a:rl/results/playout_tool_rule_2026-10-06/gate3/pair_with_dev.py). The harness's own report (kx3 with the rule - km3) is context. Stated in advance: 80 paired games a deck is a first cut; it can show a large harm, not a small gain.

## Pilots

- **Pilot under test (arm X):** `kx3_r16_c12_z2_real_t0_poolmeta_tools` (kx3_r16_c12_z2_real_t0_poolmeta_tools from claude/playout-pilot (engine/src as of dcd703d5): the development run's kx3 plus the Tool rule in the play-outs and the within-noise tie-break at its own decision; gates 1 and 2 in the cloud (rl/results/playout_tool_rule_2026-10-06/README.md))
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it must equal the pinned km3 (self-check 81b572198c04d5d1) and replay the development run's ref games)
- Program: `/home/dacz8976/kx/strength_tools` sha256 `cf73b2a4e858eb47fce6e686d8c211350d65a23e2720d3d80af48f892bdad81c`; engine: claude/playout-pilot 11b4836a engine tree 7ff2ceb93b25 (the Tool rule in the play-outs and the within-noise tie-break at kx3's own decision), built on the laptop Oct 6 with rl/strength/build.sh; km3 240/240 v the official program; self-checks km3 81b572198c04d5d1, pilot c426e4c860e836ed; KX_EXTRA_LISTS unset; repository commit: `ce8f459716a6f9ea616db5869a5a6496fa81a493`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3_r16_c12_z2_real_t0_poolmeta_tools` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3_r16_c12_z2_real_t0_poolmeta_tools games=12 seat0_wins=6 seat1_wins=6 ties=0 turns=139 digest=c426e4c860e836ed`. The same pilot code on another build must print the same digest.
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
