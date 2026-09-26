# A3: per-game calibration against the Ladder Log (prepared Sept 26, 2026; no games played yet)

**The question.** When Dustin sits down with one of his lists against a deck the simulator has a
list for, does the simulator's win chance for that exact pair tell us anything about whether he
wins? The honest comparison is against the base rate: Dustin's own win rate over the same games,
which is what he would know without any simulator.

**What is here**

| File | What it is |
|---|---|
| `calibration_games.csv` | One row per logged game whose opponent has a list file: 19 rows, 18 usable. Built from `ladder_mapping.csv` and the Ladder Log artifact (collection `logs`, read Sept 26; the Sept 24 CSV copy agrees on all 33 games). |
| `run_calibration.py` | Plays the 15 pairs on the official engine (WSL or the cloud) and writes `sim_results.csv`. |
| `calibrate.py` | Joins `sim_results.csv` to `calibration_games.csv` and prints the scores. Windows or Linux python 3, no extra packages. |
| `build_calibration_games.py` | Rebuilds `calibration_games.csv` when the log or the mapping grows. |

## The games

33 games are logged (Sept 15 to Sept 24, record 12-21). 19 were against an opponent that has a
list file: 15 against the eight panel lists (`decks/screen/opponents/t-*.txt`, 10 exact plus 5
variants with the same core) and 4 against the two off-panel lists built tonight
(`l-charizardy.txt`, `l-sharpedo.txt`, 2 games each). Of those 19, **18 are usable**: the
Sept 16 Skarmory ex / Chandelure game (a win against Hydreigon) has no deck file anywhere in
`decks/`, so it is in the CSV with `usable=0`.

Dustin's record on the 18: **6-12** (base rate 0.333). They fall into **15 pairs**:

| # | Dustin's list | Opponent list | Ladder games |
|---|---|---|---|
| 0 | brew-01 Arceus / Crobat / Xatu | t-vespiquen | 1 (0-1) |
| 1 | brew-01 Arceus / Crobat / Xatu | t-weezing (played TR Weezing / TR Magmar variant) | 1 (1-0) |
| 2 | brew-03a Arceus / Nihilego / Toxapex | t-suicune | 1 (0-1) |
| 3 | brew-03a Arceus / Nihilego / Toxapex | t-vespiquen | 1 (0-1) |
| 4 | brew-04 Xatu / TR Slowking ex | l-sharpedo | 1 (1-0) |
| 5 | brew-05b Meowstic / Hatterene / Comfey | t-altaria (inferred from "Darkrai espeon sleep") | 1 (0-1) |
| 6 | brew-05b Meowstic / Hatterene / Comfey | t-lucario (played Hitmontop variant) | 1 (0-1) |
| 7 | brew-05b Meowstic / Hatterene / Comfey | l-sharpedo (inferred from "magikarp/carvanha") | 1 (1-0) |
| 8 | brew-06 Payback (Psychic) | t-lucario (played Dugtrio and Hitmonchan ex variants) | 2 (0-2) |
| 9 | brew-06b Payback (Grass) | t-blaziken | 2 (0-2) |
| 10 | brew-06b Payback (Grass) | l-charizardy (inferred from "Charizard ex / entei ex") | 1 (0-1) |
| 11 | 02 Arceus / Crobat | l-charizardy | 1 (0-1) |
| 12 | 07 Skarmory stall | t-altaria | 1 (1-0) |
| 13 | 07 Skarmory stall | t-hydreigon (one exact, one Mega Sableye ex variant) | 2 (2-0) |
| 14 | 07 Skarmory stall | t-lucario | 1 (0-1) |

**Things to know about these 18 before reading any number**

- **Which file is "Brew 05".** The log calls the deck "Meowstic / Hatterene / Comfey (2026-09-15
  list)" and its notes mention Comfey and Peculiar Plaza. `brew-05-meowstic-hatterene-confusion.txt`
  has neither; `brew-05b-meowstic-hatterene-comfey.txt` has both, and `decks/screen/results.md`
  already pairs the same 3-3 ladder record with brew-05b. So log id `brew-05` maps to the
  **brew-05b** file. "Brew 05c" (the Cape variant) has no file, but none of its three games had a
  listed opponent, so nothing is lost.
