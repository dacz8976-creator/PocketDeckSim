# koh's reading (Sept 28, laptop): not adopted, provisional (B2e's held-out rows still to come)

**koh = kog + R′**, kph's registration (`../../kph_2026-09-27/REGISTRATION.md`) on the composed base, with amendments 1-3. R′ is kpf's projection with fix A (an evolution step counts as a missing Energy) and fix B (the Zone Energy may go to a benched Pokémon that can reach the Active).
- **Built** by the cloud at bd2907f, whose `engine/` equals the official 233bced.
- **Base:** kog3 at the same engine.
- **Read in the registered order:** footprint, mechanism check, Rayquaza check, the 45 cells, then coverage.
- **Files:** the numbers are in `mechanism_check.txt`, `rayquaza_check.txt` and `READING_numbers.txt` (with `score45_koh3_vs_kog3.txt`). The scripts were committed, and reviewed by a Sonnet agent, before anything was read (423139e).

## In plain words

- koh brings the scoreboard's real error down from 14.0 to 12.3, but that isn't reliably better than noise. The accuracy test's interval crosses zero, so by the rule koh is **not adopted**.
- Two vetoes also count, both on Altaria: koh plays Altaria worse, against Lucario and on its deck average.
- The fixes did what they were built for on Lucario and Vespiquen:
  - kpf's Lucario and Vespiquen vetoes are gone.
  - Mega Rayquaza keeps its gain.
- Altaria is where it fails. The mechanism check shows fix A doesn't hold in Altaria's Swablu/Eevee positions: koh still plays kpf's move there more often than kp3's.
- **Status: "not adopted, provisional"** (RUN5: a "not adopted" stands only once coverage is read).
  - B2e's held-out rows are still running in the cloud.
  - The Scizor row and the four second lists show no veto.
- **kog stays the working pilot.**

## The steps

1. **Footprint** (committed alone, d3664e3): 21,025 of 22,500 paired games on the 45 cells differ from kog3's, 93.44%. So the route is the ordinary adoption rule, which the registration expected.
2. **Build, identity, tests:** the cloud's `../reading/` and `598aae1`.
3. **Mechanism check** (diagnostic; the slices are the ones DIAGNOSIS prints, proven exact under amendment 3). Worse and better rows together; "reached" means koh arrived at the same position with the same moves and board:

   | Slice | Reached | kp3's move | kpf's move | other | Section 6 line |
   |---|---:|---:|---:|---:|---|
   | Swablu/Eevee (A, Altaria) | 15 of 18 | 6 | 8 | 1 | **crossed**: 0.40 is at or under half |
   | Bare Riolu (A, Lucario) | 31 of 35 | 24 | 5 | 2 | holds (0.77) |
   | Combee (A, Vespiquen) | 9 of 11 | 6 | 3 | 0 | holds (0.67) |
   | A pooled | 55 of 64 | 36 | 16 | 3 | holds (0.65) |
   | Forward swaps (B, three decks) | 70 of 84 | 33 | 24 | 13 | holds: kpf's move 0.34, not over half |

   - The Swablu/Eevee line is crossed, so by section 6 fix A isn't doing what the diagnosis says there.
   - By deck, fix B holds: kpf's move in 0 of 4 on Altaria, 22 of 49 on Lucario, 2 of 17 on Vespiquen.
   - **Reported, as designed:** koh keeps the Lucario hides (kpf's move 29 of 35) and the Vespiquen tempo trades (35 of 40).
   - **Lucario's end-of-turn Active in turn T:** in the bare-Riolu rows koh ends with a wall in 28 of 31, as kp3 does.
   - The 37 unreached rows all split earlier. That includes Altaria openings changed by kog's switch A.
4. **Rayquaza check** (diagnostic):
   - Both replays reproduce their trace pages exactly: kpf3 110 wins, Scorching Interruption 254 of 262, Mega Burst 141 of 155; koh3 116, 262 of 268 and 144 of 158.
   - koh3 minus kpf3, paired over the 200 deals: wins +0.030 per game [−0.005, +0.065]; Scorching Interruption use +0.008 [+0.000, +0.021]; Mega Burst use +0.002 [−0.021, +0.025].
   - No interval is below zero, so Rayquaza's gain is kept.
5. **The 45 cells, against kog3** (rules v2, with koh's mixed rows):
   - Real error **14.0 → 12.3**. Reported only: average miss 13.0 → 12.3, favourites right 28 → 29 of 45, correlation 0.51 → 0.43.
   - **ΔMSE −45.1, 95% interval −100.4 to +10.4: not below zero.** The by-event interval is −102.0 to +12.0.
   - **Vetoes that count** (own side worse beyond paired noise):
     - Altaria v Lucario, cell +7.4 further: Altaria's side −4.8 ± 3.8.
     - The Altaria deck, +4.8 further: its own side −1.8 ± 1.4.
   - **Investigation items** (neither side worse):
     - Altaria v Hydreigon.
     - The Hydreigon deck, +3.7 further: its own side is better, +5.7 ± 1.5, which pushes it further past Limitless. This is the open cause "Hydreigon's overshoot".
     - The Vespiquen deck.
   - Five cells never count, because their bands are wider than ±15.
   - **Rule v2's verdict: do not adopt** (the ΔMSE interval isn't below zero), and the Altaria vetoes would also block it.
6. **Coverage** (amendment 2; no harm only):
   - **Scizor:** own side +0.06 ± 1.37 (koh on Scizor against kog3 on both): no veto. The other direction, reported: +1.38 ± 1.31.
   - **Second lists:**

     | List | Opponent average kog3 → koh3 | Figure | Further by | Own side (mixed) | Result |
     |---|---|---:|---:|---|---|
     | v-lucario_2 | 55.8 → 58.5 | 50.4 | +2.7 | +3.26 ± 1.51 (better) | investigation item |
     | v-suicune_2 | 50.9 → 51.0 | 47.1 | +0.1 | +0.94 ± 1.45 | no veto |
     | v-weezing_2 | 54.4 → 47.9 | 43.8 | −6.5 (closer) | −3.77 ± 1.57 (worse) | no veto |
     | l-charizardy | 40.5 → 43.6 | 49.2 | −3.1 (closer) | +2.94 ± 1.26 | no veto |

     Weezing's second list is piloted worse under koh, −3.8 ± 1.6, but it moves closer to its real figure. Amendment 2's veto needs both conditions, so it doesn't fire. It is a finding to keep beside the Altaria harm: the R′ projection still costs some decks their own play.
   - **B2e's held-out archetypes:** still running in the cloud (`b2e_koh3`). They are read when the file lands, and the status line is updated.

## What it means

- **Fix B and fix A work where the diagnosis found the harm for Lucario and Vespiquen.** kpf's vetoes there are gone, and so is Vespiquen's own-side loss.
- **Altaria is the channel left.** koh plays kpf's move in the Swablu/Eevee positions and still plays Altaria worse. That is the next thing to understand, before any R′ variant is registered.
- **Development data:** all 45 cells were already development data for kph (registration section 5). A later candidate built from this reading declares it too.
- **kt stays on kog** as its re-issue says; its "koh contingency" doesn't apply.
