# Claude-side weekly review, Monday Oct 26

**Amended the same day after Astra's read (Dustin passed it on).** What changed: the game-date wording in A (about 24 of the 90 games were already recorded, unused, when the test was registered on Oct 21); the chance wording in A; the ten-game step no longer decides anything, it measures; the outside-tool lines are toned down; the cost figures are marked as the guesses they are; and the next step now puts the kx3 comparison first, because our own registration requires it before anyone says "beats our best bot" and it needs no Gemini calls. The verdict is unchanged.

This is the Monday follow-up to last night's review (Oct 25, main 10895032). Everything there still holds; this page adds the one fact that landed after it, exam run 3, and changes the verdict because of it.

Weekly meter at the start of this review: 91% used, about an hour before the reset. Last week's review ran at 79%, so the week's usage was spent as you asked. This review took about 2%.

Sources: main at 44d51ebd (the only commits since last night are the containment rule in START_HERE), the exam branch's RESULTS_run3.md, the upstream repository checked this morning, and project memory. No EVIDENCE.md, OUTSIDE_IDEAS.md or COMPETITIONS.md was written this week. I did not contact Astra.

## A. Are we making progress?

**Our bot (km3/kx3): no.** It plays exactly as it did last Monday. The engine re-pin on Oct 21 was a rules correction, not a playing improvement.

**One real, measured step in the direction we turned to last week.** Run 3 ran overnight (02:00-06:39Z) as registered on Oct 21. About 24 of its 90 games had already been recorded by then but never opened or labelled; the rest were played after. The labels and your answers were frozen before any bot ran.

- 258 decisions from 76 ranked games you played Oct 17-25, with your own answers to 23 questions folded in.
- Gemini 4 Argon, untuned, with the prompt frozen since Oct 20, matched your first move segment on 62% of them. km3 matched on 45%.
- Pooled with run 2 (the registered primary, stricter 97.5% bar): Gemini ahead by +0.17, interval +0.09 to +0.25. Run 3 alone, at run 2's own rule: +0.17, interval +0.10 to +0.25. Both pass. If the two were truly equal, a gap this large would show up in about 3 of 100,000 random re-labellings; that is what the p-value says, and no more. The gap shows in every deck kind and every answer kind, largest on "prepare" decisions, smallest on fast pressure.
- Cost: about $23.50 of your Google credits for the judge calls (an estimate from token counts; check the billing page). The preparation jobs on Claude credits are a separate, unmeasured cost (only caps are known). Zero failed answers.

What that does and does not mean, plainly: for the first time something picks your moves more often than our bot, on fresh games, under a test fixed in advance. It is agreement with what you played, not proof the moves were good. It has not played a single whole game. By the registration, nobody may say it beats kx3 until kx3 is tested the same way. The sensitivity repeat did not finish (one Google rate-limit refusal), so we have one measurement, not two.

**Upstream:** no new commits since Oct 21, nothing new of ours to merge (all 23 merged), and no reply yet to our dual-type proposal on issue 429. The maintainer's reinforcement-learning AI is still not public.

## B. Is the bot built the right way?

Last week I said the hand-tuned pilot is not worth improving and that its replacement is either a model as plan chooser or the maintainer's AI. Run 3 turns the first of those from a hypothesis into evidence against km3. Against kx3, our strongest pilot, it is untested. So: keep the engine, the exam and km3 as the cheap baseline and opponent; do not tune the pilot further; do not start our own learning. The open question is no longer "does a model pick like Dustin" but "does picking like Dustin win games", and that needs the model to play whole games against our pilot across different opponents, which it cannot do yet. A Gemini decision cost about 5 cents in run 3; a whole game needs an unknown number of calls per turn (it must be asked again after every draw, coin and opponent choice), so the per-game cost is a guess until measured. Whatever it is, it suits a small paired test, not thousands of games. Upstream's new MCTS sees the opponent's hand, so it is not a fair comparison until masked.

## C. Outside ideas, each with one cheap comparison

Only things someone on the project actually looked at.

1. **Upstream's bot-protocol** (docs/bot-protocol.md, checked this morning): the door for any outside bot. Comparison: the smallest adapter with a dummy policy on development positions only, checked for executing choices correctly, re-asking after draws and coins, and respecting hidden information. About $10 of API credits plus one laptop night, a guess.
2. **Oakalytics Deck Lab** (landing page read Oct 21): AI v AI against a meta snapshot. Comparison: you play 3-5 games against its CPU with brew 07 and judge its play. An hour of your time. Sensible play would make it worth a closer look, not make it trustworthy swap advice.
3. **PTCG Lab consistency tool** (opening hands only; it has its own redraw rules and opening-hand scores): one Muk list, its one-Basic-opening rate against our setup tester, after matching the assumptions. Twenty minutes, plus the matching.
4. **The maintainer's AI**: nothing to compare until it ships; watch issue 429 and his posts.

## D. Is this asinine and impossible for a student with one laptop?

Not on this week's evidence. The measurement bench you built (your recordings, your labels, a frozen test) just produced a clean answer for about $24 of judge calls, no GPU, one laptop night. That is exactly the scale a student can run. What remains out of proportion is the coordination around it: six credit-worker jobs whose actual cost nobody can read from the logs (only caps, up to about $180 in total), two sessions and an advisor trading dozens of notes per day, and 90 ranked games recorded and reviewed in nine days during a school term. The goal is sound. The swarm is the part to keep shrinking. Stopping is not warranted this week; scaling the process down still is.

## Verdict: CONTINUE

Last night's maintenance verdict was conditional on run 3. It passed, so the week has one earned experiment. Dual Fusion release night (Wed Oct 28, prepared branch, adoption only on your word) proceeds as already planned and is not the new step.

## One next step for the coming week

**Score unchanged kx3 on the same frozen exam, reusing Gemini's saved answers, so no new Gemini calls.** This is what our own registration demands before anyone says the judge beats our best bot, and it costs laptop time only: kx3 cannot run in the frozen baseline program, so the laptop runs it on its own program, one night (the Oct 19 probe put three seeds on 51 points at about 4.4 hours; 258 points fits one night at one seed, two nights at three), with the engine and label differences written down in a dated record before any row is produced. Run 3's verdict stays as filed. About 2% of the meter, no credits.

Then, in order, and only if kx3 does not match or beat Gemini on the exam: the smallest bot-protocol adapter on development positions with a dummy bot (checks above), then a handful of paid whole games to measure actual calls, cost and playing behaviour. Those games test whether the connection works and what it costs. They do not decide whether Gemini wins or whether deck testing starts; a fair comparison against our pilot across different opponents comes later, if the measured cost allows.
