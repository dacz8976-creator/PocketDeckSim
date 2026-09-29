**Diagnosis: why koh plays Altaria worse (synthesizer, Sept 28 night)**

Terms: R is kpf's projection, where next turn's Zone Energy is credited to the Active. A makes an evolution step count as a missing Energy. B lets the Zone Energy be credited to a benched Pokémon that can reach the Active. koh = kog + R + A + B.

**Short answer**
1. The "crossed" Swablu/Eevee line is mostly a reading problem. A works on Swablu and cannot act on Eevee, and the Eevee lines don't cost points.
2. koh's Altaria deficit is small and spread over three pieces. Over the 7 traced cells it is −1.33 ± 1.61, and the READING's deck figure is −1.8 ± 1.4. No single piece is significant on its own.
3. Only one piece has a mechanism I could pin down and repair with no collateral change on the registered slices. That is B's retreat-payment test (fix 1 below).
4. Altaria's evidence alone does not justify changing the player.

**What I checked (verified by rerunning or reading)**
- **Mechanism check:** 6 kp3-move / 8 kpf-move / 1 other, 15 of 18 rows reached. Read by whole turn it is 7 / 7 / 1 (I reran `classify_rows.py`).
- **Fix A on Swablu:** kpf makes the Igglybuff→bare-Swablu retreat in 8 of 18 rows, koh in 0 of 18.
- **Fix A on Eevee:**
  - Espeon costs one P, so an Eevee holding a P already reads ready in kp3.
  - A takes the larger of that and its own reading, so A cannot lower it (code plus leaf dump).
  - The 4 first-turn Igglybuff→Eevee Stampede rows come from an exact tie in the search: Copycat 498.2 vs Retreat 498.2. The tie goes to Retreat by list order, and the leaf assumes Espeon is in the draw.
- **The Eevee lines don't cost points:**
  - The category "koh retreats, kog doesn't" is 305 deals, 44 worse / 41 better.
  - The 0-of-4 failed evolutions in the rows are selection, because those rows were picked from worse/better games.
- **Cell figures:** +1.0, −1.4, −4.8, +0.6, −2.8, −0.8, −1.1, pooled −1.33 ± 1.61 (436 worse / 390 better deals).
  - The Lucario cell is consistent with the pooled figure.
  - Openings are identical in all 14,000 paired games.
  - At about 49 points of paired noise per deal, ±0.5 needs about 36,000 Altaria deals.
- **Not re-derived:** the idle-turn and fewer-attacks deltas (two lenses agree), the missed Eevee→Espeon timing (needs hand contents), and the "Zone to Active 82/54" tally.

**New: which piece of R′ causes each first difference**
I priced every first-divergence decision with the code lens's search harness under kog, kpf (R only), kpha (R+A), kphb (R+B) and koh. It reproduced both actual picks in 2,223 of 2,898 rows (77%). The other 675 rows (95 worse / 93 better) are mostly promotions after KO and trainer-order ticks.

| Caused by | Decisions | Worse / better | Points of the deficit |
|---|---|---|---|
| R alone | 1,798 (81%) | 270 / 248 | −0.64 |
| B needed | 297 (13%) | 48 / 34 | −0.40 |
| A needed | 94 (4%) | 17 / 9 | −0.23 |

- **R alone:** all of its −0.64 is the Lucario cell, 38 worse / 17 better. The other six cells are 232 / 231.
  - The mechanism is attack-skipping (the tempo trade R′ keeps by design). Among skip turns caused by R alone, Lucario is 12 / 1 (55 rows) and the other six cells are 50 / 50 (319 rows).
  - I found no list-free repair for this piece.
