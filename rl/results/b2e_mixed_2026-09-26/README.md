# B2e Raticate and Manectric: which side moves (kp3 v k3 mixed rows, Sept 26; descriptive only)

**Why.** B2e (`../b2e_rows_2026-09-26/READING.md`) found:
- the Raticate archetype list matches Limitless under k3 (41.1 against 41.2) but is 16 points over under kp3 (57.5);
- Mega Manectric ex/Heliolisk is about 15 points over under both pilots.

Fable suggested these rows to see which side carries each, as attribution only.

**What was run.**
- **Rows:** the Manectric (pairings 0-7) and Raticate (8-15) archetype pairings on the same B2e deals, with no new seeds.
  - First direction: kp3 pilots the held deck and k3 the panel opponent.
  - Second direction: the reverse.
  - 8,000 games each way.
- **Binary:** the same as B2e's rows (identity PASS 45ecfda4…).
- **Reading:** `read_mixed.py` reads the rows against B2e's k3|k3 and kp3|kp3 files, paired by deal, with the held deck's score and a 95% interval from the per-deal differences.
- **Run time:** 10 min.

**Result** (`mixed_reading.txt`; pooled per held deck, equal weight over its 8 cells):

| held deck | own side (kp3 on it) | opponents (kp3 on them) | both (B2e table change) | interaction |
|---|---:|---:|---:|---:|
| Raticate archetype | **+19.8 ± 1.6** | −4.0 ± 1.3 | +16.4 ± 1.8 | +0.6 ± 1.6 |
| Manectric archetype | +2.7 ± 1.0 | −3.1 ± 1.3 | −0.6 ± 1.4 | −0.3 ± 1.0 |

**In plain words.**
- **Raticate:** kp3's rise is its own piloting of Raticate, on every cell. The own side is +9 to +27 in each of the 8 cells. kp3 on the opponents takes back about 4, mostly Hydreigon (−16) and Weezing (−6.4).
  - kp3 plays Raticate far better than k3, mainly by using Thieving Incisors, and that puts the simulator 16 points above what real Raticate players score.
  - So either real players get less from Raticate than kp3 does, or something in how the simulator handles Raticate's cards makes it stronger than the real game.
  - Either way, kp3 on the brew side will read Dustin's three Raticate decks (13, 14, 15) as stronger than they are on the ladder. That is the failure mode Dustin named: passing brews too readily. Until this is explained, their screen results should carry that warning.
- **Manectric:** the +15 is not pricing. kp3 adds a little on Manectric's own side and takes a little back through its opponents, and the two cancel. The gap is there under k3 too, so it lies in the engine, the list, or the population, not the pilot.

**Next (for Dustin and Fable; nothing started):**
- A card check of Team Rocket's Raticate ex and the Raticate list against the engine, as was done for Altaria: Thieving Incisors' implementation, what it may take, and how often.
- Ladder evidence from Dustin's own Raticate games (Ladder Log) against the simulator's figures.
- For Manectric, the same card check of Mega Manectric ex / Heliolisk.

**Files.** `run_mixed.sh`, `read_mixed.py`, `mixed_first.*`, `mixed_second.*`, `mixed_reading.txt`, `identity.txt`, `timing.txt`.
