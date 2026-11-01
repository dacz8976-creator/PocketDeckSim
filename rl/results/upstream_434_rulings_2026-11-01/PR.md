# Misty and Sweet Honey choose before flipping; Darkrai ex's Nightmare Aura on effect attachments (#434)

This closes three items of #434's checklist: Sweet Honey's order, Misty's order, and the Darkrai ex flag. There is one commit per
change.

## What changed and why

- **Misty** (A1 220, reprint A1 267): "Choose 1 of your [W] Pokémon, and flip a coin until you get tails. For each heads, take a [W]
  Energy from your Energy Zone and attach it to that Pokémon."
  - Before: `misty_outcomes()` flipped first, then queued the target choice, so the choice was made already knowing the result.
  - Now: playing Misty queues one choice per [W] Pokémon. Only after the choice does a new `FlipUntilTailsThenAttach` action flip
    until tails (at most 5 heads) and attach one [W] from the Energy Zone per heads to the chosen Pokémon (`is_turn_energy: false`).
  - Playability is unchanged (`can_play_misty`).
  - Observed in the live game: the Pokémon is picked first and the coin screen comes after.
- **Sweet Honey** (C1 119, reprint C1 152; also Ribombee's Honey Gather rental): "Choose 1 of your Pokémon, and then flip a coin until
  you get tails. For each heads, heal 20 damage from that Pokémon."
  - Before: `sweet_honey_outcomes()` flipped first.
  - Now: playing it queues one choice per damaged Pokémon, the same targets Potion offers; #439's `can_play_potion` rule still
    decides whether it can be played.
  - Then a new `FlipUntilTailsThenHeal` action flips until tails (at most 8 heads) and heals 20 per heads on the chosen Pokémon.
  - Observed in the live game: the Pokémon is picked first, then the coins are flipped.
- **Darkrai ex, Nightmare Aura** (A2 110 and reprints): "Whenever you attach a [D] Energy from your Energy Zone to this Pokémon, do
  20 damage to your opponent's Active Pokémon."
  - Before: it had `only_turn_energy: true`, while Charizard's Flame Aura, with the same wording, has `false`.
  - Now: Darkrai ex uses `false` too, so an effect that attaches [D] from the Energy Zone triggers it. The field's doc comment says
    what each value means.
  - Observed in the live game: Flame Aura fires on effect attachments (Flareon's Assisting Heater, Moltres ex's Inferno Dance), so
    the same reading is used for Nightmare Aura.

**How the order is enforced:**
- The target choice is pushed onto `move_generation_stack` by a deterministic play effect, one action per eligible Pokémon.
- Each action's forecast (`forecast_action_unwatched` in `apply_action.rs`) returns `Outcomes::geometric_until_tails`, reusing
  `apply_attach_energy` and `apply_healing` for each heads count.
- So no coin result exists when the player chooses. Both actions are generic (energy type or heal amount, and the cap are
  fields), and no other card's behaviour changes.
- The new variants have Display and the weighted random player's weights. No other match needed them.

## Tests

- `tests/trainers/misty_test.rs` (new):
  - right after Misty (both printings) is played, the pending choices are exactly the [W] Pokémon, identical across seeds, with no
    Energy attached yet;
  - after choosing a Benched [W] Pokémon, the attached [W] count over seeds includes 0, 1 and 2, never more than 5, all on the
    chosen Pokémon.
- `tests/trainers/c1_sweet_honey_test.rs`:
  - the existing heal test, in the new order;
  - right after Sweet Honey (both printings) is played, the pending choices are only the damaged Pokémon, identical across seeds,
    with nothing healed yet;
  - the heal is 0, 20, 40... on the chosen Benched Pokémon only;
  - the existing "needs a damaged Pokémon" test is unchanged.
- `tests/pokemon/darkrai_ex_test.rs`:
  - an effect attachment (`SimpleAction::Attach` with `is_turn_energy: false`, 1 Darkness onto Darkrai ex) does 20 to the
    opponent's Active. This replaces the test that asserted the old turn-Energy-only reading.
  - a non-[D] effect attachment does nothing;
  - the turn-attachment test is unchanged and still does 20.

Before the fix, 4 of these fail: both "choose before flipping" tests, the chosen-Benched heal, and the Darkrai ex effect attachment.
After it, all pass.

## Checks

On the branch tip (base 7aa4ef0):
- `cargo fmt -- --check`: clean.
- `cargo clippy --features "tui test-utils" -- -D warnings`: clean.
- `cargo test --features "tui test-utils" --all-targets`: 1,405 passed, 0 failed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