- **B:** the best-supported family is Darkrai Active with a bare Mega Altaria ex on the Bench. The clean version is 79 games, 19 worse / 5 better.
  - It is one of 353 post-hoc groups, so the raw p = 0.007 means little.
  - The mechanism is real, though. In 54 of 69 reproduced rows only B flips the pick to koh's; R alone flips 15.
  - Leaf dump for 72000291: with R alone, feeding the Mega scores −8900 and feeding Darkrai −8924. With B, feeding Darkrai scores −8824.
  - B credits the bench Mega with the Zone Energy in the leaf where the Active was just fed, because that fresh Energy makes the retreat payable. The readiness term counts the same Energy toward the Active attacking.
  - This corrects the positions lens, which had B's payment test working in the opposite direction.
  - B decisions outside that family are neutral (35 / 30).
  - A second B route: Small Balloon lowers the retreat cost and unlocks the credit (46 of the 297 B rows, 12 worse / 7 better).
- **A:** in 21 skip turns (7 / 0), koh leaves a bare Swablu or Eevee that could have used Sing, Stampede or Lullaby. This piece is small.

**Still unknown**
- Whether any of the deficit is real beyond noise. The pooled figure includes zero, and the deck-level figure comes from a veto rule.
- Whether B's Zone family truly costs games. The mechanism is verified but the outcomes are post hoc.
- Why R's attack-skipping is harmless in six cells and costly against Lucario.
- Whether the Eevee gamble is right given the hand, since dumps hide hands.
- What new divergences a fix would create outside the current rows.

**Candidate fixes (list-free, no constants)**
1. **B's payment test counts only Energy the Active held before this turn's Zone attach.**
   - Scratch build: a per-turn marker in the engine copy under `wf_altaria/code/eng`, patched by `synth/patch6.py`. Nothing was written in the repo.
   - On the registered slices it is identical to koh: A slices 36 / 16 / 3, forward swaps 36 / 21 / 13, tempo trades 2 / 35 / 3, hides 0 / 31 / 4.
   - It sends all 54 Zone-family rows and 107 of 322 B-needed rows back to kog's move. That is worth at most about +0.2 to +0.3 points, if those games then play like kog's.
   - The blunter options fail. "Free retreat only" and "spare Energy only" undo B: the kpf-move share on the 70 forward swaps goes from 21 to 42. "Drop the payment test" keeps B's forward-swap fix but gives up the Vespiquen tempo trades in 10 more rows.
   - The scratch marker is approximate: it goes stale after a KO promotion, and it is lost for Energy attached earlier in the same turn at the root.
   - Test: the 54 rows must revert and the mechanism-check B slices must not move. Then run the 45 cells to look for harm elsewhere. The Altaria gain is too small to see at 500 deals per cell.
2. **Tie-break that reveals hidden cards before an irreversible commit** (draw before Retreat when values tie exactly).
   - It changes the 4 first-turn Eevee rows.
   - Under a first-of-ties rule, koh's Retreat picks in the Altaria slice go from 6 of 15 to 0.
   - It also moves other decks and the bases, and I expect a tiny gain. Low priority.
3. **Reading fix only.** Score the mechanism check by whole-turn end board. Split Swablu rows (A can bite) from Eevee rows (A has no lever). No player change.

Not endorsed: the code lens's smoothed threat pick raised agreement with kp from 73 to 139 of 200 rows, which I reproduced, but it also moves the base, so agreement isn't evidence of improvement. The rows lens's "readiness uses bench reach" fix would not change the Zone family, because the readiness term already prefers the Darkrai leaf under kog and it is the clock that flips.

**Housekeeping**
- The code lens reported a broad `pkill` of rustc/cargo that may have hit another session's compile. I can't confirm either way.
- My `pkill -f attr_run.py` matched only my own jobs.
- I edited the code lens's scratch engine copy, which is outside the repo.

Files are in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_altaria\synth\`:
- `attr_full.txt`
- `attr_parse.py`
- `attr_family.py`
- `attr_skip.py`
- `attr2_parse.py`
- `attr3_parse.py`
- `zone_check.py`
- `patch5.py`
- `patch6.py`
