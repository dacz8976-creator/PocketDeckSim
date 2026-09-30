# The floor check under km3 on Dustin's decks and the brews (Sept 30)

**Who wrote this and why.** The laptop session ("Project familiarization", Claude Code, Desktop). The job came through the Fable coordinator session ("Work delegation and task routing"), under the operational authority Dustin gave it on Sept 30; his own gates are unchanged. This README was written and committed before any game of this run was played.

**What this is.** The floor check (`decks/screen/floor.py`) under the new working pilot, run once on:
- each of Dustin's 15 decks (`decks/dustin/01` to `15`);
- the six brews that have a kog3 floor page (`../floor_brews_2026-09-28/`: 02, 03b, 07, 08, 09, 10).

It is the bot's approved job (RUN5, "A2: the hold lifts for the floor check only"). **It is not a ranking.** Nothing here says which deck is best, and a deck that clears the floor is not thereby good. It says which decks the bot can already tell are weak, and how.

**Why now.** The Sept 30 engine switch moved the screen and the floor from kog3 to km3 (`../engine_switch_2026-09-30/`). The floor's pre-use re-check passed under km3 (`../floor_recheck_2026-09-30/`: both Payback lists "fail", the deck 14 k3 control "untrusted"). Each deck's floor page so far is under kp3 or kog3; this gives each one its page under the pilot now in use.

**Reused, not re-run.** These pages already exist from today's re-check, with the same defaults and seeds:
- Dustin's deck 07 (`../floor_recheck_2026-09-30/07-skarmory-stall.md`);
- brew 05b (`../floor_recheck_2026-09-30/brew-05b-meowstic-hatterene-comfey.md`).

Deck 14's k3 control was also run today and is not repeated. Deck 14 is run here like any other deck, under km3 on both sides.

