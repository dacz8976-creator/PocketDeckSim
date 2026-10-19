# Plan for the week of Oct 19, 2026 (both reviews combined)

Written by the coordinator on Oct 18 evening, from the Claude-side review (CLAUDE_REVIEW.md) and Astra's review plus
its follow-up note (ASTRA_REVIEW.md), on Dustin's word: "combine the reviews and develop a plan before the reset".

## Where the two reviews agree

- **Verdict: REDIRECT.** No new bot capability was shown this week. Stop adding hand-made scoring bonuses to the pilot.
- **The finding:** in the diagnostic's positions, the bot generates his moves but scores them lower. The scoring favours
  "attack as soon as possible" over getting a Pokémon ready for a later turn.
- **One bounded experiment this week:** test whether an AI model judges these plan decisions better, on positions no
  bot was developed on, judged against his own choices.
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
- **Context from the Claude review:** in his 4 Kingambit losses, Kingambit never reached play (deck and luck, not
  piloting). So the exam must cover more than Kingambit.

## The experiment: an unseen-positions exam, then an AI plan judge

1. **Exam (Mon-Tue).**
   - Take 40-60 decision points from his recorded ladder games that no bot was developed on: not stage A, the
     diagnostic or the pause-game sets.
   - Use more than one deck. Cover all four kinds of right answer: prepare, sacrifice, attack now, and abandon the
     plan. Include positions where both bots agree.
   - The default label is his recorded move. Agents list other acceptable moves, each with a reason. He rules only
     on the genuinely ambiguous ones, a handful.
   - Labels are committed before any bot runs. If fewer than 40 usable points exist, say so rather than pad.
2. **AI plan judge (Tue-Wed).**
   - Input: the visible position (hidden cards masked), exact card text, and the legal whole-turn plans with their
     immediate results from the engine. Output: the model picks one plan. km3 cannot overrule it.
   - Shape the prompt on the old positions (stage A and the diagnostic) only, then freeze it before the exam is
     scored. Record the cost per decision.
3. **Comparison (Wed-Thu).**
   - Run km3, kx3 and the judge on the exam: agreement with his move or an acceptable move, by kind and by deck.
   - Run the judge twice to measure its run-to-run wobble.
   - It "helps" only if it beats kx3 by more than its own wobble.
4. **Finished games (Thu-Sat), only if step 3 clears the bar.**
   - Use the judge only at plan-choice points (not every move, to keep cost down).
   - Play a small number of games against two different opponent policies, and record cost and results.
5. **Decision rule (set now, before results).**
   - Expand only if better decisions carry into finished games at a cost he finds acceptable.
   - Otherwise: a maintenance period, upstream help, and waiting for the maintainer's AI.
   - The AI judge is a hypothesis to test, not an assumed improvement.

**Deliverable for next Sunday's review:** a runnable comparison with its decisions, finished-game evidence if step 4
ran, and measured cost. Not another design document.

**Rough cost:** about 3-5% of the weekly meter, $10-30 of API credits (they expire Oct 28), a few laptop hours (his
laptop stops at noon on school days unless he says otherwise), and a few minutes of his time on ambiguous labels.

## Side work this week (no new experiments)

- Respond to review comments on PRs #421-#426.
- Teach tools/battle_logs_cleanup.py the new video-archive lookup before more videos are archived.
- Watch for the maintainer's AI. Check upstream's external-bot interface (docs/bot-protocol.md) so a comparison can be
  run quickly when it is available.
