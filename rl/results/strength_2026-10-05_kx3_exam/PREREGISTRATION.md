# Pre-registration: kx3_exam

Written 2026-10-05T08:58:37Z, **before any game was played**. The manifest (`manifest.json`, sha256 `8a8397678cdb5a5df58a881714bcc4d22932b28f14158e1f5e4925a72ad694ad`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

THE FINAL EXAM of the frozen play-out pilot (kx3 as in claude/playout-pilot d513e37b, 'a promising experimental baseline, not the finished planning bot'). Does kx3 play Dustin's held-out decks (the 11 never used in development) better than km3 does, on fresh deals against the 8 panel lists, REALISTIC knowledge? Primary: the pooled paired difference in game score (win 1, tie 1/2, loss 0) with its 95% interval, over 528 paired comparisons (1,056 games); a second figure weights every deck equally. It measures overall improvement across player decks the pilot was not developed on. Six comparisons per matchup (3 deals x 2 seats) don't support ranking individual matchups; the per-pair rows are printed for completeness only. The panel lists are in the pilot's guessing pool, so this answers 'against the public meta lists', not 'against unknown decks'. Time per game reported as a fact. Approved by Dustin Oct 4 ('yes approved'), conditional on the k3 check's pre-recorded rule and the d513e37b replay check (strength_2026-10-04_kx3_v_k3/PREREGISTRATION.md, addendum).

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 from claude/playout-pilot@d513e37b, frozen Oct 4-5)
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it equals the pinned km3 (step 10's 240 games field for field, self-check 81b572198c04d5d1))
- Program: `/home/dacz8976/kx/strength` sha256 `5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2`; engine: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec (the frozen, tested development build), built on the laptop Oct 2; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa; KX_EXTRA_LISTS unset; repository commit: `cb425ca46f4873590a76698287f0c0db08d806ff`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`. The same pilot code on another build must print the same digest.
- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24500000000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 3 deals x 2 seats x 2 arms per pair; 88 pairs; **1056 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| 02-arceus-crobat | `decks/dustin/02-arceus-crobat.txt` | 8982742aa901 |
| 04-absol-hoopa-darkrai | `decks/dustin/04-absol-hoopa-darkrai.txt` | a4355e7fdb71 |
| 07-skarmory-stall | `decks/dustin/07-skarmory-stall.txt` | 62006b682027 |
| 08-garchomp-toolbox | `decks/dustin/08-garchomp-toolbox.txt` | 564575a6e2c0 |
| 11-archaludon-haxorus-dragonair | `decks/dustin/11-archaludon-haxorus-dragonair.txt` | 73eb2872cbf2 |
| 12-ariados-whimsicott-ogerpon | `decks/dustin/12-ariados-whimsicott-ogerpon.txt` | 4d059bd2c5cb |
| 13-a-ninetales-raticate | `decks/dustin/13-a-ninetales-raticate.txt` | f79ad459a118 |
| 14-comfey-raticate-hypno | `decks/dustin/14-comfey-raticate-hypno.txt` | 8e6296a40e3d |
| 15-jolteon-oricorio-raticate | `decks/dustin/15-jolteon-oricorio-raticate.txt` | 402094a1979d |
| draft-C-meowstic-hatterene-v2 | `decks/brews/drafts_2026-10-01/draft-C-meowstic-hatterene-v2.txt` | 946462dd9e4c |
| draft-D-entei-grimhound | `decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt` | 31035755a6d0 |

## Opponents

t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing

## Held-out decks

Stage `heldout`; held-out list `['02-arceus-crobat', '04-absol-hoopa-darkrai', '07-skarmory-stall', '08-garchomp-toolbox', '11-archaludon-haxorus-dragonair', '12-ariados-whimsicott-ogerpon', '13-a-ninetales-raticate', '14-comfey-raticate-hypno', '15-jolteon-oricorio-raticate', 'draft-C-meowstic-hatterene-v2', 'draft-D-entei-grimhound']`, lock `off`. A development run refuses any held-out deck on either side.

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
