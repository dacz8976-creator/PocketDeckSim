# Step 4 after rules switch 2: kx3 and the slow report on the new engine (the spec; written Oct 12, before any build)

The release package (`../engine_switch_rules2_2026-10/RELEASE_PACKAGE.md` lines 45-49) says that after the update, kx3 is rebuilt on the
new engine and checked, that its games should replay exactly except deck 10 against t-weezing (Will), and that the slow report's pinned
program is rebuilt, its self-checks replayed, and pinned again. Brew 07's and 09's slow reports wait for the new pin.

## 1. The source: the frozen kx3's players on the new engine

- **The frozen kx3** is `claude/playout-pilot` at d513e37b (engine tree 31dbd2e6; `rl/strength/slow_report_pin.json`). Its changes to `engine/`
  since its merge base with main are in `engine/src/players/`, `engine/examples/` and `engine/tests/` only. Rules switch 2 changed 26 other
  engine files (`../engine_switch_rules2_2026-10/allowed_engine_files.tsv`) and left `engine/src/players/` unchanged. On Oct 12 no engine
  file was changed on both sides (main v the playout-pilot tip, from their merge base 6f474582).
- **The merge:** a new branch `laptop/kx3-on-rules2`, holding one merge commit with parents d513e37b and main's pin merge c045ede0, made
  with `git merge-tree --write-tree`. It stops if there is any conflict, or if any engine file differs from both sides' own version.
- **Checks on its `engine/`:** `engine/src/players/` is d513e37b's, byte for byte. Every other engine file is c045ede0's, except the
  examples and tests that only playout-pilot added. `Cargo.lock` and `Cargo.toml` equal both sides', or the difference is listed and
  explained before the build.
- **What can go wrong:** the players code may call engine functions whose signatures round 2 changed. If it does, the build fails; that
  is a stop that goes back to the laptop with the compiler's errors, and no edit is made without a review.

## 2. The build, gate 1 and the self-checks (the laptop, an evening at home: about 1.5 h)

1. `rl/strength/build.sh laptop/kx3-on-rules2 /home/dacz8976/kx_r2/strength`. Record the engine tree, the program sha256 and the harness
   source; the harness is expected to stay bf9c5d68, since main's harness is unchanged.
2. **Gate 1:** km3 in this build plays as the official engine does. Its 12-game self-check must print `81b572198c04d5d1`, the pinned km3:
   step 7 of the switch replayed every pilot's identity games equal, and km3's self-check decks, t-altaria and t-suicune, hold no
   round-2 card. A different digest is a stop.
3. **kx3's self-check** (12 games, one core, about 45-50 min on the laptop and about 2.7 times that in a sandbox): expected equal to the
   pin's kx3 text, for the same reason. If it differs, that is not a failure by itself, since the rules changed. But the pin's text can't
   be kept, so the difference is traced before any new pin: which of the 12 games differ, and whether a round-2 counter fired in them.
4. **A self-check record**, written by `slow_report.py --selfcheck-only --program /home/dacz8976/kx_r2/strength` and committed, so a cloud
   rebuild of the same sha256 can register without a replay (the merged self-check branch).

## 3. The new slow-report pin

`rl/strength/slow_report_pin.json`, rewritten:
- `program`, `program_sha256` and `selfcheck_measured_on_sha256`: the new build;
- `engine_ref`: the merge commit, with its `engine_tree`;
- the `engine` and `pilot_provenance` texts: "kx3 from d513e37b's players on main-c045ede's engine";
- `harness_source_sha256`: as printed by the build;
- the self-check texts: kept only if both digests are equal (step 2). Everything else (seed block, reserved seeds, panel, scrub list) stays
  as it is.
Committed only after the laptop's own check of the diff. The old pin goes into the record as superseded. No slow report is in flight on
the old pin (the coordinator, Oct 11: the Sonnet runners are idle until the re-pin), so none is cut off. Then brew 07, brew 09, deck 13 and
draft D can be registered.

## 4. kx3's replay check

- **What:** the development run's kx3 games (`../strength_2026-10-03_kx3_dev/`, 7 decks, frozen kx3) played again on the new build.
  - The sample is deals 0 and 1 of every deck, opponent and seat: 224 kx3 games and 224 km3 games.
  - Every game of deck 10 against t-weezing is added: 10 kx3 games, Will's row.
- **How:** a new registration that is the development run's config with the new program, engine and `--repo .`. Same decks, order,
  opponents, seed_base and pair stride, with `deals` 2. Deck 10 v t-weezing's 5 deals go in a second registration. Seeds follow
  each deck's and opponent's place in the lists (`rl/strength/src/main.rs:229-233`), so that registration lists deck 10 alone and
  t-weezing alone, with seed_base 24,400,000,000 + (2 × 1,000 + 7) × 10,000 = 24,420,070,000. That gives exactly the development run's
  seeds; its deals 0-1 repeat the sample's, which does no harm. The new games are compared by key with the development run's, using `split_collect.py compare` and content without
  timing.
- **Reading, fixed now:**
  - Every pair must be equal, except deck 10 v t-weezing.
  - There, each changed game must show Will's new rule acting (round 2's `will_*` counters at or before the first difference), or kx3
    seeing it in its search. The tracing tools are 8c's: `../engine_switch_rules2_2026-10/8c/`.
  - Any other change is a stop that goes to Dustin.
- **Where:** sharded by deck on Managed Agents sessions, on the laptop's registration; the brief is `../thinking_time_2026-10/WORKER_BRIEF_MA.md`,
  with this registration's names. In a sandbox this takes about 224 × 280 s × 2.7 ≈ 47 game-hours, about 7 h each on 7 workers.

## 5. Order and who

1. The merge commit, the build, gate 1, both self-checks, the record and the pin draft: the laptop, an evening at home.
2. The pin, after the laptop's check, and step 4's registration.
3. The shards: the coordinator, on Managed Agents.
4. The compare, the reading and the report to Dustin: the laptop.
5. The slow reports for brew 07, brew 09, deck 13 and draft D, on the new pin.
