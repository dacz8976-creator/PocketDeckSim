# Outside ideas for the pilot (outside survey, Oct 16; sources checked Oct 16)

How this was made: the first draft was written from an AI model's memory (its run made no web searches). Every outside source and claim below was then checked on the web on Oct 16; items marked (unverified) could not be confirmed.

For Astra's Oct 18 check, questions B, C, D. Nothing was cloned, installed, built or run. The web check used abstracts, READMEs and
search summaries, not full papers; where something could not be confirmed, it says so. Our own status comes from `rl/RUN5.md` and the ky3
stage A README (on its branch; it failed its Oct 16 check).

## What exists outside

- **deckgym-core (bcollazo)** is the engine we forked. Its README names no strength measurement for any bot. It shows simple players
  (`r`, `e`, `e2` appear in examples, not explained; plus an external-bot hook) and an "Optimize incomplete decks" command that fills a
  deck by simulating games against a folder of opponent decks. deckgym.com's Deck Optimizer is the same idea ("thousands of games"). Its pages say nothing about who pilots
  or how strong the pilot is. So deck rankings from these tools are only as good as an unmeasured pilot, which is our problem too.
- **Cliff (IncredibleAloeVera fork)** is a 1.26M-parameter neural network pilot that sees only what a human sees (it has a belief
  module for hidden cards), trained by self-play. Its README makes **no strength claim** and gives no win rate. It reports about
  90 decisions a second on CPU, against about 740 for depth-2 expectiminimax, and it needs a GPU (we have none) to be fast. Its
  deck builder is "not built". It's a design to learn from, not evidence that the approach works.
- **Official Pokémon Kaggle contest (PTCG AI Battle Challenge, summer 2026)**: over $300k in prizes ($240k of it is the top eight
  of the Strategy track), run on the official engine for the physical game (about 2,000 Standard-format cards), not Pocket's.
  I found no team count (unverified; the "100+ teams" in the first draft belongs to the PokéAgent contest below). One forum post
  (PokeBeach, a single user's comment) says Dragapult won the leaderboard (unverified), and I found no results coverage of the September
  finals or any winners' write-ups. The one public example I opened, a PPO self-play agent (about 0.5M parameters), is small, one
  network per deck, and was only measured against a random-move opponent (20 games for two of its three agents), a low bar. The PokéAgent
  paper (Pokémon battles, not cards; NeurIPS 2025 competition, 100+ teams) says there are "considerable gaps" between LLM players, RL
  specialists and elite humans.
- **Pocket's own AI**: DeNA presented a reinforcement-learning battle AI for Pocket at CEDEC 2026 (Transformer, about 2M parameters,
  about 50M self-play matches per model; used for CPU opponents, auto-battle and deck building). The news article, as read, gives no win rates.

Honest summary: I found no public Pocket bot with a published measure of how human-like or how strong it is. We are not behind a
benchmark; I found none.

## What worked in other card games

- **Search with a hand-written scoring function** was the usual winner at small scale, with one recent exception. The Hearthstone
  AI competition (held 2018-2020) winners used MCTS, rolling-horizon evolution, pruned breadth-first search or dynamic lookahead, usually with a
  state-evaluation function (whether hand-made is not stated). In the Legends of Code and Magic contest, winners were mostly search
  plus hand-made heuristics, but the last edition was dominated by neural networks. Forge (Magic) runs on hand-written general
  rules, with some per-card logic its own wiki calls "usually not a healthy approach". In Slay the Spire, MCTS plays combat well.
  A learned policy for the *non-combat* choices (map, card picks) lifted the win rate from 6% to 14% (one author's number; a single run
  on 50 held-out seeds, no error bars), and the same author reported six failed tries to distill the search into a network.
