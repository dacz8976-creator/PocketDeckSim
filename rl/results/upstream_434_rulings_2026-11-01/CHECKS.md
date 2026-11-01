# Checks for fix/c1-434-rulings

- **Base:** bcollazo/deckgym-core main `7aa4ef0` ("Sweet Honey requires a damaged Pokémon to be played (#439)"), unchanged since the
  job was set.
- **Branch tip:** `24e8dc0` (3 commits: `9b80837` Misty, `ade28e4` Sweet Honey, `24e8dc0` Darkrai ex).
- **Patches:** `git format-patch 7aa4ef0..fix/c1-434-rulings`, the three `.patch` files in this folder. Apply with `git am`.

## CI's three commands, on the branch tip

| Command | Result |
|---|---|
| `cargo fmt -- --check` | exit 0, no diff |
| `cargo clippy --features "tui test-utils" -- -D warnings` | exit 0, no warnings |
| `cargo test --features "tui test-utils" --all-targets` | exit 0: **1,405 passed, 0 failed, 0 ignored**, in 16 test binaries |

## Tests first

- **Before the fix,** on 7aa4ef0 with the new tests (`tests_before_fix.log`), the tests selected by `sweet_honey`, `misty` and
  `darkrai_ex` gave 9 passed, **4 failed**:
  - Misty's "chooses before flipping";
  - Sweet Honey's "chooses before flipping";
  - Sweet Honey's heal on the chosen Benched Pokémon;
  - Darkrai ex's effect attachment.
- **After the fix,** all of them pass. Also passing: Ribombee's Honey Gather, Vespiquen's Honey Rush, Charizard's Flame Aura and the
  rest of Darkrai ex's tests.
- **One test of ours needed a fix while writing it:** a 60-HP Squirtle at 10 HP can't be healed more than 50, so that assertion
  allows a full heal.

## Environment

- Built and tested in a cloud container with the stable Rust toolchain, rustfmt and clippy already installed. Nothing else was
  installed.
- Nothing was pushed to deckgym-core or any fork, and no PR or comment was made.
