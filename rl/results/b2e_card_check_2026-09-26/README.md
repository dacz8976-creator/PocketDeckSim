# B2e: six held-out archetypes against the panel. Specification for the runs (Sept 26, 2026)

Decision this informs: none yet. This folder prepares the B2e runs and fixes how they will be read. The runs
themselves are not started (the laptop is training a network tonight; only 2-game smoke tests have been played).

## 1. Summary

The simulator has only ever been scored against the eight decks in its panel, so we do not know how far off it is
on a deck it was never checked against. B2e takes six more real tournament decks (ones Dustin also owns), plays
each against the eight panel decks in the simulator, and compares the result with what actually happened in
tournaments between Aug 26 and Sep 24. Everything the runs need is now in this folder: a tournament list for each
of the six decks, chosen from the best placings in that window; Dustin's own version of each deck; the real
tournament record of each deck against each panel deck (48 pairs of numbers, built from 30,216 match records and
recomputed independently to the byte); a card-by-card check that the engine's text for every card in all twelve
lists matches Limitless (it does; the only differences were wording, like "a random" against "1 random"); and a
list of the cards the bot is known not to price properly. The runs are 500 games per pairing, two pilots (k3 and
kp3) on both sides, 96 pairings, on the official engine, with seeds from 21,106,000,000. Their result is a
baseline, not a decision: it says how close the simulator gets on decks it was never tuned to, and it becomes
the reference for two rules already agreed. No later change to the bot may push a held-out deck's panel average
more than 2 points further from its real result, and the quick screen may not rank brews until each held-out
deck's simulated panel score lands inside its real result's interval. The real numbers are thin for Garchomp and
very thin for Whimsicott, so those two say little either way.

## 2. The six held-out decks

Selection rule for the archetype lists: the Cowork agent's Limitless pull for the window (development-half
events only; holdout standings were not opened), best placing first, larger event as the tiebreaker, exact
Limitless deck name. Every card is the printing the source names; every id resolves to one printing in
`lib/deckgym-database.json` (`python lib/card.py "<SET> <NUMBER>"`). All twelve files pass
`python lib/deck_check.py files <file>` ("decks clean"; note the `files` word, the bare form exits 1). The one
WARN is h-manectric's 2 Mega Manectric ex on 1 Electrike, which is what the source list runs. Each archetype list
also ran a 2-game smoke against t-lucario on the official engine (k3 on both sides, seed 21,106,999,000 with
`--seed-stream`), exit 0 in all six cases; those results are run checks, not matchup numbers.

