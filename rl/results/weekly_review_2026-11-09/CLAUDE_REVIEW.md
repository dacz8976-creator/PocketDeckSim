# Claude-side weekly review, Monday Nov 9, 2026

**Verdict: CONTINUE.** The redirect from yesterday's review was carried out overnight and gave the first deck answers. This week is cheap: your games on the trial lists come first, and no new bot rounds until they're compared.

This run fired Monday afternoon, a day after the Nov 8 review, so it covers what changed since then: the overnight deck tests. What I read: memory, the overnight result files on the laptop (three reopened at the source; the figures match), GitHub main, upstream, and a fresh outside search. No evidence folder landed (`rl/results/weekly_review_2026-11-09/` doesn't exist). Main gained only seed records. Meter: 5% used, reset this morning; last week ended near 95%.

## A. Are we making progress towards your goals?

Yes. Yesterday I wrote "deck answers from the simulator this week: none". That changed overnight.

- **What the bot did that it couldn't a week ago:** compared versions of your own decks, fast enough to repeat each comparison on fresh deals and against different opponents. About 120,000 games in one night, $0.
- **Three results held up every time** (each on three or more sets of deals, and again against opponent lists the pilot wasn't built around; Deck 13 also against the stronger opponent bot):
  - Deck 13: an Igglybuff version beats 13v2. 13v4 won 1,797 v 1,515 of 3,600 (+7.8, range +5.7 to +9.9). Against rebuilt versions of 108 decks you actually met: 696 v 644 of 1,080 (+5.0, range +1.9 to +8.0).
  - Deck 11: the Ignition Charmeleon swap beats 11v2 (+3.7, range +2.6 to +4.8, four sets of deals). 11v4 v your current 11v3: can't tell them apart.
  - Water: your two-Suicune list beats the Eiscue swap (about 4 points; ahead against 16 of 23 tournament lists).
- **Everything else showed no clear difference:** Deck 17's lists and Tool slot, Deck 01 v2 v v3, Goodra's flex slot, 13v4 v 13v3. Combo 25's Oricorio gain came mostly from one matchup.
- **Read plainly:** the bot mostly agreed with swaps you had already made (Igglybuff, the 11v3 package, two Suicune) and couldn't settle the close calls. It gave you one new list to try, 13v4.
- **What doesn't count.** The game count is activity. Every game was bot against bot. With about 43 comparisons, some "clear" results are chance; only the three above repeated. Why Deck 13 wins more isn't shown. None of it has been checked against your real games: the trial lists were posted today, with no games on them yet.
- **Engine:** nothing new. Upstream has been quiet since Nov 2; 26 of 26 of our PRs are merged.

## B. Is the bot the right way?

For this narrow job, yes for now. The pilot swap is done, and the bot is no longer what holds things up. What's unknown is whether a bot gap of 4 to 8 points means anything on your ladder. More bot-building or more bot rounds can't answer that; only your games can.

Two limits to keep in view. It takes about 3,600 games to see a 4-point gap, so one-card choices between close lists will stay "can't tell". And the deck tests found one pilot weakness (opponent bots attacking into Oricorio's Safeguard for 0 damage; in about 1 in 10 of those attacks the logs show a ready alternative, so only those can be called misplays). Written down, no fix unless you ask.

The maintainer's generalist AI: still nothing public. Upstream's newest change is Nov 2, with no releases and no model or training code. There's nothing to adopt or help test yet.

## C. Outside ideas (searched fresh today)

Almost nothing is new since yesterday's search, and nothing changes the plan.

1. **One item new to us: a Kaggle team's look-back slides** (pao, Oct 15; speakerdeck.com/go5paopao/furikaeri; main card game, not Pocket; in Japanese, read through a translation of the slide text). Their search-based bot placed 114th of 6,807. Their lessons: the top teams trained from scratch on huge volumes (first place about 180 billion actions), and deck choice has to account for the decks you expect to face. They measured one card by splitting results on whether the opponent played it: 77.4% over 745 games v 43.8% over 928. *Cheap comparison here:* already done in part. Last night's results were re-weighted by how common each opponent deck is, and the three findings kept their direction. The split-by-card idea could be run on the saved games for one card you name: no new games, well under 1% of the meter.
2. **Unchanged, checked today:**
   - deckgym upstream: newest change Nov 2, no releases (github.com/bcollazo/deckgym-core).
   - pocket-zero: only automatic tournament-list updates, the latest today; its last real code change in the list is Oct 16, and its page doesn't mention Dual Fusion (github.com/Undi95/pocket-zero). Yesterday's cheap comparison still stands, on your word only.
   - The Kaggle winner's code is still "after the second round", and the contest site still gives round 2 as "later in 2026" with no date (ptcg-abc.pokemon.co.jp).
3. **Not checked:** the maintainer's X and Discord posts. A few other GitHub projects showed up in search by name only; most are for the main card game's Kaggle engine, and I didn't open them. No new paper on Pokémon card-game AI turned up for October or November.

## D. Is this asinine for a student with one laptop?

No. Last night is the first direct evidence that the narrow goal fits one laptop: version-against-version comparisons of your decks, overnight, at no cost beyond the plan. The broad goal, a bot that plays every deck like a strong player, is still out of reach here.

The open question moved from "can it be done" to "is it worth your time". If your games on the trial lists look nothing like the bot's games (different cards doing the work, different results), then the comparisons are a curiosity, and scaling down to engine upkeep and your own play loop is the right call. That check is cheap, and it's this week's step.

## Next step (one)

**A reality check, with no new bot games: put your real games beside the bot's for the same lists.** Start with the games you've already logged on these families (13v2 5-4, 13v3 1-1, 11v3 2-2, Goodra 5-8), and add trial-list games as you play them. One small table per deck: how often each key card did its job in your games v in the bot's (Cyrus played, Sleepy Lullaby used, Ignition attached, Goodra set up by turn 4), and results.

- What it can tell you: whether the bot uses your decks the way you do. If it doesn't, its win gaps mean little.
- What it can't: which list is better. A handful of games won't confirm a 5-point gap. How many you play is up to you.
- Rough cost: about 1% of the weekly meter, $0 of credits, no laptop time. No more comparison rounds until this table exists.

## Astra's review: where we agree and differ

There is no new weekly note from Astra. Its last weekly is dated Nov 8 and was covered in yesterday's review. The newest Astra note in the mailbox is today's daily (9:16 AM), which I read only after the sections above were drafted.

- **We agree** on the main point: there is now practical deck progress, 13v4 is worth trying, 11v4 is an alternative and not a proven replacement for 11v3, and the next move is your games on the trial lists, not another broad bot round. Astra recounted the Deck 13 result from the raw game records and got the same 1,797 v 1,515.
- **Astra has one thing I left out:** against Mewtwo/Mew, 11v4 won 120 of 300 and your 11v3 won 138, with 11v3 higher in all six rounds. It's a small slice and could be chance, but it belongs beside 11v4 as a known tradeoff. The coordinator's record has the same figures.
- **Astra's caution on the leak check stands:** the planted leak was caught only once in 518 decisions on the weak version and in all five groups on the stronger one. The check was done; it doesn't prove every leak would be caught. I didn't reopen those logs.
- **One point is out of date in Astra's note, not wrong:** it says the Oricorio logs still need the counterplay count. That count was done later this morning (the 1 in 10 figure in B).
- **Small difference:** Astra counts the tournament research library as part of the progress. By your rule I'd call it a useful reference, not something the bot does.
- **No change** to my verdict or next step.

## Amendment, Monday Nov 9, evening (after Astra's reply and Dustin's corrections)

The verdict stays CONTINUE. Several statements above were stronger than the records support. Where this section and the text above disagree, this section is right.

### What I overstated

- **"The bot is no longer what holds things up" (B).** Too far. The pilot is good enough for some comparisons. Its known problems (healing, protecting combo pieces, timing plays, passing on safe knockouts, Muk with Regigigas) can still distort others. Use it selectively, and repair a mistake when it could change a deck decision.
- **"It takes about 3,600 games to see a 4-point gap" (B).** Wrong as a general rule. Last night's own tests separated +5.0 with 1,080 games and +4.1 with 1,800. It depends on the pairing, the matchups, the weights and how sure you want to be.
- **"Out of reach here" (D).** That's my judgment, not a finding. Your goal is trustworthy testing for decks you care about, which doesn't need a bot that plays every deck like a strong player. Broad reliability is not shown yet; it isn't ruled out. The Kaggle winner's 180 billion actions come from a different game with a different aim, and are not a hardware minimum for this project.
- **"No more comparison rounds until this table exists" (next step).** Withdrawn. That was a new gate. A targeted test for a question you raise is still fine, and your games stay optional.

### Corrections to section A

- **"Held up every time" fits Deck 13 only.**
  - Deck 11, Ignition alone: +2.9 on the 23 outside lists (+0.1 to +5.6), and +2.2 weighted by popularity (-1.2 to +5.5). It wasn't run on the decks you faced.
  - Deck 11, what clearly repeated is 11v4 over 11v2: +6.0 on the 23 lists (+4.0 to +8.0), and +8.0 on the decks you faced.
  - Water: the first outside round of 12 lists didn't separate the lists (-2.2, -8.6 to +4.3). The 23-list result clears zero only barely (-4.1, -8.0 to -0.2).
- **Ignition's +3.7 includes the rounds that picked it.** On the rounds after the pick it's +3.5 (1,588 v 1,462 of 3,600; range +2.4 to +4.6 as you gave it, not recomputed by me).
- **"Only the three repeated" misses Oricorio.** Pooled, it cleared zero under both opponent bots, barely (+6.2, +0.3 to +12.0; and +4.5, +0.2 to +8.8).
- **Oricorio's one-matchup share.** Vespiquen/Shuckle gave 36 to 40% of the extra wins, not "mostly". With a tie counted as half a win it's 43 to 49% (your figure; I didn't recount the ties).
- **"The 11v3 package".** The bot backed one of its three swaps, Ignition. Victini for Cyrus pointed down (-2.9, range includes zero). Flame Patch alone wasn't shown (+1.4, the two rounds disagreed).
- **"No clear difference" misses Deck 17's Tool slot.** Heavy Helmet and Giant Cape both beat the Boat list: 661 and 666 v 613 wins of 1,800. Helmet v Cape is the part that showed no difference.
- **Goodra's record.** 9-8 over 17 games on that list (Oct 29 to Nov 6), not 5-8. Four of the wins ended at setup or with no damage, so 13 games show card use. My 5-8 was the 13-game count from the Nov 8 batch. I couldn't reopen the game log from this session, so 9-8 is your figure.

### The outside idea in C

Splitting wins by whether a card was played doesn't isolate what the card adds. Matchups, draws and game length explain part of the gap. It's a way to find games worth inspecting, not a way to call a card good or bad.

### Next step, restated

**Play the trial decks as you like. Agents compare the important decisions in your games with the bot's records for the same lists.**

- **The comparison is by opportunity, not by use rate:** had the card, had a useful chance to play it, played it, and what happened next. A mismatch is something to inspect. Matching percentages don't prove good play.
- **Source:** Pause Games stores no card plays, so this needs the per-game video reviews.
- **What it can't do:** with 2 to 13 games per deck it can only show very large differences. It should not decide the scale-down question in D. That stays your call on the whole picture.
- **Repairs:** only for pilot problems that could change a useful deck choice.
- **Rough cost:** depends on how many games need a video review; about 1 to 2% of the weekly meter for the games already reviewed, $0 of credits, no laptop time.

