# The kog engine switch (Sept 28): main-83e17ae → 233bced

**Dustin, Sept 28:** "Pin it now", with the last switch's conditions. On the rules-file refactor: "Accept it — with the proof pointed at the code that changed, because the 14,000-game replay mostly isn't." The general rule is in RUN5 "Rules" (a refactor of a rules file).

**What changes in engine/** (`git diff --stat 83e17ae 233bced -- engine`):
- Bot code: `players/mod.rs` and `players/value_functions.rs` (the kog, koh, kph and kt players).
- Rules files: `hooks/core.rs` and `hooks/mod.rs`, a refactor for kt's evaluator (ed81c8b, with line endings restored in 92c4563).
- Nothing else: `state/`, `models`, `actions` and `tools.rs` are unchanged.

## 1. The source equivalence, written down

Two independent readers checked it (the workflow `hooks-refactor-proof`, Sept 28). One read the diff hunk by hunk and one traced every caller. Both found every hunk behaviour-preserving, and neither refuted anything.

| Hunk | Change | Why the rules behave the same |
|---|---|---|
| `get_metal_core_barrier_reduction` (core.rs 716-740) | The body after the early return and the defender lookup moved verbatim into a private helper `metal_core_barrier_reduction`. | Token for token the same: the same `has_tool(…B2148MetalCoreBarrier) && pokemon_is_type(…Metal)` in the same short-circuit order, the same `50 × tool_count`, the same fall-through to 0, the same debug line. The early return and the `expect` stay in the wrapper, before the call. Its one caller (`finite_damage_reductions`) is unchanged. |
| `get_turn_effect_damage_reduction` signature (1198-1209) | A new `turn: u8` parameter. | The function is private. Its callers are the rules call site and kt's new hook. |
| Its body (1216) | `state.get_current_turn_effects()` became `state.get_turn_effects(turn)`. | `state/mod.rs` is byte-identical between the commits. `get_turn_effects(t)` is `turn_effects.get(&t).cloned().unwrap_or_default()`, and `get_current_turn_effects()` is the same with `t = self.turn_count`. `turn_count` is `u8`, like the new parameter, so there is no cast. Same map, key, clone and default. |
| The rules call site (1383-1391) | Passes `state.turn_count`. | With `turn = turn_count` the body computes what it did before. The other arguments are unchanged. |
| New `temporary_defender_reduction`, `permanent_tool_reduction` (1759-1821) | Two new functions, re-exported in `hooks/mod.rs`. | No rules code calls them. The only callers are kt's clock (value_functions.rs 1718-1720, behind kt's switch 1) and tests. They take `&State`, with no side effect beyond debug logging. |
| Tests (3311-3478) | `temporary_defender_reduction_tests` | `cfg(test)` only; not in the programs. |

**What reaches those paths** (the census, 85 deck files scanned):
- None of the 8 table lists carries Metal Core Barrier, Jasmine, Cheren, Blue, Adaman or Beast Wall. So the 14,000-game table replay ran the changed lines only on their "no cut" branch.
- **Carriers:** Dustin's deck 07 (Skarmory: 2 Barrier, 2 Jasmine); Dustin's deck 05 (Cheren); the gauntlet's Scizor list (2 Barrier); the upstream `engine/example_decks/metal-barrier.txt` (Barrier and Adaman, the only ReducedDamageForType card).
- No list anywhere carries Blue or Beast Wall. A 2-Blue test list was made for this check (`lists/blue_test.txt`: the panel Weezing list with its 2 Cyrus replaced).

## 2. The suite

The full suite at 233bced (`run_suite.sh`, its own target folder, `suite.log`): **1,975 passed, 0 failed** (101 test binaries).
- It includes the touched cards' own tests (`suite_touched_tests.txt`): Jasmine, Cheren, Blue, Beast Wall and Metal Core Barrier, plus the refactor's tests.
- The refactor's tests pin the new hook against `modify_damage` for the current turn, including a Metal-type turn effect (Adaman's kind).

## 3. The touched-path games (`run_touched.sh`, `compare_touched.py` → `touched_check.txt`)

Every game was played with the same seeds on the old official build (`rl/engine-2026-09-27`, main-83e17ae) and the new build (233bced). "Identical" means equal moves (every chosen move, hashed in order), decisions, openings, winner, points and seed.

| Games | Old v new | Reached the changed code on the board (watch-only counters) |
|---|---|---|
| The carrier lists (decks 07 and 05, the metal-barrier example, the 2-Blue test list) v the 8 panel lists, kp3, 500 deals per pairing (22,801,000,000+) | **16,000 of 16,000** | Barrier cut damage in 2,878 games (3,351 hits): deck 07 1,477, the example 1,401. A turn effect cut damage in 295 games: Jasmine 26 (deck 07), Cheren 12 (deck 05), Adaman 141, Blue 116. |
| The same with k3, 250 deals per pairing | **8,000 of 8,000** | |
| The Scizor coverage row's recorded files (made on an engine tree identical to 83e17ae) replayed on the new build, kp3 and k3 | **4,000 of 4,000** each | Barrier cut damage in 1,712 games (2,009 hits) |
| Dustin's recorded Skarmory (deck 07) commands on both builds (`count.py`, the sha256 of every chosen action per game): the floor check's block (seed 7,100) and the largest Jasmine block (seed 21,102,860,000) | **1,920 of 1,920** each | 50 and 39 Jasmine plays |

- **The watch-only counters changed no play:** the watch build equals the plain new build on all 16,000 carrier games and all 4,000 Scizor games (`instrument_reach.py`: counted only while the chosen move is applied, so the bots' lookahead isn't counted).
- The records of Dustin's recorded Skarmory blocks were on the Sept 25 engine, before the rules/09 repairs, so they weren't a valid baseline. The same commands were run on both current builds instead.
- **Not reached by any game:** Beast Wall (Ultra Beasts; no list carries it). Its path is the same changed line, and its own tests pass.

**Identity for the pin** (`pin_identity.txt`):
- k3 and kp3 over the table's 14,000 deals equal the official references, 14,000 of 14,000 each.
- kog3 equals the cloud's a823b6d table and the laptop's composition table, 14,000 of 14,000 each.
- `deckgym simulate` runs k3, kp3 and kog3 on seed 7,100, and goldfish `--coverage` runs.
- **Record of a stop:** the first identity pass stopped on a script bug, not a difference: an unquoted path with spaces broke the comparison call. The k3 games equalled the reference on every field. It was fixed and re-run (`PIN_STATUS.txt`).

**Result:** all three conditions of Dustin's Sept 28 ruling hold, so the refactor is accepted and the engine is pinned.