- **Two lists were not quite the file.** brew-04's note says Giant Cape became Elegant Cape and
  X Speed became Peculiar Plaza for that game; brew-03a's Dustox note says a second Poison tool
  replaced the Cape (which may have carried over to its two panel games). The files are unchanged;
  the CSV marks both `file-deviates`.
- **The opponent's actual list is never known.** All 18 games use the archetype's Limitless list
  as a stand-in. In 5 games the opponent played a variant (Lucario with Hitmontop, Dugtrio or
  Hitmonchan ex; Hydreigon with Mega Sableye ex; Weezing with TR Magmar), and in 3 the archetype
  itself is inferred from partial information (`list_match` column: exact / variant / inferred).
- **Who moved first** is known for 1 game (brew-06 vs Lucario/Hitmonchan, "Went first"). The
  engine decides the starting player from the seed, not from the `-p` slot, so the runner reports
  one pooled chance per pair. `calibrate.py` will use a `seat=first/second` row if someone later
  produces one (from `legality_scan --games-out`), otherwise the pooled row.
- Two of the three brew-06 games carry Dustin's own verdict "no shot of winning", and the
  Payback lists already read "fail" on the floor check. Those 4 Payback games are a quarter of the
  sample, and they will make almost any sim look good on the loss side.

## What the laptop has to run

Not tonight: a training run holds the laptop. Everything below is a WSL command from the repo root.

```bash
cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
python3 decks/screen/panel_ladder_2026-09-26/run_calibration.py --pairs-only     # lists the 15 pairs and their seeds, plays nothing
python3 decks/screen/panel_ladder_2026-09-26/run_calibration.py                  # the run: 15 pairs x 500 games, kp3 both sides
```

- **Engine:** the manifest's available release, `rl/engine-2026-09-25/deckgym` (sha256
  f4d235e5…), resolved and hash-checked by `current_engine.py` exactly as `run_screen.py` does.
- **Pilots:** kp3 on Dustin's deck and kp3 on the opponent, the plan's pilot on both sides.
  `--pilot`/`--meta-pilot` change that (a k3 row for comparison would be a separate `--out`).
- **Games:** 500 per pair, 250 with Dustin's deck in slot 0 and 250 in slot 1, `--seed-stream`.
  At 500 games the sim's own chance has a standard error of about ±2 points, well under anything
  18 ladder games can resolve; fewer (200) would also do.
- **Seeds:** pair *i* (0-based, in the printed order) uses 21,107,000,000 + *i* × 10,000 + *g* for
  slot 0 and + 5,000 + *g* for slot 1, so the run uses 21,107,000,000 to 21,107,149,999. **Reserve
  21,107,000,000 – 21,107,199,999 for this in START_HERE's seed table** when this is wired in.
  It sits above the B2e block (21,106,000,000+, its smokes at 21,106,999,000) and below the
  cloud's 22,000,000,000+; tonight's smokes used 21,107,990,000/995,000 (this runner) and
  21,107,999,000 (the two list smokes), all outside the reserved range.
- **Time:** the 2-game smoke took 3.9 s with the training run loading the laptop, so about 2 s a
  game: roughly 4 hours for 7,500 games under that load, less on an idle laptop. The output is
  appended one pair at a time, so a stopped run keeps what it finished; `--resume` continues it.
- **Output:** `sim_results.csv` next to this file, columns `deck_file, opponent_file, pilot,
  games, wins, draws, seat` plus the per-slot counts, seeds, engine path and hash, and seconds.

Then, on Windows or in WSL:

```
cd "C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\decks\screen\panel_ladder_2026-09-26"
python calibrate.py --sim sim_results.csv --json calibration_report.json
```

`calibrate.py --help` lists the options (`--draws half` to count a sim draw as half a win,
`--clip`, `--boot`, `--pilot`, `--strict`). It was tested on synthetic sim files: a sim that
knows every result scores Brier 0.0004 and 16.0 bits; a sim equal to the base rate scores
exactly 0 difference in every resample; a reversed one comes out below zero; path spellings,
missing pairs, several pilots, seat rows, draws and duplicate rows behave. The 2-game smoke
output joins correctly (1 game scored, 14 pairs reported missing).

