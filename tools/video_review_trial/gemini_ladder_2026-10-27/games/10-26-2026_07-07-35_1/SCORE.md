# Score: Review G (Gemini) vs Review X (Codex), ScreenRecording_10-26-2026 07-07-35_1

Frames opened: 44 of the allowed 120 (t = 1, 2, 3, 23, 25, 31, 64, 70, 76, 81, 97, 101, 107, 121, 124, 128, 132, 134, 135, 136, 139, 143, 145, 148, 153, 156, 158, 162, 164, 167, 169, 170, 171, 172, 173, 174, 176, 185, 192, 195, 201, 202, 203, 204).

## What the frames show (the truth used here)
- Owner (Dacz8976) goes first ("You are going first", t=25). Owner Energy Zone: Water. Opponent Energy Zone: Fire (t=70, 124).
- Owner opening hand (t=25, 31): Small Balloon, Poke Ball, Soothing Shore, Team Rocket's Koffing (gold), Team Rocket's Koffing. Active Koffing, one Koffing on the right Bench.
- Opponent: Charmander 60 HP Active, empty Bench (t=64).
- Turn 1 (owner): draws Seadra (t=70), Poke Ball gets Horsea (t=76, Poke Ball in discard t=81), Horsea to left Bench (t=81), Small Balloon on Active Koffing ("Retreat Cost is 1 less", t=97), retreat to Horsea (t=101). No Energy, no attack. Hand left: Soothing Shore, Seadra.
- Turn 2 (opponent): plays May (t=121, May card in discard from t=136), Fire Energy attached to Charmander (animation at t=135, attached by t=136), Combustion 20 on Horsea (t=143), Horsea 50 to 30 (t=145).
- Turn 3 (owner): "Current turn: 3" (t=145). Draws Team Rocket's Weezing ex (t=148), evolves the right-Bench Koffing (t=153, Weezing ex 140 HP on the Bench t=156), Boiler Smog: "Charmander is now Poisoned and Burned" (t=158), Water Energy to Horsea (t=164 to 167), Hook with a "Weakness 50" popup (t=169), Charmander 60 to 10 (t=170 to 171). Poison 10 popup (t=171), Charmander at 0 HP with a Burned 20 popup (t=172), "Your opponent conceded" (t=173 fading in, full at t=174). No point is awarded.
- Result: Victory, went first, 3 turns, points 0 to 0 (empty dots), damage done 50, Card of the Game Horsea (t=195); opponent Card of the Game Charmander (t=201). Master Ball Rank: 977 pts before the game (t=2), result page shows 977 transitioning at t=202 and "986 pts, 1 pts gained, Win streak pts 8, 3 win streak" at t=203. The clip's last frame (t=204) is the Player EXP (15) screen.

## Disagreement table (G vs X)
| Turn | Item | G says | X says | Frames | Verdict |
| --- | --- | --- | --- | --- | --- |
| Result page | Rank points after the game | 977 to 986 (+1 pts gained, +8 win streak pts, 3-win streak) at t=202-203 | "Final ranked page still displays 977"; "Clip ends on the ranked page" | t=2 shows 977 before the game; t=202 shows 977 mid-transition with +1 / +8; t=203 shows 986 pts, 1 gained, win streak 8, "3 win streak"; t=204 (last frame) is the Player EXP screen | G right |

Everything else the two reviews state agrees. Differences of 3 s or less are not errors and are listed only for completeness:

| Item | G | X | Frames | Note |
| --- | --- | --- | --- | --- |
| Opponent Fire attach | t=138 | "visible by 140" | attach animation at t=135, attached t=136 | within tolerance (G 3 s) / "visible by" is true |
| Combustion | t=141-144, hit at 143 | 142, hit at 143 | hit popup t=143 | agree |
| Poison / Burn zero-HP sequence | Poison 171-172, Burn popup 172 | zero HP 172, Burn popup 173 | Poison popup t=171, Burned 20 at t=172 | within tolerance |
| Concession | t=173 | t=174 | text fades in at 173, full at 174 | within tolerance |
| Opponent Charmander first seen | 63-64 | 64-68 | t=64 shows it | agree |

