# Notes for Claude sessions

- Pocket (the mobile game) is not the physical Pokémon TCG. Read `RULES_FOR_AGENTS.md` before
  touching game logic, and look cards up with `python3 lib/card.py <name or id>`, never from memory.
- Current plan and decisions: `rl/RUN5.md`, section "The plan, revised Sept 24". History:
  `rl/FEASIBILITY.md`. Rules sources, open questions and known engine bugs: `rules/README.md`.
- The yardstick is the 28-matchup k3-vs-k3 table vs Limitless
  (`rl/results/limitless_check_2026-09-23.md`), not a bot's margin over k3.
- Build: `cd engine && cargo build --release`. Tests: `cargo test --release`.
- Long runs still happen on Dustin's laptop in the old `Pocket Deck Lab` folder; paths under
  `Boss Folder/` don't exist in this repo.
- Dustin is new to GitHub. Explain git steps in GitHub Desktop terms (Commit, Push origin, Fetch
  origin, Pull origin), not command lines.
