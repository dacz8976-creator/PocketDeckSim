# Ladder-weighted panel and A3 calibration prep (Sept 26, 2026; nothing here is wired in)

Written by Fable (the "Deck pilot bot project review" session) in an overnight workflow on Dustin's
Sept 25 instruction "keep us on track for tonight and make progress". Everything in this folder is a
proposal or a preparation. No screen, floor or calibration game was played beyond the 2-game smokes
noted below; `decks/screen/run_screen.py`, `floor.py`, `opponents/` and `START_HERE.md` are untouched;
the ranking hold from Dustin's Sept 25 decision still stands (section 4).

## 1. What Dustin actually faces on the ladder

Source: the Ladder Log artifact (collection `logs`, 10 deck documents, read Sept 26), 33 games from
Sept 15 to Sept 24, record 12-21. The Sept 24 CSV copy agrees on all 33 games, and `ladder_mapping.csv`
here is the game-by-game mapping. One game is 3 points of share, so every percentage below is a first
read, not a measurement.

| Who he met | Games | Share | His record |
|---|---|---|---|
| one of the eight panel decks, exact list | 10 | 30% | 3-7 |
| a panel deck's core with a different partner (3 Lucario, 1 Hydreigon, 1 Weezing) | 5 | 15% | 2-3 |
| panel family (the two rows above) | 15 | 45% | 5-10 |
| a top-30 Limitless deck the panel lacks | 8 | 24% | 3-5 |
| a deck Limitless lists outside its top 30 | 9 | 27% | 4-5 |
| a homebrew (Weezing / Nihilego / Darkrai ex poison pile) | 1 | 3% | 0-1 |

By panel deck, family view (exact-list games in brackets): Lucario 4 games, 0-4 (1); Altaria 2, 1-1
(one of them inferred from "Darkrai espeon sleep"); Sceptile 0, never met; Vespiquen 2, 0-2; Suicune 1,
0-1; Weezing 1, 1-0 (the TR Magmar variant; the Hoopa ex form never came up); Blaziken 2, 0-2;
Hydreigon 3, 3-0 (2). Off the panel, two decks came up twice: Mega Charizard Y ex / Entei ex (0-2) and
Mega Sharpedo ex / Gyarados (2-0). Everything else came up once: Manectric, Rayquaza, Whimsicott and
Garchomp from the top 30; Milotic/Igglybuff, Rotom ex, Raticate/Lucario, Chandelure/Oricorio,
Vaporeon/Greninja, the puppy pile, Dustox/Magmar, Beautifly/Dustox and Mega Kangaskhan from outside it.

Record by Dustin's deck: Deck 02 Arceus/Crobat 1-3, Brew 01 Arceus/Crobat/Xatu 1-3, Brew 05 Meowstic/
Hatterene/Comfey 3-3 (plus the Cape variant 1-2), Brew 03a Arceus/Nihilego/Toxapex 1-3, Brew 04 Xatu/
TR Slowking 1-0, Deck 07 Skarmory stall 3-1, Skarmory ex/Chandelure 1-0, Brew 06 Payback 0-3, Brew 06b
Payback (Grass) 0-3.

Things to keep in mind:
- Six of the 33 mappings are inferences from partial notes (marked `likely` in the CSV): Darkrai/Espeon
  sleep -> Altaria; magikarp/carvanha -> Sharpedo/Gyarados; "Charizard ex / entei ex" -> Mega Charizard
  Y; igglybuff/darkrai/milotic -> Milotic ex Igglybuff; eevee/greninja ex -> Vaporeon ex Greninja ex;
  lucario + raticate -> Raticate ex Mega Lucario ex. Card facts behind them were checked with
  `lib/card.py` (Darkrai B2b Bad Dreams, Espeon B3a Hypnoblast, Growlithe B3b / Lillipup B3 Puppy Pile).
- "Panel variant" means the same main attacker line with a different partner (Mega Lucario ex with
  Hitmontop, Dugtrio or Hitmonchan ex; Hydreigon with Mega Sableye ex; TR Weezing ex with TR Magmar).
  Exact-only counts are given everywhere so the family rule can be rejected without redoing anything.
