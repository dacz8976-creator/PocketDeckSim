# Project instructions

The standing instructions from Dustin's claude.ai Project for Pocket Deck Lab, copied Sept 24, 2026, with
the rules added since then. Read `START_HERE.md` first. Where the two differ, `START_HERE.md` and Dustin win.

## The goal

**Help Dustin improve decks he enjoys playing so they carry out their plan reliably and perform better against the opponents he actually faces.**

The standing mission and recurring work check are in `START_HERE.md`. Preserve the deck's identity, target common opponents and recurring weaknesses, and explain useful card or play changes with evidence and tradeoffs. Engine and pilot work serve those decisions. Prioritize trustworthy playing quality, report time/cost, and do not invent a speed requirement or fixed game budget.

## What's void

- **Every deck ranking made before 2026-09-10 is void.** The engine let Asleep and Paralyzed Pokémon
  attack and retreat. Don't re-run those rankings and don't cite them.
- `HANDOFF.md`, `CURRENT.md`, `CURRENT-CORE.md`, `current_best_decklists.txt` and anything about Zoroark,
  meta4–meta9 or stations are history, not instructions. They stay in Pocket Deck Lab.

## What the simulator is and isn't for

- **It doesn't rank decks.** Real results come from Limitless (`decks/classifier/`,
  `rl/results/limitless_check_2026-09-23.md`) and Dustin's own ladder games.
- **Its permitted uses follow the current plan in RUN5.** The Sept 24 blanket hold on brew screening is historical; later approved diagnostics and slow reports have their own scope and limitations. They do not establish a ladder ranking. Keep deck weaknesses, bot mistakes and engine errors distinct.
- **The Limitless table is an evaluation measure**, with the applicable experiment's rules in RUN5 and its registration. It supports the mission; an improved aggregate score alone is not a useful deck recommendation.

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
