# Claude-side weekly review, Oct 18 (for Monday Oct 19)

Weekly meter at the end of this review: 92% used (resets Mon 12:00Z). This review took about 1% by itself.

## A. Are we making progress?
**Not on what the bot can do.** Nothing new was demonstrated this week. The Kingambit pilot tests (stage A) failed their bar: 2 of 12 right, the bar was 6. Tests, documents, game counts and the new diagnostic don't count as progress.

What did change, and it is real but secondary:
- **Upstream engine fixes: 17 of our pull requests are now merged** in bcollazo's simulator (#335, #383, #403-#417). Batch 3 (#421-#426) opened tonight and is waiting. What it changes for you: the simulator everyone uses follows more card rules correctly, and the maintainer trusts our fixes (he merged batches within hours). It does not yet make any bot play better.
- **One useful finding:** the diagnostic says the bot *does* see your moves in all 14 missed positions. It just scores them lower, because its scoring rewards "whatever can attack soonest" and ignores "get a Benched Pokémon ready for a later turn". Looking deeper (depth 5 to 8) never picked your move. So the problem is the scoring, not the searching. That is the first clear answer we have had on *why*.
- **Another finding worth sitting with:** in your 4 Kingambit losses, Kingambit never reached play (no Rare Candy, Copycat shuffled it away, Pawniard sniped). In the 4 wins it was never knocked out. So for that deck the main loss cause is *getting it out*, which is a deck-build and luck question, not a piloting one. A better pilot would not have fixed those four losses.

## B. Is the bot built the right way?
Partly. Search plus a hand-written score is the proven small-team design, so I would keep the engine, the search and the evidence. What isn't working is the *way we improve it*: one hand-added plan term per named failure. The diagnostic confirms that: each missed position needs a different "get ready for later" credit, and 14 positions from 8 games are too few to tell a good general fix from one that just memorizes them.
- **Learned part vs. our own pilot:** the maintainer is building one generalist AI that plays every card, trained by reinforcement learning, results "soon". The Kaggle winners used small learned policies (2 to 4 million parameters), but trained on 4 to 8 high-end GPUs for days. We can't copy that on a laptop. The realistic role for us is *helper*: rules fixes (wrong rules teach a learner wrong habits), your labelled real-game positions as a "plays like a person" test, and your off-meta decks as the hard case a generalist may fail on.
- **My view:** stop building our own pilot further until there is an exam of unseen positions. Keep helping upstream. Don't start our own RL.

## C. Outside ideas, each with one cheap comparison
I only list what the repo's checked files support (sources verified on the web Oct 16, and the competitions file read in a browser).
1. **Ask an AI model for a second opinion on positions** (not as the pilot: it would cost several dollars a game). Compare its agreement with *your* move against km3's and kx3's on 100-150 positions it never saw. About $10-30 of credits. Helps only if it beats kx3 by more than its own run-to-run wobble.
2. **A "what you would do" tie-breaker learned from your recorded games**, tested on whole held-out games. No credits, a few laptop hours. Fails if you haven't recorded enough games (we haven't counted).
3. **Competition ideas** (done; read COMPETITIONS.md): nothing can be plugged into our bot, since all of it is for the physical game or other games. One idea is worth a look: score a move *together with where its follow-up choices land*. The diagnostic already says that wouldn't fix your cases (the payoff is several turns away), so I would not do it first.
4. **Maintainer's deeper search** (his tip): already tested in the diagnostic. It didn't help. Done.

## D. Is this asinine and impossible for a student with one laptop?
**Not impossible, but part of it is.** A bot that plays any deck exactly like you, with multi-turn plans: nobody has shown that for Pocket, and the groups trying have GPUs and teams. Don't count on getting it from this laptop. What is realistic is (a) the cheap tools that already help you (setup odds, deck journal, ladder notes), (b) being the person who fixes rules and supplies real-game test positions to the community effort, and (c) waiting for the maintainer's AI and testing it on your decks. Scaling down to that is a sound plan, not a failure, and it keeps the door open as the technology improves. It would be wrong to claim today that the bot "tests and hones decks" for you: it can't yet, and the Kingambit result is the evidence.

## Verdict: REDIRECT
Stop adding plan terms to the pilot. Spend the week on a test of unseen positions, and on cheap ways to see if an outside tool (an AI second opinion, or the maintainer's AI) beats our pilot on it.

## One next step for the coming week
**Build the unseen-positions exam, then run the AI-second-opinion comparison on it.**
- Take about 40-60 decision points from your ladder games that were *not* used to develop any bot (including some where waiting is right and some where attacking now is right, and some where km3 and kx3 agree but play badly). You label your move and what other moves would be acceptable *before* anyone runs a bot. Ambiguous ones are the only things asked of you, kept to a handful.
- Run km3, kx3 and an AI model's second opinion on them once, report agreement in plain words.
- Cost: about 3-5% of the weekly meter, roughly $10-20 of the API credits (which expire Oct 28 anyway), a few laptop hours; a few minutes of your time on the ambiguous ones.
- If the AI second opinion doesn't beat kx3, the week's answer is maintenance plus upstream help, and we wait for the maintainer's AI.
- Caveat: a bot-score test only tells us something if it's judged against *your* choices, which is why the labels come first.
