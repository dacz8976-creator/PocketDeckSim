# Plan for the week of Oct 19, 2026 (both reviews combined)

Written by the coordinator on Oct 18 evening, from the Claude-side review (CLAUDE_REVIEW.md) and Astra's review plus
its follow-up note (ASTRA_REVIEW.md), on Dustin's word: "combine the reviews and develop a plan before the reset".
**Revised the same evening with Astra's four corrections** (on the comparison, the finished-game baseline, future
leakage, and the Kingambit-losses wording). Exam preparation continues under the revised plan.

## Where the two reviews agree

- **Verdict: REDIRECT.** No new bot capability was shown this week. Stop adding hand-made scoring bonuses to the pilot.
- **The finding:** in the diagnostic's positions, the bot generates his moves but scores them lower. The scoring favours
  "attack as soon as possible" over getting a Pokémon ready for a later turn.
- **One bounded experiment this week:** test whether an AI model judges these plan decisions better, on positions no
  bot was developed on, judged against his own choices. Other equally good moves also get credit.
- **Upstream help continues** (17 PRs merged, 6 open), and we watch for the maintainer's generalist AI.

## Where they differ, and what this plan takes

- **Deeper search.** The Claude review says "deeper search didn't help, done". Astra corrects it: depth 5-8 did not
  test real multi-turn planning. The tree stops at the turn boundary, and km3 plays the simulated later turns. So
  "the settings we tried didn't help" stands, but "search can't help" does not. This plan keeps that open; it is
  not this week's experiment.
- **Second opinion or plan chooser.** The Claude review asks for an AI second opinion's agreement with his moves. Astra
  asks for a plan chooser with no km3 veto, and finished-game evidence if the decisions are better. This plan does
  both, in that order: decisions first, finished games only if the decisions clear the bar.
- **Which positions.** Both reviews include positions where km3 and kx3 agree but play poorly. Neither limits the test
  to their disagreements.
- **Kingambit's losses (wording corrected).** Kingambit did not reach play in his four Kingambit losses. How much of
  that was draws, deck construction or decisions remains unresolved: earlier Energy placement, protection, draw
  choices and sacrifices can affect whether it arrives. The Claude review's "deck and luck, not piloting" is
  withdrawn. The exam covers more than Kingambit, for variety.

## The experiment: an unseen-positions exam, then an AI plan judge

1. **Exam (Mon-Tue).**
   - Take 40-60 decision points from his recorded ladder games that no bot was developed on: not stage A, the
     diagnostic or the pause-game sets.
   - Use more than one deck. Cover all four kinds of right answer: prepare, sacrifice, attack now, and abandon the
     plan. Include positions where both bots agree.
   - Record each point's game. Points from one game are not independent, and no whole game may also feed
     development.
   - The default label is his recorded move. Agents list other acceptable moves, each with a reason, and any of them
     earns credit. He rules only on the genuinely ambiguous ones, a handful.
   - Labels are committed before any bot runs. If fewer than 40 usable points exist, say so rather than pad.
2. **AI plan judge (Tue-Wed).**
   - Input: the visible position (hidden cards masked), exact card text, and the legal whole-turn plans.
   - **No future leakage.** A plan's shown results must not reveal the actual next draw, prize or coin result before
     the decision. Show the possible outcomes with their chances, or let the judge decide again once they are
     visible.
   - **No hidden filter.** The plan list comes from the engine's full set of legal moves, not km3's candidates. km3
     must not quietly drop useful plans before the judge sees them; removing its final veto is not enough.
   - The model picks one plan, and km3 cannot overrule it.
   - Shape the prompt on the old positions (stage A and the diagnostic) only, then freeze it before the exam is
     scored. Record the cost per decision.
3. **Comparison (Wed-Thu).**
   - Score km3, kx3 and the judge on the same exam positions (paired): agreement with his move or an acceptable
     move, by kind and by deck.
   - Report the judge-minus-kx3 difference with an uncertainty interval that treats positions from the same game as
     one cluster (for example, a game-level bootstrap).
   - The judge "helps" only if that interval sits above zero. If it straddles zero, the result is **inconclusive**,
     not a win.
   - Running the judge twice checks its consistency only; it does not show it is better.
4. **Finished games (Thu-Sat), only if step 3 clears the bar.**
   - Before any game, write down three things: when the judge is consulted (which decision points), who plays the
     remaining moves (frozen kx3), and what result would justify expansion.
   - Compare the judge-assisted pilot with **frozen kx3 on the same fresh deals** (a registered seed block), in both
     seats, against both opponent policies, and record the cost.
   - A few wins alone do not show improvement.
5. **Decision rule (set now, before results).**
   - Expand only if better decisions carry into finished games, against a matching baseline, at a cost he finds
     acceptable.
   - An unclear result is reported as inconclusive.
   - Otherwise: a maintenance period, upstream help, and waiting for the maintainer's AI.
   - The AI judge is a hypothesis to test, not an assumed improvement.

**Deliverable for next Sunday's review:** a runnable comparison with its decisions, the uncertainty, finished-game
evidence if step 4 ran, and measured cost. Not another design document.

**Rough cost:** about 3-5% of the weekly meter, $10-30 of API credits (they expire Oct 28), a few laptop hours (his
laptop stops at noon on school days unless he says otherwise), and a few minutes of his time on ambiguous labels.

## Side work this week (no new experiments)

- Respond to review comments on PRs #421-#426.
- Teach tools/battle_logs_cleanup.py the new video-archive lookup before more videos are archived.
- Watch for the maintainer's AI. Check upstream's external-bot interface (docs/bot-protocol.md) so a comparison can be
  run quickly when it is available.
