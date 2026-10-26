# Compare: Review C vs Review X (Dustin vs Zavs65, ranked, Master Ball)

Review C = `out_check/REVIEW_FINAL.md` + `OPPONENT_FINAL.json`. Review X = `codex/REVIEW.md` as amended by `FINDINGS.json` (v2 checker correction to turn 9 order), `COVERAGE.md`, `UNCERTAINTIES.json` and `LEAD_ACCEPTANCE.json`.

## Where the reviews agree (checked, no conflict)
Both reviews agree on the following:
- **Setup:** the opponent went first. Dustin's opening hand was Magikarp, Cabbie, Copycat, Poké Ball, Mega Gyarados ex. Dustin's Energy Zone is Water.
- **Knock Outs and score:** the two Furfrou Double Headbutt KOs (Magikarp on T3, Feebas on T5; 1 heads, 30 damage, 1 point each). The game ended with Dustin conceding during T15. Final score 0–2, 15 turns, 120 damage done.
- **Dustin's attacks:**
  - Expert Splasher on T2: 2 tails, 0 damage.
  - Turbo Shark on T6: 70 − 20 = 50, Furfrou 70 → 20, plus a Water onto the benched Carvanha.
  - Turbo Shark on T14: Luxray 130 → 60, plus a Water onto the Bench (4 Water).
- **Dustin's Energy and evolutions:** all of Dustin's Energy attachments, both Elegant Capes, Wallace evolving the benched Aqua Jet Carvanha on T8, the free retreats on T8/T10/T12, and every Soothing Shore and Irida heal value.
- **Sylveon and Oricorio:** Sylveon healed Furfrou 20 → 50 and 50 → 70. Furfrou retreated on T7, discarding its Lightning. Oricorio hit with Zzzap for 70 (with Weakness) on T7, T9 and T11.
- **Luxray:** Shinx got Lightning on T9, T11 and T13. Rare Candy made Luxray, Oricorio retreated keeping 1 Lightning, and Volt Bolt did 140 (220 → 80).
- **Ending:** Volkner on T15, then the concession.

Timestamp gaps under about 2 s, or ranges that overlap (for example Soothing Shore at 99 vs 102–106; frames t_0099/t_0103 show it inspected and then placed), are not counted.

## Disagreements

| Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|
| 5 (opp) | Opponent's Energy attachment | Lightning attached to benched Oricorio about 196–199 | Generated Lightning left unspent | t_0194: zone full, Oricorio has no Energy. t_0200: zone faded, Lightning icon on benched Oricorio. Still 1 on Oricorio at t_0283 | t_0194, t_0200, t_0283 | **C right** |
| 7 (opp) | When the T7 Lightning was attached | About 0280, before the heal and the retreat | 291–293, onto Oricorio after Furfrou retreated | Zone still full at t_0280/t_0283. At t_0291 the Lightning is being dragged onto the now-Active Oricorio. Zone empty and Oricorio at 2 Lightning at t_0293 | t_0280, t_0283, t_0291, t_0293 | **X right** |
| 9 (opp) | Zzzap timing | 0365–0366 | 369–371 | t_0366: Active still 220, no attack. t_0370: "Weakness 70" lands. Damage is the same in both | t_0366, t_0370 | **X right** |
| 15 (opp) | Energy Zone attachment on T15 | JSON lists a T15 Lightning attachment to Luxray ("2 Lightning via Volkner") | Generated Lightning kept; Volkner puts 2 from the discard pile onto Luxray | t_0494/t_0498: zone Lightning still full. Luxray has exactly 2 Lightning, Volkner in the discard. No zone attachment | t_0494, t_0498 | **X right** (C's narrative is fine, but its JSON entry is misleading) |

## Only in C (confirmed by the frames)
- The opponent's Energy Zone is Lightning (zone icon, e.g. t_0194, t_0498).
- The opponent's +20 HP Tool on Oricorio is named Giant Cape. X only says "+20 HP cape". Oricorio shows 90 HP with a Tool at t_0366.
- After Volkner on T15, Luxray has exactly 2 Lightning and Volkner is in the discard pile (t_0498).

## Only in X (confirmed by the frames)
- The Turbo Shark preview against Oricorio shows **0** damage because of Safeguard (t_0383).
- A "Waiting for opponent to return" overlay appears briefly and does not interrupt the game (t_0383; also t_0370).
- The first Carvanha is the Sharp Fang version (t_0194). The second is Aqua Jet (t_0283).
- Eevee's attack is Find a Friend (t_0099).

## Claims contradicted by the frames where the other review is silent
None found beyond the table above. X's turn 5 claim ("unspent") also clashes with X's own turn 7 wording ("Oricorio receives its *second* Lightning").

## Which review to rely on
Both reviews agree on every result that matters: KOs, points, damage, HP, heals and the ending. So either one gives a player a correct account of the game. Where they disagree, X is right three times and C once, but X's error is the more important one. X says the opponent left its turn 5 Energy unspent, which is a wrong board-state fact. C's three errors are timing or bookkeeping: the turn 7 attachment placed about 10 s too early (before the retreat rather than after it), the Zzzap about 4 s early, and a JSON entry that makes Volkner look like a zone attachment. C also tracks the opponent's Energy count on each Pokémon more fully, and it names the opponent's Energy type and Giant Cape. X adds useful context: the Safeguard 0-damage previews and which Carvanha versions were played.

For working out the board turn by turn, C is slightly more reliable. For exact timing and order within a turn, X is more reliable.
