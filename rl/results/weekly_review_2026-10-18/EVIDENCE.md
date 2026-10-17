# Evidence sheet for the weekly reviews, week of Oct 12-18, 2026

Written by the coordinator (Claude, "Multi-agent project orchestration") on Fri Oct 16 at about 21:10Z, for the two Monday Oct 19 reviews: the Claude side and Astra's outside view. Anything after Friday evening (PR reviews, weekend games) is not in here; read it live.

## A. What the bot can do now that it couldn't last week

**Nothing new has been demonstrated.** Stage A (Oct 16) tested the Kingambit-aware pilots on positions from his own games, using a test registered beforehand. Results are in `rl/results/next_pilot_2026-10/stageA_2026-10-16/README.md` (main 880ad428).
- kmb3, which puts a price on the Blade, changed 0 of 92 positions.
- kmbc3, which adds expected points, made his recorded play in 2 of the 12 counted positions; the bar was 6.
  - In games against itself it won 4.3 and 1.5 points more often (seat 0 and seat 1).
  - But the opponent was closer to winning by the time Kingambit first attacked, and the bot sent Energy to Regigigas instead of Kingambit.
  - Verdict: not "pilots Kingambit better".
- Dustin's correction: bringing Kingambit out late is fine. What matters is Kingambit not being knocked out too soon, and no current measure counts that directly.
- Astra's milestone isn't met: no pilot has been tested on positions outside the set it was developed on, because no such held-out exam exists yet.

## Real, smaller wins this week (not bot progress)

- **Upstream engine:**
  - bcollazo merged our PR #383 on Oct 16.
  - We opened 6 more small card-text PRs, #403-#408, on Oct 16. Each passed upstream's format, lint and test checks first.
  - The upstream comparison (main c0fcff86) found nothing upstream that changes a game his decks play.
  - Taking upstream's B4b card data (438 cards, including Mega Garchomp ex) is planned for the next engine update.
- **For his decks:**
  - The setup tester compared his Kingambit list with two variants (A, A1, A2).
  - The deck journal has his 10 ladder games filed.
  - He liked the Claydol Heal Block idea ("this is the creativity I like").

## Maintainer input (Oct 16 evening, deckgym Discord)

The original deckgym creator (Discord: AMANSA) thanked Dustin for the PRs and said "those screen recordings are gold".
- **On bots:** "The best Bot right now follows the Expectiminimax Algorithm on search 3 on the website. But you can get stronger bots in the CLI if you go deeper in depth (maybe 8 is the strongest yet meaningful), but it will take its time to think! ... not useful for simulating thousands of games."
- **New work:** "I am working on a new generation of AI which will be stronger and faster, was about to post about it."
- **On PRs:** either single PRs or one batch, with one commit per fix.

**Follow-up at 7:08 PM:** he posted his new AI (x.com/CodeAMANSA, Oct 16). It is "trained via Reinforcement Learning", and it "learned the Rainbow Cave + Flame Patch + Entei ex play all on its own". His caption: "Deck building tools require strong AIs ... Results soon!"
- His replay viewer shows the AI's probability for each option at each step; in the clip, "Play Rainbow Cave" is at 99%.
- That is the kind of card-combination play Dustin wants, learned without hand-coding.
- Unknown so far: whether it is one model for all decks or one per deck, its strength numbers, and whether it will be public.

**His earlier public posts** (X, @CodeAMANSA; screenshots Dustin shared on Oct 16):
- **Kaggle Pokémon TCG competition (physical TCG, judging by the cards shown):** his Ogerpon entry placed 425th of 6,807. It was "trained entirely via self-play for ~10 hours using PPO + League Play", with a model of about 500K parameters: "no transformers, no embeddings, just feature engineering and some network design".
  - Hand-designed features instead of card numbers is the fix our September RL notes named and never built: describe cards by what they are.
  - League play (training against a pool of past opponents) is the other piece.
- **Deck structure (Aug 30):** from 115 Pocket tournaments (June data, via DeckGym's Limitless integration), the winning structure is 8 Pokémon, 7 Supporters and 5 other cards. Champion decks peak at 8 Pokémon (29 decks), then 7 (25).
  - That is the kind of real-results check Dustin said would make pilot-free checks worth having. His own lists can be compared against it.

What this means for B and C:
- **A cheap comparison is available now.** Upstream's deeper expectiminimax (depth 5-8) can be run on the stage A plan positions. Position checks need only a few decisions, so the slowness doesn't matter.
- **His new AI may be the "different way".** Waiting for it, and offering Dustin's labelled real-game positions as a test of whether a bot plays like a person, could beat building our own. Sharing that data is Dustin's call.

## Spend

- **Weekly meter:** 91% on Fri 21Z (67% on Thu 17Z, 86% on Fri 17Z). It resets Mon 12:00Z.
  - The biggest costs were Sonnet's thorough upstream comparison, which he approved, and long-lived sessions re-reading big contexts.
- **API credits:** about $40 since Oct 14, out of the $200 monthly pool that expires Oct 28. That covered the pilot builds, tools, 6 PRs (~$2.70), research and checks.
- **Laptop time:** stage A about 10 hours; builds kept to one at a time (WSL has 7.6 GB).

## Blockers

1. **The pilot's method of improvement doesn't generalise.** Adding one hand-built plan term per named failure (ky3) didn't produce his plan.
2. **No held-out exam exists.** There's no fixed set of unseen positions labelled with his choices, so no pilot change can be judged beyond its own development set.
3. **The one laptop is tight:** one cargo build at a time, a disk that was nearly full, and the app needs to stay open for scheduled work.
4. **His time:** ladder games and labels are the only ground truth, and he's a student.

## Outside ideas

See `OUTSIDE_IDEAS.md` next to this file.
- **How it was made:** the draft came from model memory, because the credit worker has no web access. Every source and claim was then checked on the web on Oct 16: 21 links checked, 4 descriptions fixed, 1 invented source removed. Items it couldn't confirm are marked.
- **Top 3, each with a small comparison:**
  1. An AI model as a second opinion only where km3 and kx3 disagree. Test it on 100-150 positions he has labelled, for about $10-30 in credits. It helps if it agrees with him more often than kx3 does.
  2. A "what Dustin would do" guide learned from his recorded games, used only to order the search's moves or break its ties. Test it on whole held-out games. It fails if he hasn't recorded enough games.
  3. Read the Kaggle and PokéAgent competition write-ups for methods we lack. Whether they can be read is unverified.
- **Not recommended now:** more per-deck reinforcement-learning networks, ReBeL or Student of Games, an AI model as the whole pilot, or more hand-added plan terms before the exam exists.

## His direction this week (his words are in memory)

- Collaborate with the deckgym community.
- No AI-built decklists.
- A synergy search is chat-level help, not a project job.
- Checks that don't use the bot are "useless" unless they're shown to predict results.
- The simulator is paused, but he wants it to keep improving "unless it really is impossible".
- He wants these reviews every Monday.

## Open decisions for Monday

- The next pilot step: build the held-out exam first, try outside idea 1 or 2, or take a maintenance week.
- Batch 2 of upstream PRs (needs his OK).
- When to bring in upstream's B4b card data (planned for the next engine update).
