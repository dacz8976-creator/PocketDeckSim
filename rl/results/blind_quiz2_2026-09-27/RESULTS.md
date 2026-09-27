# Grading: "Your Move, Blind 2" (Dustin's answers, Sept 27, 2026)

The quiz page is https://claude.ai/artifact/DZRnfhgNyggS9tgCr988tG. It has 10 positions from `../kpf_2026-09-26/diagnosis/DIAGNOSIS.md` section 5.
- **What's here:** `positions.json` (what he saw), `answer_key.json` (published now that he's finished), `answers/` (his answers), and `BUILD_NOTES.md` and `VERIFY_NOTES.md` (all 20 games replay the table games; blindness checks passed).
- **How it was graded:** by a workflow. Two independent graders marked the answers and a reconciler checked the close calls. The text below is the reconciler's.

Two graders marked the ten answers on their own. They agreed on all ten, so no grade needed a tiebreak. I checked the three close calls (Q07, Q08, Q09) against the boards and kept them as graded.

## In plain words

- **Tally: kp3 8, kpf 1, neither 1, unclear 0, needs follow-up 0.**
- **Fixes A and B: 7 out of 7 his way went with kp3.** In every position that tests fix A (Q03-Q05) or fix B (Q01, Q02, Q06, Q07), he kept the cheap attacker in front and built on the Bench, as kp3 did. He never moved a Pokémon up early the way kpf did.
- **He attacks whenever he can.** Nine positions had an attack available, and he attacked in all nine. That includes Q09, where neither bot attacked.
- **The two things the fix is built to keep, he didn't choose.** Those are the Lucario "hide" (Q09) and Vespiquen's tempo trade (Q10). One answer each is thin evidence, but both point the same way: the fix shouldn't treat losing them as a failure.
- **Q08 (his own hypothesis):** he fed the Active Darkrai, like kpf, but for a different reason. He wanted fuel to retreat into Igglybuff next turn, not a push toward Dark Slumber. He didn't call feeding the Active a mistake, so this spot doesn't say the evaluator is wrong under both bots.
- **One gap to test:** his notes keep budgeting next turn's retreat cost. Fix B, as written, doesn't. See section 3.

## 1. Outcome per position

