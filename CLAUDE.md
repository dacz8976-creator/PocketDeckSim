# Notes for Claude sessions

- **Read `START_HERE.md` first, then `PROJECT_INSTRUCTIONS.md`.** They win over every other file,
  including this one. In short: the goal is creative decks Dustin wins with on the ladder; the
  simulator doesn't rank decks; no new files, gates or process documents unless Dustin asks; report
  in plain language.
- Pocket (the mobile game) is not the physical Pokémon TCG. Read `RULES_FOR_AGENTS.md` before
  touching game logic, and look cards up with `python3 lib/card.py <name or id>`, never from memory.
- Current plan: `rl/RUN5.md`, "The plan, revised Sept 24". The yardstick is the 28-matchup table vs
  Limitless (`rl/results/limitless_check_2026-09-23.md`; tool in `rl/results/deep_search_table/`).
- Pick seeds outside every range in START_HERE's seed table. Claude Code's diagnostics use
  20,000,000,000 and up.
- Build: `cd engine && cargo build --release`. Tests: `cargo test --release --features test-utils`.
  A cloud build reproduces the Sept 23 table exactly (Altaria v Blaziken 58.3% on its seeds).
- The official engine program is `rl/engine-2026-09-25/deckgym` (since Sept 25; built from main at 7fc6ccb,
  same rules as rules4 plus the kp/kd players; `rl/engine-2026-09-25/README.md`). The rules4 program
  (`rl/addon-0.7.2/deckgym`) is kept as history. The verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`)
  is unchanged. Hashes for all of them are in `project_manifest.json`. Run identities bind to that wheel:
  copy it, never rebuild it. All are Linux files (WSL or the cloud).
- `engine/CLAUDE.md` is upstream deckgym's card-implementation guide, not the project's instructions.
- Dustin is new to GitHub. Explain git steps in GitHub Desktop terms (Commit, Push origin, Fetch
  origin, Pull origin), not command lines.