| # | Limitless archetype (deck_name) | Archetype list (this folder, `decks/`) | Provenance: player, event, date, placing, source | Dustin's file | Diff, archetype list against Dustin's |
|---|---|---|---|---|---|
| 1 | Mega Manectric ex Heliolisk | `h-manectric.txt` | nyrq, The PokeBounty Showdown $1000 Prize Pool (#2NA), 142 players, 2026-09-14, 1st. Source: Cowork pull `rl/results/limitless_skill_model_2026-09-25/decklists/manectric_heliolisk.txt` (deck id mega-manectric-ex-b2b-heliolisk-b4; `decklist_sources.json`). The same 20 cards were played by 9 of the 11 top-8 finishers in the window, including 3rd of 219 and 1st of 110. | `decks/dustin/09-mega-manectric-heliolisk.txt` | +1 Clemont B1a 068 (1 to 2), -1 Electrike B2b 026 (2 to 1); the other 18 cards and the Energy line are identical. |
| 2 | Team Rocket's Raticate ex Alolan Ninetales ex | `h-raticate.txt` | shmo, Pop Up Series 9 \|\| FA OAK, 27 players, 2026-09-17, 3rd. Source: Cowork pull `decklists/raticate_ninetales.txt` (deck id team-rockets-raticate-ex-b4a-alolan-ninetales-ex-b2); the same list placed 7th of 34 on 2026-09-06. Only 3 eligible top-8 entries in the window, all at small events. Provenance copy: `decks/h-raticate.source.json`. | `decks/dustin/13-a-ninetales-raticate.txt` | +2 Alolan Vulpix A3 040, +1 Copycat (1 to 2), +1 Repel A3a 064, +1 Training Area B2 153; -2 Alolan Vulpix B2 028, -1 Field Blower, -1 Ilima, -1 Sightseer. The Vulpix swap is functional: A3 040 attaches Energy (Call Forth Cold), B2 028 attacks (Gnaw). |
| 3 | Hoopa ex Mega Absol ex | `h-hoopa_absol.txt` | seedax, TBC x HYPE PACKS: AFTERMADS #1 - $150, 134 players, 2026-09-13, 1st (10-2-1). Source: Cowork pull raw standings `raw/6a989e74a4272c53be6453c4_standings.json.gz` (deck id hoopa-ex-b4-mega-absol-ex-b1). Equals the 12-of-20 consensus list with 1 Starting Plains in place of 1 Mars. Provenance: `provenance/h-hoopa_absol.json`. | `decks/dustin/04-absol-hoopa-darkrai.txt` (also the base of `decks/brews/brew-07-hoopa-darkrai-sableye.txt`) | +1 Mega Absol ex B1 151, +1 Cyrus, +1 Pokémon Center Lady, +2 Lucky Ice Pop, +1 Repel, +1 Field Blower; -2 Absol B4 100, -1 Bombirdier, -1 Happiny, -1 Sabrina, -1 Copycat (2 to 1), -1 Starting Plains (2 to 1). 11 of 20 shared. |
| 4 | Garchomp | `h-garchomp.txt` | cosmooo (FrogEX \| Cosmo, FR), Dark League Pop Up, 21 players, 2026-08-28, 2nd (6-3-0). Source: Cowork pull `decklists/garchomp.txt` (deck id garchomp-b4a), verified against `raw/6a91426eabb94822375023de_standings.json.gz`. The only exact-"Garchomp" top-8 finish in the window; better-placed Garchomp lists carry other archetype names (Garchomp Meowth, Garchomp Greninja) and were not used. | `decks/dustin/08-garchomp-toolbox.txt` | 8 slots shared. +1 Gible B4a 052, +1 Happiny, +1 Mantyke, +1 Cleffa, +1 Cynthia (1 to 2), +1 Cyrus, +1 Lisia, +2 Rare Candy, +1 Protective Poncho; -1 Celebi, -1 Gible A2 121 (2 to 1), -2 Gabite, -1 Munchlax, -1 Poké Ball (2 to 1), -1 Pokémon Flute, -1 Lucky Ice Pop, -1 Small Balloon, -1 Mesagoza. The tournament list skips Gabite (Rare Candy line); Dustin runs the Gabite line. |
| 5 | Whimsicott ex Ariados | `h-whimsicott.txt` | birdnest (US), The Breakfast Club Xastur's Showdown-$5+OAK+, 97 players, 2026-08-28, 3rd (7-4-0). Source: Cowork pull `decklists/whimsicott_ariados.txt` (deck id whimsicott-ex-b1-ariados-b1a), verified against `raw/6a90e8157a62de8130140dee_standings.json.gz`. Best placing among the 45 entries of this name in the window. Provenance: `provenance/h-whimsicott.json`. | `decks/dustin/12-ariados-whimsicott-ogerpon.txt` | +1 Pheromosa A3a 007, +1 Cyrus, +1 Quick-Grow Extract (1 to 2), +2 Fragrant Forest; -1 Teal Mask Ogerpon ex, -1 X Speed, -1 Poké Ball, -1 Lisia, -1 Hiking Trail. The 2-2 Cottonee/Whimsicott ex, 2-2 Spinarak/Ariados, 2 Goo-zooka, 1 Leaf Cape, 2 Professor's Research, 1 Copycat core is shared. |
| 6 | Mega Charizard Y ex Entei ex | `h-charizardy_entei.txt` | sinorci200 (FGR \|\| Sinorci200, IT), Umbreon99's Team Rocket's Bash: $10 USD, 172 players, 2026-09-08, 3rd (8-2-1). Source: Cowork pull raw standings `raw/6a9f6899a4272c53be64a894_standings.json.gz` (deck id mega-charizard-y-ex-b1a-entei-ex-a4a). Best placing among the 13 top-8 entries of this deck id in the development events; not the `decklist_sources.json` representative (ibfasting, 6th of 97, the most frequent list). Provenance: `provenance/h-charizardy_entei.json`. | `decks/brews/brew-08-entei-rainbow-cave.txt` (the brew's base) | +2 Charmander B2b 007, +2 Charmeleon B2b 008, +1 Mega Charizard Y ex B1a 014, +1 Wally, +1 Poké Ball (1 to 2); -1 Sabrina, -1 Cyrus, -1 Lucky Ice Pop (2 to 1), -1 Repel, -1 Giant Cape (2 to 1), -1 Rainbow Cave (2 to 1), -1 Starting Plains. 13 of 20 shared. brew-08 has no Charizard line at all (Entei ex is its only Pokémon), so the archetype name fits the brew loosely. |

Limitless deck names for the panel labels: lucario = Mega Lucario ex Lucario, altaria = Mega Altaria ex Espeon,
sceptile = Butterfree Mega Sceptile ex, vespiquen = Vespiquen ex Shuckle ex, suicune = Suicune ex Baxcalibur,
hydreigon = Hydreigon Mega Absol ex, weezing = Team Rocket's Weezing ex Hoopa ex, blaziken = Mega Blaziken ex.
The panel files are `decks/screen/opponents/t-<label>.txt`; they hold the same 20 cards as the table's
`decks/research/<label>.txt` (checked line by line; the research files carry ids only).

## 3. The Limitless cells each deck is read against

**Source and window.** `rl/results/limitless_skill_model_2026-09-25/matches.csv`, 30,216 match records.
Window 2026-08-26 to 2026-09-24 (UTC event start dates; first event start 2026-08-26T10:35Z, last
2026-09-24T17:00Z). 126 events, split at random into 63 development and 63 holdout (seed 26092500001). Records:
development 14,127, holdout 16,089; modes BO1 20,037, BO3 10,177, BO5 2 (the BO5 records touch no held deck).

**Counting rules** (the scoreboard's, `cells.py`): the held side is identified by exact deck_name, the panel side
by archetype label (each label maps to exactly one deck_name); a tie is half a point and counts in n; a double
loss (winner = -1) is excluded from W-L-T and n and reported in a DL column; byes have no opponent side and never
form a pair; mirrors cannot occur; every record is one unit, BO1 and BO3 alike, with BO1-only figures beside it in
the CSV; score = (W + 0.5 T) / n; band = 1.96 sqrt(p(1-p)/n) in points, which collapses to 0 at 0% or 100% (read
those cells as "no information", not as certain). The unlabeled same-name variants (garchomp-a2, 24 records;
heliolisk-b1a, 7) count for the held side because the key is the deck name. An independent recompute, written
without reading `cells.py`, reproduced all 180 rows and 3,600 values of `limitless_cells.csv` byte for byte
(SHA256 32040E53…CBE4 for both files; `independent_recompute/`).

**How to read these cells.** The holdout half was spent once, on Sept 25, to confirm kp3 as the pilot
(`rl/results/holdout_kp3_2026-09-25/READING.md`). So nothing here is a fresh test; the cells below, development
and pooled alike, are descriptive baselines. **Pooled (both halves) is the reference for the "+2 further from
Limitless" veto**, because it has twice the matches; the development-half figure is reported beside it. Any later
pilot adoption is confirmed on events after the freeze date (events starting after the window's last event on
Sept 24, 2026), never on these cells.

Cell format below: W-L-T, n, score %, +/- 95% band. "Equal-weight" is the unweighted mean of the eight cell
scores (opponents with n > 0), with its band from the same binomial formula (`panel_bands.py`,
`panel_intervals.csv`); "match-weighted" is all panel matches pooled. DL = double losses excluded.

### 3.1 Mega Manectric ex Heliolisk

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 14-21-1 | 36 | 40.3 | 16.0 | 35-55-3 | 93 | 39.2 | 9.9 |
| altaria | 26-22-3 | 51 | 53.9 | 13.7 | 55-48-7 | 110 | 53.2 | 9.3 |
| sceptile | 13-23-2 | 38 | 36.8 | 15.3 | 29-45-3 | 77 | 39.6 | 10.9 |
| vespiquen | 12-17-1 | 30 | 41.7 | 17.6 | 35-32-2 | 69 | 52.2 | 11.8 |
| suicune | 17-9-2 | 28 | 64.3 | 17.7 | 27-14-6 | 47 | 63.8 | 13.7 |
| hydreigon | 8-12-0 | 20 | 40.0 | 21.5 | 24-27-0 | 51 | 47.1 | 13.7 |
| weezing | 4-8-0 | 12 | 33.3 | 26.7 | 7-13-0 | 20 | 35.0 | 20.9 |
| blaziken | 10-3-2 | 15 | 73.3 | 22.4 | 22-12-3 | 37 | 63.5 | 15.5 |
| **Equal-weight average** | 8 opp. | | **48.0** | 6.8 | 8 opp. | | **49.2** | 4.8 |
| Match-weighted | 104-115-11 (DL 9) | 230 | 47.6 | 6.5 | 234-246-24 (DL 16) | 504 | 48.8 | 4.4 |

### 3.2 Team Rocket's Raticate ex Alolan Ninetales ex

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 12-13-0 | 25 | 48.0 | 19.6 | 22-32-0 | 54 | 40.7 | 13.1 |
| altaria | 1-9-0 | 10 | 10.0 | 18.6 | 3-29-0 | 32 | 9.4 | 10.1 |
| sceptile | 8-7-1 | 16 | 53.1 | 24.5 | 9-19-1 | 29 | 32.8 | 17.1 |
| vespiquen | 6-8-0 | 14 | 42.9 | 25.9 | 19-21-1 | 41 | 47.6 | 15.3 |
| suicune | 8-11-0 | 19 | 42.1 | 22.2 | 16-17-1 | 34 | 48.5 | 16.8 |
| hydreigon | 3-4-0 | 7 | 42.9 | 36.7 | 9-9-0 | 18 | 50.0 | 23.1 |
| weezing | 4-9-1 | 14 | 32.1 | 24.5 | 10-20-1 | 31 | 33.9 | 16.7 |
| blaziken | 7-1-0 | 8 | 87.5 | 22.9 | 12-6-0 | 18 | 66.7 | 21.8 |
| **Equal-weight average** | 8 opp. | | **44.8** | 8.8 | 8 opp. | | **41.2** | 6.1 |
| Match-weighted | 49-62-2 (DL 5) | 113 | 44.2 | 9.2 | 100-153-4 (DL 12) | 257 | 39.7 | 6.0 |

Altaria is a near-shutout for this deck (3-29 pooled).

### 3.3 Hoopa ex Mega Absol ex

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 29-30-1 | 60 | 49.2 | 12.6 | 41-53-1 | 95 | 43.7 | 10.0 |
| altaria | 54-21-6 | 81 | 70.4 | 9.9 | 95-35-10 | 140 | 71.4 | 7.5 |
| sceptile | 18-27-2 | 47 | 40.4 | 14.0 | 24-50-3 | 77 | 33.1 | 10.5 |
| vespiquen | 5-20-3 | 28 | 23.2 | 15.6 | 12-38-3 | 53 | 25.5 | 11.7 |
| suicune | 14-15-1 | 30 | 48.3 | 17.9 | 25-25-1 | 51 | 50.0 | 13.7 |
| hydreigon | 17-9-0 | 26 | 65.4 | 18.3 | 32-15-1 | 48 | 67.7 | 13.2 |
| weezing | 7-12-0 | 19 | 36.8 | 21.7 | 13-20-0 | 33 | 39.4 | 16.7 |
| blaziken | 9-2-1 | 12 | 79.2 | 23.0 | 16-7-1 | 24 | 68.8 | 18.5 |
| **Equal-weight average** | 8 opp. | | **51.6** | 6.1 | 8 opp. | | **49.9** | 4.7 |
| Match-weighted | 153-136-14 (DL 10) | 303 | 52.8 | 5.6 | 258-243-20 (DL 13) | 521 | 51.4 | 4.3 |

### 3.4 Garchomp

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 9-9-2 | 20 | 50.0 | 21.9 | 13-18-4 | 35 | 42.9 | 16.4 |
| altaria | 4-7-0 | 11 | 36.4 | 28.4 | 9-9-0 | 18 | 50.0 | 23.1 |
| sceptile | 3-3-0 | 6 | 50.0 | 40.0 | 5-10-0 | 15 | 33.3 | 23.9 |
| vespiquen | 2-3-0 | 5 | 40.0 | 42.9 | 8-10-0 | 18 | 44.4 | 23.0 |
| suicune | 2-7-0 | 9 | 22.2 | 27.2 | 7-14-0 | 21 | 33.3 | 20.2 |
| hydreigon | 2-4-0 | 6 | 33.3 | 37.7 | 4-9-0 | 13 | 30.8 | 25.1 |
| weezing | 1-9-1 | 11 | 13.6 | 20.3 | 2-13-1 | 16 | 15.6 | 17.8 |
| blaziken | 1-1-0 | 2 | 50.0 | 69.3 | 1-9-0 | 10 | 10.0 | 18.6 |
| **Equal-weight average** | 8 opp. | | **36.9** | 13.8 | 8 opp. | | **32.5** | 7.5 |
| Match-weighted | 24-43-3 (DL 2) | 70 | 36.4 | 11.3 | 49-92-5 (DL 3) | 146 | 35.3 | 7.8 |

Thin everywhere (cells of 10 to 35 matches pooled; bands 16 to 25 points).

### 3.5 Whimsicott ex Ariados

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 5-3-0 | 8 | 62.5 | 33.5 | 6-10-0 | 16 | 37.5 | 23.7 |
| altaria | 1-0-0 | 1 | 100.0 | 0.0 | 1-3-0 | 4 | 25.0 | 42.4 |
| sceptile | 0-2-0 | 2 | 0.0 | 0.0 | 1-4-0 | 5 | 20.0 | 35.1 |
| vespiquen | 3-4-0 | 7 | 42.9 | 36.7 | 5-6-0 | 11 | 45.5 | 29.4 |
| suicune | 3-3-0 | 6 | 50.0 | 40.0 | 5-4-0 | 9 | 55.6 | 32.5 |
| hydreigon | 2-3-0 | 5 | 40.0 | 42.9 | 3-3-0 | 6 | 50.0 | 40.0 |
| weezing | 1-4-0 | 5 | 20.0 | 35.1 | 2-6-0 | 8 | 25.0 | 30.0 |
| blaziken | no games | 0 | | | 0-1-0 | 1 | 0.0 | 0.0 |
| **Equal-weight average** | 7 opp. | | **45.1** | 12.1 | 8 opp. | | **32.3** | 11.2 |
| Match-weighted | 15-19-0 (DL 2) | 34 | 44.1 | 16.7 | 23-37-0 (DL 5) | 60 | 38.3 | 12.3 |

Every cell is thin (1 to 16 matches pooled; bands 24 to 42 points, and 0 where the cell is one-sided). Treat this
deck's cells as near-uninformative; its equal-weight band understates the real uncertainty because three cells
contribute nothing to it.

### 3.6 Mega Charizard Y ex Entei ex

| Opponent | Dev W-L-T | n | Dev % | +/- | Pooled W-L-T | n | Pooled % | +/- |
|---|---|---:|---:|---:|---|---:|---:|---:|
| lucario | 34-13-0 | 47 | 72.3 | 12.8 | 60-29-4 | 93 | 66.7 | 9.6 |
| altaria | 21-32-1 | 54 | 39.8 | 13.1 | 41-60-2 | 103 | 40.8 | 9.5 |
| sceptile | 23-8-0 | 31 | 74.2 | 15.4 | 45-16-1 | 62 | 73.4 | 11.0 |
| vespiquen | 12-10-1 | 23 | 54.3 | 20.4 | 34-20-2 | 56 | 62.5 | 12.7 |
| suicune | 3-12-0 | 15 | 20.0 | 20.2 | 5-27-1 | 33 | 16.7 | 12.7 |
| hydreigon | 10-13-1 | 24 | 43.8 | 19.8 | 19-21-3 | 43 | 47.7 | 14.9 |
| weezing | 6-7-1 | 14 | 46.4 | 26.1 | 13-11-3 | 27 | 53.7 | 18.8 |
| blaziken | 4-7-0 | 11 | 36.4 | 28.4 | 9-19-0 | 28 | 32.1 | 17.3 |
| **Equal-weight average** | 8 opp. | | **48.4** | 7.2 | 8 opp. | | **49.2** | 4.8 |
| Match-weighted | 113-102-4 (DL 2) | 219 | 52.5 | 6.6 | 226-203-16 (DL 6) | 445 | 52.6 | 4.6 |

### 3.7 The intervals in one place (pooled; the reference for section 5)

| Archetype | Pooled equal-weight % | +/- | Interval | Development % | +/- | Matches pooled | Thinnest cell |
|---|---:|---:|---|---:|---:|---:|---:|
| Mega Manectric ex Heliolisk | 49.2 | 4.8 | 44.4 to 54.0 | 48.0 | 6.8 | 504 | 20 |
| Team Rocket's Raticate ex Alolan Ninetales ex | 41.2 | 6.1 | 35.1 to 47.3 | 44.8 | 8.8 | 257 | 18 |
| Hoopa ex Mega Absol ex | 49.9 | 4.7 | 45.3 to 54.6 | 51.6 | 6.1 | 521 | 24 |
| Garchomp | 32.5 | 7.5 | 25.0 to 40.0 | 36.9 | 13.8 | 146 | 10 |
| Whimsicott ex Ariados | 32.3 | 11.2 | 21.1 to 43.5 | 45.1 (7 opp.) | 12.1 | 60 | 1 |
| Mega Charizard Y ex Entei ex | 49.2 | 4.8 | 44.3 to 54.0 | 48.4 | 7.2 | 445 | 27 |

## 4. The run specification

**Engine.** The official engine `rl/engine-2026-09-25/` (main-7fc6ccb; version string 0.1.0-pdl.rules4):
`deckgym` sha256 f4d235e596cdd713546c17450fd66bd9d5eefe4baf53e93d66d8bbe1628e1034 and `legality_scan` sha256
d5c0a9528e076299875ac603667f7076951de885ea8465f3be0d1089b5afbbfb (`project_manifest.json`, `available_release`).
Nothing else may play a game that is read here.

**Pilots.** Two rows per pairing: k3 on both sides, then kp3 on both sides, both on the same deals so the two are
paired by deal. No mixed rows (kp3 against k3) in B2e; they belong to a later candidate's veto reading, on these
deals, if one fires. Never the jev bot.

**Pairings: 96, listed row by row in `b2e_pairings.tsv`.**
- Block A (pairings 0 to 47): each of the six archetype lists in `decks/h-<key>.txt` against each of the eight
  panel lists `decks/screen/opponents/t-<label>.txt`.
- Block B (pairings 48 to 95): each of Dustin's six own files (section 2) against the same eight.
- No held-out deck plays another held-out deck, no archetype list plays Dustin's version, and the panel does not
  play itself (its 28 pairings are the existing table).
- Order: pairing p = 8 × d + o (block A) or 48 + 8 × d + o (block B), with d the deck's row in section 2
  (0 Manectric, 1 Raticate, 2 Hoopa/Absol, 3 Garchomp, 4 Whimsicott, 5 Charizard Y/Entei) and o the opponent in
  the cells' order (0 lucario, 1 altaria, 2 sceptile, 3 vespiquen, 4 suicune, 5 hydreigon, 6 weezing, 7 blaziken).

**Games and seats.** 500 games per pairing per pilot, deals i = 0 to 499. The table's deal convention: even i puts
the first-named deck (the held-out deck) in seat 0, odd i puts the panel deck in seat 0, so each pairing is 250
games per seat. The cell score is the held-out deck's (wins + 0.5 × ties) / 500, a tie being the engine's draw
(`winner_seat` = -1 in the per-game file); report the tie count per cell.

**Seeds.** Block 21,106,000,000 to 21,106,999,999, claimed for B2e; it lies outside every range in START_HERE's
seed table (the nearest used ranges are 21,101,000,000 to 21,101,300,001 below it and 22,000,000,000 up above it).
One sub-block of 10,000 per pairing: seed(p, i) = 21,106,000,000 + p × 10,000 + i, i < 500; the rest of each
sub-block stays unused, as in the table. Sub-block 99 (21,106,990,000 up) holds the six 2-game smokes already
played (seed 21,106,999,000 and 21,106,999,001, k3 on both sides, against t-lucario). Sub-blocks 96 to 98 are spare.

| Block | Deck (d) | Pairings p | First seed | Last seed used |
|---|---|---|---:|---:|
| A | h-manectric | 0 to 7 | 21,106,000,000 | 21,106,070,499 |
| A | h-raticate | 8 to 15 | 21,106,080,000 | 21,106,150,499 |
| A | h-hoopa_absol | 16 to 23 | 21,106,160,000 | 21,106,230,499 |
| A | h-garchomp | 24 to 31 | 21,106,240,000 | 21,106,310,499 |
| A | h-whimsicott | 32 to 39 | 21,106,320,000 | 21,106,390,499 |
| A | h-charizardy_entei | 40 to 47 | 21,106,400,000 | 21,106,470,499 |
| B | dustin/09 Manectric | 48 to 55 | 21,106,480,000 | 21,106,550,499 |
| B | dustin/13 Raticate | 56 to 63 | 21,106,560,000 | 21,106,630,499 |
| B | dustin/04 Hoopa/Absol | 64 to 71 | 21,106,640,000 | 21,106,710,499 |
| B | dustin/08 Garchomp | 72 to 79 | 21,106,720,000 | 21,106,790,499 |
| B | dustin/12 Whimsicott | 80 to 87 | 21,106,800,000 | 21,106,870,499 |
| B | brew-08 Charizard Y/Entei base | 88 to 95 | 21,106,880,000 | 21,106,950,499 |

When the run is recorded, this block gets one row in START_HERE's seed table (a shared page: say so in the report
rather than editing it unasked).

**The tool, and the one change it needs.** The table's games are played by `legality_scan`, which checks every
offered move and resulting state against the rules page in the same pass and writes one JSON line per game
(`--games-out`); that per-game file is the table. Today the program hard-codes the eight panel names, their 28
pairings and the seed base 72,000,000 (`engine/examples/legality_scan.rs`, `NAMES`, `SEED_BASE`, the `pairs`
list), so B2e needs a small extension, built from main at 7fc6ccb plus that change only:
- `--pairs <tsv>`: play the pairings listed in `b2e_pairings.tsv` (pairing number, held file, panel file); the
  held file is the first-named deck; `first_seat = 0` for even i, `1` for odd i, exactly as `play_one` does now.
- `--seed-base <n>`: replaces 72,000,000; seed = base + pairing × 10,000 + i.
- Output lines as today, with `a` = held key, `b` = opponent label, `pairing` = p, plus `bot_a`, `bot_b`,
  `first_seat`, `winner_seat`, `points`, `turns`, `first_deck_score`, `moves` (the move hash).
- Without either flag the program must behave as today. Identity check before any B2e game is read: the new
  binary, with default flags, replays the table's reference files field by field including the move hash,
  `rl/results/per_game_table_2026-09-25/k3_500.jsonl` for k3 and `rl/results/public_pricing_2026-09-25/kp3_500_*.jsonl`
  for kp3, at least pairings 0, 5, 13 and 23 × 500 deals for each pilot (4,000 games; the full 14,000 each if time
  allows), the way `rl/results/engine_identity_2026-09-25/` did it. Record the new binary's sha256 in the run
  folder's `identity.txt`. The engine crate itself is not touched, so `deckgym`'s hash above stays the reference.
- Fallback only if the extension is refused: `deckgym simulate --players k3,k3 --seed-stream --results-output`
  with two calls per pairing (held deck in seat 0 on seeds base + p × 10,000 + 0 to 249; in seat 1 on
  + 5,000 to 5,249). That is a different deal convention from the table's, gives no legality findings, and would
  need a separate scan pass; if used, the run's README must say so and the two conventions must never be mixed.

**The legality scan** runs on exactly these 96 pairings (both pilots), not on the 28 panel pairings, which were
scanned on the official binary already (k3 `per_game_table_2026-09-25`, kp3 `public_pricing_2026-09-25`,
kp3 mixed rows `kp3_mixed_rows_2026-09-25`, all with no rule findings). Report findings per pairing: RULE (the
rules page says the move or state is impossible) stops the reading of that pairing until explained; CHECK is
listed with its example and the card that may allow it.

**Run folder and files.** A new results folder `rl/results/b2e_runs_<date>/` with: `run_b2e.sh` (the commands),
`identity.txt` (sha256 of the scan binary used and of `deckgym`), `b2e_k3_arch.{txt,jsonl}`, `b2e_kp3_arch.{txt,jsonl}`,
`b2e_k3_dustin.{txt,jsonl}`, `b2e_kp3_dustin.{txt,jsonl}`, `timing.txt` (wall seconds per file), and `READING.md`
with section 5's tables filled in. Cite this README as the specification. Re-run `python lib/deck_check.py files`
on all twelve files first and paste the output into `READING.md`.

**Time.** 28 pairings × 500 deals took 1,792 s (k3) and 1,561 s (kp3) of wall time in the cloud; 96 pairings is
3.4 times that, so about 1.7 hours per pilot at cloud speed and more on the laptop. Run it when the network
training has finished, not beside it, and never more than the 2-game smokes before then.

**Not part of B2e.** No ranking of the twelve decks, no adoption or tuning decision, no change to any list, no
runs of Dustin's other decks or the brews, no mixed rows.

## 5. The reading (descriptive only; no adoption decision is taken from it)

Fill one table per deck in `READING.md` in this form, with the Limitless columns copied from section 3 and the
simulator columns from the per-game files (cell score = mean of `first_deck_score` over the 500 deals, × 100):

| Opponent | Limitless pooled % (+/-) | Limitless dev % (+/-) | k3 % | kp3 % | Miss k3 (k3 minus pooled) | Miss kp3 | Beyond the band? |
|---|---|---|---|---|---|---|---|

- **Panel score**: the equal-weight mean of the deck's eight cell scores under that pilot (the same average a
  screen readout reports). Report it under k3 and under kp3, for the archetype list and for Dustin's file.
- **Gap**: panel score minus the Limitless equal-weight average, pooled (the reference) and development (beside
  it). For Whimsicott's development figure use the same seven opponents (no development games against blaziken).
- **Per-cell miss**: simulator cell minus the Limitless pooled cell; "beyond the band" when the absolute miss
  exceeds the combined band sqrt(band_L² + band_S²), with band_S the simulator's own 95% band at 500 games
  (4.4 points at 50%). Expect the panel's known misses to show through here: the 28-cell table overrates Sceptile
  by about 12 points and underrates Vespiquen by about 11 and Altaria by about 4 under kp3, so a held-out deck's
  sceptile, vespiquen and altaria cells will carry those errors from the other side; note them, do not fix them.
- **The list difference**: the archetype list's panel score minus Dustin's file's, per pilot. Dustin's files have
  no Limitless cells of their own; this number only says how much the list, rather than the pilot, moves the deck.
- **What kp3's row adds over k3's**: k3 scores cards that read the opponent's hand (Copycat, Darkness Claw) as
  doing nothing, and the Hydreigon gain of the pricing pilots was traced to exactly those cards
  (`rl/results/per_game_table_2026-09-25/README.md`, `rl/results/unpriced_census_2026-09-25/`); kp3's public
  pricing is the pilot that reproduced that gain with no list. The two rows bracket that effect for the decks
  flagged in section 6.

**The baseline for RUN5's held-out veto.** The plan (`rl/RUN5.md`, "The plan, revised Sept 25", rules): a later
candidate may not move any held-out deck's panel average more than 2 points further from its Limitless value. The
reference row is the confirmed pilot's, kp3 (k3's row is kept as the reproduction reference; if the table pilot
ever changes, the veto is re-based on the adopted pilot's B2e row on these same deals). For a candidate C on the
same deals, per held-out deck: veto if |C − L| − |kp3 − L| > 2, with L the pooled equal-weight average from
section 3.7 (development beside it, reported only). Rule v2 applies as pre-registered: the veto counts only when
mixed rows on the same deals show the changed pilot's own side got worse beyond the mixed row's paired noise
(about ±4 at 500 games), and it never counts on a cell whose Limitless band is wider than about ±15. Whimsicott's
average rests on 60 matches with three one-sided cells, so a Whimsicott-only veto should be reported as resting on
almost nothing; whether it counts is Dustin's call under that rule.

**The baseline for A2's bar.** The screen may rank brews only once each held-out archetype's panel score lands
inside its Limitless interval (`docs/REVIEW_2026-09-24_direction.md`, B2e and A2). The interval is the pooled
equal-weight interval in section 3.7 (the plan estimated "about ±5 at deck level"; the actual bands are 4.8, 6.1,
4.7, 7.5, 11.2 and 4.8). The pilot the bar reads is the screen's pilot, kp3 on both sides, on the archetype lists
(block A); Dustin's files and k3's rows are context. This README states the bar; it does not lift or apply the
hold, which stays as Dustin set it on Sept 25.

## 6. The card check

**How.** Twelve lists (the six archetype lists and Dustin's six files), 163 card checks in all (81 in the
archetype lists, 82 in Dustin's; cards shared between lists were checked in each). For every card the engine's
text came from `python lib/card.py "<SET> <NUMBER>"` (`lib/deckgym-database.json`) and the Limitless text from
`pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched the same day; compared: HP, type, stage and evolves-from,
weakness, retreat cost, every attack's cost, damage and effect, ability name and text, Trainer subtype and text.
Coverage flags came from the official `goldfish --coverage` (0 games), raw output in the `coverage_*.json`
files. Per-list reports: `card_check_arch_<key>.md` and `card_check_dustin_<key>.md`. Every reported mismatch was
then re-derived by two independent skeptics.

**Confirmed mismatches after two skeptics each: none.** So there is no rules item for the engine from this pass
and no cell needs a card-text note. (Lookup note for anyone repeating it: `card.py` takes a name or an id, not
"Name (ID)"; that combined form returns 0 hits. The Mega Evolution ex rule box, 3 points when Knocked Out, has no
database field but is applied in code, `engine/src/models/card.rs` `is_mega`.)

**Refuted, one line each.**
- Poké Ball P-A 005, effect text, reported from the 11 lists that run it (all but h-whimsicott): engine "Put a
  random Basic Pokémon from your deck into your hand.", Limitless "Put 1 random Basic Pokemon from your deck into
  your hand." Same printing on both sides (the A2b 111 reprint reads identically), article against numeral and a
  dropped accent; the engine routes it to a single-card random Basic search. Wording only.
- Team Rocket's Rattata B4a 058, Ambush damage shown as "20+" on Limitless and as the integer 20 in the engine,
  with the identical sentence "Flip a coin. If heads, this attack does 20 more damage."; the database has no
  notation field and the effect maps to a coin-flip +20, the same convention as 78 other cards. Formatting only.

**Coverage flags per list** (which cards the bot's search cannot price; classes: *unpriced text rule* = the text
reads the opponent's hand or deck, which k3 does not price; *printed-damage estimator* = a damage-changing effect
priced at printed damage; *pays off on the opponent's turn* = k3 never searches that turn). Every card in all
twelve lists reports "Fully implemented" with no engine limitation; nothing is not implemented.

| List | Flagged cards | Untrusted-prone? |
|---|---|---|
| h-manectric | Copycat (unpriced text rule) | no: Copycat only |
| h-raticate | Copycat (unpriced); Alolan Ninetales ex, Binding Snow (pays off on the opponent's turn: the Energy lock lasts through it); Team Rocket's Raticate ex, Thieving Incisors (flagged "unpriced" by the tool's substring rule, but the hand it reads is your own: a false positive) | yes: the deck's lock is on the opponent's turn |
| h-hoopa_absol | Mega Absol ex, Darkness Claw (unpriced: reads the opponent's hand); Copycat (unpriced) | yes: the main attacker's attack; the same blind spot the Hydreigon run found (Darkness Claw at 0 under k3) |
| h-garchomp | Garchomp, Mach Stealth (pays off on the opponent's turn); Happiny, Chubby Cheer (estimator at printed damage); Copycat (unpriced) | yes: the main attacker's ability |
| h-whimsicott | Whimsicott ex, Grass Knot (estimator: +30 per Energy in the opponent's Retreat Cost valued as flat 40); Copycat (unpriced); Team Rocket's Goo-zooka (pays off on the opponent's turn) | yes: the main attack and the deck's tempo card |
| h-charizardy_entei | Copycat (unpriced) | no: Copycat only |
| dustin/09 Manectric | Copycat (unpriced) | no: Copycat only |
| dustin/13 Raticate | Copycat (unpriced); Alolan Ninetales ex, Binding Snow (opponent's turn); Team Rocket's Raticate ex (false positive, as above) | yes |
| dustin/04 Hoopa/Absol | Copycat (unpriced); Absol, Enhanced Blade (estimator: the +30 with a Tool is not priced); Happiny, Chubby Cheer (estimator) | yes: an attacker's attack |
| dustin/08 Garchomp | Copycat (unpriced); Garchomp, Mach Stealth (opponent's turn) | yes: the main attacker's ability |
| dustin/12 Whimsicott | Whimsicott ex, Grass Knot (estimator); Copycat (unpriced); Team Rocket's Goo-zooka (opponent's turn) | yes |
| brew-08 (Charizard Y/Entei base) | Copycat (unpriced) | no: Copycat only |

Copycat is in all twelve lists and in all eight panel lists (1 or 2 copies), so it sits on both sides of every
pairing and is not a reason to distrust one deck over another under k3; its flag is reported, not weighed. The
"untrusted-prone" column marks the eight lists whose main attacker, main ability or tempo card carries a flag:
their numbers are the ones to read with the coverage flag beside them, as the plan requires of every brew number.
Manectric and Charizard Y/Entei (both versions) are the cleanest of the six. The estimator and opponent's-turn
flags apply to k3 and kp3 alike; the opponent's-hand flags (Copycat, Darkness Claw) are what kp3's public pricing
addresses, so the k3 and kp3 rows together show how much they matter for Hoopa/Absol.

**Unverified cards: none.** Every card in all twelve lists was read from both sources.

## 7. Files in this folder

| File | What it is |
|---|---|
| `README.md` | This specification. |
| `decks/h-manectric.txt`, `h-raticate.txt`, `h-hoopa_absol.txt`, `h-garchomp.txt`, `h-whimsicott.txt`, `h-charizardy_entei.txt` | The six archetype lists (20 cards each, UTF-8, LF). |
| `decks/h-raticate.source.json` | Provenance record for h-raticate. |
| `provenance/h-hoopa_absol.json`, `h-whimsicott.json`, `h-charizardy_entei.json` | Provenance records (player, event, placing, deck id, URL, alternatives considered). |
| `b2e_pairings.tsv` | The 96 pairings with deck files, opponent, and each one's seed sub-block (section 4). |
| `cells.py` | Builds the Limitless cells from `matches.csv`. |
| `limitless_cells.csv`, `limitless_cells.md`, `limitless_cells_summary.json` | The cells: development, holdout and pooled, per archetype and opponent, with W-L-T, DL, n, score, band, BO1-only figures; the markdown and JSON views of the same. |
| `independent_recompute/recompute_cells.py`, `recomputed_cells.csv`, `recompute_diff.json` | The independent recompute (byte-identical result) and its diff. |
| `panel_bands.py`, `panel_intervals.csv` | The equal-weight panel averages with 95% bands (section 3.7). |
| `card_check_arch_<key>.md` (6), `card_check_dustin_<key>.md` (6) | The card-text checks, one per list, with per-card tables, mismatches, coverage flags and unverified cards. |
| `coverage_arch_<key>.json` (6), `coverage_dustin_<key>.json` (4), `card_check_dustin_manectric_coverage.json`, `brew08_coverage.json` | Raw `goldfish --coverage` output per list (the last two are the Dustin Manectric and brew-08 coverage files under their authors' names). |

Scratch, not needed to reproduce anything: the six smoke scripts, the recompute's working copy, the Poké Ball raw
fetch and the pairing-table generator, under the session scratchpad `.../scratchpad/b2e/`.
