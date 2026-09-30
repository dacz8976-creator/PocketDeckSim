# The official engine from Sept 30: main-d363ba8

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud). Committed with the executable bit (git mode 100755), so a Linux clone runs them as they are.
- **Built** in WSL from `git archive` of 14c39f4, the merge candidate: main plus the cloud branch `claude/pensive-ptolemy-spwc0b` at 53fc5a1, whose `engine/` is B's (km's build, 1f6319e; tree 9c84fef). `cargo build --release`, `--example legality_scan`, `--example goldfish`.
  - main's merge commit d363ba8 has an `engine/` byte-identical to it (checked by `../results/engine_switch_2026-09-30/pin.sh`). Main had moved since the candidate, so `pin.sh` made main's merge commit itself; its `engine/` equals the built candidate 14c39f4's byte for byte. 14c39f4 is kept only on the laptop (`refs/pocketdecksim/engine-switch-candidate`; not a branch, not pushed); elsewhere, build from main's merge commit, the same `engine/`.
- **What it is:** a players-only switch. The rules are the Sept 28 engine's, unchanged (rules4 plus the ten rules/09 repairs); three files in `engine/src/players/` changed.
  - `kta<N>` is ec7e1a8's kog-based kta: kog + switch 1, the Tool cut. Adopted "unconfirmed" Sept 30.
  - `km<N>` is kta + N2, the attacker's lasting Stadium damage bonus in the clock, as built at B. Adopted in the tables "unconfirmed" Sept 30.
  - km3 is the working pilot, on both sides of the screen and the floor. k3 stays the reproduction reference. k3, kp3 and kog3 play exactly as on the Sept 28 engine.
  - **Name change:** `kt3`, `kta3`, `ktb3` and `ktc3` are now the kog-based presets as B defines them. kt3, ktb3 and ktc3 are diagnostic: no identity claim, never adopted. The older kp-based presets (the Sept 26-28 kt records) replay only on `../engine-2026-09-28/`.
- **Approved:** Dustin, Sept 30: "Yes, pin if all pass (Recommended)", with km3 as the default pilot and the rules items kept out (RUN5, km, "The official engine switch carrying kta and km").
- **Evidence** (`../results/engine_switch_2026-09-30/README.md` and `identity_check.txt`; every replay matched by pairing and game number, counts asserted):
  - kta3 equals ec7e1a8's committed games on the fresh deals (table 14,000, new decks 8,500) and on the development deals (14,000 and 8,500).
  - km3 equals B's committed games (14,000 and 8,500).
  - k3, kp3 and kog3 equal the Sept 28 pin's references, 14,000 of 14,000 each.
  - `deckgym simulate` repeats Sept 28's k3, kp3 and kog3 lines on seed 7,100 and runs kta3 and km3; goldfish `--coverage` runs.
- **History:** `../engine-2026-09-28/` (main-9b4df9b) and earlier are kept unchanged, with their hashes in the manifest's historical releases.
