# Where the Altaria network beats kp3 (B2c), Sept 26: the result

**In plain words:** most of what the Altaria network does better than the current bot happens before the first turn: which Pokémon it puts in the Active Spot at the start of the game.
- **kp3 usually opens with Darkrai Active:** 103 of the 235 games where it had a choice. The network almost never does (6 of 235).
- **The network opens with Eevee or Swablu instead.** Eevee's Boosted Evolution lets it evolve on the first turn, but only from the Active Spot. Darkrai's Bad Dreams works from the Bench.
- **Where the two openings differ, the network's opening is worth +19.4 points (±4.6) to Altaria**, played out with kp3 piloting both decks afterwards. Spread over all 400 games, that is about +7.7 points per game, roughly half of the network's whole +15.8 edge over kp3 (D, `../altaria_network_readout/kp3_rows.txt`). Gains don't add exactly, so treat that share as a rough size.
- **The benching habit, the most visible difference in the counts** (66% vs 88% of offered turns), **is worth little.** Neither direction clears zero: network benches and kp3 doesn't, +2.1 (−0.6, +4.8); kp3 benches and the network doesn't, +0.3 (−1.1, +1.7). My guess in the readout note (a smaller Bench keeps weak Basics away from Lucario's snipes) is not supported.

**What was run** (design and groupings fixed in `README.md` before the run, committed b6b0eb9):
- **Games:** the first 400 of the recorded net|kp3 games (network Altaria v kp3 Lucario, the run's bar deals). All 400 replayed in sync, 0 rejected.
- **Probes:** at each of the network's 7,339 decisions, kp3 was asked for its move from the same position (3 probes; it agreed with itself at 90%).
- **Play-outs:** the moves differed beyond move order at 3,025 positions. Each was played out 8 + 8 times, kp3 piloting both decks afterwards, each pair sharing a chance seed.
- **What it measures:** what kp3 would gain by making the network's move there, not how good the network's whole plan is.
- **Run time:** 1,781 s wall on 14 threads.
- **Seeds:** play-outs 21,110,000,000 + i × 100,000 + j × 100 + r; probes 21,160,000,000 + i × 100,000 + j × 10 + p.
- **Overall:** the network's move is worth **+1.7 points (±0.9 by position, ±0.8 by game)** per differing position.

**The rows that clear zero** (`analysis.txt`; 58 rows tested, so one or two small ones could clear by chance):

| row | positions | network − kp3, points (95%) | total per game |
|---|---:|---:|---:|
| 3e: Darkrai Active after kp3's move, not the network's | 150 | **+20.2 (+15.8, +24.6)** | +7.56 |
| 3c: the two moves leave different Pokémon Active (includes 3e) | 767 | +6.6 (+4.4, +8.7) | +12.56 |
| place / place (move-kind pair; mostly the opening) | 279 | +9.9 (+6.6, +13.3) | +6.94 |
| 4c: both put Energy on the Bench, different Pokémon (mostly network Swablu, kp3 Darkrai) | 68 | +5.5 (+0.4, +10.6) | +0.94 |
| end turn / play supporter | 39 | −9.3 (−16.9, −1.7) | −0.91 |
| end turn / play item | 33 | −10.6 (−19.4, −1.8) | −0.88 |
| attack / energy to bench | 33 | −7.2 (−12.1, −2.3) | −0.59 |

The negative rows are small spots where kp3's move was better: passing the turn instead of playing a Supporter or an Item, and attacking instead of charging the Bench.

**Inside 3e: the opening Active choice** (`opening_choice.py` / `.txt`, a look inside the pre-set rows 3e and place/place, not a new test):

| network opens | kp3 opens | games | network − kp3, points (95%) |
|---|---|---:|---:|
| Eevee | Darkrai | 56 | +27.0 ± 7.8 |
| Eevee | Swablu | 49 | +16.1 ± 8.5 |
| Swablu | Darkrai | 41 | +18.6 ± 8.0 |
| Eevee | Igglybuff | 12 | +0.0 ± 12.8 |
| any, where they differ | | 158 | **+19.4 ± 4.6** |
| kp3 opens Darkrai, the network doesn't | | 97 | +23.5 ± 5.7 |

**Card-agnostic reading (to be checked, not yet tested as a bot change):** kp3 chooses its opening Active by how the position scores right away, and its search can't see past its own first turn.
- So it can't see that an ability which only works from the Active Spot on the first turn (Eevee's Boosted Evolution) needs that Pokémon placed there now.
- Nor can it see that a Pokémon whose value is a passive ability that works from the Bench (Darkrai's Bad Dreams) is better kept safe there than put in front, where it gets hit and its own attack is the weaker choice.
- This is a **B5 feature candidate, "the opening Active choice"**, to be registered and read on its own, as PRESET_READING says. Nothing about the pilot changes because of this study.
- **Limits:**
  - Only Altaria v Lucario was examined, and only kp3 continued the play-outs.
  - 235 of 400 games had an opening choice.
  - Whether other decks with Active-only first-turn abilities, or Bench-working passive abilities, show the same gap is the candidate's own question.

**Files:**
- `decisions.jsonl`: every network decision with both moves, the context, the kp3 probes, and the 8 + 8 play-outs where they differ.
- `analysis.txt`: the pre-set tables.
- `opening_choice.py` / `.txt`: the look inside.
- `net_divergence.txt`, `sync_check.txt`, `timing.txt`: the run's summary lines.