## What the numbers will mean, and what they will not

**Definitions.** The Brier score is the average of (chance − result)² with result 1 for a win, 0
for a loss: 0 is perfect, 0.25 is a coin, and a constant chance equal to the base rate scores
p(1−p), which on 6-12 is 0.222. The script prints the sim's Brier, the base rate's (in-sample
and leave-one-out, because the in-sample base rate is fit on the same 18 games and gets a free
edge of about 0.012 at this size), the coin's, a skill score (1 − sim/base), and the
log-likelihood ratio in bits (how much more likely the sim's chances made Dustin's actual
results than the base rate did, chances clipped to 2%–98%). The paired bootstrap resamples the
18 games with replacement and reports 90% and 95% intervals on the Brier difference (base minus
sim, positive = sim better) and on the bits.

**Read it this way (decided before any game is played).**
- The 90% interval on the leave-one-out Brier difference **above zero** and the bits interval
  above zero: the sim beat the base rate on these games.
- Either interval **below zero**: the sim was worse than knowing nothing, on these games.
- Anything else: **cannot tell**, which is the expected outcome at 18 games (next paragraph).
- Separately, the "average sim chance" against the observed 0.333: the observed rate has a
  standard error of about ±11 points at n = 18, so only a gap of about 22 points or more
  (the sim averaging over 55% for these pairs while Dustin won a third) would be outside noise.
  That check needs no bootstrap and is the single most likely thing to show.

**What 18 games can and cannot do.** The synthetic power check (200 worlds each, true
per-pair chances drawn uniformly on the stated spread, the same 15-pair structure, 90% interval
on the Brier difference):

| games | the sim is | true chances | interval above zero | interval below zero |
|---|---|---|---|---|
| 18 | perfectly calibrated | 30%–70% | 5% | 3% |
| 18 | perfectly calibrated | 15%–85% | 15% | 1% |
| 18 | calibrated with ±10-point noise | 15%–85% | 14% | 1% |
| 18 | useless (unrelated to the truth) | 30%–70% | 2% | 18% |
| 18 | useless | 15%–85% | 1% | 30% |
| 100 | perfectly calibrated | 30%–70% | 24% | 1% |
| 100 | perfectly calibrated | 15%–85% | 64% | 0% |
| 100 | useless | 15%–85% | 1% | 66% |

So: a **perfect simulator would pass this test 5% to 15% of the time at 18 games**, about the
false-positive rate. A useless one would be caught 18% to 30% of the time. The run can therefore
show that the sim is badly wrong on Dustin's decks (a confident 70% on a pair he went 0-2, several
times over) and it can show a large gap in the average, but it **cannot confirm** that the sim is
right, and "cannot tell" must not be read as "the sim is fine". At about 100 games against listed
opponents a well-calibrated sim starts to show (24% to 64% depending on how spread the true chances
are); a real verdict wants several hundred, which means keeping the Ladder Log going and rebuilding
this CSV as it grows. The per-game bits are the running tally to carry forward: each new game
adds its own term, and the interval narrows as n grows.

**Also worth saying.** The sim's chance is kp3 piloting Dustin's exact list against kp3 on the
archetype's Limitless list. Dustin's real games have Dustin (not kp3) on his side, a human on the
other, and the opponent's actual list unknown, so even a perfect engine would not be calibrated to
these results; the test measures the whole chain, not the engine alone. The screen's own screen-vs-
ladder anchors in `decks/screen/results.md` (Payback 8%/16% went 0-6, Skarmory 57% went 3-1,
brew-05b 28% went 3-3) are the same idea at deck level and are consistent with the direction the
per-game test would take.

## Rebuilding the games file

`build_calibration_games.py` reads `ladder_mapping.csv` and the artifact's `logs` collection
exported as one JSON file per deck (`ArtifactData list`, collection `logs`, with an `out_dir`;
pass the folder with `--logs`). New games need a row in `ladder_mapping.csv` first (the archetype
mapping is by hand), and a new deck id needs an entry in the script's `DECK_FILES` table. It
cross-checks the mapping against the artifact and against the Sept 24 CSV copy and refuses to
write if they disagree.
