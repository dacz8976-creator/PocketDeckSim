# Claude-side weekly review, Sunday Nov 8, 2026

**Verdict: REDIRECT.** Stop building bots for now. Use the one the sprint produced on one deck you name.

What I read: memory, the sprint's own result files on the laptop, GitHub main, upstream, and a fresh outside search. No evidence folder landed for this week (`rl/results/weekly_review_2026-11-08/` doesn't exist), and main hasn't changed since Nov 5: all sprint work is on the laptop only. Meter at review time: 88%, after the free reset you used on Nov 6.

## A. Are we making progress towards your goals?

Yes on the bot, for the first time in weeks. No on your decks yet.

- **A new pilot** (`wt_evn_r1_h1_d0.1_f1`, the first choice on your play page). On 25 of your own lists that it never trained on, against 18 current tournament lists, it won 43.0% where the old quick bot won 31.2% on the same deals: +11.8, give or take 4 across decks, 2,250 games. It takes about half a second a game. The old slow bot needs 40 seconds or more and sat in the same range on a much smaller test.
- **Fewer of two countable mistakes** than the old quick bot, by the sprint's counts: missing a save (0.45 v 2.55 per 100 turns) and putting Energy on a Pokémon about to be knocked out (0.62 v 4.23), both counted on the version just before the evolve fix. After the fix for your evolve rule, skipped evolutions fell from 2.99 to 0.33. That last count is the builder's own.
- **What didn't improve.** On the private exam of your own choices, no fast bot showed a clear gain over the old one. Only Opus as the pilot did. The new pilot still passes on safe knockouts and free attacks more often than the old bot, and it still misplays Muk with Regigigas.
- **What doesn't count.** Every opponent was a bot. Nothing is on main, and the official deck tools still use the old bots. The tens of thousands of sprint games, the faster engine and the mistake counter are activity, not progress.
- **Engine.** Since Nov 4 every Dual Fusion card plays in the official engine, so your newer decks can be simulated at all. Upstream merged #441 on Nov 2 (26 of 26 PRs merged), so the public simulator now follows what you filmed for Misty and Sweet Honey.
- **Deck answers from the simulator this week: none.** Your 50 logged games (23-27) were read by agents. That's your play, not the bot.

## B. Is the bot the right way?

The old construction is finished as a line of work. Three separate attempts to tune its scoring came out flat or worse, and its slow version was too slow to test. The sprint already replaced the pilot and kept the engine and the evidence, which was the right swap.

More bot-building isn't the best use of next week, though. Bots trained by self-play win more but don't play more like you. The only thing that moved that measure was an AI model as the pilot, which costs meter (about 25-30 games per point). So: the fast pilot for volume and for counting whether a combo comes together, Opus for spot checks on your word, and no more tuning until a deck comparison shows a weakness that matters.

The maintainer's generalist AI: still nothing public. No model, no training code, and upstream has been quiet since Nov 2. There's nothing to adopt or help test yet. Someone else did publish one; see C.

## C. Outside ideas (searched fresh today; the pages were read)

1. **pocket-zero** (github.com/Undi95/pocket-zero; started Oct 9, last update Nov 5). New to us. A deckgym fork with a trained AlphaZero-style bot you can download, and a "forge" that tries one card change at a time against current tournament lists on the same games, with cards you lock. Its author says it beats upstream's standard bot about 72% of the time and matches 15 real tournament matchups within 7.3 points (upstream's bot: 13.9; chance alone: 4.7). Limits: nobody has checked those claims, it has no Dual Fusion cards, and it was trained for about 30 hours on two top-end graphics cards. *Cheap comparison, on your word only:* build it from its source, play it against our new pilot on four of your older decks (about 200 paired games each), and run its forge once on deck 01 with your key cards locked. $0, about 1% of the meter, one laptop evening. It tells us whether a free ready-made pilot is as good as ours. It doesn't tell us whether its deck advice is right.
2. **deckgym-evalbot** (github.com/uahawke/deckgym-evalbot, August). Another fork that tuned the old bot's scoring by the same method we tried. Its newest version scored 50.24% against its previous one over 6,000 games: no gain. *Comparison:* already done; our tuning track read -0.1 to -2.2. It backs stopping.
3. **Imitate first, then search** (Rubin, arXiv 2609.06816, September; abstract only). In another card game, a net that copied a strong player won 26.8% alone and 51.35% with search added, over 10,000 games. Our Opus-copying net was tried as a first-move guide, not inside the search. *Comparison, only if bot work reopens:* use it to order moves inside the planner and replay the 2,160 saved test games. About 2% of the meter and a laptop night.
4. **Unchanged:** the Kaggle winner's code is still not out and round 2 has no date. PTCG-Bench's update (Sept 19) again found no reliable gain from five self-improvement methods. Nothing found on AI models piloting Pocket with costs.

## D. Is this asinine for a student with one laptop?