- **Information-set MCTS** (Cowling, Powley, Whitehouse 2012; Whitehouse's thesis) was built to fix a known flaw of "guess the hidden cards, then
  search as if you knew": the bot acts as if it could tell apart states it cannot. Whitehouse's thesis reports it beat the
  guess-and-search method on several card and board games, and Ihara et al. (2018) report the same in a Pokémon battle simulator.
  (The first draft also said Magic; unverified.) Our kx3 samples hidden cards from the pilot's own view, which is the same family; the
  flaw is reduced, not removed.
- **Supervised learning from human play plus search**: supervised models guiding MCTS in Hearthstone "substantially improve the win
  rate" (abstract of 1808.04794; the first draft's "beat Legend-rank players" claim is unverified and removed). ISMCTS with a model of
  human moves was tested on the Cheat card game against 120 human players (1709.09451), and did better as the model got more accurate.
- **ReBeL and Student of Games** (poker-scale, belief-aware learned values plus search) are the principled answer for
  hidden-information games. ReBeL's abstract claims superhuman heads-up poker; Student of Games beat the strongest openly available
  poker agent (not top humans) and also plays chess, Go and Scotland Yard. Both come from research labs; I found no compute figures (unverified). Not for one laptop.
- **LLM pilots**: PokéLLMon (GPT-4 on Showdown) won 49% of ladder games and 56% of invited games against humans (over 100 battles, authors'
  numbers); bare GPT-4 won 26% against a heuristic bot. PTCG-Bench (submitted May 2026, Pokémon TCG) says LLM agents reach "non-trivial"
  play, that performance is sensitive to harness design, and that sustained, stable self-improvement from experience "remains
  challenging". I found no cost per Pocket game. For scale: the PokerSkill paper reports about $0.07 a hand for Claude Opus 4.6/4.7
  (about $0.30 for GPT-5.5 at its highest setting). **My estimate, not a source:** a Pocket game is roughly 100-150
  decisions, so an LLM choosing every move would cost several dollars a game. That kills it as the main pilot at our game
  counts, but not as an occasional judge.

## B. Is the bot as built the right way?

The skeleton (search plus a hand-tuned score, hidden cards sampled from what the pilot may know) is the proven small-team
approach, so I wouldn't replace it. What the evidence doesn't support is the *method of improvement*: adding one plan term per
named failure (ky3, Blade pricing). It fixed cases it was shown and failed the check, and kx3 changes only about 3% of km3's
decisions. The Slay the Spire result (one small test) points the same way: the search was fine, and the gap was in multi-turn planning. So
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
ISMCTS work shows predictive models help search a bit; in Slay the Spire's one small test, learned *strategic* choices lifted the win
rate while combat stayed with search.
- *Run:* leave-games-out test on all his recorded games: hold out whole games, fit a small model (even logistic regression on a few
  hand features, no GPU), compare top-1 agreement with his move against km3's and kx3's on the held-out games.
- *Helps if:* it beats kx3 on held-out games and on the "Bench-building" and "don't pass up an attack" decisions he flagged.
  Stop if his data is too small (my guess is a few thousand decisions; I haven't counted) or if it only wins on decks it saw.
- *Cost:* no API money, a few hours on the laptop or cloud, modest coding. It fits as an extra term in km3's ordering.

**3. Read the Kaggle winners' and PokéAgent write-ups before building anything else.** A $300k+ contest on the official TCG engine
is the best public source of what actually plays a Pokémon TCG well. *Run:* a one-hour read by Sonnet, producing a list of
what the top teams did about hidden information, rollouts and training. *Helps if:* it names a concrete step we lack that is
cheap to test against the same exam. *Cost:* a few dollars. I found no public winners' write-ups or final results yet (the
Strategy reports were due mid-September), so whether they can be read is unverified.

**Not recommended now:** more per-deck RL networks (Cliff has no published strength, and ours generalised badly); ReBeL or
Student of Games (compute); an LLM as the full pilot (cost, and no strength evidence in Pocket); more hand-added plan terms until the exam exists.

## D. Is this impossible for a student with one laptop?

**A pilot that plays exactly like Dustin on any position: I would not promise it.** Nobody has shown one for Pocket, and a funded
$300k+ contest on the physical game's engine was set up to find it (I found no published results). **A pilot good enough to tell him which decks aren't worth his 10-minute games** is a more
reachable target and is what he asked for: kx3 already beats km3 by +21 points on held-out decks. The honest scale-down is
to claim only that, deck triage with stated uncertainty, until the unseen-position exam shows planning that holds up. Spend
the next week on the exam and the two cheap tests above, not on a new pilot.

## Sources

- bcollazo/deckgym-core: https://github.com/bcollazo/deckgym-core
- Cliff fork: https://github.com/IncredibleAloeVera/deckgym-core
- deckgym.com: https://deckgym.com
- Kaggle PTCG AI Battle Challenge news (both checked; neither names winners or a team count): https://www.edtechinnovationhub.com/news/the-pokmon-company-seeks-ai-agents-for-tcg-competition-on-kaggle , https://www.misprint.com/posts/pokemon-ai-tcg-competition-explained
- "Dragapult won" forum comment (seen in a search summary only, unverified): https://pokebeach.com/forums/posts/3102317/
- PPO self-play agent (cabt engine): https://huggingface.co/TomatoCream/pkm-cabt-ppo
- DeNA RL for Pocket (CEDEC 2026 talk): https://www.invenglobal.com/articles/24133/how-reinforcement-learning-ai-tackles-the-complex-rules-of-pok%C3%A9mon-trading-card-game-pocket
- PokéLLMon: https://arxiv.org/abs/2402.01118 (abstract has the 49% and 56%; the 26% is from the paper's text via search)
- PTCG-Bench: https://arxiv.org/abs/2605.29653
- PokéAgent Challenge: https://arxiv.org/abs/2603.15563
- ISMCTS with human-move prediction (Cheat game, Bitan and Kraus): https://arxiv.org/abs/1709.09451 ; Whitehouse thesis https://etheses.whiterose.ac.uk/id/eprint/8117/ ; ISMCTS in a Pokémon battle simulator (Ihara et al. 2018, abstract only): https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/72345
- MCTS + supervised learning in Hearthstone (Świechowski et al. 2018): https://arxiv.org/abs/1808.04794
- Hearthstone and Legends of Code and Magic winners, summarised in the Tales of Tribute AI Competition paper (not a Hearthstone paper itself): https://arxiv.org/abs/2305.08234
- ReBeL: https://arxiv.org/abs/2007.13544 ; Student of Games: https://arxiv.org/abs/2112.03178
- Forge AI (rule-based, "not trained"): https://github.com/Card-Forge/forge/wiki/ai
- Slay the Spire learned non-combat policy: https://huggingface.co/Jialeiv/sts-rl-agent
- PokerSkill (LLM cost per hand, Section 4.1): https://arxiv.org/abs/2605.30094
- Removed: the Stanford AA228 2018 report (final151.pdf). It is a reinforcement-learning Pokémon battle project, not "expectimax on Showdown", and nothing above uses it.