- The Sept 24 review summarised the same 33 games as "7-1 against homebrew piles, 5-10 against the
  panel, 0-10 against other established decks". Tonight's mapping keeps 5-10 against the panel family
  but finds a Limitless name for all but one of the other 18 (3-5 against top-30 decks, 4-5 against
  listed decks outside the top 30). The games are the same; the labels differ because "listed on
  Limitless" is a low bar (Dustox/Magmar has 5 match rows, Milotic/Igglybuff 43, the puppy pile 47,
  Vaporeon/Greninja 52), so most of what the review called homebrew piles are fringe lists, and two of
  those seven wins were opponents who quit early (the Sharpedo player before evolving, the Eevee player
  before Greninja). Either label supports the same message: he is losing to the decks the panel has,
  and the decks he beats are mostly ones the panel does not see.
- Dates are Dustin-local; the artifact's UTC timestamps are kept in the CSV's `ts` column.

## 2. The proposed ladder-weighted panel

Ten lists: the eight in `decks/screen/opponents/` plus the two built tonight for the only off-panel decks
he met twice, `l-charizardy.txt` (Mega Charizard Y ex / Entei ex) and `l-sharpedo.txt` (Mega Sharpedo ex /
Gyarados). Weights come from the 19 logged games against one of these ten (family view for the eight),
with one rule for lists he never met.

**The floor rule, proposed: count every list as met one more time than it was ("add one").** With 19
games over 10 lists that puts the total at 29, and a never-met list gets 1/29 = 3.4%, about one logged
game's worth. Why that and not zero: one game is the smallest thing this log can resolve, so 0 games and
1 game are the same evidence; Sceptile is the third-largest tournament deck (4.95% on Sept 10), and even
if the ladder matched Limitless exactly there is about a 1-in-5 chance of meeting none in 33 games
(0.9505 to the 33rd power is 0.19), so its absence is not evidence it is gone; a zero weight would make
the screen blind to a top-3 tournament deck, which the B4b refresh and the held-out checks still need it
to see. Why "add one" and not a fixed 5% or the 50/50 blend with Limitless recorded in `ladder_counts.md`:
it is one sentence to explain, it needs no second data source, and it fades on its own as the log grows
(at 100 logged games the floor is under 1%). The 50/50 blend is a fine alternative if Dustin would rather
lean on the tournament meta; it is tabulated for the eight in `ladder_counts.md`.

| List | Ladder games (family) | Raw share of 19 | Proposed weight (add one, of 29) | Limitless Sept 10, rescaled over these ten |
|---|---|---|---|---|
| t-lucario | 4 | 21.1% | **17.2%** | 20.4% |
| t-altaria | 2 | 10.5% | **10.3%** | 12.1% |
| t-sceptile | 0 | 0% | **3.4%** (floor) | 11.8% |
| t-vespiquen | 2 | 10.5% | **10.3%** | 11.5% |
| t-suicune | 1 | 5.3% | **6.9%** | 11.3% |
| t-weezing | 1 | 5.3% | **6.9%** | 9.9% |
| t-blaziken | 2 | 10.5% | **10.3%** | 8.7% |
| t-hydreigon | 3 | 15.8% | **13.8%** | 8.3% |
| l-charizardy | 2 | 10.5% | **10.3%** | 4.2% |
| l-sharpedo | 2 | 10.5% | **10.3%** | 1.8% |

If the family rule is rejected (variants not counted), the exact-only counts are Lucario 1, Altaria 2,
Sceptile 0, Vespiquen 2, Suicune 1, Weezing 0, Blaziken 2, Hydreigon 2, Charizard Y 2, Sharpedo 2 (14
games), and the same add-one rule gives Lucario 8.3%, Sceptile and Weezing 4.2% each, Suicune 8.3%, and
the other six 12.5% each.

**How the weighted readout differs from today's equal-weight average.** `run_screen.py` reports one
number: total wins over total games against the eight lists, so each list is 12.5% of the answer and
Charizard Y and Sharpedo are 0%. The weighted readout is each list's win rate times its weight, summed:
Lucario becomes 17% of the answer instead of 12.5%, Sceptile 3.4% instead of 12.5%, and the two new
lists take 21% between them. A toy example shows the size of the shift: a deck at 60% against everything
except 10% against Sceptile reads 53.8% on today's eight-list average, 55.0% on a ten-list equal average
and 58.3% ladder-weighted; the same deck with its 10% against Lucario instead reads 53.8%, 55.0% and
51.4%. On the Sept 24 screen, Skarmory's worst cells were Blaziken 23%, Sceptile 35% and Lucario 40%;
under ladder weights its Sceptile problem matters less and its Lucario problem more, which is what the
ladder says too (0-4 against Lucario decks). No weighted number is computed for any deck here: the two
new lists have no cells yet, and the ranking readout is held (section 4). Two practical points for
whoever wires it in: keep the games per matchup equal (240 for the floor, 60 for the quick screen) and
weight only the readout, so every cell keeps the same noise; and the floor's verdict is unaffected by
weights by design (it counts total wins over all cells), so adding the two lists to `opponents/` would
change the floor's definition (10 x 240 = 2,400 games, band about +/-1.6 points, edges fail <= 441,
borderline 442-518, clears >= 519 by the same arithmetic as `floor.py`'s) and would need the Payback
pre-use check re-run before any floor verdict is used.

