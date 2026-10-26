# Comparison: Review C vs Review X (Dustin vs Zavs65, ranked, 15 turns, conceded at 0-2)

Review X's final word is REVIEW.md v2, which already contains the checker's turn 9 timing correction (FINDINGS.json, COVERAGE.md, LEAD_ACCEPTANCE.json). Review C's final word is out_check/REVIEW_FINAL.md plus OPPONENT_FINAL.json.

## Where both reviews agree (checked, not counted)
- The opponent went first.
- Opening hand: Magikarp, Cabbie, Copycat, Poké Ball, Mega Gyarados ex.
- Dustin's Energy Zone is Water.
- Setup: Magikarp vs Furfrou.
- Turn 1: Poké Ball, Eevee and Oricorio benched, Professor's Research.
- Turn 3: Double Headbutt (1 heads) knocked out Magikarp, 0-1.
- Turn 4: Copycat, Carvanha with Elegant Cape and a Water.
- Turn 5: Double Headbutt knocked out Feebas, 0-2.
- Turn 6: Mega Sharpedo ex at 220. Turbo Shark did 50 (Furfrou 70 → 20) and sent a Water to the Benched Carvanha.
- Turn 7: Sylveon. Furfrou healed 20 → 50. +20 HP Tool on Oricorio (90). Copycat, Shinx. Zzzap 70 (220 → 150).
- Turn 8: Wallace evolved the second Mega Sharpedo. Retreat, no attack. Soothing Shore 150 → 170.
- Turn 9: Soothing Ribbon 50 → 70. Shinx got a Lightning. Zzzap 220 → 150.
- Turn 10: Lisia found nothing. Water to the Active. Retreat. Heals to 190/170.
- Turn 11: Lightning to Shinx. Zzzap 190 → 120.
- Turn 12: Irida (+40 each). Water attached. Retreat. Heals to 220/180.
- Turn 13: Lightning attached. Rare Candy Shinx → Luxray. Oricorio retreated. Volt Bolt 140 (220 → 80).
- Turn 14: no draw (deck empty). Turbo Shark 70 (Luxray 130 → 60) and a Water to the Bench (3 → 4). Heals to 100/200.
- Turn 15: Dustin conceded at 499 s. Defeat.
- Results: 0-2, 15 turns, 120 damage done.
- Opponent Pokémon seen: Furfrou, Oricorio, Eevee, Sylveon, Shinx, Luxray.

## Disagreements

| Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|
| 2 (Dustin) | Order of Cabbie and Soothing Shore | Soothing Shore listed as played before Cabbie | Cabbie first (97-101 s), which fetched Soothing Shore, played at 102-106 s | Cabbie played at 97 s; Soothing Shore shown at 99 s | t_0097, t_0099 | **X right** |
| 5 (opp) | Lightning attachment | Lightning to Benched Oricorio (197 s) | Generated Lightning left unspent | Oricorio shows 1 Lightning at 197 s and the Zone is empty | t_0193, t_0197 | **C right** |
| 7 (opp) | Order of Oricorio's 2nd Lightning and Furfrou's retreat | Attach, then retreat | Retreat (288-290 s), then attach (291-293 s) | At 290 s Oricorio is already Active while the Lightning is still in the Zone | t_0283, t_0290 | **X right** |
| 9 (opp) | Zzzap timing (220 → 150) | 363-364 s | 369-371 s | At 364 s the Active is still 220 ("Waiting for opponent"); "Weakness 70" at 370 s | t_0364, t_0370 | **X right** |
| 12 (Dustin) | Was Irida a new draw? | No, it had been in hand since turn 4 | Yes, drawn at 414-416 s | The turn 6 Copycat shuffled the old hand away (no Irida at 254 s). Irida is zoomed as the new card at 414 s, and it is not in the hand there | t_0254, t_0414 | **X right** |
| 15 (opp) | Lightning attachment | Zone glowed, so an attachment was made (to an unknown target) | Generated Lightning kept in the Zone | Lightning is still in the Zone at 495-497 s; nothing attached before the concession | t_0492, t_0495, t_0497 | **X right** |
| 15 (opp) | Card played and the yellow streak | Unidentified face-down card; streak "from Luxray" | Volkner (attach 2 Lightning from discard to Luxray), effect starting at 497 s | Volkner shown face-up at 495.5 s; the streak runs from the discard to Luxray | t_0495, half/t_0495.5, t_0497 | **X right** |

## Facts only one review records (confirmed by the frames)

**Only C:**
- Turn 7: the opponent's +20 HP Tool is **Giant Cape** (t_0297).
- The opponent's Energy Zone is stated as Lightning (Zone icon at t_0057 and t_0197).

**Only X:**
- Turn 1: **Protective Poncho** attached to Eevee (t_0056, t_0058). It is also missing from C's opponent trainer list.
- Turn 2: Magikarp attacked with **Expert Splasher**. Both coins were tails, for 0 damage (t_0110, t_0113).
- Turn 6: Dustin played a **second Copycat**, which produced a new hand: Wallace ×2, Mega Gyarados ex, Soothing Shore, Elegant Cape, Aqua Jet Carvanha (t_0243, t_0254).
- Turn 8: **Water attached to the newly evolved Benched Mega Sharpedo ex**, 1 → 2 (t_0336 vs t_0339). C calls this attachment "unseen".
- Turn 13: Oricorio's **retreat cost 1 Lightning**, leaving it with 1 (t_0492, t_0497).

## Which review to rely on
For this game a player should rely more on **Review X**.

- **Opponent's last turn.** X correctly identifies Volkner as the card played on the final turn and correctly says the generated Lightning was never attached. C left the card as unidentified and claimed an attachment that didn't happen.
- **Missing plays in C.** C has no record of:
  - the opponent's Protective Poncho;
  - Magikarp's Expert Splasher attack;
  - Dustin's second Copycat. Missing it led C to wrongly say Irida was never a turn 12 draw.
  - the turn 8 Energy attachment.
- **Order and timing.** X also has the right order for Cabbie and Soothing Shore and for the turn 7 retreat, and the right timing for the turn 9 Zzzap.
- **X's one error.** X said the turn 5 Lightning went unspent. In fact it went to Oricorio, as C says, and X contradicts itself on this two turns later.

Both reviews agree on everything that decides the result: both KOs, every damage number and HP total, the heals, the score and the concession.
