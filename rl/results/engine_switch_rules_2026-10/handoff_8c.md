# The hand-off for step 8c: the changed games of steps 8b and 8

Rebuilt by sitting2.sh (`sitting2_check.py handoff`) at every checkpoint from the per-scan-set rows (`handoff_<step>_<bot>.tsv`); every changed game is a row of `handoff_8c.tsv`. Nothing here is a verdict: 8c (the cloud's traces, Sonnet reading every hand trace) decides each row by the rule below.

**CONDITION 3 (PLAN.md:95: such games must be identical): 1 games (changed, coin_full_prevention fired, no reach counter fired); a ruling is needed before the pin.**

## Totals

Every changed game needs its first difference placed (tick k, its turn, the cause tick), not only the rows with no reach counter: a counter that fired after k, or in an earlier turn other than the cause tick, explains nothing.

| step | bot | changed games (each traced to its first difference) | with different moves | no reach counter anywhere | CONDITION 3: coin_full_prevention fired, no reach counter |
|---|---|---:|---:|---:|---:|
| 8b | km3 | 32 | 32 | 3 | 1 |
| 8b | k3 | 31 | 31 | 0 | 0 |

Changed games in which each exact counter fired (anywhere in the game; 8c places it against the first difference):

| step | bot | vs_confusion_first_built | coin_cut_recorded | coin_full_prevention | coin_queued_offered | coin_queued_offered_any | vs_confused_choice_chosen | vs_confused_choice_offered |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 8b | km3 | 8 | 0 | 17 | 21 | 21 | 6 | 6 |
| 8b | k3 | 8 | 0 | 17 | 23 | 23 | 7 | 7 |

## The engines

- **old**: the official engine, main-d363ba8 (engine/ tree 9c84fef), the pinned programs `rl/engine-2026-09-30/`
  (legality_scan sha256 fe244ecd92e159706c1ee0fc9933037e87d885c4a1cb9b4f37ee7adf96067be1).
- **new**: the candidate 5a18d31657897545a9eaaf849c9d0cb5b0a08ffa (main c9f4224 + R f8cfa9c; engine/ = R's tree 38af8b0), built by sitting 1:
  `programs.sha256` (the plain legality_scan) and `watch.sha256` (the watch build, both F5 instrument scripts).

## The tracer and the probes

`vs_trace.rs` at the candidate, `5a18d31:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs`,
built as an example in a scratch copy of each engine. It sets a game up as legality_scan's `--pairs` row does
(seed = seed base + pairing x 10,000 + i; even i puts the first-named deck in seat 0), with the same bot in both seats:
`vs_trace --a <held_file> --b <panel_file> --seed-base 23100000000 --pairing <P> --bot <bot> --deals <i>,<i>,...`
- **Pass each row's own bot** (its `bot` column: km3 or k3). vs_trace defaults to kog3, and so do `coin_probe.rs`
  and `coin_lookahead.py`: a trace or probe under the default bot is another game.
- **Check each trace's last line** (legality_scan's move fingerprint) against the row's old_moves (the old engine's
  trace) and new_moves (the candidate's) before reading anything else from it: a trace that does not reproduce its
  game explains nothing.
- **The probes:** `vs_probe.rs` for A, at the candidate,
  `5a18d31:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_probe.rs`; `coin_probe.rs` and `coin_lookahead.py`
  for B, in `rl/results/engine_switch_rules_2026-10/` at the candidate (again with the row's bot).
- **Rows with moves_differ = no** (the games differ only in points, winner or another field, with the same moves):
  their two traces can agree tick for tick, and then `first_difference` returns kind "length" (no tick to look at),
  which the rule reads as UNEXPLAINED. Look at those rows' state hashes and final boards by hand.

## The classifier

`tightened_rule.py` at the candidate, `5a18d31:rl/results/engine_switch_rules_2026-10/tightened_rule.py`
(first_difference, counter_hits; the coordinator accepted its reading, Oct 1). Its loaders key games by i alone
(`load_trace`: one game per i), so trace one pairing per folder, or adapt the loader to (pairing, i).

## The files

The rows: `handoff_8c.tsv` (columns: step, bot, pairing, i, seed, held_file, held_blob, panel_file, panel_blob, old_moves, new_moves, moves_differ, differing_fields, old_winner, new_winner, old_points, new_points, exact_counters, superset_counters, vs_confused_choice, offgate_counters, no_reach_counter, full_prevention_only). exact_counters and offgate_counters are compact JSON with every firing tick of each counter that fired; superset_counters holds the three superset counts; vs_confused_choice holds that count and vs_confused_choice_first (its own name: not a superset counter, not reach). no_reach_counter is yes when none of the six reach counters fired; full_prevention_only is yes for a CONDITION 3 row. The games (legality_scan --games-out, sha256):

- `engine_switch_rules_2026-10/5a18d31_8b_old_km3.jsonl`: 160 games, sha256 e1c69f02714ae3e907891458e7665632556cbc3039f32e42a2fb4e148e2f9125
- `engine_switch_rules_2026-10/5a18d31_8b_new_km3.jsonl`: 160 games, sha256 bf5405377a887ac9afb379b1a45573647720c07928ea989b1d56698c07577eff
- `engine_switch_rules_2026-10/5a18d31_8b_watch_km3.jsonl`: 160 games, sha256 027381c0fd421ad0b1e44cd86a8c02bb890723a98b0c9f93d64c62e01df1b30d
- `engine_switch_rules_2026-10/5a18d31_8b_old_k3.jsonl`: 160 games, sha256 1a563abb026752f31aae9a259f4cb261f9beff35e056cc3f03d596b90f7590c2
- `engine_switch_rules_2026-10/5a18d31_8b_new_k3.jsonl`: 160 games, sha256 2d4ad0b4fa2d500b3c220c64cdacbfe967259250268da9fbe1721036442b65ec
- `engine_switch_rules_2026-10/5a18d31_8b_watch_k3.jsonl`: 160 games, sha256 b7587ca217aa1005e253a15c95ff1e5f486bbd6eb0ff88900ea3a51924b93d5f

Seeds: 23,100,000,000 + pairing x 10,000 + i (`pairs_8.tsv`, `seeds_8.txt`); held list in seat 0 for even i.

## The rule

PLAN.md's mechanic check, as `tightened_rule.py` applies it: a changed game is explained on the board only when an
exact reach counter (A: vs_confusion_first_built, vs_confused_choice_offered, vs_confused_choice_chosen; B(a):
coin_cut_recorded; B(b) and Chase Order: coin_queued_offered, coin_queued_offered_any) fired at a tick at or before the
first differing tick k, in k's turn or at the cause tick. A firing after k, or in an earlier turn other than the cause
tick, explains nothing. A board difference (offered moves, a forced move, the state after identical moves, a prefix)
with no such counter is UNEXPLAINED and stops the switch. A lookahead difference (the same state and offered moves, a
different choice) needs both halves: the code gate, and a probe (vs_probe.rs for A; coin_probe.rs and coin_lookahead.py
for B) showing the gate's condition within the mover's search depth at k. A trace that needs a judgment call goes to
Dustin, and the pin waits for his word. coin_full_prevention, vs_confused_choice and the superset counters never explain
a game. The refactor rule's condition 3 (PLAN.md:95) says a game where coin_full_prevention fired and no reach counter
did must be identical: every such changed game is counted as CONDITION 3 above, and a ruling is needed before the pin.
The runner already stopped on any changed game whose repair counters all read 0.