Facts both reviews state and the frames confirm: owner first; opening hand and setup; Water / Fire Energy Zones; every turn-1, turn-2 and turn-3 action above; Hook 30 + 20 Weakness = 50, Charmander 60 to 10; Horsea 50 to 30; Boiler Smog by the owner's Weezing ex (so Poison and Burn came from the owner, not the opponent); 0 to 0 score; opponent conceded during turn-3 Checkup before any Knock Out point; Horsea Card of the Game; opponent seen: Charmander only; opponent Trainer May; no healing, no Bench damage.

## Claims only one review makes that the frames contradict
- X (REVIEW.md, last table row and Outcome section): "Final ranked page still displays 977 during the captured result sequence. Clip ends on the ranked page." The result sequence ends at 986 pts (t=203) and the clip ends on the Player EXP screen (t=204). The 977 frame (t=202) is the start of the points animation. X also never records the +1 / +8 rank gain.
- G: nothing found that the frames contradict. G's unverifiable detail (opponent hand 5 to 6, May draw/shuffle order) is not contradicted by anything seen.

## Errors by review
Review G (Gemini): 0 major, 0 minor.

Review X (Codex): 0 major, 1 minor.
- Minor: reports the final rank page as still 977 and the clip as ending on the ranked page; the result shows 986 pts (+1 gained, +8 win streak, 3-win streak) and the clip ends on the Player EXP screen. This is the result screen, not a game event, so it is graded minor. (X's QR, deck, source-hash and coverage material was not checked against the frames beyond the deck grid at t=1, which matches.)

## Opponent sheets (12 fields each)
| Field | Truth | gemini/OPPONENT.json | gemini_cheap/OPPONENT.json | codex/OPPONENT.json |
| --- | --- | --- | --- | --- |
| went_first | dustin | dustin OK | dustin OK | dustin OK |
| global_turns | 3 | 3 OK | 3 OK | 3 OK |
| final_score | 0-0 | 0-0 OK | 0-0 OK | 0-0 OK |
| end | concede_opponent | concede_opponent OK | concede_opponent OK | concede_opponent OK |
| opponent Energy Zone | Fire | Fire OK | Fire OK | Fire OK |
| opponent Pokemon names | Charmander | Charmander OK | Charmander OK | Charmander OK |
| attack names | Combustion | Combustion OK | Combustion OK | Combustion OK |
| Trainer names | May | May OK | May OK | May OK |
| special_conditions (from opponent's cards/attacks) | none (Poison and Burn came from the owner's Boiler Smog) | [] OK | ["Poisoned","Burned"] WRONG | [] OK |
| healed | false | false OK | false OK | false OK |
| bench_damage | false | false OK | false OK | false OK |
| card of the game | Charmander | Charmander OK | Charmander OK | Charmander OK |
| **Right / checked** | | **12 / 12** | **11 / 12** | **12 / 12** |

Not among the 12 fields: first_seen_turn differs (G 1, cheap 0, codex null); Charmander is on the board from setup (t=64), before turn 1, so 0 is the closest.

## Which record to rely on
For this game both reviews are accurate on every game event: who went first, the opening hand, both Energy Zones, each turn's plays, the Combustion and Hook damage with HP before and after, Boiler Smog being the owner's, the turn-3 Poison/Burn zero-HP sequence, the concession before any point, the 0 to 0 score and the opponent's cards. They differ only on the rank-points screen at the very end, where Review X reports 977 and the frames show 986 (+1, +8). Review G is the record to rely on: it has no error I could find, it gives HP and card identities at every step, and it gets the result page right, while Review X is equally correct on the game itself but carries the one wrong result-page claim. A player could use either for the game itself. Among the opponent sheets, gemini and codex are fully right and gemini_cheap wrongly lists the owner's Poisoned and Burned as opponent special conditions.
