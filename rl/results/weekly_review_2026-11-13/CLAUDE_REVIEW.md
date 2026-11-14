# Claude-side weekly review, Friday Nov 13, 2026

**Verdict: CONTINUE**, on one condition: the next job is one deck you pick. If no pick comes, this is a low-cost maintenance week by default, and that is fine.

This run fired on Friday, not Sunday, so it covers Nov 9 afternoon to today. What I read: memory, GitHub main, upstream, the mailbox's daily notes, and a fresh outside search. No evidence folder landed (`rl/results/weekly_review_2026-11-13/` doesn't exist), so the result figures below come from the coordinator's notes, not from files I reopened. Meter: 75% all models and 93% Fable, 2 days 13 hours before Monday's reset.

## A. Are we making progress towards your goals?

A little, and not in the bot itself. The pilot is the same build as last week. It plays no better than it did.

What is new is use, and a measure of how far to trust it:

- **Last week's step was done.** Your real games were put beside the bot's for the same lists (13v4, 11v4, Goodra v3, Charizard V1, Hoopa/Absol). On some lists the bot uses the deck roughly as you do. On others it doesn't: in Deck 11 the bot had Charizard Active in 82-86% of games and you in 2 of 6, and on Charizard V1 the Stage 2 was out by turn 3 in 2 of your 10 games v 47-48% for the bot. Bot results for Deck 11 now get less weight. Small samples; they flag things to look at and prove nothing.
- **A wide screen of 58 real tournament decks** gave five leads, posted with QR codes. All five repeated on a second set of deals.
- **How well the screen tracks reality: weakly.** Bot score against real tournament results lines up poorly for whole decks (0.12 earlier, 0.36 on ten decks this time) and moderately for single matchups (0.54). Two of the five leads, Diancie and Blaziken, have poor real records (29.8% of 47 and 38.6% of 44 matches, thin data, and for the whole archetype, not that exact list).
- **One caution held up in your games.** The Dedenne page said bots flatter the deck because they attack Oricorio with ex Pokémon. Your first five games went 3-2, and both losses came from non-ex attackers going through Oricorio. Two games, so a hint only.
- **Two pilot habits were measured:** it passes up a counted knockout about 11% of the time, and it attacks into Safeguard. You deferred the fix.

What doesn't count: the game totals, the pages, the counts themselves. No confirmed card upgrade came out of this week. Nothing has happened since Nov 11; the next move was yours.

Engine: nothing new. Upstream's last change is Nov 2. All 26 of our PRs there are merged.

## B. Is the bot the right way?

For one job, yes: comparing versions of a deck you already want to play, with the "had it / could use it / used it" counts beside the win numbers. For finding decks, no. This week's own numbers say a high bot score is a weak reason to play a deck. I would not run another broad screen.

The pilot's known habits (skipped knockouts, Safeguard, Deck 11's Charizard) are the reason to keep each comparison narrow and to read the traces when a result depends on them. A repair is worth it only when one of those habits could change a choice you care about.

The maintainer's generalist AI: still nothing public. No commit since Nov 2, no release, no model or training code. Nothing to adopt or test yet.

## C. Outside ideas (searched fresh today)

Nothing new that changes the plan. A helper read the pages; I did not reopen them.

1. **New to us: a Kaggle entry's notes** (github.com/Makkkelyie/pokemon-tcg-ai; main card game, not Pocket; final entry Nov 9). Mid-table. Its author found that adding search on top of the trained policy made no measurable difference. That is the third outside report saying search alone doesn't lift a card bot. *Cheap comparison here:* none needed; it agrees with what our own sprint found, and it is a reason not to spend on deeper search.
2. **pocket-zero** (github.com/Undi95/pocket-zero): still only automatic list updates (latest Nov 12); last real change Oct 16; its page names no card sets, so Dual Fusion support is unconfirmed. Its claim to match real tournament matchups within 7.3 points is the author's own, and its notes don't say which matchups or data. *Cheap comparison, on your word only:* build it from source and run one of your older decks against lists we already have real results for; one laptop evening, under 1% of the meter.
3. **Opened for the first time:** alexotsu/bills-pc is a deckgym copy with a way to plug in outside bots, no strength figures. shou6/pocket-ai-simulator-server is gone (404). Two small Python Pocket simulators turned up with no bots or figures.
4. **Unchanged:** deckgym upstream and deckgym.com; the Kaggle winner's code still "after the second round"; round 2 still "later in 2026", no date; PTCG-Bench same version.
5. **Not checked:** Kaggle's own pages (search snippets say final results are posted; I did not open them), Reddit, the maintainer's X and Discord. No new paper on Pokémon card-game AI turned up for October or November.

## D. Is this asinine for a student with one laptop?

No, but the cost has moved. The laptop handles the games at $0. What this week spent was the meter and coordination: 75% of the week's usage by Friday, the Fable share at 93%, for one wide screen, the game counts, and five leads. Then three days of nothing while everything waited on a pick.

What you got: five decks to try, one of which you played, and a clearer picture of when the bot's numbers mean little. That is real but modest. If the next single-deck comparison doesn't give you a change you'd actually make, scaling down to engine upkeep and your own play is a fair call.

## Next step (one)

**Pick one deck, a lead or your own, and name what you'd like answered about it. Then one comparison of two to four versions of that deck against the 23 tournament lists, on two sets of deals, with the "could use / used" counts.**

- What it can tell you: whether a swap helps that deck in bot games, and where it costs.
- What it can't: your ladder win rate, or whether the deck is good.
- Rough cost: about 2 to 4% of the weekly meter, one laptop night, $0 credits. My estimate; the last two jobs ran over theirs.
- No broad screens and no bot rebuilding this week.

## Astra's review: where we agree and differ

There is no weekly note from Astra yet (it's Friday). The newest is today's daily (9:02 AM), read after the sections above were drafted.

- **We agree:** today's progress is human evidence for one lead, "not a new bot capability or confirmed card upgrade". No more broad screens. The figures match the coordinator's notes: Dedenne 3-2, Hoopa/Absol 8-8 in 16, 13v4 6-4 in 10.
- **Astra caught two things I didn't have:** the nine new games were Emblem Event games, not verified ranked games; and two of the three Dedenne wins were against an opponent's only Pokémon, so they don't show the deck holding up against a full board.
- **We differ on the next step.** Astra would study your two Dedenne losses: when to move Energy from Oricorio to Dedenne. I'd wait for your pick first. Both are consistent with the files; the difference is who chooses the deck. If you pick Dedenne, Astra's question is the right one to start with, and it is cheaper than mine (a read of saved games, under 1%).
- **Checked myself:** main is unchanged since Nov 9 and your laptop's copy is 6 commits ahead and 2 behind, as Astra says. I did not open the game review files or the wide-screen results.
- **No change** to my verdict or next step.
