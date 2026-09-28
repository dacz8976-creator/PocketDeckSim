# The official engine from Sept 28: main-9b4df9b

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud).
- **Built** in WSL from `git archive` of 233bced, the head of `claude/pensive-ptolemy-spwc0b`: `cargo build --release`, `--example legality_scan`, `--example goldfish`.
  - main merged it as 9b4df9b, whose `engine/` is byte-identical (checked).
- **What it is:** the Sept 27 engine's rules unchanged (rules4 plus the ten rules/09 repairs), with the kog, koh, kph and kt players added.
  - kog3 is the working pilot (composition check passed Sept 28, `../results/kog_composition_2026-09-27/READING.md`), on both sides of the screen and the floor.
  - k3 stays the reproduction reference.
- **Approved:** Dustin, Sept 28, "Pin it now", with the last switch's conditions and his ruling on the rules-file refactor (RUN5 "Rules").
- **Evidence** (`../results/engine_switch_2026-09-28/README.md`):
  - k3 and kp3 over the table's 14,000 deals equal the official references, and kog3 equals both kog tables, 14,000 of 14,000 each.
  - The refactor of `hooks/core.rs` and `hooks/mod.rs` (kt's build) was accepted on RUN5's three conditions: the source equivalence written down (two independent readers); the full suite, 1,975 passed and 0 failed; and games that reach the touched code identical on the old and new builds.
  - Those games: 16,000 kp3 and 8,000 k3 carrier games, the 4,000-game Scizor row under kp3 and k3, and Dustin's two recorded Skarmory blocks (1,920 each).
  - In them a Barrier cut damage in 4,590 games, and a Jasmine, Cheren, Adaman or Blue cut in 295.
- **History:** `../engine-2026-09-27/` (main-83e17ae) and earlier are kept, with their hashes in the manifest's historical releases.
