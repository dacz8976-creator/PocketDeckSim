# Outside ideas for the pilot (read-only web research, Oct 16)

For Astra's Oct 18 check, questions B, C, D. Nothing was cloned, installed, built or run. I read abstracts, READMEs and search
summaries, not full papers; where I could not confirm something, it says so. Our own status comes from `rl/RUN5.md` and the ky3
stage A README (on its branch; it failed its Oct 16 check).

## What exists outside

- **deckgym-core (bcollazo)** is the engine we forked. Its README names no strength measurement for any bot. It lists simple players
  (`r`, `e`, `e2`, an external-bot hook) and an `optimize` command that fills a deck by simulating games against a folder of
  opponent decks. deckgym.com's Deck Optimizer is the same idea ("thousands of games"). Its pages say nothing about who pilots
  or how strong the pilot is. So deck rankings from these tools are only as good as an unmeasured pilot, which is our problem too.
- **Cliff (IncredibleAloeVera fork)** is a 1.26M-parameter neural network pilot that sees only what a human sees (it has a belief
  module for hidden cards), trained by self-play. Its README makes **no strength claim** and gives no win rate. It reports about
  90 decisions a second on CPU, against about 740 for depth-2 expectiminimax, and it needs a GPU (we have none) to be fast. Its
  deck builder is "not built". It's a design to learn from, not evidence that the approach works.
- **Official Pokémon Kaggle contest (PTCG AI Battle Challenge, summer 2026)**: 100+ teams, a $240k prize pool, run on the physical
  game's engine rather than Pocket's. I found that Dragapult won the ladder, but only in an unverified forum post, and I did not
  find the winners' write-ups. The one public example I opened, a PPO self-play agent, is small, one network per deck, and was
  only measured against a random-move opponent (20 games). The PokéAgent paper (Showdown, not cards) says there are
  "considerable gaps" between LLM players, RL specialists and elite humans.
- **Pocket's own AI**: DeNA built reinforcement-learning AI for the real game, with a company team (news article only).

Honest summary: no public Pocket bot has a published measure of how human-like or how strong it is. We are not behind a
benchmark; there isn't one.

## What worked in other card games

