# Claude-side weekly review, Monday Oct 26

This is the Monday follow-up to last night's review (Oct 25, main 10895032). Everything there still holds; this page adds the one fact that landed after it, exam run 3, and changes the verdict because of it.

Weekly meter at the start of this review: 91% used, about an hour before the reset. Last week's review ran at 79%, so the week's usage was spent as you asked. This review took about 2%.

Sources: main at 44d51ebd (the only commits since last night are the containment rule in START_HERE), the exam branch's RESULTS_run3.md, the upstream repository checked this morning, and project memory. No EVIDENCE.md, OUTSIDE_IDEAS.md or COMPETITIONS.md was written this week. I did not contact Astra.

## A. Are we making progress?

**Our bot (km3/kx3): no.** It plays exactly as it did last Monday. The engine re-pin on Oct 21 was a rules correction, not a playing improvement.

**One real, measured step in the direction we turned to last week.** Run 3 ran overnight (02:00-06:39Z) exactly as registered on Oct 21, before any of its games existed:

- 258 decisions from 76 ranked games you played Oct 17-25, labelled before any bot ran, with your own answers to 23 questions folded in.
- Gemini 4 Argon, untuned, with the prompt frozen since Oct 20, matched your first move segment on 62% of them. km3 matched on 45%.
- Pooled with run 2 (the registered primary, stricter 97.5% bar): Gemini ahead by +0.17, interval +0.09 to +0.25, chance of a fluke about 3 in 100,000. Run 3 alone, at run 2's own rule: +0.17, interval +0.10 to +0.25. Both pass. The gap shows in every deck kind and every answer kind, largest on "prepare" decisions, smallest on fast pressure.
- Cost: about $23.50 of your Google credits (an estimate from token counts; check the billing page). Zero failed answers.

What that does and does not mean, plainly: for the first time something picks your moves more often than our bot, on fresh games, under a test fixed in advance. It is agreement with what you played, not proof the moves were good. It has not played a single whole game. By the registration, nobody may say it beats kx3 until kx3 is tested the same way. The sensitivity repeat did not finish (one Google rate-limit refusal), so we have one measurement, not two.

**Upstream:** no new commits since Oct 21, nothing new of ours to merge (all 23 merged), and no reply yet to our dual-type proposal on issue 429. The maintainer's reinforcement-learning AI is still not public.

## B. Is the bot built the right way?

Last week I said the hand-tuned pilot is not worth improving and that its replacement is either a model as plan chooser or the maintainer's AI. Run 3 turns the first of those from a hypothesis into evidence. So: keep the engine, the exam and km3 as the cheap baseline and opponent; do not tune the pilot further; do not start our own learning. The open question is no longer "does a model pick like Dustin" but "does picking like Dustin win games", and that needs the model to play whole games against kx3 on the same deals, which it cannot do yet. A Gemini decision costs about 5 cents, so one side of one game is roughly 50 cents to a dollar: fine for a 20-40 game paired swap test, useless for thousands of games. Upstream's new MCTS sees the opponent's hand, so it is not a fair comparison until masked.

## C. Outside ideas, each with one cheap comparison

Only things someone on the project actually looked at.

1. **Upstream's bot-protocol** (docs/bot-protocol.md, checked this morning): the door for any outside bot. Comparison: the smallest adapter with a dummy policy on development positions only, then Gemini playing 10 finished games against kx3 on the same deals, both seats. About $10 of API credits plus one laptop night for the adapter; roughly $10-20 of Google credits for the games. This is the next step below.
2. **Oakalytics Deck Lab** (landing page read Oct 21): AI v AI against a meta snapshot. Comparison: you play 3-5 games against its CPU with brew 07 and judge its play. An hour of your time, nothing else. If it plays sensibly, it already is the deck tester you asked for.
3. **PTCG Lab consistency tool**: one Muk list, its one-Basic-opening rate against our setup tester. Twenty minutes.
4. **The maintainer's AI**: nothing to compare until it ships; watch issue 429 and his posts.

## D. Is this asinine and impossible for a student with one laptop?

Not on this week's evidence. The measurement bench you built (your recordings, your labels, a frozen test) just produced a clean answer for about $24, no GPU, one laptop night. That is exactly the scale a student can run. What remains out of proportion is the coordination around it: six credit-worker jobs whose actual cost nobody can read from the logs (only caps, up to about $180 in total), two sessions and an advisor trading dozens of notes per day, and 90 ranked games recorded and reviewed in nine days during a school term. The goal is sound. The swarm is the part to keep shrinking. Stopping is not warranted this week; scaling the process down still is.

## Verdict: CONTINUE

Last night's maintenance verdict was conditional on run 3. It passed, so the week has one earned experiment. Dual Fusion release night (Wed Oct 28, prepared branch, adoption only on your word) proceeds as already planned and is not the new step.

## One next step for the coming week

**Build the smallest bot-protocol adapter and let the Gemini judge play 10 finished games against kx3 on the same deals, both seats, on development positions only, never exam material.** Rough cost: about 3% of the weekly meter, about $10 of API credits for the adapter and $10-20 of Google credits for the games, one laptop night. The question it answers: does agreeing with you more often turn into winning more games? If yes, the next thing is a paired swap test on a deck you name. If no, the judge stays a per-position second opinion and the week after is maintenance and upstream.
