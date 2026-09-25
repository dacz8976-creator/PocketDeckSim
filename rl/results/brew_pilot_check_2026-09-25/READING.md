# Brew pilot check: k3 understates Dustin's Raticate brews by 11 to 16 points (Sept 25)

**What was asked:** how much does the pilot change the numbers for Dustin's own brews?
- Decks 13, 14 and 15 each run Team Rocket's Raticate ex.
- Its Thieving Incisors moves an Energy from the opponent's Active to Raticate when it evolves.
- k3 leaves that ability unpriced: its text mentions "your hand" and "your opponent", so k3's hidden-text rule scores it as if nothing happened. kp prices it.
- All three decks also run Copycat, whose text k3 leaves unpriced too.

The reading was fixed in `brew_pilot.py` before any game (script saved 06:04:04; the smoke run started after that). It is descriptive only. **This is not a table and not a deck ranking.**

## Results

Each brew against the 8 research decks, 200 paired deals per matchup (1,600 per brew). Seeds 21,030,000,000 + brew × 1,000,000 + opponent × 10,000 + i. 0 of 14,400 games unclean.

| brew | k3 pilot, k3 meta | kp3 pilot, k3 meta | what k3 understates | kp3 pilot, kp3 meta | when the meta prices too |
|---|---|---|---|---|---|
| 13 Alolan Ninetales / Raticate | 41.9% | 58.1% | **+16.2 ± 2.4** | 52.3% | −5.8 ± 2.2 |
| 14 Comfey / Raticate / Hypno | 8.4% | 19.2% | **+10.8 ± 1.9** | 17.2% | −1.9 ± 1.9 |
| 15 Jolteon / Oricorio / Raticate | 26.3% | 41.9% | **+15.6 ± 2.3** | 35.6% | −6.3 ± 2.3 |

**Share of the brew's turns with the card on offer where it was used:**

| brew | Thieving Incisors, k3 | Thieving Incisors, kp3 | Copycat, k3 | Copycat, kp3 |
|---|---|---|---|---|
| 13 | 38 of 1,279 (3%) | 1,487 of 1,490 (100%) | 298 of 3,105 (10%) | 871 of 1,551 (56%) |
| 14 | 45 of 1,348 (3%) | 1,517 of 1,517 (100%) | 519 of 2,300 (23%) | 805 of 1,599 (50%) |
| 15 | 61 of 1,213 (5%) | 1,424 of 1,425 (100%) | 347 of 2,761 (13%) | 823 of 1,746 (47%) |

The per-matchup lines are in `brew_pilot.txt`.

## Reading, plainly

- **k3 almost never uses Thieving Incisors (3–5%); kp3 always does.** Taking the opponent's Energy is nearly always good, so 100% is the sensible rate.
- **With a kp3 pilot, every brew wins 11 to 16 points more** against the same k3 opponents on the same deals.
  - Any number the simulator gave for these three decks under k3 was too low by about that much.
  - How the gain splits between Thieving Incisors and Copycat is not separated here; kp3 also plays Copycat about four times as often.
- **When the meta side prices too (kp3 on both sides), 2 to 6 points of that come back.**
  - The research decks run Copycat as well, and Hydreigon's Darkness Claw gets priced.
  - The net change from all-k3 to all-kp3 is still +8.8 to +10.4 points per brew.
- **The meta-side drop is largest against Hydreigon** (−13.5 and −19.0 for decks 13 and 15). That fits kp3's Hydreigon using Darkness Claw properly: it discards a Supporter from the brew's hand.

## All 15 of Dustin's decks (two rows, 100 paired deals per matchup)

`brew_pilot_all15.txt`:
- Rows k3|k3 and kp3|k3, 800 paired deals per brew.
- Seeds 21,050,000,000 + brew × 1,000,000 + opponent × 10,000 + i, a different block from the Raticate run above.
- 0 of 24,000 games unclean.
- The reading was set in the script before its first game: descriptive only, and about which brews' numbers depend on the pilot, not how good any brew is.
- The output's header line says "all three rows"; this run had two.

| brew | k3 pilot | kp3 pilot | what k3 understates |
|---|---|---|---|
| 13 Alolan Ninetales / Raticate | 43.0% | 59.1% | **+16.1 ± 3.4** |
| 15 Jolteon / Oricorio / Raticate | 26.6% | 40.5% | **+13.9 ± 3.1** |
| 14 Comfey / Raticate / Hypno | 8.1% | 19.8% | **+11.6 ± 2.6** |
| 06 Mega Blaziken (tournament list) | 57.6% | 64.1% | **+6.5 ± 3.3** |
| 02 Arceus / Crobat | 31.8% | 36.2% | **+4.5 ± 2.5** |
| 04 Absol / Hoopa / Darkrai | 33.9% | 37.2% | **+3.4 ± 3.1** |
| 01 Muk / Glimmora / Kingambit / Regigigas | 18.1% | 20.5% | +2.4 ± 2.8 |
| 10 Xatu / Oricorio / TR Weezing | 18.0% | 19.4% | +1.4 ± 2.3 |
| 09 Mega Manectric / Heliolisk | 62.3% | 63.1% | +0.9 ± 2.3 |
| 08 Garchomp toolbox | 31.6% | 32.2% | +0.6 ± 2.4 |
| 11 Archaludon / Haxorus / Dragonair | 15.1% | 15.8% | +0.6 ± 2.0 |
| 03 Wailord / Indeedee wall | 63.0% | 63.4% | +0.4 ± 2.5 |
| 05 Indeedee / Stoutland | 28.7% | 28.6% | −0.1 ± 2.4 |
| 12 Ariados / Whimsicott / Ogerpon | 36.8% | 36.1% | −0.6 ± 2.2 |
| 07 Skarmory stall | 51.4% | 51.4% | 0.0 (identical games) |

