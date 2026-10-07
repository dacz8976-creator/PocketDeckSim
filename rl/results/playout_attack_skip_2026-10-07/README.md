# The skip bar: "attack when you can", narrowed (the cloud, Oct 7)

Set by the Fable coordinator via Dustin, Oct 7.
- **Background.** Quiz 4's attack bar (`_za`, `../playout_quiz4_items_2026-10-06/`) is not shipped: it also stopped moves
  that attack later in the turn, such as Misty, Copycat or a retreat first.
- **The ask.** The larger lead is required only when switching away from km3's attack would leave this turn without an
  attack in the candidate's own line. That is read from its play-outs' first turn: did the pilot's side attack before
  the turn ended? Then re-run the 26 development-run cases: which of the 9 true skips it keeps, and whether it touches
  the 17.
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **What doesn't change.** km3, `mod.rs`, the official engine, and kx3's default play (the parameter is off unless the
  code names it).
- **No table games.**

## In short

- **It keeps km3's attack at 7 of the 9 true skips, and touches none of the 17 moves made before an attack.**
  - `_za3` had kept 8 of the 9, but also stopped 14 of the 17.
- **The two skips it lets stand.**
  - **Deck 05 v Lucario, End Turn:** a lead of 3.4 standard errors, past the bar of 3. `_za3` let it stand too.
  - **Deck 01 v Hydreigon, Copycat:** in the play-outs km3 attacks after the Copycat in 16 of 16. In the game, kx3 then
    ended the turn instead. That later End Turn (same game and turn) is one of the 7 the bar keeps, so in that game the
    turn would still end with Giga Turbo.
- **Q12** (End Turn instead of Supernatural Feather) is among the 7.
- **Gate 1 passed** (see below).
- **Combined with close calls** (`_tools_zs3_m64`, the fix round, `../playout_close_calls_2026-10-07/README.md`): km3's
  attack is kept at only 2 of the 9 true skips, and 6 of the 15 moves before an attack that reproduce are touched. With
  64 rounds, 5 of the skips this bar kept lead km3's attack by more than 3 standard errors.
- **Gate 2:** it changes nothing at the 20 positions, by its rule. km3's move is an attack at only one of them, where kx3
  already keeps it.

## What was built

- **Every play-out records whether the pilot's side attacked before the decision's turn ended** (the first move
  included).
  - It reads the state only while that turn lasts, and play is unchanged.
  - Each candidate reports in how many of its play-outs that happened (`attacks_this_turn`).
- **The parameter.** `_zs<z>`, e.g. `kx3_r16_c12_z2_real_t0_poolmeta_zs3`. It can't be combined with `_za`.
  - The bar is z_skip when km3's move is an attack, the best candidate isn't one, and the best's line attacks this turn
    in fewer than half of its play-outs.
  - Otherwise the bar is z.
- **The reason names the count either way.**
  - Stopped: "the skip bar: the best move leads km's attack by +0.312, 2.1 standard errors, past z 2 but not the skip
    bar 3, and no attack this turn in its line (an attack in 0 of 16 play-outs) (km's attack 0.250, this move 0.562):
    km's attack kept".
  - Standing: "...; away from km's attack to a line that attacks this turn in 16 of 16 play-outs: ...".
- **The trace** carries each candidate's count when the parameter is on.
- **Code:** `skip_bar` and the decision block in `engine/src/players/playout_player.rs` (f03780eb).
- **Tests:** four in `engine/tests/playout_quiz4_test.rs`, written first (`tests_before.log`, 094962a1):
  - the code spells the bar, and refuses it with `_za`;
  - the bar's rule (z_skip only below half; half or more is not a skip);
  - the per-candidate count: an attack always attacks, End Turn never does, some other move's line attacks later, and
    the play-outs are the same with the bar on or off;
  - at 12 test-deck decisions (seeds 20,000,000,211-216 and 230-235), the bar stops only switches whose line skips the
    attack: here 1 stopped and 3 standing.

## The 26 development-run cases (`skip_scan.*`)

- **How.** The same scan as quiz 4 item 1, on the development run's kx3 games, all 560 replayed exactly.
  - At each decision where km3 proposed an attack and kx3 played something else, kx3 decided again from the game's own
    observation and randomness.
  - It did this twice: with the run's own code, which now gives every candidate's count
    (`attack_scan_poolmeta.jsonl`), and with `_zs3` (`attack_scan_poolmeta_zs3.jsonl`).
  - "In the game" is what kx3 did after the switch. "In the play-outs" is the candidate's own line with km3 continuing,
    which is what the bar reads.
- **What it found.** The game and the play-outs agree at all but one case.
  - Every move after which kx3 attacked later in the game (15 that reproduce) has a line that attacks this turn in 15
    or 16 of its 16 play-outs.
  - 8 of the 9 true skips have no attack this turn in any play-out (0 of 16).
  - The exception is the Copycat above: kx3 didn't attack after it in the game, but km3 does in all 16 play-outs.

| | true skips (no attack that turn in the game) | moves before an attack |
|---|---|---|
| cases | 9 | 17 |
| reproduced by a fresh kx3 | 9 | 15 |
| the line attacks this turn in most play-outs | 1 (the Copycat) | 15 of 15 |
| `_zs3` keeps km3's attack | **7** | **0** |
| `_za3` kept km3's attack (quiz 4) | 8 | 14 |

The full table, with every case's count, lead and verdict, is `skip_scan.txt`.

## Gates

- **Gate 1** (`checks/`, at f03780eb in a separate worktree):
  - **The suite:** 2,084 passed, 0 failed.
  - **km3's 240 games** (seed 7100): game for game equal to the official program's (digest 9dde28db2de6c9bc), and equal to
    the pinned record on every line but the wall time.
  - **The harness self-checks.**
    - km3: 81b572198c04d5d1, unchanged.
    - `kx3_r2_c3_lab`: 3a2eb43bd9053639 twice, unchanged.
    - `kx3_r2_c3_lab_zs3`: the same digest. The bar never acted in those 2 games.
- **Gate 2 (the 12 + 8 positions).** The bar can act only where km3's move is an attack. That is 1 of the 20 positions
  (B-214254-t06, Turbo Shark), and kx3 already keeps the attack there. So the bar changes nothing at the 20, by its
  rule; the 26 cases above are its real test.

## Files

- `tests_before.log`: the tests before the code.
- `attack_scan_poolmeta.jsonl` and `attack_scan_poolmeta_zs3.jsonl`: the two scans.
- `skip_scan.py` and `skip_scan.txt`: the summary and the full table.
- `checks/`: gate 1.
- `engine/examples/trainer_habits.rs`: the attack scan also writes each candidate's count.