No, but the reachable goal is narrower than the original one. This week one laptop trained a small bot in a day that held up on decks it had never seen. A bot that plays every deck like a strong player is out of reach here: the people who got close used far more computing power, and our own exam says we aren't there. What's in reach is "which of these three or four versions of my deck does better, with the limits stated".

The cost was high: nearly two weekly meters in one week, plus your hours on the quiz and the reviews, for no deck answer yet. If next week's named-deck test also gives you nothing you can use, scaling down to engine upkeep and your own play loop is the right call.

## Next step (one)

**You name one deck. We compare three or four versions of it with the new pilot against the tournament panel, and report three counts kept apart: drew the pieces, could use them, actually used them.** The Mawile/Goodra, Combo 30 and Water families from your Nov 8 games are ready starting points.

- What it can tell you: whether a version comes together more often, and which panel decks it struggles against.
- What it can't: your ladder win rate, or the better list when the gap is small. Every conclusion stays provisional.
- Before any result is read: the two checks the coordinator already has planned for tonight (the planted-leak test for this exact pilot, and whether its assumed opponent lists include your decks).
- Rough cost: 3-4% of the weekly meter, mostly building the three counts and one blind check. $0 of credits. About two laptop hours of games. Opus games only if you say yes.

## Astra's review: where we agree and differ

I read Astra's weekly note (Nov 9 01:07Z) only after the sections above were drafted.

- **We agree** on the verdict and the next step: redirect to one deck comparison with the three counts kept apart. We quote the same fresh-deck result (43.0% v 31.2%, 2,250 games), and neither of us recounted the raw mistake counts. Astra also says more quizzes aren't needed to start; I agree.
- **A differs in emphasis.** Astra says "yes, materially" and counts the Dual Fusion engine release. I count it as a secondary win and add what Astra can't see: on the private exam no fast bot clearly beat the old one. The exam record supports that, so the gain is in winning bot games, not yet in playing like you.
- **C differs.** Astra offers two long-established training methods (DAgger and AggreVaTe) as fallbacks if a deck test gets blocked. I didn't open those two pages. One 2026 study my search did read (arXiv 2607.06854, a Gin Rummy agent, abstract only) reports that DAgger-style imitation didn't help there, so I'd hold them as fallbacks too. Astra's note has none of this week's new outside work: pocket-zero and deckgym-evalbot are missing from it.
- **Astra caught two things I missed.** First, the leak review and the tests against a different opponent bot and unseen opponent lists were run on the earlier versions, not on the exact pilot now on your page. The scoreboard backs this: `_d0.1_f1` has only been read against the old quick bot. Second, the official tools default to an older, smaller opponent set as well as the old bots, so a comparison has to name both the pilot and the opponents. I didn't open that settings file myself; START_HERE agrees on the bots.
- **One addition I'd take from Astra:** if a second pilot reverses the comparison's conclusion, say so instead of recommending the swap. That costs laptop time only.
- **No change** to my verdict or next step.

## Scheduled re-run, Sunday 8:13 PM CT (added)

The review above was run early, at about 7:15 PM. The scheduler fired it again at its usual time, in a fresh session. I rechecked it at the sources instead of rewriting it. **Verdict and next step are unchanged.**

- **Rechecked, all match.** The scoreboard row for the exact pilot: 43.0% v 31.2%, +11.8, 2,250 games, across-deck spread 2.0. The sprint's mistake table: missed saves 0.45 v 2.55, Energy on a doomed Pokémon 0.62 v 4.23, skipped evolutions 2.99 before the fix. Upstream: 26 of 26 PRs merged, nothing new since Nov 2, no open PRs. pocket-zero: nothing new since Nov 5.
- **Two gaps in the first version closed.** I opened the official tools' settings: the quick screen uses the old quick bot on both sides by default, and the slow report is pinned to the old slow bot against the older "panel8" opponents. Astra was right. I also opened Astra's two links: they are the 2011 and 2014 papers by Ross and Bagnell that introduced those two training methods (abstracts only). Established methods, no Pocket results.
- **Astra's first catch confirmed directly.** The scoreboard has three rows for the exact pilot, and all three are against the old quick bot on the same tournament panel.
- **One outside item added to C.** The fork `dgcastillof/deckgym-core` (its author sent upstream #440 and #442; last update Nov 7). By its own description (`docs/FORK.md`, in Spanish; I read the first 120 lines and ran nothing): one person, own search bots kept apart from upstream's. One of those bots scores each move at the end of its own turn, the same idea as our whole-turn planner. It also has a per-game recorder that counts, for each player, how often each Ability and attack was used and on how many turns it was available. Those are two of the three counts in the next step (could use / used). I saw no strength figures. *Cheap comparison:* read how its recorder works before building ours, and borrow the idea if it's simpler. Reading only, $0, almost no meter, no outside code run.
- **Nothing else new** in a short search: no public deckgym AI model, and no new Pocket bot project on GitHub since Nov 1. The search summary of the Kaggle contest's site still gives round 2 as "late 2026 or later"; I didn't reopen that page.
- Meter: 89% at 8:13 PM (88% at the first run).
