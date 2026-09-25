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

## What this does not show

- **How these brews do on the ladder.** The eight research decks are the table's meta, not the ladder's, and the simulator still overrates or underrates some of them.
- **Anything about the table pilot.** That decision is separate and is Dustin's.

## Build

- These games need kp3, so they ran on the scratch diagnostic add-on: engine at c7cb688, sha256 `c048388b4bcf7103375ea0a1e7c9e965be8e350000c3ac873bd111b69e1eae19`. Its conditions are in `../hydreigon_network_readout/READING.md`.
- All three rows ran on that one build.
- The engine's command-line scan at c7cb688 would give win rates only: its per-game output keeps a hash of the moves, so it can't count these cards.
