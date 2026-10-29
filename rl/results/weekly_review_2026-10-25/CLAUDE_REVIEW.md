# Claude-side weekly review, Oct 25 (for Monday Oct 26)

Weekly meter at the start of this review: 79% used (resets Mon 12:00Z). Last Sunday it was 92% at the same point, so about a fifth of this week's usage goes unspent. This review took about 2%.

Note on sources: this week's evidence folder (EVIDENCE.md, OUTSIDE_IDEAS.md, COMPETITIONS.md) did not land on main or on any branch; the coordinator spent the week on exam run 3. This review is built from main (tip b78c8997, no commits since Oct 22), the exam branch's aggregate result files, the upstream repository checked tonight, and the project memory. I did not contact Astra.

## A. Are we making progress?
**On what the bot can do: no.** The pilot (km3/kx3) is unchanged. The engine was re-pinned Oct 21 with rules corrections (an attack cut to 0 gets no Weakness, a hit back counts as attack damage, four upstream fixes). That changed the bot's play in exactly two floor rows (brews 07 and 09 against two opponents) and nothing else. Tests, the Dual Fusion branch, 258 new exam points and the run 3 kit are activity, not progress.

Real but secondary:
- **Upstream: all 23 of our pull requests are merged**, the last six (#421-#426) between Oct 18 and 21. The simulator the community uses now follows those rules, and our fork took four of upstream's fixes back. It does not make any bot play better.
- **One new fact about outside AI:** run 2 (Oct 21) had Gemini 4 Argon, with no tuning, pick your first move segment on 30 of 49 decisions; km3 did on 22. That is not a pass (the interval includes 0), but it is the first time anything beat our bot at "what would Dustin do", and it cost $5.64. The Sonnet judge in run 1 did worse than km3 (11 of 49).
- **Run 3 is armed for tonight (02:00Z):** 258 decisions from 76 of your games played Oct 17-25, labels frozen before any bot ran. Pooled with run 2 under a stricter bar, it decides this question. The number lands after this review.

## B. Is the bot built the right way?
The engine, the exam and the evidence are worth keeping. The hand-tuned pilot is not worth improving further: last week's diagnostic said its scoring is the problem, and this week an untuned outside model matched your choices more often than it did. Two honest limits on that: run 2 was inconclusive, and a Gemini decision costs about 6 cents, so a full game for one side is roughly 60-90 cents. That is fine for a second opinion on a position or a 20-40 game paired swap test ($15-40), and useless for thousands of games.

The maintainer's generalist reinforcement-learning AI is still not public (upstream's commits this week are an MCTS rewrite and rules fixes; no model). Upstream's new MCTS sees the opponent's hand and deck order, so it is not a fair comparison until it is masked. Upstream's bot-protocol document exists, which is the door for any outside bot, including the maintainer's when it arrives.

My view: km3 stays as the cheap baseline and opponent. The pilot's replacement is either a model as plan chooser (if run 3 passes) or the maintainer's AI through bot-protocol (when it exists). Don't tune km3, and don't start our own learning.

## C. Outside ideas, each with one cheap comparison
Only things someone on the project actually looked at (landing pages read Oct 21; upstream repo read tonight).
1. **Oakalytics Deck Lab** (AI v AI against a meta snapshot; an "AI training sim"). Comparison: you play 3-5 games against its CPU with brew 07 and judge its play; then run Deck Lab on brew 07 as is and with the X Speed swap. Your time only, about an hour. If its AI plays sensibly, that is the deck tester you wanted, built by someone else, and our bot work narrows to rules fidelity and upstream.
2. **Upstream's bot-protocol** (checked: docs/bot-protocol.md exists). Comparison: the smallest adapter with a dummy policy on development positions only, about $10 and one laptop night. It only pays off once there is a bot worth plugging in, which is why I make it conditional below.
3. **PTCG Lab's consistency tool** (opening hands only, no attacks). Comparison: one Muk list, its one-Basic-opening rate against our setup tester's. Twenty minutes of your time. Agreement validates our tester against an outside tool; disagreement means one of them is wrong.
4. **TCGmini sandbox** (any board state, online play). Use: set up shot-list situations before recording in the real app. Minutes. Not rules evidence.
5. Information-set search (ISMCTS) and OpenSpiel: reference only, no comparison worth its cost now.

## D. Is this asinine and impossible for a student with one laptop?
A generalist bot that plays every deck like you: not from this laptop, and nobody has one for Pocket yet. A trustworthy second opinion on your own decisions, measured against your own labelled games: plausible, and this week shows it costs dollars, not GPUs. What is out of proportion is the scaffolding, not the goal: by the advisor's count, 378 commits on main in one week, 128 mailbox messages in six days, and a 52-72 ladder season across 20 deck versions, only three of which got 13 or more games. The project is now a measurement bench plus a rules contributor. That is doable on one laptop. The part that is not sustainable is you coordinating a swarm around it during a school term. Scaling to "exam, upstream, and whichever outside bot tests best" is a sound shape, not a retreat.

## Verdict: LOW-COST MAINTENANCE WEEK
Run 3 reads itself tonight at no new cost. Dual Fusion lands Wednesday evening, and without the prepared branch the simulator cannot read any game you play from Thursday on. Nothing else should start before that number and that release are in.

## One next step for the coming week
**Dual Fusion release night (Wed Oct 28): take the new card data on the prepared branch, refresh the QR catalog, adopt only on your word.** Cost: about 5% of the meter, no API credits, two laptop nights. Then, if run 3 passes its registered rule, the one question to put to you is the bot-protocol adapter ($10 plus a night) so the judge can play whole games against kx3 on the same deals. If run 3 does not pass, the week stays maintenance and upstream, and the Oakalytics check above is the cheapest thing you could do yourself.
