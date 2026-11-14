# Notes for Claude sessions

- **Read `START_HERE.md` first, then `PROJECT_INSTRUCTIONS.md`.** They win over every other file,
  including this one. The mission is a better simulator for finding better decks, for players in
  general. Use START_HERE's brief mission check when choosing work and in daily reviews. The simulator doesn't establish ladder rankings; no new
  files, gates or process documents unless Dustin asks; report in plain language.
- Pocket (the mobile game) is not the physical Pokémon TCG. Read `RULES_FOR_AGENTS.md` before
  touching game logic, and look cards up with `python3 lib/card.py <name or id>`, never from memory.
- Before proposing substantial work, read the tried-before index
  (`..\..\tried-before-ledger\LEDGER_INDEX.txt` from this folder, full detail in `LEDGER.txt` beside it) and say
  what was tried before, what your proposal changes and why that matters (wording in START_HERE). Current work is
  in the shared queue note in the Claude memory folder. `rl/RUN5.md` is history up to Nov 5, 2026. The
  scoreboard's 45 cells vs Limitless (`rl/results/scoreboard_v3_2026-09-27/`) are an evaluation measure;
  START_HERE's mission determines why work is useful. Preserve each registered experiment's rules.
- Pick seeds outside every range in START_HERE's seed table. Claude Code's diagnostics use
  20,000,000,000 and up.
- Build: `cd engine && cargo build --release`. Tests: `cargo test --release --features test-utils`.
  A cloud build reproduces the Sept 23 table exactly (Altaria v Blaziken 58.3% on its seeds).
- The goldfish card-support check (plain build, in `engine/`): `cargo build --release --example goldfish`, then
  `cargo test --release --test goldfish_card_support_test`, in that order (a filtered run does not rebuild the example).
- The official engine program is `rl/engine-2026-11-04/deckgym` (since Nov 4; main-543dad0: main-affe56e's engine plus
  R8: upstream's card code through #439, so all 260 Dual Fusion C1, SP1 and P-C printings now play (256 Complete,
  4 RulesUnverified) and the official programs refuse no real printing any more (the card-support refusal stays in the
  code for a card the engine cannot play); the bot-protocol adapter (`deckgym simulate --players proto,...`, opt-in
  `pdl_*` keys); the rule rows R8-10a to R8-10e and item 11 (`rl/results/r8_catchup_2026-10-29/RELEASE_NOTES.md` §2);
  `engine/src/players/` changed for the adapter and the new cards; `rl/engine-2026-11-04/README.md`). The slow report
  has been kx3 on this engine since its re-pin (Nov 5, after kx3's replay check on it; `rl/strength/README.md`).
  Every slow report made before then ran on main-affe56e or an older engine: say which when you hand one over.
  The working pilot is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-29/`, `-10-21/`, `-10-12/`, `-10-02/`, `-09-30/`,
  `-09-28/`, `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
  unchanged, and run identities bind to it: copy it, never rebuild it.
  Hashes for all of them are in `project_manifest.json`. All are Linux files (WSL or the cloud).
- `engine/CLAUDE.md` is upstream deckgym's card-implementation guide, not the project's instructions.
- Dustin is new to GitHub. Explain git steps in GitHub Desktop terms (Commit, Push origin, Fetch
  origin, Pull origin), not command lines.
