# Claude-side weekly review, 2026-11-01

Written Sunday evening, Nov 1. Main is at 84dc7f17. This week's folder `rl/results/weekly_review_2026-11-01/` did not land on main, so there was no EVIDENCE, OUTSIDE_IDEAS, COMPETITIONS or DIAGNOSTIC file to read. Instead I used memory, the main log, the Gemini test's results file (on its test branch, commit 17d429e8) and upstream's PR list. The weekly meter stood at 80% before this review.

**Amended Nov 1, twice, after Dustin's read:**
1. The next step changed (see the verdict).
2. Section C now holds the outside research I should have done the first time. Astra's review prompted it, and three of Astra's corrections are adopted in sections B, C and the next step.

## A. Are we making progress?

**Yes, and this time the bot can do something it couldn't last week.**

- **An AI pilot beat our best bot on two of your decks, in whole games.** Gemini made the decisions in one copy of each game and kx3 made them in a matched copy. Over 128 matched games, Gemini won 73 and kx3 won 56. That passed the bar we set before the test (+0.13 per game; the true gain could be anywhere from +0.04 to +0.23).
  - It's the first win for a better pilot in full games on your decks, not just single positions.
  - **Limits:**
    - The opponents were bots.
    - There were only 2 opponent lists.
    - It ran on the older engine.
    - kx3 still chose the opening setup in both copies.
    - Almost all of the gain came from the Archaludon deck (+0.25). On Manectric the two pilots came out even (40 v 39).
  - **Cost:** about $0.50 and 12 minutes per game. The whole test came to about $71 in Google credits plus $12 in Claude credits.
- **We now know two concrete kx3 habits that cost games.** Reading the 24 Archaludon games where the results differed showed that kx3 plays Copycat too early and builds up the Pokémon in the Active Spot. Neither habit is fixed yet.
- **Engine:** the Dual Fusion cards went in on Oct 28 (205 of 260 new printings). The other 55 are in R8, which is still local and not adopted.
- **Upstream (secondary):** #433 and #438 merged, and #441 is open with its checks green. Those are your C1 card batches. Every deckgym user, including the maintainer's future AI, now plays them by the real rules.
- **The most useful thing for you this week wasn't the bot.** It was the play-and-adjust loop on your decks:
  - 01 v2 went 8-2 and was kept;
  - Raboot went 3-7 and was dropped;
  - the sleep deck went 5-4, and your Igglybuff idea became v3.

## B. Is the bot the right way?

**Keep the engine. Change the pilot.** This week's result is the first hard evidence on the question: our search pilot is beaten by a general AI that reads the board and plans the turn.

- **Gemini as the pilot:** it is strong enough to matter, but too slow and costly to run thousands of games.
  - The Google credits run out around Dec 1, and the price doubles after Nov 30.
  - So don't build on it long term, and don't make up tests just to spend the credits (Dustin, Nov 1: "I don't really care what we do with the gemini credits").
- **The serious long-run answer is a small learned pilot, and the outside evidence now says so clearly** (section C).
  - It isn't something one laptop can train.
  - The maintainer's generalist model is the realistic way to get one. But nothing has been released (upstream's code hasn't changed since Oct 28), so "free to run" and "easy to plug in" are hopes, not facts. That's Astra's correction, and I agree.
- **What I'd stop:** open-ended tuning of our own pilot. The one exception is a narrow repair where the games showed it losing.

## C. Outside ideas

Researched on Nov 1, after Dustin asked. Each idea below names its source and one cheap way to check it here.

**1. Bot deck rankings partly measure the pilot, not the deck. The field also shifts week to week.**
- **Source:** a 66th-place team in the Kaggle Pokémon TCG AI Battle Challenge (the main TCG, not Pocket; ran Jun-Aug 2026; 6,807 teams).
  - Across 64,200 games, a deck's strength in other teams' hands and in theirs had a rank correlation of **−0.24**.
  - Within one week, one archetype's share of the field fell from 11.1% to 1.6%.
  - They chose decks by win rate against a **field weighted by how often each deck appears**.
- **What it means for you:** this is outside backing for both your doubt about bot deck tests and your point about the decks you actually meet.
- **Cheap check:** count the opponents in your Pause Games logs and see whether any deck is a big share of what you face. It's free, takes under 1% of the meter, and tells us whether tuning for one matchup could ever pay off for you.