**Reading, plainly:**
- **The three Raticate decks move most, and the result replicates on new seeds** (+16.1, +11.6 and +13.9 here, against +16.2, +10.8 and +15.6 above).
- **Three more decks move by 3 to 7 points** (06, 02, 04). None of them runs Thieving Incisors. The likely source is Copycat: k3 plays it on 4–12% of the turns it is offered in those decks, kp3 on 45–57%.
- **Eight decks don't move beyond noise.** Their simulator numbers don't depend on the pilot.
- **Skarmory stall (07) plays the same games move for move.** Its list has no card whose text kp prices, and kp is built to play exactly like k3 then. That is a live confirmation of that property on a deck it was never tested on.
- **Copycat is played far more often under kp3 in every deck that runs it,** but in most decks that changes the win rate by little.

## The A2 screen re-run with kp3 on both sides (for Dustin's decision on the screen hold)

`screen_rerun_kp3.txt`:
- **Decks:** 24 in all.
  - The screen's calibration decks: Payback brew-06 and brew-06b, brew-05b, and Skarmory (07).
  - brew-01 and brew-03a.
  - New brews 07–10.
  - All 15 of Dustin's decks.
- **Opponents:** the 8-deck panel, identical card for card to `decks/screen/opponents`.
- **Pilots:** 60 paired deals per matchup, rows k3|k3 and kp3|kp3.
- **Seeds:** 21,070,000,000 and up.
- **Cleanliness:** 0 of 23,040 games unclean.
- **Build:** the scratch diagnostic add-on.
- **Timing:** the reading was fixed in the script's docstring at 09:19:47, before the first game at about 09:22.

**Checked by three independent agents before this was written:**
- A recompute from the per-matchup lines found no discrepancies.
- A ladder cross-check used the 33 ladder games, Sept 15–24, with each deck mapped card for card.
- A skeptic judged the wording, adopted below.

**The rule fixed before the run is met.** With kp3 on both sides, the screen's four reference decks stay on the side of their lines that the ladder puts them. The ± values are 95% binomial half-widths at 480 games.

| reference deck | ladder | k3 both sides | kp3 both sides | line | how clear |
|---|---|---|---|---|---|
| brew-06 Payback (Psychic) | 0-3 | 8.1 | 4.4 ± 1.8 | under 20 | clear |
| brew-06b Payback (Grass) | 0-3 | 18.8 | 17.3 ± 3.4 | under 20 | **within noise** |
| brew-05b Meowstic/Hatterene/Comfey | 3-3 | 31.7 | 29.4 ± 4.1 | 20 or more | clear |
| 07 Skarmory stall | 3-1 | 52.7 | 47.7 ± 4.5 | 45 or more | **within noise** |

**Against Dustin's ladder, kp3 does at least as well as k3.**
- Seven decks have ladder records and map card for card to the files.
- kp3 on both sides puts 6 of the 7 on the ladder's side of the 20% bar; k3 puts 5.
- The only deck that crosses the bar is brew-01 (1-3 on the ladder): 22.5 under k3, 17.7 under kp3.
- On the three decks that aren't reference decks (brew-01, brew-03a, deck 02), kp3 gets 2 right and k3 gets 1.
- Both miss deck 02 Arceus/Crobat: 1-3 on the ladder, about 30% on the panel.
- Rank agreement with the ladder is about the same for both pilots. The ladder is 16 games, so it can't separate them.

**What moved:**
- 20 of the 24 decks run neither Team Rocket's Raticate ex nor the Mega Blaziken list. 18 of those drop, by about 3 points on average, fairly uniformly. That is the meta side pricing its own Copycat and similar cards.
- The three Raticate decks rise by 8 to 13, and Mega Blaziken by 7.
- The order of decks barely changes (rank correlation 0.94). What changes is which decks sit near the 20% bar.

**What this does and does not support** (the skeptic's wording, adopted):
- **"The reference-deck condition for the screen is met on the diagnostic build, with two of the four within noise. Nothing more."**
- It is a necessary condition, not proof that the screen works. The plan's full A2 readout is not in this run:
  - a panel weighted to Dustin's ladder (about half of his ladder opponents are off-panel, and he has never met Sceptile, which counts as 1/8 of every average here);
  - worst matchups and failure modes instead of an average;
  - one-sided rows;
  - B2e's check that held-out archetypes land inside their Limitless intervals.
- The lines were drawn around the k3 numbers on Sept 24. They were fixed before any kp3-on-both-sides game, but the test had little room to fail.
- **The screen tool itself (`decks/screen/run_screen.py`) cannot run kp3 yet.** It will once the merged-main engine passes its identity replay and becomes the official build.
- **Lifting the hold is Dustin's call.** If he lifts it, the screen should report the full A2 readout, not the 8-deck average alone.

## What this does not show

- **How these brews do on the ladder.** The eight research decks are the table's meta, not the ladder's, and the simulator still overrates or underrates some of them.
- **Anything about the table pilot.** That decision is separate and is Dustin's.

## Build

- These games need kp3, so they ran on the scratch diagnostic add-on: engine at c7cb688, sha256 `c048388b4bcf7103375ea0a1e7c9e965be8e350000c3ac873bd111b69e1eae19`. Its conditions are in `../hydreigon_network_readout/READING.md`.
- All three rows ran on that one build.
- The engine's command-line scan at c7cb688 would give win rates only: its per-game output keeps a hash of the moves, so it can't count these cards.
