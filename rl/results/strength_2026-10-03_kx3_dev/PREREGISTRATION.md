# Pre-registration: kx3_dev

Written 2026-10-03T03:18:14Z, **before any game was played**. The manifest (`manifest.json`, sha256 `3c8bac353ca09a23c2e5e872a964a3c4467c34ecd603cbeb4c27c9cbf2f5d54e`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

REALISTIC (the default knowledge mode). Does the play-out chooser kx3 (km3 proposes; every distinct legal move, up to 12, is played out 16 times to the end of the game with km3 on both sides, each play-out from a world sampled from what the pilot may see: the opponent's hidden cards drawn from a pool of 8 meta lists consistent with the cards and Energy types seen so far; it switches only on a paired lead beyond 2 standard errors) play Dustin's development decks better than km3 does, on the same deals against the 8 panel lists? Primary: the pooled paired difference in game score (win 1, tie 1/2, loss 0) with its 95% interval; every deck's and every pair's row printed; time per game reported as a fact. Development only: the held-out decks are locked out. Caveat stated in advance: the 8 panel lists are also the pool's lists, so once a few cards are seen the pilot's guess of the opponent narrows to the right list; against a deck outside the pool it would not. A LAB run (exact list told, labelled) can follow on these same deals.

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 from claude/playout-pilot@d513e37b (the cloud, Oct 2): reviewed once at f1aacbe2, fix round 1 verified (no blockers))
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it equals the pinned km3: step 10's 240 km3 games field for field v rl/engine-2026-10-02/deckgym, and self-check digest 81b572198c04d5d1)
- Program: `/home/dacz8976/kx/strength` sha256 `5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2`; engine: claude/playout-pilot d513e37b (after fix round 1) engine tree 31dbd2e6e8ec, built on the laptop Oct 2 (rl/strength/build.sh against that tree); KX_EXTRA_LISTS unset; repository commit: `15f30e49fbb5b665209a49e28fe469d621d73ba6`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`. The same pilot code on another build must print the same digest.
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
