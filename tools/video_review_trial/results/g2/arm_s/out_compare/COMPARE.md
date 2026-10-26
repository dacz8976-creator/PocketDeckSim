# Review C vs Review X: Dustin (Dacz8976) vs Point n Click, ranked, Master Ball

Review X's final word = `codex/REVIEW.md` + `FINDINGS.json` / `LEAD_ACCEPTANCE.json` / `UNCERTAINTIES.json` / `COVERAGE.md` / `QR_ID.json` (no `VERIFICATION.json` exists; the lead acceptance made no corrections).

## Where the two reviews agree (checked against the frames)
- **Setup:** the opponent went first and Dustin went second. Dustin's opening hand was Carvanha, Cabbie, Poké Ball, Wallace and Mega Sharpedo ex, with Carvanha Active and no Bench. Dustin's Energy Zone is Water.
- **Global 1:** the opponent's Supporter Confuses Carvanha. The coin is Heads, so Mawile is not Confused. No attack.
- **Global 2:**
  - Dustin draws Lisia and plays Poké Ball → Magikarp, which he benches.
  - Wallace evolves Carvanha into Mega Sharpedo ex, which clears the Confusion.
  - Water attached to Sharpedo.
  - Turbo Shark for 70 (170→100), and its effect gives Magikarp a Water.
- **Global 3:**
  - Steel Apron.
  - Lucky Ice Pop twice, each healing 20 (100→120→140), both coins Tails.
  - Starting Plains (Mawile 140→160, Magikarp 30→50).
  - One Metal attached. No attack.
- **Global 4:**
  - Dustin draws and benches Carvanha (70 HP under Plains).
  - Cabbie → Soothing Shore, which replaces Plains (160→140, 70→50, 50→30).
  - Water attached to Magikarp.
  - Turbo Shark for 60 after Apron (140→80), and its effect gives Magikarp a 3rd Water.
- **Global 5:** Pokémon Center Lady heals 30 (80→110). 2nd Metal attached. Heat-Up Crunch for 60 on Sharpedo (190→130), with the "+30 next time" banner.
- **Global 6:**
  - Dustin draws Wallace and evolves Magikarp into Mega Gyarados ex, which keeps its 3 Water.
  - Sharpedo retreats keeping its 1 Water. Water attached to Gyarados (4 Water).
  - Mega Blaster for 130 after Apron (110→0), discarding the top 3 cards of the opponent's deck (identities unreadable).
  - KO, +3 points. **Final score 3–0, decided on points.**
- **Opponent Pokémon seen:** only Mega Mawile ex (170 HP), with no Bench all game.

## Disagreements and verdicts
| # | Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | Global 1 | Opponent's Supporter | Team Rocket's Master Plan | Team Rocket Grunt | Title reads "Team Rocket's Master Plan" (Confuse the opponent's Active; flip a coin, on tails your own Active is also Confused) | full/t_0074 | **C right** |
| 2 | Global 3 | When the 1st Metal is attached | Last action, after Starting Plains (t≈157.5–158) | First action, before Steel Apron | No Energy on Mawile at t=127 or t=150 (the Metal is still in the Zone at t=150); attach sparkle at t=157.5; icon on Mawile at t=158 | full/t_0127, full/t_0150, half/t_0157.5, full/t_0158 | **C right** |
| 3 | Global 5 | When the 2nd Metal is attached | After Pokémon Center Lady (t≈199.5–200) | Before Lady (t≈191–192) | t=193: 80 HP, 1 Metal. t=199.0: 110 HP, still 1 Metal. t=200.0: 2 Metal | full/t_0193, half/t_0199.0, half/t_0200.0 | **C right** |
| 4 | Result | Statistics screen | No other statistics are shown | t=249 shows went second, 6 turns played, 3–0, 260 damage | t=242–251 show the Victory card, loading, Card of the Game (Gyarados, then Mawile), then the rank panel. No turns or damage statistics appear (X's numbers are correct for the game, but they are not shown on screen) | full/t_0242, t_0248, t_0249, half/t_0249.5, full/t_0250, half/t_0251.0 | **C right** |
| 5 | Result | Rank points | Panel fading in, 924 shown faded | 925, +1 | t=250–250.5: 924 pts, +1. t=251.0: **925 pts**, pts gained 1 | full/t_0250, half/t_0250.5, half/t_0251.0 | **X right** |
| 6 | Score | Points taken by Mawile | OPPONENT_FINAL.json: `points_taken: 3` | Opponent earned 0 | +3 goes to Dacz8976. The opponent stays at 0 (C's own md also says 3–0, so this is a JSON field error) | full/t_0238 | **X right** |
| 7 | Header | Deck list from the QR code | QR not readable, list unknown | Decoded: 20 cards, Water | t=0 shows a clean full QR. It can't be decoded by eye. Every owner card seen in play is in X's list | full/t_0000 | **unsettled** |

No timing differences of 2 seconds or more occur except rows 2–3, where the order of actions within the turn also differs.

## Facts only C records (frame-confirmed)
- Opponent is Lv. 60 (full/t_0010).
- Card of the Game: Mega Gyarados ex for Dustin and Mega Mawile ex for the opponent (full/t_0248, t_0249).
- Mega Mawile ex is Metal type (full/t_0249).
- Both players hold 5 cards and Dustin's deck shows 15 after setup (full/t_0030).
- Lisia and a second Mega Sharpedo ex stay in Dustin's hand to the end (full/t_0127, t_0193).
- Opponent's Energy Zone is Metal (full/t_0150).

## Facts only X records (frame-confirmed)
- The two Carvanha are different printings: the starter has Sharp Fang 30 (full/t_0030) and the turn-4 Carvanha has Aqua Jet 10 with Bench damage (full/t_0193).
- Magikarp's attack is Expert Splasher (full/t_0127).
- Heat-Up Crunch costs Metal + Colorless, which is why one Metal couldn't attack on turn 3 (full/t_0249).

## Which review to rely on
**Review C is more reliable for this game.** Both reviews get the full damage and HP chain, the Knock Out and the 3–0 points finish right. C is right on all three play-by-play disagreements:
- the opponent's turn-1 Supporter (Team Rocket's Master Plan, not Grunt);
- when the opponent attached its first Metal Energy (last action of turn 3, not first);
- when it attached its second (after Pokémon Center Lady on turn 5, not before).

X also says the result screen showed turns and damage statistics, which the frames don't show. X's edges are outside the play itself:
- the correct final rank of 925 (+1);
- the two different Carvanha printings;
- a QR decklist that can't be checked here.

C's one real slip is a JSON field (`points_taken: 3`) that its own write-up contradicts. For "what happened, in what order", trust C. Use X for deck identity and rank bookkeeping.