| # | Tests | His first tap | Outcome | His words | Confidence |
|---|---|---|---|---|---|
| Q01 | fix B | Professor's Research (neither bot's) | **kp3** | "Retreating puts the more valuable piece in a vulnerable position and doesn't help anything." | leaning |
| Q02 | fix B (paid retreat) | Professor's Research (kp3's) | **kp3** | "evolve riolu to mega lucario, attach fighting energy to him. Attack suicune with hitmonlee" | leaning |
| Q03 | fix A (bare Riolu) | F on the Benched Riolu (kp3's) | **kp3** | "Attach energy to riolu, attack with bonsly end turn." | sure |
| Q04 | fix A (Swablu) | Training Area (neither) | **kp3** | "attach psychic energy to swablu ... attack with igglybuff, end turn" | leaning |
| Q05 | fix A (Combee) | Fragrant Forest (kpf's; only an order difference) | **kp3** | "If the basic Pokemon forest gave me was shuckle, I would use x speed to retreat combee and promote shuckle, attach energy to shuckle and attack." | leaning |
| Q06 | fix B (Vespiquen) | Use Fragrant Forest (neither) | **kp3** | "evolve combee to vespiqueen, attach energy to vespiqueen, attack with shuckle" | leaning |
| Q07 | fix B (Darkrai, his scenario) | P on Swablu (neither) | **kp3** | "Attach psychic energy to swablu so if I get mega altaria next turn, they will be able to attack, attack with igglybuff" | sure |
| Q08 | his pure hypothesis | Bench Igglybuff (neither) | **kpf** | "attach energy to darkrai (hoping they don't evolve and kill the active darkrai with Hydreigon next turn and will retreat to igglybuff)" | leaning |
| Q09 | the helpful Lucario hide | Protective Poncho (kp3's) | **neither** | "Play poncho on bench riolu, attach energy to active riolu and attack" | leaning |
| Q10 | R's tempo credit | Use Fragrant Forest (neither) | **kp3** | "retreat ogerpon, promote shuckle, attach energy and attack with shuckle" | sure |

How the close calls were settled (both graders agreed on each):

- **Q01.** His written order (F on Riolu, evolve on the Bench, then Research) doesn't match his first tap (Research). Neither order has a retreat, and his note rules the retreat out. Before the draw, that is kp3's turn, and the "evolve on the Bench, then retreat" path to kpf's board is excluded.
- **Q05.** The fork comes after Fragrant Forest's random pick. His plan answers the Shuckle ex case, which is what both games got: X Speed, retreat Combee, G on Shuckle ex, attack. That is kp3's turn move for move. His other branch (Combee attacks) is only for a pick that isn't Shuckle ex. No follow-up is needed.
- **Q07.** On the tested choice he matches kp3: Igglybuff stays in front and uses Sleepy Lullaby, and Darkrai isn't moved up. Both bots put the P on the Darkrai that already had one. He puts it on Swablu instead. That part was shared by both bots, so it doesn't separate them. A strict reading could call this "neither".
- **Q08.** "darkrai" alone is ambiguous: there are two. The rest of his plan settles it. Darkrai's Retreat Cost is 2, so retreating the Active Darkrai into Igglybuff next turn works only if today's P goes on the Active Darkrai (today's P plus next turn's P). So this is kpf's placement. A confirmation question is below.
- **Q09.** He splits the bots. His F goes on the Active Riolu (kpf's move), but Riolu stays in front and attacks (kp3 keeps Riolu in front but doesn't attack). His Poncho goes on the Benched Riolu, which neither bot did. On the tested point, hiding Riolu behind Hitmonlee, he doesn't hide, and neither does the alternative in his note ("Sacrificing my active riolu to give me time to set up").

## 2. What his answers decide (DIAGNOSIS.md section 5)

**Fix A (a Pokémon that still has to evolve counts each evolution step as a missing Energy): supported, 3 of 3.**
- Q03 (sure): Bonsly stays in front, and Riolu stays on the Bench with the F. He doesn't put a bare Riolu forward.
- Q04: Igglybuff stays in front, and the P goes to a Benched Swablu. He doesn't put Swablu forward to Sing. This is the Swablu slice, 15/3.
- Q05: when the Forest gives Shuckle ex, he pays X Speed to put it in front rather than attacking with the half-ready Combee (Combee 9/2, inside the 37/14 cell).
- The data already pointed this way (48/16 pooled). His answers agree.

**Fix B (the clock may credit the Zone Energy to any one Pokémon, Bench included): supported, 4 of 4.**
- Q01: the Mega evolves on the Bench, and Bonsly attacks. Per the diagnosis, the clock crediting only the Active slot is the error.
- Q02: he keeps Hitmonlee, a wall whose retreat has to be paid, in front and attacks. This also counts against his own gate idea. The gate would take Hitmonlee's credit away here and push toward the retreat he rejected.
- Q06: Vespiquen ex is evolved and fed on the Bench, and Shuckle ex chips. He plans to move it up "next turn", not a turn early.
- Q07 (sure): Igglybuff stays, and Lullaby plus Bad Dreams do the work. Darkrai isn't moved up.
- In the data, B was the weaker half (52/32, p about 0.04, slices chosen after looking). His four answers are the best independent support B has.

**His pure hypothesis (Q08): silent on the fixes; the pure form stays "not what hurts".**
- He chose kpf's placement (the Active Darkrai) and didn't call it a mistake. So the diagnosis's branch "the evaluator gets this spot wrong under both bots" is not triggered. That fits the balanced 17/14 count.
- His reason isn't kpf's. He wants retreat fuel to get Igglybuff in front next turn, not a start on Dark Slumber. He also benches Igglybuff, which neither bot did. So the game results (kp3 won, kpf lost) don't grade his line.

**The helpful Lucario hide (Q09): he doesn't choose it, a weak lean toward "the helpful pattern is luck".**
- The fix is expected to make the hide more likely. Fix A marks a bare Riolu in front as unready, while Hitmonlee stays ready. He kept Riolu in front, so on this spot his play goes against that side effect of A. It doesn't touch A's main claim (Q03-Q05).
- One answer can't overturn the 15/30 count. It does mean "kph abandons the Lucario hides", one of the diagnosis's listed signs of overshoot, shouldn't be read as a failure on its own.

**R's tempo credit (Q10, sure): contradicted for this spot.**
- He retreats into Shuckle ex and attacks. He never considers putting Vespiquen ex in front. By the diagnosis's own note, the tempo trade is then not worth keeping here.
- This goes against a deliberate design choice in section 4: B keeps the tempo trade, and "kph abandons the Vespiquen tempo trades" is listed as overshoot. As with Q09, that sign of overshoot needs care.

**Scorecard.** Supports fix A and fix B. Contradicts keeping R's tempo credit (Q10) and, weakly, the value of the Lucario hide (Q09). Silent on the fixes at Q08, where he agrees with kpf's placement for his own reason and doesn't back his hypothesis in its pure form.

## 3. What his notes point to that the diagnosis missed

1. **Retreat cost next turn.** He plans each move-up and prices it.
   - Q06: "next turn retreat with shuckle", paid with the Energy Shuckle ex holds.
   - Q10: he rejects feeding the Benched Vespiquen ex because "you would need another xspeed to retreat shuckle".
   - Q08: he feeds the Active Darkrai so it can retreat into Igglybuff.
   - The clock already lets a benched Pokémon attack next turn without paying a retreat. Fix B builds on that. The diagnosis dropped the variant "limit B to Pokémon the Active can retreat into" because it changes none of the diagnosed kp3/kpf choices. That is true, but Q10 shows a line where it matters: Shuckle ex in front with no Energy and the G on the Benched Vespiquen ex. Under B, Vespiquen ex reads as attacking next turn (G now plus next turn's G), but it is stuck behind Shuckle ex unless you draw another X Speed.
   - Worth one constructed test board in the mechanism check.
   - Separately, Energy on the Active as retreat fuel (Q08) isn't discussed anywhere in the diagnosis. Whether any score counts it was not checked.
2. **Which piece is at risk, by points.** Q01: "puts the more valuable piece in a vulnerable position" and "I only lose if they KO mega lucario". Q09: "Sacrificing my active riolu".
   - His rule: while the 3-point Mega can't attack yet, a cheap 1-point piece should stand in front.
   - DIAGNOSIS section 3 says the small scores left after the big pulls (safety as HP per knockout point, and the Active's HP as the first victim in the clock) favour the bigger Pokémon in front. That is the opposite of his rule.
   - If kph still makes the forward swaps in the mechanism check, look at those small scores next.
   - His reason is the "the wall should take the next hit" idea the data could not confirm (hit rates were equal in worse and better games). So this is a lead, not a finding.
3. **He takes the free or cheap attack every time.** He did in all nine positions where one was available. That backs the diagnosis's point that kpf attacks less. It also shows kp3 skipping one: in Q09, kp3 put F on Hitmonlee and ended the turn without attacking, where he attacks with Riolu. It's a small chip, but it's something neither fix touches.
4. **Shared by both bots, outside R** (listed so they aren't lost; neither is a kp3/kpf difference):
   - **Stadium play.** He plays Training Area in Q04 only to remove the opponent's Fragrant Forest, which neither bot did. He holds back a Stadium that doesn't help now and could be removed or help the opponent (Q03, Q07).
   - **Copycat and hand size.** He skips Copycat when the opponent holds only 2 cards (Q03), where kp3 played it. In Q08 he plays out his Training Area partly to have "fewer cards" in case the opponent has a Copycat.
   - **Q07 note on the opponent.** The opponent (kp3 in both games) attached Fire to an Asleep Heatmor that Bad Dreams then knocked out at the end of the turn. The bot may not foresee end-of-turn Bad Dreams damage when it picks where to attach. Worth a quick check; it is not part of this diagnosis.
5. **Page note.** In Q02 he asked "Who did hitmonlee hit last turn?". The log line reads "Hitmonlee attacked with Stretch Kick" with no result, because the opponent had no Benched Pokémon then. Future quiz pages should say it did nothing.

## 4a. Dustin's answers to the follow-ups (Sept 27)

1. **Q08: yes, the Active Darkrai.** "That deck works with darkrai on the bench, I'm trying to get him to the bench asap."
   - Darkrai B2b 040's Bad Dreams works from anywhere, while Dark Slumber costs [CCC] and its Retreat Cost is 2 (`lib/card.py`). So the P on the Active Darkrai is retreat fuel.
   - That is the missing mechanism of section 3 (Energy on the Active as retreat fuel). It also backs koa's part B idea: Altaria shouldn't have Darkrai in front (`../koa_2026-09-26/reading/READING.md`, diagnostics).
2. **Q09: the hide wastes an Energy.** "You are basically wasting an energy to put it on the active riolu, retreat and promote hitmonlee who can't attack. Next turn, that's what I would do."
   - So kpf's "helpful" Lucario hide (15/30 in the diagnosis) is the right idea a turn too early. kph dropping it is expected, not an overshoot.

## 4. Follow-up questions (only two needed)

1. **Q08 (confirmation):** When you wrote "attach energy to darkrai", did you mean the Active Darkrai (80 HP), so it could retreat into Igglybuff next turn?
2. **Q09:** You kept the first Riolu in front. The other option was F on that Riolu, then retreat it into Hitmonlee (paying with that F), with Poncho on Hitmonlee and no attack. Would that be better or worse than your plan, and why?
