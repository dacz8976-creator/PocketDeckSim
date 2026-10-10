# Card check: c-magnezone_ex_magnezone.txt for switch 2's step 8b block-coin rows (the cloud, Oct 10)

**RESULT: PASS.** 15 of 15 cards pass, nothing flagged beyond Sept 26's two notes. This is the check PLAN.md's step 8b asks for before the
block-coin rows run ("deck 10 v c-magnezone_ex_magnezone.txt (Mirror Shot), after the cloud's card checks"). In switch2.env it is
`MAGNEZONE_CARD_CHECK`. It was read-only: no game was played.

## What was checked, at P = 31616338 (engine tree 639d2f80)

The list is `rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt` (15 distinct cards). For each card, `check.py`
(output in `check_output.txt`) checks four things:

1. **The card text.** `python3 lib/card.py <id>` prints it (all 15 are in `check_output.txt`).
2. **The engine's card data.** `lib/deckgym-database.json`'s entry equals the entry in P's `engine/database.json`: 15 of 15.
3. **The engine's own status.** P's `card_status --json` gives "Complete" with no listed limitation: 15 of 15.
4. **The coverage flags.** P's goldfish with `--games 0 --coverage` (0 games, exit 0) gives "Fully implemented" for all 15, and every
   card's coverage entry equals Sept 26's (`../../kt_carrier_census_2026-09-26/coverage_c-magnezone_ex_magnezone.json`). The two flags
   are Sept 26's: Mirror Shot "pays off on the opponent's turn" and Copycat "unpriced text rule". Neither is an engine gap.

## Mirror Shot (Magnezone B1a 026), the card the rows are for

- Text: "During your opponent's next turn, if the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that
  attack doesn't happen." The engine (`apply_attack_action.rs`, `coin_flip_to_block_attack_next_turn`) puts that block coin on the
  Defending Pokémon.
- It is one of the 8 block-coin attacks that round 2 handles with Will and Victory Star (TEXT_AUDIT.md). These tests all pass in the
  suite at P (`../../coin_prevention_round2_2026-10-01/revert_switches/suite_default.txt`):
  - `magnezone_mirror_shot_test`;
  - the block-coin tests: Will makes the block coin heads; a block coin comes first, then Victory Star;
  - their G4/G5 revert tests.

## The text against Limitless

The Sept 26 check (`../../kt_carrier_census_2026-09-26/card_check_c-magnezone_ex_magnezone.md`) compared all 15 cards with Limitless:
- no high-severity mismatch;
- one wording difference with the same meaning (Poké Ball).

`lib/deckgym-database.json` is unchanged since then (its last commit is the project upload), so that comparison stands. It was not
fetched again.

## Programs

- Built at P with `cargo build --release --locked`.
- goldfish sha256 `3488e3ae60b624477ed788d048a7bc34d792697e250db450d38cf35853d3c2ce`.
- card_status sha256 `3b0d5d8f2b90ecc0603eb6c6cd856a5057934d6b982a8e20be7f5479c50b2266`.
