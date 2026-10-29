# Notes for Claude sessions

- **Read `START_HERE.md` first, then `PROJECT_INSTRUCTIONS.md`.** They win over every other file,
  including this one. The mission is a better simulator for finding better decks, for players in
  general. Use START_HERE's brief mission check when choosing work and in daily reviews. The simulator doesn't establish ladder rankings; no new
  files, gates or process documents unless Dustin asks; report in plain language.
- Pocket (the mobile game) is not the physical Pokémon TCG. Read `RULES_FOR_AGENTS.md` before
  touching game logic, and look cards up with `python3 lib/card.py <name or id>`, never from memory.
- Current plan and status: `rl/RUN5.md`, "The plan, revised Sept 25" and its "Where things stand". The
  scoreboard's 45 cells vs Limitless (`rl/results/scoreboard_v3_2026-09-27/`) are an evaluation measure;
  START_HERE's mission determines why work is useful. Preserve each registered experiment's rules.
- Pick seeds outside every range in START_HERE's seed table. Claude Code's diagnostics use
  20,000,000,000 and up.
- Build: `cd engine && cargo build --release`. Tests: `cargo test --release --features test-utils`.
  A cloud build reproduces the Sept 23 table exactly (Altaria v Blaziken 58.3% on its seeds).
- The official engine program is `rl/engine-2026-10-29/deckgym` (since Oct 29; main-affe56e: main-4d48844's engine plus
  the Dual Fusion release, a partial compatibility update: the B4b and P-B 095-103 cards (all 438 Complete) and the Dual
  Fusion C1, SP1 and P-C cards (205 of their 260 printings implemented; `deckgym simulate`, `optimize` and `goldfish`
  refuse a deck that holds one of the other 55), dual-type Pokémon and the corrected Ultra Beast list;
  `engine/src/players/` changed only so that the bots read the new cards; `rl/engine-2026-10-29/README.md`). The slow
  report stays kx3 on main-4d48844 until its re-pin (`rl/strength/README.md`): say so when you hand one over. The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-21/`, `-10-12/`, `-10-02/`, `-09-30/`,
  `-09-28/`, `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
  unchanged, and run identities bind to it: copy it, never rebuild it.
  Hashes for all of them are in `project_manifest.json`. All are Linux files (WSL or the cloud).
- `engine/CLAUDE.md` is upstream deckgym's card-implementation guide, not the project's instructions.
- Dustin is new to GitHub. Explain git steps in GitHub Desktop terms (Commit, Push origin, Fetch
  origin, Pull origin), not command lines.
