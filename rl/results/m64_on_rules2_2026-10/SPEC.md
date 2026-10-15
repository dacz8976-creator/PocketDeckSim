# m64 on the current engine: the replay check (the spec; written Oct 14, before any build result or game)

**Why.**
- The held-out exam's fixed rule picked m64 (`../exam_m32_m64_2026-10/READING.md`).
- Dustin then decided (`../exam_m32_m64_2026-10/DECISION.md`):
  - keep the frozen kx3 for routine screening;
  - use m64 selectively, on deck questions he cares about;
  - **no slow-report pin change.**
- This check carries m64 to the current engine (rules switch 2), at low priority, so it is ready when he asks. It mirrors step 4
  (`../kx3_on_rules2_2026-10/SPEC.md`, READING 202 of 202 equal).
- **What it hands over for that later use:**
  - the program and its sha256, with its build record;
  - the full engine tree;
  - both self-check texts.

  Running a report with m64 then needs a small pin-safe option in the slow-report tool, or documented hand steps. `slow_report.py`
  accepts only the pinned program today, so that is a separate piece of work.

## 1. The source: m64's players on the current engine

- **m64:** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` from `claude/playout-pilot` 172cbe9c. The combined run and the exam played
  it on program f5a6ae95 (Oct 5 rules), with self-check `724e581a9c51711f`.
- **The merge:** `laptop/kx3cand-on-rules2` 9a0bc5ac, with parents 172cbe9c and c045ede0. Checked on Oct 14:
  - `engine/src/players/` is 172cbe9c's, byte for byte (tree 21ffbe5bd4aa).
  - Every other engine file is c045ede0's, apart from playout-pilot's examples and tests.
  - The engine tree is 5d557d350b6d3d69bbe739b57814ef9769ebdc1d.

## 2. The build and gate 1 (the laptop)

1. `rl/strength/build.sh 9a0bc5ac28ccf421044c3c68dc2779123b607bca /home/dacz8976/kx_r2c/strength`.
   - It must print the engine tree above and harness source bf9c5d68. Main's harness source is unchanged.
   - The cloud's parked label change, 70660ac5 and f068cbce, is not on main and must not be in this build.
2. **The self-checks are replayed by the first registration (section 3), not separately.**
   - km3 must print `81b572198c04d5d1`; a different digest is a stop.
   - m64 is expected to print `724e581a9c51711f`. Its self-check decks, t-altaria and t-suicune, hold no rules-switch-2 card, and the
     frozen kx3's self-check was unchanged by the switch.
   - **If m64's digest differs:** the difference is traced first, game by game. Go on only if it traces to a round-2 rule acting;
     anything else is a stop that goes to Dustin.

## 3. The replay check

- **What:** the combined run's m64 games (`../strength_2026-10-08_kx3_combined/`, arm X, the development decks on the development run's
  deals) are played again on the new build. Wailord is left out (Dustin, Oct 10).
  - `replay_a`: 09, 06, 10 v the 8 panel lists, deals 0-1, seed_base 24,400,000,000.
  - `replay_b`: 01, 05, draft A v the 8 panel lists, deals 0-1, seed_base 24,440,000,000.
  - `replay_c`: Will's row, 10 v t-weezing, deals 0-4, seed_base 24,420,070,000.
  - In all, 202 m64 games and 202 km3 games. That is 198 distinct keys plus 4 played twice: deck 10 v t-weezing, deals 0-1, are in
    both replay_a and replay_c.
  - `make_replay_configs.py` asserts that every key gets the combined run's own seed. It reads the program's build record for the tree
    and the harness.
- **Registration (the laptop):** `replay_a` first, and its self-check digests are read before the other two are registered. Each
  registration replays m64's 12-game self-check (about 5 h on the laptop), so allow about 10-11 h in all.
- **Comparison:** `compare_replay.py`, committed before any game.
  - It compares each slice's games with the combined run's games on the same keys, content without timing (`split_collect.py`'s
    `content`).
  - It also checks that the 4 keys played twice match each other.

**Reading, fixed now:**
- **km3:** all 202 games must equal the combined run's, Will's row included. km3's code is the same in both builds, and step 4's km3
  replayed all 202. Any km3 difference is a build fault.
- **m64:** every game must be equal, except on deck 10 v t-weezing.
- **On Will's row,** a changed m64 game passes only if a revert check gives back the old move. That means turning Will's new rule off
  for the first differing decision, as in 8c's revert driver.
  - The tracing tools must be rebuilt on 9a0bc5ac and 172cbe9c (8c's were built on an engine without the playout players).
  - A change the revert check can't settle is a judgment call that goes to Dustin.
- **Any other change is a stop that goes to Dustin,** with its first difference traced.
- **If everything holds,** m64 on the current engine plays as m64 did, wherever the new rules don't change games. On the development
  decks that is everywhere but Will's row. The exam's result carries in the same sense.

**Where and cost (Managed Agents; Fable launches):**
- **Brief:** start from the exam's `../exam_m32_m64_2026-10/WORKER_BRIEF_MA.md`, which covers m64's long stamp and digest, with:
  - branch `laptop/kx3cand-on-rules2`;
  - tree 5d557d35…;
  - program `$HOME/kx_r2c/strength`;
  - one registration per worker.
- **Play,** in worker hours at 2 threads (estimated from the laptop's m64 time × 2.75): deck 01 about 12.4, 05 10.8, draft A 5.6,
  10 4.4, 09 4.0, 06 3.4, replay_c 0.6. About 41 worker hours in all.
- **Stamps:** each worker's m64 stamp took 5-11 h in the exam, build included.
- **Layout:** about 4-5 workers, one registration each. replay_b can be split by deck across two or three workers; replay_c is played
  on the laptop with the registered program. Wall time about 18-24 h. Cost roughly $10-15.

## 4. Order and who

1. The build; the registrations with their self-checks (replay_a first); the comparison script; SHARDS.md. The laptop, about 11-12 h.
2. The shards: Fable, on Managed Agents.
3. replay_c, the seal checks, the merges, the comparison, the reading and the report: the laptop.

## 5. The pin: not moved (Dustin, Oct 14)

No pin change. Moving it would also have needed:
- full 40-character `engine_ref` and `engine_tree`;
- the `_note` and `reference_provenance` texts;
- the `selfcheck` key renamed from `kx3`;
- `test_slow_report.py`'s hard-coded kx3 pin values (its lines 505-517) updated;
- the README's cloud-route section updated;
- a self-check record committed.

It is recorded here only so that a later pin-safe m64 option knows what the pin binds.

Files: `SPEC.md` (this), `make_replay_configs.py`, `compare_replay.py`, `configs/`, and later `replay_*/`, `SHARDS.md`, `workers/`,
`READING.md`.
