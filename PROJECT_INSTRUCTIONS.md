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
- **It doesn't judge brews; the ladder does.** Brew screening and its cutoffs wait until the engine is trustworthy and realistic (Dustin, Sept 24): fixing the engine comes first.
  Until then the simulator's brew job is "does the combo fire".
- **The Limitless table is the scoreboard** for any change to how the simulator plays
  (`rl/results/deep_search_table/`).

## Who does what (changed Sept 24 evening; owners updated Sept 25)

The current owners are the "Owners" line of "The plan, revised Sept 25" in `rl/RUN5.md` (approved by Dustin): the WSL
session runs on the laptop, the laptop session coordinates and owns the readings, the cloud session does engine items,
a Cowork agent does Limitless data, Fable reviews on request, Dustin decides. The roles below are the Sept 24 text and
are kept for the record; where they differ, RUN5.md wins.

- **Dustin** owns the project, decides, and starts runs on his laptop.
- **The Claude Code agent (this repo)** owns the engine, the add-on and all runs: builds, tests, training and
  simulator tables. Its results are committed here.
- **Astra (Codex)** reviews engine code. It's expensive, so use it for targeted reviews, not routine work.
- **The Cowork side (Pocket Deck Lab):** Opus does deck discovery and Limitless reading and reviews results,
  including reading the Hydreigon run's verdict, which it designed. Fable reviews designs and results; it's
  expensive, so it builds or runs things only when Dustin asks. An auditor re-checks results when asked.

## How to work

- Don't create files, gates, stations or process documents unless Dustin asks. Build the simplest thing
  that answers the question, and keep it cheap.
- Report status in plain language, not code language.
