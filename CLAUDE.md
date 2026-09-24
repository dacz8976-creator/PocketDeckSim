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
- Laptop-only: the training launchers (`rl/run_training_v*.sh`) and the scoreboard tool's module
  check expect the add-on 0.7.2 wheel from Pocket Deck Lab; `project_manifest.json` and
  `current_engine.py` point at the Lab's engine program.
- `engine/CLAUDE.md` is upstream deckgym's card-implementation guide, not the project's instructions.
- Dustin is new to GitHub. Explain git steps in GitHub Desktop terms (Commit, Push origin, Fetch
  origin, Pull origin), not command lines.
