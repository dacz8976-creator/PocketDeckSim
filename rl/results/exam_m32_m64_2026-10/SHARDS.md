# The held-out exam of m32 and m64: the shard table (the coordinator picks the worker count and sends the briefs)

A slice is one held-out deck of one registration: 48 kx3 and 48 km3 games, 96 in all. There are 22 slices, 11 decks × 2 registrations
(`reg_m32`, `reg_m64`).

The estimated hours are play only, in a 4-core sandbox at the registered `--threads 2`. For each deck, the frozen kx3's laptop time on
it in the Oct 5 exam (48 games) is multiplied by:
- **2.1 for m32:** 4.2, the sandbox-to-frozen-laptop ratio m32 measured on the development decks (3.7 to 4.7), ÷ 2 threads;
- **3.9 for m64:** 4.2 × about 1.85 ÷ 2 = 3.885.

They are estimates until the first slices finish.

| deck (the `--only-deck` name) | group | frozen kx3, laptop h | m32 est. h | m64 est. h |
|---|---|---:|---:|---:|
| 02-arceus-crobat | middle | 3.6 | 7.6 | 14.0 |
| 08-garchomp-toolbox | middle | 3.3 | 7.0 | 12.9 |
| 07-skarmory-stall | setup | 3.2 | 6.7 | 12.4 |
| draft-C-meowstic-hatterene-v2 | setup | 3.0 | 6.3 | 11.7 |
| draft-D-entei-grimhound | fast | 2.9 | 6.1 | 11.3 |
| 12-ariados-whimsicott-ogerpon | fast | 2.9 | 6.1 | 11.2 |
| 04-absol-hoopa-darkrai | middle | 2.7 | 5.6 | 10.3 |
| 15-jolteon-oricorio-raticate | fast | 2.6 | 5.4 | 10.1 |
| 11-archaludon-haxorus-dragonair | setup | 2.6 | 5.4 | 9.9 |
| 14-comfey-raticate-hypno | fast | 2.3 | 4.8 | 8.8 |
| 13-a-ninetales-raticate | setup | 1.4 | 3.0 | 5.6 |
| **all** | | **30.4** | **64** | **118** |

## Rules for the layout

- **One registration per worker,** and **one stamp per worker.** A worker stamps one folder for all of its decks, repeating
  `--only-deck` once per deck, and plays them in that folder.
  - The stamp replays the 12-game self-checks before play.
  - That takes up to about 4 hours for m32 (the thinking-time stamps took 2.9 and 3.8) and about 7.5 for m64 (estimate) on a 4-core
    sandbox.
  - So every extra worker costs one more self-check of that length.
  - The harness plays a folder's decks in the registration's order, whatever order `--only-deck` names them in.
- The registered program must be rebuilt in the sandbox, exactly as in the thinking-time test:
  - claude/playout-pilot 172cbe9c, engine tree `69a5a4419da2`, harness source `bf9c5d6814007f1f`;
  - main's harness is unchanged since then.

  The collector admits the rebuild when its stamp's replayed digests equal the registration's: km3 `81b572198c04d5d1`, m32
  `869789a10142e83f`, m64 `724e581a9c51711f`.
- **A risk to decide before launch:**
  - m64's digest has so far been produced only by the laptop build. The thinking-time sandboxes replayed km3, m32 and m16, never m64.
  - m64 differs from m32 only by a parameter, so a mismatch is unlikely. But if it did happen, every m64 stamp would stop after about 7.5
    hours (about 75 sandbox hours), with no games played.
  - Either launch everything at once and accept the risk, or start one m64 worker first and the other m64 workers once its stamp shows
    `724e581a…`. The second option costs about 7.5 hours of wall time. The coordinator's call.
- **A deck is played by one worker only.** A deck whose worker stopped, or any extra slice, goes to a fresh worker with a fresh brief: a new
  worker name, its own folder and its own stamp, on the same registration. A sealed folder is never touched again.
- **The hand-off** goes to `rl/results/exam_m32_m64_2026-10/workers/`, one folder per worker, sealed.
  - The laptop re-checks each seal and commits each folder unchanged.
  - When a registration's 11 decks are in, the laptop merges it into its own folder:
    `split_collect.py merge --manifest .../reg_<s>/manifest.json --worker ... --out rl/results/exam_m32_m64_2026-10/reg_<s>`.

## A suggested layout: 14 workers, about 23 hours of wall time at most (build, stamp and play, estimates)

| worker | registration | decks | play est. h | + stamp |
|---|---|---|---:|---:|
| E1 | reg_m32 | 02-arceus-crobat, 11-archaludon-haxorus-dragonair | 13.0 | ~4 |
| E2 | reg_m32 | 08-garchomp-toolbox, 04-absol-hoopa-darkrai, 14-comfey-raticate-hypno | 17.4 | ~4 |
| E3 | reg_m32 | 07-skarmory-stall, draft-D-entei-grimhound, 13-a-ninetales-raticate | 15.8 | ~4 |
| E4 | reg_m32 | draft-C-meowstic-hatterene-v2, 12-ariados-whimsicott-ogerpon, 15-jolteon-oricorio-raticate | 17.8 | ~4 |
| E5 | reg_m64 | 02-arceus-crobat | 14.0 | ~7.5 |
| E6 | reg_m64 | 08-garchomp-toolbox | 12.9 | ~7.5 |
| E7 | reg_m64 | 07-skarmory-stall | 12.4 | ~7.5 |
| E8 | reg_m64 | draft-C-meowstic-hatterene-v2 | 11.7 | ~7.5 |
| E9 | reg_m64 | draft-D-entei-grimhound | 11.3 | ~7.5 |
| E10 | reg_m64 | 12-ariados-whimsicott-ogerpon | 11.2 | ~7.5 |
| E11 | reg_m64 | 04-absol-hoopa-darkrai | 10.3 | ~7.5 |
| E12 | reg_m64 | 15-jolteon-oricorio-raticate | 10.1 | ~7.5 |
| E13 | reg_m64 | 11-archaludon-haxorus-dragonair | 9.9 | ~7.5 |
| E14 | reg_m64 | 14-comfey-raticate-hypno, 13-a-ninetales-raticate | 14.4 | ~7.5 |

Sandbox time in all, for this layout:
- play: about 182 hours;
- stamps: about 91 hours (4 × 4 + 10 × 7.5);
- builds: about 1 hour each.

Other layouts trade wall time against stamps:
- **12 workers** (4 m32 + 8 m64): about 28 hours of wall time, with 15 fewer stamp hours. The m64 pairs would be 12 + 13, 04 + 14 and
  15 + 11.
- **22 workers** (one deck each): about 22.5 hours, hardly faster than 14, with about 36 more stamp hours.
