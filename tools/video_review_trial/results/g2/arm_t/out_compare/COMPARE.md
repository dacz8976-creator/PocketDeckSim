# Review C vs Review X: Dustin (Dacz8976) vs Point n Click, checked against the frames

Review X's final word is `codex/REVIEW.md`, together with `FINDINGS.json`, `UNCERTAINTIES.json`, `COVERAGE.md` and `LEAD_ACCEPTANCE.json`. None of these files changes any game fact in REVIEW.md, and there is no VERIFICATION.json or correction note.

## Where the two reviews agree (checked, not counted)
- The opponent went first.
- Dustin's opening hand was Carvanha (Active), Cabbie, Poké Ball, Wallace and Mega Sharpedo ex. Lisia was his turn-2 draw.
- Dustin's Energy Zone is Water.
- Every attack and HP change matches in both reviews:
  - Turbo Shark 70 (Mawile 170→100).
  - Steel Apron, two Lucky Ice Pops (+20 each, Tails both times) and Starting Plains (Mawile to 160, Magikarp to 50).
  - Turn 4: Carvanha benched, Cabbie → Soothing Shore (Mawile 140, Carvanha 50, Magikarp 30), manual Water to Magikarp, Turbo Shark 60 (Mawile 140→80), effect Water to Magikarp (3 Water).
  - Pokémon Center Lady +30 (Mawile 110), then Heat-Up Crunch 60 (Sharpedo 190→130).
  - Turn 6: Wallace evolves Magikarp into Mega Gyarados ex, Sharpedo retreats keeping its Energy, 4th Water on Gyarados, Mega Blaster 130 after Apron. Mawile is KO'd, +3, and Dustin wins 3–0 over 6 global turns.

## Disagreements

| Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|
| G1 (opp) | Supporter played | Team Rocket's Master Plan | Team Rocket Grunt | The card title reads "Team Rocket's Master Plan" | t_0074 | **C right** |
| G3 (opp) | Timing of the 1st Metal attachment | End of turn (t_0157 none, t_0158 one) | First action, before Steel Apron | No Energy icon at t_0124, t_0136 or t_0157. The Metal icon first appears at t_0158 | t_0124, t_0136, t_0157, t_0158 | **C right** |
| G5 (opp) | Timing of the 2nd Metal attachment | After Pokémon Center Lady (t_0198→t_0200) | 191–192 s, before Pokémon Center Lady | t_0192: 80 HP, 1 Metal. t_0198: PCL in discard, 110 HP, 1 Metal. t_0200: 2 Metal | t_0192, t_0198, t_0200 | **C right** |
| Result | Turn count / damage total on screen | None shown | "turns played 6 … damage done 260" at 249 s | 0242–0251 show only the Victory splash, Card of the Game screens and the rank panel. No stats panel appears. t_0249 is the opponent's Card of the Game | t_0242, t_0248, t_0249, half t_0247.5/0248.5/0249.5, t_0250 | **C right** |
| Result | Final rank points | 924 pts, gained 1 | 924 → 925 (+1) | 924 at t_0250, then 925 at half t_0251.0 | t_0250, half t_0250.5, half t_0251.0 | **X right** |

## Facts only one review records (confirmed by the frames)

**Only C**
- The opponent's Energy Zone is Metal (Zone icon at top left, t_0124 and t_0192).
- Card of the Game: Mega Gyarados ex for Dustin (t_0248) and Mega Mawile ex for the opponent (t_0249).
- Starting Plains went to the opponent's discard after Soothing Shore replaced it (t_0192).

**Only X**
- Dustin used two different Carvanha cards: the starter has Sharp Fang 30 (t_0075), and the turn-4 Carvanha has Aqua Jet 10 (t_0192).
- Pokémon Center Lady stays visible in the opponent's discard afterward (t_0198).

No claim was found in either review that the frames contradict while the other review is silent.

## Which review to rely on
Review C is the more reliable account of this game. It wins 4 of the 5 disputed points:
- **Turn-1 Supporter:** C names the card correctly. X calls it "Team Rocket Grunt", a different card.
- **Metal Energy timing:** C has both opponent Metal attachments at the right point in the turn. X puts both at the start of the turn, which misstates the order of the opponent's plays.
- **Result screen:** X says it shows "6 turns / 260 damage". That screen does not appear in any frame. X likely built it from its own damage sum and passed it off as something seen on screen, even though its lead acceptance says this was checked.

X's one win is the final rank. C reported the 924 shown before the count-up, but the panel finishes at 925. X's extra details (the two Carvanha versions, PCL in the discard) are correct but minor. For the gameplay itself the two reviews are equally accurate. Where they differ on order of play or on what the screen shows, the frames side with C.
