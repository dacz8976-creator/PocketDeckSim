# Rules switch 2, reader two (Sonnet): the second read of (a), (b) and (e) against PLAN.md

Oct 10. Read-only, lean, by myself, no agents. I did not open reader one's files before committing these.

**Which text I read against.** Your line numbers (257, 258, 261, 305-308) are rows (a), (b), (e) and the mechanic check in the PLAN
before 201c450e. That commit inserted 17 lines at 47-63, so on main they are PLAN.md lines 274, 275, 278 and 322-325 (§4 rows a, b, e;
§6 "The mechanic check", changes 1-3). I read main's text (201c450e), including the coordinator's new note under the heading
"Oct 10: the final P is c7a25df4" and the closed open test of (a).

**Which tool files I read.** Eight of `tools_8c.tsv`'s nine blobs; my copy of each equals the pinned blob by `git hash-object`
(commit 31380294): `tightened_rule.py` 9817f8bc, `test_tightened_rule.py` 6a5e7924, `classify_8c.py` a487a34f,
`coin_lookahead.py` 25122f62, `classify_8b.py` 18a7cc14, `coin_probe_v2.rs` 31857834, `run_revert_gates.sh` 0c7c2b90,
`score_dump_round2.rs` b2553655. The ninth, `vs_trace.rs` 3fbc20d2, is the last switch's Victory Star tracer; I did not read it. Also read: the readiness README (§2, §3),
`coin_probe_v2_selftest.txt`, `open_test_gate_R/`, `classify_check_8b/` (README, run output, `lookahead.tsv`), the `revert_switches/`
README, run output and scripts, `f1_promotion/` logs, `tests_after_review_fixes.log` (43 of 43 OK), and main's `counters.tsv`.

## 0. Verdict

**(c) does not fully match the plan.** The list of deviations (details below):
- **Substantive:** a-D1 (the PLAN's "free exactly where gate_R > 0" and the coordinator's "never `free`"); a-D2 (the probe's evidence is at 31616338, not at P); b-D1 (the negative controls are weaker than "find nothing"); e-D1 (the revert check at the 8b ticks was run for G1+G2, P2 and all-off only); e-D2 (the revert evidence is at 31616338, not at P, and F1 changed G2's arm).
- **Wording only (stale text):** a-D3, a-D4, b-D2.
Everything else I read matches. Nothing here stops the switch; a-D1, b-D1, e-D1 and e-D2 are what the revert-check driver should close.

## 1. (a) coin_probe v2 and RESULT_R2 (PLAN row a, line 274)

**Matches the plan.**
- The ply counting is the row's list: the root move is ply 1; game over, a forced turn end, pure frames and complete promotion frames are free; it crosses a forced EndTurn into the mover's next turn and stops when the opponent acts; every other offered move costs a ply, the opponent's stack choices included; an unpriced move is a leaf.
- RESULT_R2 carries the row's six round-2 conditions as seven kinds in `R2_KINDS` (will, vs, trap, own, guts, plain, perish) plus `trapleaf`; RETURN is RESULT_P2's `ret`. `parse_probe` refuses an output without the RESULT_R2 line (a probe built before (a)). Two or more Trap Territories read is `trap`; a Retreat Cost a leaf's value reads is `trapleaf`.
- The 600,000-node retry: `nothing_found` plus `truncated` (classify_8c.py:167, coin_lookahead.py:65), tested.
- The self-test is 46 checks and 3 frame checks, 0 failures (`coin_probe_v2_selftest.txt`, last line), made of 32 new boards (19 positives, 13 negatives) and the 14 old boards now expecting none in every round-2 field; before the check exactly the 19 positives failed.