**Nothing new is decided here.** Every rule is the one already fixed:
- floor.py's own defaults:
  - pilot km3 on both sides;
  - the official engine `rl/engine-2026-09-30/` (the manifest's available release, hash checked);
  - 240 games per matchup against each of the eight panel decks in `decks/screen/opponents/` (1,920 per deck);
  - seeds 7,100 + 1,000 × opponent (+500 for seat 1).
- Verdicts by the A2 bar, read from floor.py's page as printed:
  - under 20% of the panel on both sides fails;
  - within the floor's own noise of 20% reads "borderline";
  - "untrusted" keys on the coverage flag only.
- Card roles are floor.py's defaults, from each card's flag. No role is set for any deck here. If a page's printed role looks wrong to Dustin, that is his to say on the page, as A2 already provides.

**Reading note, fixed before any game.** Each page prints every flagged card's role and where it came from. Where a flagged card carries a default role, a "fail", "borderline" or "untrusted" there may be a wrong-role problem rather than a deck problem, and the readout will mark that verdict **provisional**. For the six brews, the readout sets each km3 page beside its kog3 page (Sept 28) with the wins and the verdict, and says only "changed" or "unchanged". No other interpretation is made.

**What is not claimed.** No prediction about these verdicts is registered, so nothing here confirms or refutes one. Dustin's ladder games stay the only score of a deck.

**Run:** `run_floor.sh`, at the lowest CPU priority, with nothing else on the laptop beside it. Pages, per-game files and coverage land in this folder, and timing goes in `timing.txt`. The readout goes below once the pages exist.

## Readout (Sept 30; the run finished 21:28 UTC, 20 of 20 pages, `timing.txt`)

Floor bar, as printed on every page: 349 wins of 1,920 or fewer fail, 350-418 borderline, 419 or more clear. All 20 pages in this folder say "km3 on the deck, km3 on the panel" and engine `rl/engine-2026-09-30/deckgym`. Every number below is copied from the pages named in each section. **Nothing here ranks the decks, and clearing the floor is not a recommendation.**

How to read the columns:
- **Weakest matchups:** the first three lines of the page's "Worst matchups" list. The page lists all eight, lowest first, and each line is ±6 points at 240 games.
- **Coverage flag:** every flagged card on the page, with its role and its use share (used of opportunities). "Under 25%" appears only where the page prints it.
- **Provisional?:** per this README's reading note, a "fail", "borderline" or "untrusted" verdict is marked provisional where a flagged card carries a default role. Every flagged card in this run has the role source "default from the flag", because no role was set for any deck. Where the verdict is "clears", the column says "no" and still names the default-role cards.

### Dustin's 15 decks

Deck 07's page is the one from today's re-check (`../floor_recheck_2026-09-30/07-skarmory-stall.md`). It was reused, not re-run, with the same defaults and seeds. Deck 14's row is its km3 page from this run. The re-check's k3 control for deck 14 is a control reading, not this deck's floor verdict.

| deck | floor verdict as printed | wins of 1,920 (%) | weakest matchups (each ±6) | coverage flag: flagged cards (role: use share) | provisional? (card, role source) |
|---|---|---|---|---|---|
| 01 Muk / Glimmora / Kingambit / Regigigas | **fail** | 307 (15.99%) | Suicune 10% (23/240), Blaziken 10% (25/240), Sceptile 10% (25/240) | Kingambit (attacker: 775 of 776, 99.9%) | **yes**: Kingambit, attacker, default from the flag |
| 02 Arceus / Crobat | clears | 579 (30.16%) | Suicune 19% (45/240), Lucario 19% (46/240), Weezing 27% (64/240) | Lucky Egg (Trainer (played): 1,192 of 2,137, 55.8%) | no (clears; Lucky Egg's role is default from the flag) |
| 03 Wailord / Indeedee wall | clears | 1,178 (61.35%) | Lucario 53% (127/240), Vespiquen 56% (134/240), Suicune 61% (146/240) | none | no (no flagged cards) |
| 04 Absol / Hoopa / Darkrai | clears | 627 (32.66%) | Sceptile 18% (42/240), Suicune 20% (47/240), Vespiquen 25% (59/240) | Absol (attacker: 659 of 855, 77.1%); Happiny (attacker: 316 of 824, 38.3%) | no (clears; both roles default from the flag) |
| 05 Indeedee / Stoutland | clears | 578 (30.10%) | Sceptile 18% (44/240), Blaziken 20% (47/240), Weezing 22% (52/240) | Cheren (Trainer (played), a Supporter: 433 of 2,152, 20.1%, **under 25%**) | no (clears; Cheren's role is default from the flag) |
| 06 Mega Blaziken tournament list | clears | 1,110 (57.81%) | Altaria 40% (95/240), Weezing 48% (116/240), Lucario 51% (122/240) | Rocky Helmet (Trainer (played): 1,270 of 1,859, 68.3%) | no (clears; Rocky Helmet's role is default from the flag) |
| 07 Skarmory stall (re-check page) | clears | 1,098 (57.19%) | Blaziken 26% (63/240), Lucario 32% (78/240), Sceptile 40% (97/240) | Jasmine (Trainer (played), a Supporter: 1,786 of 3,299, 54.1%); Metal Core Barrier (Trainer (played): 2,419 of 3,667, 66.0%); Skarmory ex (attacker: 8,397 of 8,398, 100.0%) | no (clears; all three roles default from the flag) |
| 08 Garchomp toolbox | clears | 500 (26.04%) | Weezing 12% (30/240), Blaziken 18% (42/240), Hydreigon 18% (44/240) | Garchomp (bench piece/passive ability: 1,417 of 1,541, 92.0%) | no (clears; Garchomp's role is default from the flag) |
| 09 Mega Manectric / Heliolisk | clears | 1,124 (58.54%) | Lucario 46% (110/240), Sceptile 48% (114/240), Weezing 48% (116/240) | none | no (no flagged cards) |
| 10 Xatu / Oricorio / TR Weezing | **fail** | 324 (16.88%) | Weezing 3% (8/240), Suicune 5% (13/240), Vespiquen 12% (29/240) | Poison Barb (Trainer (played): 2,513 of 3,686, 68.2%); Xatu (attacker: 981 of 1,050, 93.4%) | **yes**: Poison Barb, Trainer (played), and Xatu, attacker, both default from the flag |
| 11 Archaludon / Haxorus / Dragonair | **untrusted** | 295 (15.36%) | Sceptile 12% (28/240), Blaziken 12% (30/240), Suicune 12% (30/240) | Archaludon (attacker: 424 of 429, 98.8%); Iris (Trainer (played), a Supporter: 233 of 3,068, 7.6%, **under 25%**) | **yes**: Archaludon, attacker, and Iris, Trainer (played), both default from the flag |
| 12 Ariados / Whimsicott / Ogerpon | clears | 602 (31.35%) | Blaziken 15% (37/240), Lucario 23% (56/240), Sceptile 26% (63/240) | Team Rocket's Goo-zooka (Trainer (played): 1,858 of 5,380, 34.5%); Whimsicott ex (attacker: 2,151 of 2,187, 98.4%) | no (clears; both roles default from the flag) |
| 13 Alolan Ninetales / Raticate | clears | 1,068 (55.62%) | Altaria 39% (94/240), Hydreigon 46% (110/240), Weezing 51% (122/240) | Alolan Ninetales ex (attacker: 4,251 of 4,369, 97.3%) | no (clears; Alolan Ninetales ex's role is default from the flag) |
| 14 Comfey / Raticate / Hypno | **untrusted** | 321 (16.72%) | Suicune 7% (16/240), Sceptile 8% (19/240), Weezing 11% (27/240) | Team Rocket's Goo-zooka (Trainer (played): 185 of 4,473, 4.1%, **under 25%**); Team Rocket's Hypno (attacker: 1,234 of 1,361, 90.7%); Team Rocket's Researcher (Trainer (played), a Supporter: 1,040 of 1,294, 80.4%) | **yes**: Goo-zooka, Trainer (played); TR Hypno, attacker; TR Researcher, Trainer (played); all three default from the flag |
| 15 Jolteon / Oricorio / Raticate | clears | 698 (36.35%) | Lucario 28% (66/240), Sceptile 30% (71/240), Altaria 37% (89/240) | Team Rocket's Goo-zooka (Trainer (played): 175 of 4,590, 3.8%, **under 25%**) | no (clears; Goo-zooka's role is default from the flag) |

### The six brews: kog3 (Sept 28) beside km3 (today)

The kog3 pages are in `../floor_brews_2026-09-28/` (engine `rl/engine-2026-09-28/`, kog3 on both sides). The km3 pages are in this folder. "Changed" or "unchanged" refers to the verdict only. The wins change is km3 minus kog3.

| brew | kog3, Sept 28 (verdict, wins of 1,920) | km3, Sept 30 (verdict, wins of 1,920) | wins change | verdict | km3 weakest matchups (each ±6) | km3 coverage flag (role: use share) | provisional? (km3 page) |
|---|---|---|---|---|---|---|---|
| 02 Arceus / Tandemaus / Persian | **fail**, 273 (14.22%) | **fail**, 268 (13.96%) | -5 | unchanged | Weezing 5% (12/240), Suicune 6% (15/240), Lucario 11% (27/240) | Maushold (attacker: 2,194 of 2,313, 94.9%) | **yes**: Maushold, attacker, default from the flag |
| 03b Arceus / Crobat / Nihilego / Toxapex | **borderline**, 397 (20.68%) | **borderline**, 397 (20.68%) | 0 | unchanged | Lucario 13% (31/240), Suicune 15% (35/240), Weezing 15% (36/240) | Mareanie (attacker: 111 of 123, 90.2%); Team Rocket's Goo-zooka (Trainer (played): 92 of 4,449, 2.1%, **under 25%**); Toxapex (attacker: 426 of 491, 86.8%) | **yes**: Mareanie, attacker; Goo-zooka, Trainer (played); Toxapex, attacker; all three default from the flag |
| 07 Hoopa / Darkrai / Sableye | clears, 1,177 (61.30%) | clears, 1,168 (60.83%) | -9 | unchanged | Sceptile 37% (88/240), Vespiquen 50% (119/240), Lucario 58% (140/240) | Mega Sableye ex (attacker: 1,088 of 1,195, 91.0%) | no (clears; Mega Sableye ex's role is default from the flag) |
| 08 Entei / Rainbow Cave | clears, 1,040 (54.17%) | clears, 1,067 (55.57%) | +27 | unchanged | Blaziken 36% (86/240), Suicune 43% (104/240), Altaria 46% (110/240) | none | no (no flagged cards) |
| 09 Sableye / Obstagoon | clears, 835 (43.49%) | clears, 835 (43.49%) | 0 | unchanged | Sceptile 32% (76/240), Weezing 32% (76/240), Suicune 34% (82/240) | Galarian Obstagoon (attacker: 1,033 of 1,048, 98.6%); Mega Sableye ex (attacker: 4,326 of 4,499, 96.2%) | no (clears; both roles default from the flag) |
| 10 Diancie / Giratina | clears, 779 (40.57%) | clears, 779 (40.57%) | 0 | unchanged | Weezing 20% (49/240), Suicune 27% (65/240), Blaziken 35% (85/240) | none | no (no flagged cards) |

For a second reader: 03b, 09 and 10 have the same total under both pilots. Their per-seat engine lines in "For a second reader" differ between the kog3 and km3 pages (for example, 10 against Altaria in seat 1: 59 deck wins under kog3, 58 under km3). So these are different games that happen to give the same total. The km3 pages are not copies of the kog3 pages.

**Brew 05b, for reference.** Its page is from today's re-check (`../floor_recheck_2026-09-30/brew-05b-meowstic-hatterene-comfey.md`), reused, not re-run. Under km3 it **clears**, 577 of 1,920 (30.05%). Weakest matchups: Hydreigon 13% (32/240), Weezing 18% (43/240), Suicune 22% (52/240); Vespiquen and Sceptile are also at 22%; each line is ±6. One card is flagged: Hatterene (attacker: 2,416 of 2,496, 96.8%). Provisional: no; the verdict clears, and Hatterene's role is default from the flag. Under kog3 on Sept 28 (`../floor_recheck_2026-09-28/brew-05b-meowstic-hatterene-comfey.md`) it cleared with 584 (30.42%). Wins change: -7. Verdict: unchanged. The re-check's `verdicts.txt` also lists 597 under kp3 (Sept 25).

**Not done here:** no ranking, and no deck named best or recommended for play. No role was set for any deck; A2 leaves that to Dustin, on the page. No calibration, no comparison with the ladder record, and no explanation of why any number moved between kog3 and km3.
