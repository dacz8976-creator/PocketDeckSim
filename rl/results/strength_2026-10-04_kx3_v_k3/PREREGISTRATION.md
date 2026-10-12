# Pre-registration: kx3_v_k3

Written 2026-10-04T14:19:30Z, **before any game was played**. The manifest (`manifest.json`, sha256 `b1bd74601de31995a50996ef033c50a0235aecee2f21cb75155a2efcb97a9824`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

Run A (kx3 on the deck, k3 the opponent and the reference). The exploit check of the kx3 development result (+16.6 +- 3.5 against km3, rl/results/strength_2026-10-03_kx3_dev). kx3 plays its play-outs with km3 on both sides, so against a km3 opponent its model of the opponent is exact. Here the opponent is k3, a different pilot, on the first 3 of the same deals (same seeds, both seats). Two paired runs share their reference arm (k3 v k3): run A has kx3 on the deck, run B has km3 on the deck. The pre-registered reading is the per-deal difference between the two runs' X arms, kx3 minus km3 against k3, pooled with mean +- 1.96 sd/sqrt(n) and printed per deck; each run's own report is read too. If the gain against k3 is near the gain against km3, kx3's edge is not just exploiting km3; if it is much smaller, part of it was. REALISTIC mode; development decks only; held-out decks locked out.

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 from claude/playout-pilot@b96296a5)
- **Reference (arm ref, and the opponent in both arms):** `k3` (k3 in the same build (the original depth-3 pilot, a different scoring formula from km3))
- Program: `/home/dacz8976/kx2/strength` sha256 `4f6fa88af31dd689dc76820e157aaffb6968a2d89bcb172df90354de7c061a42`; engine: claude/playout-pilot b96296a5 (fix round 2) engine tree, built on the laptop Oct 3-4; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa (equal to the d513e37b build), suite 2,042/0; KX_EXTRA_LISTS unset; repository commit: `5aa09f60ca95f6b15c83a6dd0a6471d28ae9fed8`
- Self-check of `k3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=k3 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=121 digest=bd62fa9645b3002d`. The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24400000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 3 deals x 2 seats x 2 arms per pair; 56 pairs; **672 games in all**.
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

## Addendum, Oct 4: the freeze rule, the build question and the exam

Written while run A was still playing, before any of its result was read. Run B's own report (km3 v k3) had been seen.

Dustin approved the conditional freeze, verbatim "yes approved" (relayed by the coordinator, Oct 4). Astra's three
tightenings are conditions of that approval, and they are written here.

1. **The rule.**
   - The reading is kx3 minus km3, both facing k3, pooled over the same deals (`analyze_kx_minus_km.py` in this folder,
     committed with this addendum).
   - 95% interval above zero: **freeze**.
   - Interval crossing zero: **hold the exam**. The check is inconclusive; it does not mean "the play-out policy failed".
   - Interval below zero: **hold**. kx3 played worse than km3 against k3.
   - Either way, the size is reported beside the development run's +16.6 ± 3.5.
2. **The freeze names d513e37b.** That is the tested development build (+16.6 ± 3.5,
   `../strength_2026-10-03_kx3_dev/`). The exam program is the strength harness built from d513e37b's engine tree on the
   laptop (`/home/dacz8976/kx/strength`, sha256 `5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2`).
   - Run A used b96296a5, whose kx3 self-check equals d513e37b's (`31d638dbc818b0fa`).
   - In what kx3 plays, the code differs in one path only. When a decision has more than 12 distinct moves AND the
     world the cap ranks them in panics, d513e37b keeps km3's move and b96296a5 plays out the first 12 moves in the order
     offered.
   - b96296a5's other changes don't touch REALISTIC play here:
     - `KX_EXTRA_LISTS` refuses brew copies by content, but the variable is unset in these runs;
     - the opponent's list is now held only for LAB;
     - the rest are test changes.
   - **Before the exam, a replay.** With the d513e37b program, replay 56 of run A's kx3 games: deal 0, seat 0, every
     pair, same seeds. Every one must equal run A's game: winner, points, turns, plies and every logged decision. If any
     differs, hold, and rerun the k3 check on d513e37b.
3. **The exam, stated honestly.**
   - 11 locked decks × the 8 panel lists × 3 deals × 2 seats: 528 paired comparisons, 1,056 games.
   - It runs REALISTIC, on deals no development run used.
   - It measures overall improvement across player decks the pilot was not developed on.
   - Six comparisons per matchup don't support ranking individual matchups. The exam's page says so.
   - The panel lists are in the pilot's guessing pool, so it answers "against the public meta lists", not "against
     unknown decks".
   - The frozen version is labelled **a promising experimental baseline, not the finished planning bot**: the examples
     show no clear multi-turn planning yet (`../playout_pilot_positions_2026-10-04/`).
   - The official engine stays unchanged.
   - If the exam runs into a class morning, it is stopped by 7:00 am and resumed afterwards; it is resumable.