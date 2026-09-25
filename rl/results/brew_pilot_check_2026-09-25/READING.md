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

## What this does not show

- **How these brews do on the ladder.** The eight research decks are the table's meta, not the ladder's, and the simulator still overrates or underrates some of them.
- **Anything about the table pilot.** That decision is separate and is Dustin's.

## Build

- These games need kp3, so they ran on the scratch diagnostic add-on: engine at c7cb688, sha256 `c048388b4bcf7103375ea0a1e7c9e965be8e350000c3ac873bd111b69e1eae19`. Its conditions are in `../hydreigon_network_readout/READING.md`.
- All three rows ran on that one build.
- The engine's command-line scan at c7cb688 would give win rates only: its per-game output keeps a hash of the moves, so it can't count these cards.