**2. The strong card-game AIs are small networks trained by playing themselves, not search bots.**
- **The evidence:**
  - **Kaggle 1st place:** a 2.24M-parameter network trained by self-play reinforcement learning on 4 top-end gaming graphics cards. Search "didn't sufficiently benefit" it. Its deck work changed fewer than 4 cards at a time, tested with 256-512 games per pair, and the author says ~100 games against an opponent is too few (500+ needed).
  - **Kaggle 15th place:** 5.5 billion training decisions, about 5 days on one gaming graphics card plus many processor cores. No search at play time, and no card-specific hand fixes.
  - **The official TCG Pocket AI** (DeNA's talk at CEDEC, Jul 24, 2026): a ~2M-parameter network, 50 million training games per model on six 32-core cloud machines. Cards are described by their features, with the opponent's hidden cards masked. Search trees were rejected because of the hidden information.
- **What it means for you:** our September RL failed with card-number networks, and these all describe cards by features. That's the missing piece we already suspected. But the compute is far beyond one laptop, which is the strongest argument for helping the maintainer's model rather than building our own.
- **Cheap check:** one Discord message from you asking whether his model will be shared and what would help him test it. Offer your filmed positions and off-meta decks as a test set. Cost: nothing but the message.
- **To watch:** the 1st-place code comes out after the competition's second round (late 2026 or later).

**3. For an AI-model pilot like Gemini, the setup around the model matters more than features like "learning from experience".**
- **Source:** PTCG-Bench (EMNLP 2026 Findings), which tested ten AI models on the main Pokémon TCG.
  - Removing the legal-move list, the game history and the structured board cost up to 151 rating points.
  - Five "learn from experience" add-ons (memory, reflection and the like) gave no reliable gain.
  - Bigger models usually beat their cheaper versions, but strength and price didn't line up neatly.
- **What it means for you:** our Gemini setup already has the parts that mattered. Don't pay for memory or reflection add-ons.
- **Cheap check:** only if Gemini is used again after Dec 1, run a cheaper model on stage 1's 16 deals (stage 1 cost $7.59 on the current model) to see whether it holds up.

**4. Searching across the possible hidden hands (Astra's suggestion; OpenSpiel has a lightly tested version).**
- Ideas 2's sources lean against search: the Kaggle winners and DeNA found it didn't help, or didn't fit hidden cards.
- So keep it only as a fallback if the kx3 repair fails, and try it on saved positions first, not as an engine rewrite.

**Not viable now:** training a small pilot to copy Gemini's choices. Stage 2 gave about 1,300 Gemini decisions. The 66th-place team needed 2.61M replay decisions just for its head start, before self-play.

## D. Is this asinine for a student with one laptop?

**No, but the research makes the limits clearer.**

- **What one laptop can do:**
  - follow the real rules (engine fixes, which help everyone upstream);
  - read your games;
  - make careful, targeted bot repairs;
  - run small, paid AI-pilot experiments.
- **What it can't do:** train the kind of pilot that wins competitions. That takes days of high-end graphics cards or many cloud machines.
- **The honest risk:** the strong pilot we can use today costs about $0.50 a game. After Dec 1 that becomes real money, and the price doubles. If the maintainer's model doesn't arrive, the bot side may shrink back to engine fixes plus reading your games. That's a reasonable size for one laptop, not a failure.

## Verdict: CONTINUE

**Next step (amended Nov 1, with Astra's diagnosis-first correction):** find out where kx3 loses the useful plan in the 24 Archaludon games, then make the smallest fix that diagnosis supports.

- **The question:** in each game, was the good move missing from kx3's short list of candidates, or was it on the list but scored low because the simulated rest of the game mishandled the plan?
- **What we won't do:** blanket rules like "always draw first", and card-specific patches.
- **How we'll check it:**
  - The 24 games become practice examples once they guide the fix.
  - The other 104 games are only a check that nothing got worse; they don't confirm the fix.
  - A real gain has to show up on fresh deals and other decks before we call the bot better.
- **Rough cost:**
  - about 3% of the weekly meter;
  - no Google money and no API credits;
  - one or two laptop nights, after R8's builds finish.

**Why the first draft's step was dropped:** it was a Gemini test of sleep deck v2 against v3, and so was the one-matchup version we talked about next. Dustin, Nov 1: "If I make a deck better against it, but worse against the other 90% of decks I face, I lose overall ground."

- A swap is only worth making if it helps across the decks you actually face, counted by how often you face each one.
- The test's two made-up opponents can't show that, and neither can a single matchup.
- On top of that, how well Gemini plays depends on the deck, which adds another unknown.
- So deck questions stay with your own 10-game loop. No deck test with a bot is planned.

## Sources (checked Nov 1)

- **Kaggle 1st place (Simulation track), "Aim to Be a Pokémon Master":** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1784257142000
- **Kaggle 15th place:** https://www.kaggle.com/c/pokemon-tcg-ai-battle/writeups/15th-place-solution
- **Kaggle 66th place, "Who's That pokepilot?":** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/writeups/whos-that-pokepilot
- **Competition and second-round timing:** https://ptcg-abc.pokemon.co.jp/?lang=en
- **The 1st-place code** (to be released after round 2): https://github.com/yijieyuan/kaggle-pokemon-tcg
- **DeNA's official TCG Pocket AI talk (CEDEC 2026):** https://www.invenglobal.com/articles/24133/how-reinforcement-learning-ai-tackles-the-complex-rules-of-pok%C3%A9mon-trading-card-game-pocket
- **PTCG-Bench:** https://arxiv.org/html/2605.29653v1 and https://github.com/zjunet/PTCG-Bench
