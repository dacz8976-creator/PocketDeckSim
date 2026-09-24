# Project instructions

The standing instructions from Dustin's claude.ai Project for Pocket Deck Lab, copied Sept 24, 2026, with
the rules added since then. Read `START_HERE.md` first. Where the two differ, `START_HERE.md` and Dustin win.

## The goal

- **Decks:** creative decks that also win, built around what Dustin enjoys: off-meta, the kind that
  catches people off guard. The output that counts is a deck Dustin plays on the ladder and wins with.
- **The bot:** one that can pilot as many of the common (meta) decks as possible, then learn to play other
  decks against them. The meta set can be refreshed whenever wanted.

## What's void

- **Every deck ranking made before 2026-09-10 is void.** The engine let Asleep and Paralyzed Pokémon
  attack and retreat. Don't re-run those rankings and don't cite them.
- `HANDOFF.md`, `CURRENT.md`, `CURRENT-CORE.md`, `current_best_decklists.txt` and anything about Zoroark,
  meta4–meta9 or stations are history, not instructions. They stay in Pocket Deck Lab.

## What the simulator is and isn't for

- **It doesn't rank decks.** Real results come from Limitless (`decks/classifier/`,
  `rl/results/limitless_check_2026-09-23.md`) and Dustin's own ladder games.
- **It doesn't judge brews; the ladder does.** Two current wordings:
  - `rl/RUN5.md` ("The plan, revised Sept 24"): until run 6 passes a held-out-deck test, the simulator
    doesn't screen brews. Its brew job is "does the combo fire."
  - `START_HERE.md` (updated later that day): a quick screen only catches clearly broken lists (under 35%
    against the panel isn't handed to Dustin), and it doesn't rank decks.

  `START_HERE.md` wins where they differ.
- **The Limitless table is the scoreboard** for any change to how the simulator plays
  (`rl/results/deep_search_table/`).

## Who does what

- **Dustin** owns the project, decides, and starts the long runs on his laptop.
- **Opus (Claude, Cowork)** leads and builds the RL work, runs checks and simulator runs, and does deck
  discovery.
- **Fable (Claude)** reviews designs and results. It's expensive, so it builds or runs things only when
  Dustin asks.
- **Astra (Codex)** owns the engine and reviews code. It's expensive too, so use it for targeted reviews,
  not routine work.
- **An auditor (Claude, Cowork)** runs independent measurements.
- **A Claude Code agent** works in this repo on GitHub.

## How to work

- Don't create files, gates, stations or process documents unless Dustin asks. Build the simplest thing
  that answers the question, and keep it cheap.
- Report status in plain language, not code language.
