# Switch 2 precondition (e): one revert switch per gate (the cloud, Oct 9)

Decision this informs: whether rules switch 2 can trust its "in lookahead" verdicts. For each of those, the PLAN's revert check needs a
switch that turns the round-2 gate back off and gives the old engine's move.

## In plain words

- **Each gate of the round-2 package has its own off switch.** There are 11 gates (G1 to G11), built the same way as P2's
  `DECKGYM_FLAT_RETURN_DAMAGE`. Each one is on by default. Setting its `DECKGYM_*` variable to 1 turns it off for the whole program, and
  its `with_*` function turns it off for one call. `DECKGYM_ROUND2_OFF=1` (or `with_round2`) turns every gate off, P2 included. The
  list, with what each switch-off brings back, is in `engine/src/actions/apply_action_helpers.rs` (the G1 to G11 comments). Commit
  31616338.
- **Switch on, nothing changes.** The 8b deals, the P3 smoke and 240 km3 v km3 deckgym games all play byte for byte as before.
- **Every gate off is the official engine.** The 8b rows equal the official engine's recorded rows byte for byte. The 240 deckgym games
  are game for game the official program's (digest 59dd3e38108dd725, on worker threads).
- **The revert check passes at all 21 look-ahead ticks.** These are the ticks of the 8b sorting. Turning the right gate off for that one
  decision brings back the official engine's choice, with every candidate's score within 1e-9. Turning every gate off does too. At 4
  control ticks with nothing to change, the head, each gate off alone and all of them off all give the official choice and scores.

## The gate run (`run_revert_gates.sh`, output in `run_output.txt`)

Run as `run_revert_gates.sh <work dir> 31616338 384d91dc`, where 384d91dc is the engine just before the switches.

1. **The 8b deals.** Pairings 32 to 37, 40 deals each, km3 and k3 (240 deals per bot).
   - On by default: equal to the recorded new rows and to the engine before the switches.
   - `DECKGYM_ROUND2_OFF=1`: equal to the recorded old rows.
   - One gate off at a time: every deal plays either as the head or as the official engine.
     - km3: G1 + G2 off brings back 11 of the 13 changed deals (pairing 35), and P2 off brings back the other 2 (pairing 37).
     - k3: G1 + G2 off brings back 7 of the 12, and P2 off brings back 5.
     - With G2 off alone, k3's deal (35, 9) plays as neither engine. That is expected: G2's old damage also needs G1 off (its comment
       says so), and with both off it is the official engine.
     - G3 to G11 off alone change no 8b deal.
2. **The later round's smoke** (80 games):
   - every gate off gives the games of R (1abdbe8);
   - every gate off except G2 gives the games of 29e126a (the seven sites).
3. **The counter smoke** (120 games): P2 and G11 off gives 3090abb's games.
4. **The P3 smoke** (640 games): the default and G11 off each give the recorded P3 games.
5. **deckgym, km3 v km3, Altaria v Blaziken, 240 games at seed 7100:**
   - The official program, the head and the head with every gate off all match the pinned record, except for the wall time.
   - The head and the head with every gate off each match the official program game for game.
6. **The revert check** (`score_dump_round2.rs`):
   - pairing 35's 17 ticks with G1 + G2 off: 17 of 17;
   - pairing 37's 4 ticks with P2 off: 4 of 4;
   - all 21 ticks with every gate off: 21 of 21;
   - the 4 controls: all match.
   - One fix to `score_dump_round2.rs` before this run: `with_off` needed `R: 'a` to compile (Rust error E0309).

## The full test suite (`suite_default.txt`, `suite_off.txt`)

`cargo test --release --features test-utils --no-fail-fast` at 31616338:

- **On by default:** 2,102 of 2,102 pass.
- **`DECKGYM_ROUND2_OFF=1`:** 2,051 pass and 51 fail.
  - All 51 are tests added since the official engine (8626a358). `changed_tests.py` checks each failing test's body against 8626a358;
    the result is in `suite_off_failures_new_since_8626a358.tsv`.
  - They are the round-2 rules' own tests, and they should fail with round 2 off.
  - Three are revert tests: `revert_g1_..._through_a_queued_choice`, `revert_g3_..._on_your_own_meowth` and `switch_scoping`. Each
    turns one gate off and checks the result with the other gates on, so it can't pass with every gate off.

## Coverage gaps (what no test covers yet)

- **G2's pending-hit arm.** It has no revert test of its own: the G2 tests reach the seven sites through the queued choice. The
  8b deals and the smokes do play through it.
- **`with_round2`.** Its test only checks P2's return damage, not the other gates. The 240 deckgym games and the 8b rows check the
  process-wide variable.
- **G5's old-paths test** (`revert_g5_a_block_coin_result_is_the_old_paths`). It has no switch-on control in the same test.

## Files

- `run_revert_gates.sh`, `run_output.txt`: the gate run.
- `score_dump_round2.rs`: the score dump for the revert check, with gates off for one decision.
- `suite_default.txt`, `suite_off.txt`: the suite's test lines.
- `changed_tests.py`, `suite_off_failures_new_since_8626a358.tsv`: the check that every failure with round 2 off is a new test.