## 3. A3 calibration prep (prepared, not run)

Full detail and the pre-registered reading rule are in `calibration_README.md`. The short version:

- **Games:** 19 logged games have an opponent with a list file; 18 are usable (the Sept 16 Skarmory ex /
  Chandelure win has no deck file). Dustin is 6-12 on the 18, base rate 0.333. They make 15 distinct
  (Dustin's deck, opponent list) pairs; `calibration_games.csv` has the rows.
- **Runner:** `run_calibration.py` (WSL or the cloud) plays the 15 pairs at 500 games each, kp3 on both
  sides, 250 games per slot, on the official engine resolved and hash-checked through `current_engine.py`
  like `run_screen.py`. Seeds: 21,107,000,000 + pair x 10,000 (+5,000 for slot 1), so the run uses up to
  21,107,149,999; **the block 21,107,000,000 to 21,107,199,999 should be added to START_HERE's seed
  table when this is wired in** (I did not edit START_HERE). It appends one pair at a time and `--resume`
  continues a stopped run; `--pairs-only` lists the pairs and seeds without touching the engine.
- **Scorer:** `calibrate.py` (Windows python, standard library only): Brier score of the sim against the
  constant base rate (in-sample and leave-one-out), the coin, a skill score, log-likelihood ratio in
  bits with a 2% clip, paired bootstrap over games with 90% and 95% intervals, a reliability table, a
  per-game list, `--json`. Tested on synthetic files (all passed) and joined to the 2-game smoke.
- **Smoke only:** `run_calibration.py --games 2 --only 1 --seed 21107990000` ran on
  `rl/engine-2026-09-25/deckgym` (f4d235e5...) in 3.9 s under tonight's training load, about 2 s a game,
  so roughly 4 hours for 7,500 games under load and less on an idle laptop.
- **What it can show, decided in advance:** at 18 games a perfectly calibrated sim gets a 90% interval
  above zero only 5-15% of the time, and a useless sim is caught 18-30% of the time, so the expected
  result is "cannot tell". The run can only expose a sim that is badly wrong on these decks, or a gap of
  about 22 points or more between the sim's average chance and Dustin's 33%. About 100 games would give
  24-64% power. The base rate's Brier is 0.222.
- **Resolutions worth knowing:** log id `brew-05` maps to `brew-05b-meowstic-hatterene-comfey.txt`, not the
  confusion file (the confusion file has no Comfey and no Peculiar Plaza, the game notes mention both,
  and `decks/screen/results.md` pairs the same 3-3 record with brew-05b); brew-04 and brew-03a played
  slightly off their files per the notes (marked `file-deviates`); 5 games were against variants, played
  against the panel list; 3 archetypes are inferred; who went first is known for 1 game only (the engine
  picks the starter from the seed, so the runner reports pooled chances, and `calibrate.py` accepts
  optional seat rows).
- **One dependency:** pairs 10 and 11 point at `l-charizardy.txt`. If the other Charizard Y list is chosen
  (section 5), change `opponent_file` on those two rows (or the table in `build_calibration_games.py`)
  before running.

## 4. What is ready to wire in, and what needs Dustin

Ready (nothing is wired; the laptop session owns `decks/screen` and the engine):
- `l-charizardy.txt` and `l-sharpedo.txt`: `lib/deck_check.py files` clean, 2-game smoke each on the
  official engine (loads and plays; a 2-game result is not a matchup number).
- The weights in section 2, as a table the screen can read (a `--weights` file or option for
  `run_screen.py` is the simplest form; nothing was added to the script).
- `run_calibration.py`, `calibrate.py`, `build_calibration_games.py`, `calibration_games.csv`.

Needs Dustin (decisions, in the order they block things):
1. **The ranking hold.** His Sept 25 decision lifted the hold for the floor check only; ranking stays held
   "until the ladder-weighted panel and the held-out decks exist". The panel is now proposed here and the
   held-out decks are in B2e prep (`rl/results/b2e_card_check_2026-09-26/`). Whether that lifts the
   hold, and when, is his call; until then the weighted readout is not to be used for ranking.
2. **The floor rule:** add one (proposed), the 50/50 blend with Limitless, or the pure ladder shares.
3. **The family rule:** count variants as the panel deck (proposed) or exact names only.
4. **Where the two new lists live:** readout only (weights, no change to the floor), or into `opponents/`
   (which redefines the floor and requires the Payback pre-use check again).
5. **Which Charizard Y list** represents the archetype, `l-charizardy.txt` or B2e's `h-charizardy_entei.txt`
   (section 5; they differ by two cards).
6. **Whether Manectric joins the panel.** The Sept 24 review's A2 named Entei/Charizard, Darkrai/Espeon and
   Manectric; Darkrai/Espeon turned out to be the panel Altaria list, Charizard is here, and Manectric was
   met once (0-1). A list exists in B2e prep (`h-manectric.txt`). Proposal: not on one game; revisit when
   the log grows.
7. **Go/no-go for the calibration run** (about 4 laptop hours under load), and the seed-table line in
   START_HERE.
8. Whether to keep the `l-sharpedo.provenance.json` sidecar next to the deck file (delete it if unwanted;
   the Charizard one is in the scratchpad).

## 5. Provenance of every list

- **The eight `t-*.txt` panel lists** are the Sept 8 competitive study's archetype lists (Pocket Deck Lab,
  `competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/`), kept in this repo
  as `decks/research/*.txt` (card ids only) and `decks/screen/opponents/t-*.txt` (ids with names).
  Checked tonight: all eight `t-` files match `decks/research` card id for card id. Their file
  fingerprints are in `rl/results/limitless_check_2026-09-23.md`. The player and event behind each are in
  the study's own notes and were not re-checked tonight.
