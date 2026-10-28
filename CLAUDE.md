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
- The official engine program is `rl/engine-2026-10-21/deckgym` (since Oct 21; main-4d48844: main-c045ede's engine plus the
  Growl-to-0 rule (an attack cut to 0 by an attacker-side effect does 0, no Weakness), an attack's hit back as attack
  damage for the Attacking Pokémon's own cards, and upstream #385, #390, #401 (Fossil part), #344 (narrow) and #367/#418;
  `engine/src/players/` unchanged; `rl/engine-2026-10-21/README.md`). The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-12/`, `-10-02/`, `-09-30/`, `-09-28/`,
  `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
  unchanged, and run identities bind to it: copy it, never rebuild it.
  Hashes for all of them are in `project_manifest.json`. All are Linux files (WSL or the cloud).
- `engine/CLAUDE.md` is upstream deckgym's card-implementation guide, not the project's instructions.
- Dustin is new to GitHub. Explain git steps in GitHub Desktop terms (Commit, Push origin, Fetch
  origin, Pull origin), not command lines.
