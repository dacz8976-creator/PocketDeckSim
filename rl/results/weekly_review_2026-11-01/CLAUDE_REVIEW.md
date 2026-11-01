# Claude-side weekly review, 2026-11-01

Written Sunday evening, Nov 1. Main is at 84dc7f17. This week's folder `rl/results/weekly_review_2026-11-01/` did not land on main, so there was no EVIDENCE, OUTSIDE_IDEAS, COMPETITIONS or DIAGNOSTIC file to read. Instead I used memory, the main log, the Gemini test's results file (on its test branch, commit 17d429e8) and upstream's PR list. The weekly meter stood at 80% before this review.

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
- **The maintainer's generalist reinforcement-learning AI:** still the best long-run answer, since it would be free to run and built for every card. Upstream's code hasn't changed since Oct 28, and I found nothing public to test. I didn't check Discord or X.
- **What I'd stop:** more tuning of our own pilot, beyond the two habit fixes the games pointed to.

## C. Outside ideas worth a cheap check

This week's outside-ideas file didn't land, and I didn't do new outside research. Two ideas from sources I checked earlier:

1. **The maintainer's generalist AI, when it's released.**
   - **Check:** run it on the same 128 matched deals against kx3.
   - **Cost:** no Google money, about one laptop night.
2. **Upstream's deeper search setting** (the maintainer's own advice: depth up to 8).
   - **Catch:** it sees the opponent's hidden cards, so it's only a fair comparison once that's masked.
   - **Check:** the 24 Archaludon split games. Does it avoid kx3's two habits?
   - **Cost:** about one laptop night.

## D. Is this asinine for a student with one laptop?

**No. It isn't impossible, but it does depend on the free credits running out.**

- **This week, in plain terms:**
  - an AI pilot measurably beat our bot on your deck;
  - your card fixes went into the shared simulator, and the maintainer's answer was "Yes please!";
  - you have a working loop of decks you play and we adjust.
- **The honest risk:** the strong pilot costs about $0.50 a game. After Dec 1 that becomes real money, and the price doubles.
  - If the maintainer's AI doesn't arrive, the bot side may have to shrink back to engine fixes plus reading your games.
  - That's a reasonable size for one laptop, not a failure.

## Verdict: CONTINUE

**Next step (amended Nov 1 after talking with Dustin):** fix kx3's two habits that the Archaludon games showed: playing Copycat too early, and powering up whatever Pokémon is in the Active Spot.

- **The check:** in the 24 Archaludon games where the results split, do the fixed bot's choices improve, without its results on the other 104 test games getting worse?
- **Rough cost:**
  - about 2-3% of the weekly meter;
  - no Google money and no API credits;
  - one laptop night, after R8's builds finish.
- **What it buys:** a better bot for every deck. It does not judge any of your decks.

**Why the first draft's step was dropped:** it was a Gemini test of sleep deck v2 against v3, and so was the one-matchup version we talked about next. Both are the wrong question. Dustin, Nov 1: "If I make a deck better against it, but worse against the other 90% of decks I face, I lose overall ground."

- A swap is only worth making if it helps across the decks you actually face, counted by how often you face each one.
- The test's two made-up opponents can't show that, and neither can a single matchup.
- On top of that, how well Gemini plays depends on the deck, which adds another unknown.
- So deck questions stay with your own 10-game loop. No deck test with a bot is planned.