- **Search with a hand-written scoring function** was the usual winner at small scale. The Hearthstone AI competition's winners
  (2018-2020) used MCTS, rolling-horizon evolution or pruned search, each with a hand-made evaluation. Forge (Magic) runs
  mostly on hand-written per-card rules. In Slay the Spire, MCTS plays combat well. A learned policy for the *non-combat*
  planning choices (map, card picks) lifted the win rate from 6% to 14% (one author's number), and the same author reported six
  failed tries to distill the search into a network.
- **Information-set MCTS** (Cowling, Powley, Whitehouse 2012; Whitehouse's thesis) was built to fix a known flaw of "guess the hidden cards, then
  search as if you knew": the bot acts as if it could tell apart states it cannot. It beat the guess-and-search method in
  Magic and in a Pokémon game. Our kx3 samples hidden cards from the pilot's own view, which is the same family; the
  flaw is reduced, not removed.
- **Supervised learning from human play plus search**: an MCTS + supervised Hearthstone bot reportedly beat Legend-rank players
  (the authors' own claim), and ISMCTS with a model of human moves was tested in 1709.09451.
- **ReBeL and Student of Games** (poker-scale, belief-aware learned values plus search) are the principled answer for
  hidden-information games. They beat top poker players, but with research-lab compute, and I found no compute figures. Not for one laptop.
- **LLM pilots**: PokéLLMon (GPT-4 on Showdown) won 49% of ladder games and 56% of invited games against humans (about 100 battles, authors'
  numbers); bare GPT-4 won 26% against a heuristic bot. PTCG-Bench (May 2026, physical TCG) says LLM agents reach "non-trivial"
  play, depend heavily on the surrounding harness, and don't improve reliably from experience. I found no cost per game. For scale:
  one poker paper reports about $0.07 a hand for Claude Opus. **My estimate, not a source:** a Pocket game is roughly 100-150
  decisions, so an LLM choosing every move would cost several dollars a game. That kills it as the main pilot at our game
  counts, but not as an occasional judge.

## B. Is the bot as built the right way?

The skeleton (search plus a hand-tuned score, hidden cards sampled from what the pilot may know) is the proven small-team
approach, so I wouldn't replace it. What the evidence doesn't support is the *method of improvement*: adding one plan term per
named failure (ky3, Blade pricing). It fixed cases it was shown and failed the check, and kx3 changes only about 3% of km3's
decisions. The Slay the Spire result points the same way: the search was fine, and the gap was in multi-turn planning. So
the better use of time is a **fixed, human-labelled exam of positions the pilot never developed against**, judged by
Dustin's choices, before any more tuning. That exam is also Astra's stated milestone.

## C. Outside ideas that could help (ranked)

**1. An LLM as a second opinion on flagged positions, tested offline.** Print a position as plain text (board, hand, legal actions) and ask
Claude for its choice and a one-line plan. Use it only where km3 and kx3 disagree (about 3% of decisions), never in every move.
- *Run:* take Dustin's labelled decisions (Quiz 4 answers, the pause-game positions, his journal games); 100-150 positions, kept out of
  anything used to tune. Compare agreement with Dustin's choice: LLM v kx3 v km3. Run each position 3 times to see how stable the LLM is.
- *Helps if:* the LLM agrees with Dustin more than kx3 does on the positions where those two differ, by a margin larger than the spread across
  the 3 repeats, and its one-line plans name the same idea he does (e.g. "arm the Bench"). Stop if it's no better than a coin flip there.
- *Cost:* about 150 positions x 3 runs x a few cents is roughly $10-30 of credits and one day of Sonnet work. It needs a
  text-board printer (small; Cliff's TUI and our logs may already do most of it). It plugs in as a critic that flags suspect
  decisions, so no change to the engine is needed. Evidence: PokéLLMon and PTCG-Bench show the idea has some signal, not that it matches Dustin.

**2. A "what Dustin does" prior learned from his recorded games, used only to order or break ties in search.** Hearthstone and
ISMCTS work shows human-move models help search a bit; Slay the Spire shows learned *strategic* choices matter more than
combat tactics.
- *Run:* leave-games-out test on all his recorded games: hold out whole games, fit a small model (even logistic regression on a few
  hand features, no GPU), compare top-1 agreement with his move against km3's and kx3's on the held-out games.
- *Helps if:* it beats kx3 on held-out games and on the "Bench-building" and "don't pass up an attack" decisions he flagged.
  Stop if his data is too small (my guess is a few thousand decisions; I haven't counted) or if it only wins on decks it saw.
- *Cost:* no API money, a few hours on the laptop or cloud, modest coding. It fits as an extra term in km3's ordering.

**3. Read the Kaggle winners' and PokéAgent write-ups before building anything else.** A $240k, 100-team contest on a full TCG engine
is the best public source of what actually plays a Pokémon TCG well. *Run:* a one-hour read by Sonnet, producing a list of
what the top teams did about hidden information, rollouts and training. *Helps if:* it names a concrete step we lack that is
cheap to test against the same exam. *Cost:* a few dollars. I couldn't open the write-ups, so this is unverified.

**Not recommended now:** more per-deck RL networks (Cliff has no published strength, and ours generalised badly); ReBeL or
Student of Games (compute); an LLM as the full pilot (cost, and no strength evidence in Pocket); more hand-added plan terms until the exam exists.

## D. Is this impossible for a student with one laptop?

**A pilot that plays exactly like Dustin on any position: I would not promise it.** Nobody has shown one for Pocket, and a funded
100-team contest is still working on it. **A pilot good enough to tell him which decks aren't worth his 10-minute games** is a more
reachable target and is what he asked for: kx3 already beats km3 by +21 points on held-out decks. The honest scale-down is
to claim only that, deck triage with stated uncertainty, until the unseen-position exam shows planning that holds up. Spend
the next week on the exam and the two cheap tests above, not on a new pilot.

## Sources

- bcollazo/deckgym-core: https://github.com/bcollazo/deckgym-core
- Cliff fork: https://github.com/IncredibleAloeVera/deckgym-core
- deckgym.com: https://deckgym.com
- Kaggle PTCG AI Battle Challenge news: https://www.edtechinnovationhub.com/news/the-pokmon-company-seeks-ai-agents-for-tcg-competition-on-kaggle , https://www.misprint.com/posts/pokemon-ai-tcg-competition-explained
- PPO self-play agent (cabt engine): https://huggingface.co/TomatoCream/pkm-cabt-ppo
- DeNA RL for Pocket: https://www.invenglobal.com/articles/24133/how-reinforcement-learning-ai-tackles-the-complex-rules-of-pok%C3%A9mon-trading-card-game-pocket
- PokéLLMon: https://arxiv.org/abs/2402.01118
- PTCG-Bench: https://arxiv.org/abs/2605.29653
- PokéAgent Challenge: https://arxiv.org/abs/2603.15563
- ISMCTS and human-move prediction: https://arxiv.org/pdf/1709.09451 ; Whitehouse thesis https://etheses.whiterose.ac.uk/id/eprint/8117/
- MCTS + supervised learning in Hearthstone: https://arxiv.org/pdf/1808.04794
- Hearthstone/LOCM agents overview: https://arxiv.org/html/2305.08234v4
- ReBeL: https://arxiv.org/pdf/2007.13544 ; Student of Games: https://arxiv.org/pdf/2112.03178
- Forge AI: https://github.com/Card-Forge/forge/wiki/ai
- Slay the Spire learned non-combat policy: https://huggingface.co/Jialeiv/sts-rl-agent
- PokerSkill (LLM cost per hand): https://arxiv.org/pdf/2605.30094
- Stanford expectimax on Showdown (2018): https://web.stanford.edu/class/aa228/reports/2018/final151.pdf