- **`l-charizardy.txt`** (Mega Charizard Y ex / Entei ex; Limitless deck id
  mega-charizard-y-ex-b1a-entei-ex-a4a; top-30 #12, 1.77% on Sept 10). Copied from the local pull
  `rl/results/limitless_skill_model_2026-09-25/decklists/charizardy_entei.txt` (sha256 b3fe8356...,
  verified against `decklist_sources.json`), which is the most frequent exact list among the archetype's
  13 top-8 entries (3 of 13 share it). Representative: player ibfasting, "TBC Presents: Breakfast &
  Breakdowns" (6a9b4f52ab080c8c957fa3d7), Sept 6, 97 players, 6th; the same 20 cards placed 8th of 116
  (winsters, Tournament Vegegras, Sept 5) and 8th of 97 (guunnz, same TBC event). All 12 ids resolved to
  one printing each with `lib/card.py`. Known limits: the pull stored only this one list of the 13
  entries, so a higher-placing list may exist; it runs a single Mega Charizard Y ex on a 2-2 Charmander
  line with Wally and no Rare Candy, as published; one of its two ladder games is the inferred one.
  Sidecar: scratchpad `panel/l-charizardy.provenance.json`.
  **A second list for the same archetype was built tonight by the B2e job**,
  `rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt`: player sinorci200, 3rd of 172 at
  Umbreon99's Team Rocket's Bash (6a9f6899a4272c53be64a894), Sept 8, chosen as best placing in the
  largest development-split event. The two share 18 of 20 cards: `l-` has Protective Poncho B2 147 and
  a second Rainbow Cave B4 155 where `h-` has Pokémon Center Lady A2b 070 and Lucky Ice Pop B2 145
  (names checked with `lib/card.py`). Either is a fair stand-in; the `h-` list is the better-placed one,
  the `l-` list the more common one. One should be chosen before wiring (section 4, item 5).
- **`l-sharpedo.txt`** (Mega Sharpedo ex / Gyarados; Limitless deck id mega-sharpedo-ex-b4-gyarados-a4;
  top-30 #24, 42 players / 0.74% on Sept 10). Player nandosgude ("PGX | Nandosgude"), 1st of 27 (5-0-0),
  Trinity Tournament 3 (6aa17016a4272c53be64bb41), Sept 12, read from the cached API standings
  `rl/results/limitless_skill_model_2026-09-25/raw/6aa17016a4272c53be64bb41_standings.json.gz`, not the
  web. Selection: best placing then largest event among 81 player-events of this deck id in the cached
  Aug 26 to Sep 24 standings; the only 1st place. The identical 20 cards also placed 2nd (hectordf) and
  7th (victorssito) at a 27-player OTS event on Sept 9. All 13 ids resolved to one printing each.
  Known limits: the source event is in the skill model's frozen holdout split (only the decklist was
  read, no match outcomes; the holdout is already spent per its README), and a development-only
  alternative is recorded in the sidecar (shmo, 3rd of 64, TBC Kelp Classic #9, Sept 10: 2 Wallace /
  1 Lisia / 1 Irida, no Soothing Shore); the event is small and no 100+ player top-8 uses this exact
  list; the API record has no energy field, so Energy: Water was inferred (every Pokémon is Water and
  the 2nd-place copy lists Water); one of its two ladder games is the inferred one. Sidecar:
  `l-sharpedo.provenance.json` here.

## 6. Files

In this folder (`decks/screen/panel_ladder_2026-09-26/`):
- `README.md` (this file), `ladder_counts.md` (the counts with tables and the mapping notes),
  `ladder_mapping.csv` (33 rows, one per game: opponent text, mapped archetype, class, result, panel key,
  confidence, UTC timestamp).
- `l-charizardy.txt`, `l-sharpedo.txt`, `l-sharpedo.provenance.json`.
- `calibration_README.md`, `calibration_games.csv`, `run_calibration.py`, `calibrate.py`,
  `build_calibration_games.py`.

## 7. The skeptic's pass (`skeptic.md`), added after the sections above were written

An independent agent re-read the Ladder Log, recounted everything and tried to refute the mapping and
the weights. Nothing above changes as a number, but Dustin should read these before choosing:

- **Every count reproduces** (classes, per-panel strict and family counts, the record by deck, the
  weights, the floor arithmetic, the toy example); all ten lists pass `deck_check`; both new lists'
  provenance was confirmed against the Limitless page once and the cached standings.
- **Two mapping fixes were made in `ladder_mapping.csv`:** the Sept 16 "Hydreigon / bombirdier" row is an
  inference, not an exact match (so seven mappings are inferred, not six; `ladder_counts.md` still says
  six); and "Mega Blaziken ex / castform sunny form" is Limitless's separately named "Mega Blaziken ex
  Castform Sunny Form" (217 rows), which is what `t-blaziken.txt` itself runs, so the panel's Blaziken
  list is by Limitless naming the Castform build and not the 1,522-row bare archetype. Neither fix moves
  a weight.
- **Pushbacks, left as flags:** (a) the weights cover 19 of the 33 games, so the weighted readout is
  "against the 58% of the ladder we have lists for" and is more concentrated than the ladder itself;
  (b) each of the two new lists earns its place through one exact game plus one inferred game, which
  puts Charizard Y, Sharpedo and Manectric (one exact game each) on equal footing, so declining
  Manectric "on one game" while admitting the other two is a choice to make knowingly (confident-only
  add-one weights are in `skeptic.md`); (c) uniform add-one funds Sceptile's floor partly out of
  Lucario's four-game count; a floor-the-zero-cells-only variant is tabled beside it; (d) the Weezing
  "variant" is the weakest family case, since the TR Magmar build changes the attacker, not the partner;
  dropping it halves Weezing's weight to 3.4%; (e) the Sept 10 top-30 is stale against the Sept 25 pull
  (Beautifly Dustox has more match rows than three current top-30 decks), so the split should be re-run
  when the classifier snapshot is refreshed; (f) "listed on Limitless" is a low bar for "established"
  (Dustox / TR Magmar is one player's list), so the homebrew count depends on where the bar sits, and the
  reconciliation with the Sept 24 review's "7-1 against homebrew piles" depends on it too; (g) two of
  Dustin's wins in the calibration set are concessions the simulator cannot reproduce, so a sensitivity
  run without them (16 games, 4-12) should be reported beside the 18-game result.
- **Understated caveat on `l-charizardy`:** 6th of 97 on 6-2-2 is a top-8 by tiebreak, and the
  archetype has 11 distinct lists among 13 top-8 entries, so there is no consensus build; the B2e list
  (3rd of 172) is the better-placed one.

In the scratchpad (`...\scratchpad\panel\`, session-local, not in the repo): `check_counts.py` (recomputes
`ladder_counts.md` from the CSV; re-run tonight, agrees), `l-charizardy.provenance.json`,
`extract_sharpedo.py`, `sharpedo_candidates.json`, `smoke_l-charizardy.sh`, `smoke_sharpedo.sh`,
`smoke_calibration.sh`, `smoke_sim_results.csv`, `test_calibrate.py`, `synthetic/` (the power check),
`artifact_db/` (the artifact export: `logs/`, `decks/`), `calibration_games_check.csv`.