**Deviations.**
- **a-D1. "free exactly where gate_R > 0" does not hold as worded, and the new PLAN note does not match the code.** As worded it holds in 540 of 1,126 games (the PLAN's own figure). The coordinator's note (PLAN lines 47-63) closes it with a refined reading: the probe walking past queued frames with R's own frame definition finds R's gate in 1,126 of 1,126 games and in none of the 279 controls, and "8c's look-ahead verdict uses `queued` ... never `free`". The refined walk is not in the pinned probe (`tools_8c.tsv` keeps the official probe), and the verdict code does read `free`: `lookahead_verdict` (tightened_rule.py:249) has `leaf_only = coin and queued == 3 and not free and ...`. So a pure frame at ply 3 gives BOTH_HALVES and a mixed one gives JUDGMENT; `free` does decide a verdict. The direction is safe: a `free` the probe misses (the shortest queued path not pure) sends a game to JUDGMENT, never to "explained". The unsafe direction (a false `free=true`) is what the refined walk's 0 of 279 controls speak to, but that test is a different computation. **Reword** the note to "uses `queued`; `free` only separates a pure frame at ply 3 from a mixed one, and a wrong `free=false` gives JUDGMENT".
- **a-D2. The probe's evidence is at 31616338, not at P.** The self-test, the P2 checks, the 8b ticks (21 look-ahead and 4 controls, RESULT_R2 all none in them) and the gate run all say "built on 31616338". Row (a) says "build it on P". F1 changed only the promotion floor under G2, so I expect no change, but the self-test and the 21 + 4 ticks at P are not on record. **Rerun them at P** (cheap), as the driver's first step.
- **a-D3. Stale count in the README.** Readiness README §3 (lines 187-188) still says "14 checks and 3 frame checks"; the file, and the README's own later line 299, say 46 and 3.
- **a-D4. Stale "Still to do" in the PLAN row.** Row (a) still lists "must also report the ply at which round 2's conditions are priced" and "boards for round 2's conditions" as to do. The README and the self-test show both done (77aa8e3d and the check commit).
- **Note.** The round-2 kinds are proven only on the 32 constructed boards; RESULT_R2 was all none on every real 8b tick, so 8c is their first use on real games.

## 2. (b) the classifier copies (PLAN row b, line 275)

**Matches the plan.**
- `first_difference`'s length branch: k is the first tick only the longer game has, the cause k-1; `counter_hits` reads the turn from the rows that exist; a length difference is a board difference (`board_hits`: `counter_hits` plus `extra_tick_hits` when the new game is the longer one). The "new engine's game is the shorter one" case, which row (b) lists as still to do, is done and tested (`test_the_new_game_shorter_*`, `BoardHits.test_the_new_game_shorter`), as are no counter, an earlier turn (never explains), and keyed counters (`watch_from_counters` refuses a keyed counter given as a list, `test_a_keyed_counter_is_flattened_and_a_first_round_coin_site_is_left_out`). 43 tests, 43 OK (`tests_after_review_fixes.log`).
- `ROUND2_QUEUED` is the eight attacks of counters.tsv's header (Wild Swing, Wellspring Dance, Tornado Shot, Double Splash, Triple Bombardment, Mischievous Ring, Litter, Double-Punching Family). A title the probe cut at 87 characters is read as the later-round attack it begins (`_title`). The supersets (`trap_territory_two_in_play`, `coin_defender_attack`, `vs_confused_attack`) are not reach (§6 change 1; counters.tsv roles `superset2`, `r1_superset`).
- `lookahead_verdict` and its strict reading are as the docstring says and as `LookaheadVerdict` tests; the golden check is `golden_ok` (a round-2 kind or RETURN at ply 1, a queued choice after 0 moves or a cut at ply 1).

**Deviations and notes.**
- **b-D1. `control_clean` is weaker than "find nothing".** Row (a) says the negative controls find nothing, and step 8b required no condition at all. `control_clean` (tightened_rule.py:230) requires only `queued`, `cut` and `ret` to be absent; the round-2 kinds and `trapleaf` are not required absent (the docstring: a Will in hand or two Ariados can be found in an unchanged game, and the board summary shows no hand). `classify_8c.py:283` and `coin_lookahead.py:143` use it. So the controls cannot catch a probe that over-reports a round-2 kind; only the 13 negative self-test boards do. Acceptable if you accept it; it is a change from the plan's wording.
- **b-D2. Stale "Still to do" in the PLAN row (b)** (shorter case, keyed names, synthetic tests): all done (above).
- **b-N1. "LOOKAHEAD ONLY, both halves hold" (`BOTH_HALVES`) is not a final verdict.** §6 change 3 needs the revert check as well, and a game that meets the first two but fails it is a stop. With no driver yet, the label means "code gate + probe", not "explained"; the pin refuses without the driver.
- **b-N2. Three counters have no golden check:** `luxury_coin_opp_stadium` and `fossil_item_lock` (the probe has no condition for them), and `coin_queued_by_attack` when it fired only for Double-Punching Family (the engine queues the second punch when any of the opponent's Pokemon has a coin Ability, the probe's QUEUED only when a target has one). A board-explained game by those counters has no probe confirmation. This is by design (`golden_ok` docstring), not in the PLAN.

## 3. (e) the gate plumbing (PLAN row e, line 278)

**Matches the plan.**
- A switch that empties `forecast_apply_damage`'s coin targets (G1); one switch per gate: the seven sites (G2), the own side (G3), Will (G4), the Victory Star gate (G5), Trap Territory (G6), Guts (G7), Perish Body (G8); plus G9, G10, G11 (P3) and P2 beyond the row. All twelve environment spellings, the twelve settings of `with_round2` and `counters.tsv`'s `revert_switch` column agree (checked name by name).
- "Each switch first shown to give the old engine's scores where its gate doesn't act": on by default the 8b deals, the P3 smoke and 240 km3 v km3 games are byte-equal to the engine before the switches; every gate off equals the official engine (the 8b rows, 240 games, digest 59dd3e38108dd725, on worker threads); at the 4 control ticks the head, each gate off alone and all off give the official choice and scores.
- The revert check passes at all 21 look-ahead ticks: pairing 35's 17 with G1 + G2 off, pairing 37's 4 with P2 off, all 21 with every gate off.
- My own read of each gate's off branch against the official code (EQUIVALENCE_reader2_sonnet.md §2, §4) agrees: every gate off is the official engine's behaviour.

**Deviations.**
- **e-D1. At a look-ahead tick the revert was run for G1 + G2 together, P2, and all-off only.** The row says "each switch run alone and all together". Run alone, one gate at a time, the gates were played over the 8b deals (every deal plays as the head or as the official engine; G3 to G11 off alone change no 8b deal), but the 8b ticks contain only the sites G1 + G2 and P2 reach. For a game where the probe finds a round-2 kind (will, vs, trap, own, guts, plain, perish), the single-gate revert at its tick has never been run on a real game; G3 to G8 are covered by their unit revert tests and the controls. The driver is their first use.
- **e-D2. The revert evidence is at 31616338, not at P, and F1 changed a G2 arm.** The gate run, the 240-game equality and the score dump all ran at 31616338 ("Run as `run_revert_gates.sh <work dir> 31616338 384d91dc`"). The README's own gap list says G2's pending-hit arm "has no revert test of its own"; F1 (c7a25df4) is a change to exactly that arm. F1's new test fails at its parent and passes at P (`g2_copied_second_punch_waits_for_the_copiers_promotion_after_rocky_helmet`); the arm's inertness with G2 off rests on my reading (`queued_site_coin_on() && ..`, EQUIVALENCE_reader2_sonnet.md 4.11) and on the existing `revert_g1_g2_second_punch_gives_the_old_hit`. **Rerun the 21 + 4 ticks and the 8b equality at P** with the driver.

**Notes for the driver.**
- Take the gate from counters.tsv's `revert_switch` column, which already joins what a gate needs with "+": the queued counters need `DECKGYM_PLAIN_QUEUED_SITES+DECKGYM_NO_PLAIN_HIT_COIN` (G2's old damage needs G1 off too; G2 off alone plays as neither engine, as k3 pairing 35 deal 9 showed), RETURN needs `DECKGYM_FLAT_RETURN_DAMAGE`, each round-2 kind its single gate (will G4, vs G5, trap G6, own G3, guts G7, plain G1, perish G8), and every game gets the all-off run (`DECKGYM_ROUND2_OFF`) as well.
- The variables are read once per process (a `LazyLock`), so the driver must set them per process; `with_*` is thread-local and is what `score_dump_round2.rs` uses.
- Coverage gaps the README names and I confirm: `with_round2`'s test checks P2 only; `revert_g5_a_block_coin_result_is_the_old_paths` has no switch-on control in the same test.

**(c) does not fully match the plan** — deviations: a-D1, a-D2, b-D1, e-D1, e-D2 (substantive); a-D3, a-D4, b-D2 (stale wording). Notes: a, b-N1, b-N2, the driver notes.
