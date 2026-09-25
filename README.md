# PocketDeckSim

A simulator and bots for Pokémon TCG Pocket, used to find decks that hold up in real play.
The simulator's matchup table is scored against real tournament results from Limitless.

## What's where

| Folder | What's in it |
|---|---|
| `START_HERE.md`, `PROJECT_INSTRUCTIONS.md` | **Read first.** What's true now, who does what, seed ranges in use. |
| `engine/` | The game engine (Rust), a fork of [deckgym-core](https://github.com/bcollazo/deckgym-core) with the rules4 fixes. Includes the k-bots (`k3` looks three of its own moves ahead). |
| `rl/` | Self-play training (Run 5 scripts, `pdl_rl_env/` Python wrapper), plans and reports. |
| `rl/RUN5.md` | **The current plan.** See "The plan, revised Sept 24". |
| `rl/results/limitless_check_2026-09-23.md` | The scoreboard: simulator vs Limitless, 28 matchups. |
| `rules/`, `RULES_FOR_AGENTS.md` | Pocket's rules with sources, open questions and known engine bugs. |
| `lib/` | Card lookup, deck checker, deck-code/QR tools, and the card database. |
| `decks/` | Dustin's decks, brews, the 8 meta lists (`research/`) and the quick-screen panel (`screen/`). |

## Running things from this repo

```bash
# build the engine (2-3 minutes)
cd engine && cargo build --release && cd ..

# play 100 k3-vs-k3 games (-p runs them in parallel)
engine/target/release/deckgym simulate --num 100 --seed 1 --seed-stream --players k3,k3 -p \
    decks/research/lucario.txt decks/research/altaria.txt

# look up a card's exact text (never trust memory: Pocket isn't the physical TCG)
python3 lib/card.py "Vespiquen ex"

# quick-screen a brew against the 8 meta lists (the official engine, kp3 on both sides)
python3 decks/screen/run_screen.py decks/brews/brew-03a-arceus-nihilego-toxapex.txt

# the A2 floor check (240 games per matchup; see the file's docstring)
python3 decks/screen/floor.py decks/brews/brew-03a-arceus-nihilego-toxapex.txt --out /tmp/floor
```

**Verified builds:**
- The training launchers (`rl/run_training_v*.sh`) install the hash-checked add-on wheel from `rl/addon-0.7.2/wheels/`. The scoreboard tool (`rl/results/deep_search_table/`) checks for that same add-on build.
- The official engine since Sept 25 is `rl/engine-2026-09-25/`: `deckgym`, `legality_scan` and A1's `goldfish`, built from main at 7fc6ccb (see its README).
  - `project_manifest.json` names it and holds the hashes. `current_engine.py` resolves to it and checks the hash.
  - The screen (`decks/screen/run_screen.py`) and the floor check (`decks/screen/floor.py`) use it.
- The rules4 program at `rl/addon-0.7.2/deckgym` is kept as history.
- `candidate_run.py` is retired: nothing in the plan uses it, and it refuses the new manifest.
- All of these are Linux files (WSL or the cloud).

## Keeping the laptop and GitHub in sync (GitHub Desktop)

- **Send your work up:** make changes, then write a Summary, click **Commit to main**, then **Push origin**.
- **Get changes made in the cloud:** click **Fetch origin**, then **Pull origin** if it offers.
- Cloud sessions work on their own branch and open a pull request. Merge it on github.com,
  then pull in GitHub Desktop.
