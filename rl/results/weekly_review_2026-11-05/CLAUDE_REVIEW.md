# Claude-side weekly review, 2026-11-05

Written Thursday evening, Nov 5. This run fired off-cycle (the regular slot is Sunday evening; the last review was Nov 1), so it covers Nov 1 to Nov 5 only. Main is at 660d9a71. No `rl/results/weekly_review_2026-11-05/` folder landed, so there was no EVIDENCE, OUTSIDE_IDEAS, COMPETITIONS or DIAGNOSTIC file. I used memory, the main log since Oct 28, the kx3 diagnosis files on the laptop (`~/relplan/gemini/arch_diag/SUMMARY.md` and `~/relplan/gemini/k40read/K40_READ.md`, kept off GitHub), the R8 release notes, the kx3 re-pin reading, upstream's commits and PR list, and two fresh web searches. The weekly meter stood at 62% before this review, with 3 days 15 hours to the reset.

## A. Are we making progress?

**The engine moved. The bot's play did not.**

- **R8 is adopted (your "Adopt all three", Nov 4).** The official programs now play every real printing: all 260 Dual Fusion, SP1 and P-C cards (256 complete, 4 with unverified rulings), and the programs refuse no real card any more. Last week 55 of those printings were refused. The bot-protocol adapter is in the official build, and five rule rows went in from your clips and decisions (Misty and Sweet Honey choose first, Darkrai ex on effect attachments, Iris on every Haxorus printing, Triple Bombardment with one Benched Pokémon, the Starting Plains Knock Out).
- **The bot's decisions are unchanged on purpose.** The slow report's pilot was rebuilt on R8 and replayed its 202 development games: every game identical, kx3 and km3 alike. So no slow report moved because of R8.
- **We now know why kx3 lost the 20 Archaludon games to Gemini, and it is not what we guessed.** The diagnosis ran Nov 5 on the laptop at no cost. Of 21 judged decisions, Gemini's move was in kx3's candidate list every time, so the "missing from the shortlist" theory is dead. In 16 of 21, the 16 play-outs per move simply could not tell the moves apart, and kx3 kept km3's move as designed. In the 5 clear cases, the play-outs overrode km3 and every time chose a passive move (end turn or retreat). One of those was read in full: on turn 6, with a ready 2-point Knock Out, kx3 passed because its play-outs assumed the opponent would waste Energy on the stuck Pokémon and that kx3 would attack next turn. In the real game neither happened and kx3 lost 2-3. That is understanding, not a fix. The bot plays exactly as it did last week.
- **Upstream (secondary):** #441 merged Nov 2, so every deckgym user now gets Misty and Sweet Honey choosing the target before the coins, as the real game does. That makes 28 of your PRs merged in all. Upstream's main also took two fixes from another contributor (#440 Clear Veil Energy discard, #442 stale Ability offer after a Knock Out while evolving) that our fork does not have yet.
- **Your decks:** 17v2 went 4-6, 14v4b 2-3, 11v3 2-2, 13v3 1-1. Decks 25 to 31 are built with no games yet. Astra's 14v5b (Steel Apron) is on the page, your call.

## B. Is the bot the right way?

**Your own Nov 5 summary was mostly right: kx3 is an adapter on km3, and neither gets smarter.** The numbers: kx3 changed km3's move at 28 of 686 decisions (4%). On the labelled exam, Gemini agreed with the labels 62%, km3 about 45%, kx3 43%; of kx3's 89 overrides there, 6 were right and 25 wrong. In bot-versus-bot games kx3 beats km3 53% to 32%. So kx3 is better at beating bots and no better at matching a person's judgment.

- **The diagnosis narrows the cheap fixes to almost none.** The limiting part is the play-out evaluation (km3 against km3, 16 rounds, an opponent that misplays), not the candidate list. More rounds would be a new pilot code and roughly four times slower; kx3 already took 188 seconds on one decision under load this week. Gemini inside the play-outs would cost about $700 to $1,300 per game. Training a pilot on Gemini's 1,278 decisions is far short of the 2.6 million the smallest outside team used.
- **The maintainer's generalist model is still the realistic route to a better pilot, and it still has not appeared.** I checked upstream's commits through Nov 2: card fixes only, no model code. Nothing on the web either.
- **What I'd do:** take the laptop's proposal when it lands (you said "See proposal first"), and treat "no change to kx3" as the default answer unless the proposal shows a small, supported repair. Keep the engine, keep converging with upstream, keep reading your games.

## C. Outside ideas

Searched Nov 5. Thin week: nothing new changes the plan.

1. **The deckgym generalist AI:** no release, no code upstream through Nov 2 (checked by listing the repository's commits). The cheap check stands from Nov 1: one Discord message from you asking whether it will be shared and what test positions would help. Cost: the message.
2. **Pocket Showdown (jiro-games)** is a Pocket simulator with a battle mode against AI difficulty levels. I could not confirm a licence or how its AI plays. Cheap check, only if you feel like it: three hand games against its hardest setting with one of your decks, to see whether it carries a plan better than km3 does. Cost: your time, nothing else. Low value; skip it if the proposal keeps you busy.
3. **From Nov 1's Kaggle winner, now directly usable:** when comparing two versions of a deck, 100 games per pairing is too few and 500 or more are needed. That backs your doubt about the bot deck tests and your 10-game habit being a feel, not a verdict.
4. **From this week's own diagnosis, one cheap comparison:** re-score the 5 passive overrides with 64 play-out rounds instead of 16 on the trace build, no pilot change, to see whether the passive preference survives more rounds. About one laptop hour, no credits. This belongs inside the laptop's proposal, not as a separate job.

## D. Is this asinine for a student with one laptop?

**No. But the bot side has reached its honest ceiling for one laptop, and this week showed where that ceiling is.** One laptop did, this week: full card coverage on the engine, a $0 diagnosis that explained the Gemini gap mechanically, one more rules fix accepted upstream. One laptop cannot: make the pilot judge positions like a person without heavy compute or a paid AI on every decision. The shape that fits one laptop is engine upkeep, upstream fixes, readings of your games, and your own deck loop. That is a smaller project than the one started in the summer, not a failed one.

## Verdict: LOW-COST MAINTENANCE WEEK, amended the same evening to REDIRECT

**Amended Nov 5 ~22:30Z after Dustin's read.** The laptop's proposal had landed earlier that day and Dustin chose "no change" (A). Then he pasted an outside AI review of kx3 and, after my check of its claims, reopened kx3 in his own words: "Yes, the replay", and "Stepwise repairs are going nowhere, a few big swings are needed sometimes. If it fails, at least we tried something new."

**What the outside review got right (checked on main and the K8 commit):** kx3's play-outs run a full km3 search on both sides to the end of every practice game, 16 rounds per move. km3's evaluator leaves most of its own switches off: the Bench-attacker weight is 0, two other weights are 0, and the old "HP times Energy plus one" board score is still in use, so Energy on the Active Spot scores higher than Energy on a Benched attacker. Its "loses 20-4" is the split deals only; the whole Gemini test was 73 to 56. Its switches are "written and tested", but most were tried one at a time and lost to km3, so written is not the same as shown to help.

**Next step (his decision):** on a branch, on the laptop, no credits, in this order:
1. **Tonight:** sequential halving in the play-outs (same total work, the top two moves get 48 to 64 paired rounds) replayed on the six Archaludon decisions where 16 rounds could not separate the moves or chose a passive override (0024, 0044, 0047, 0090, 0091, 0010 K[40]). Report: time, the top-two gap, whether it clears the noise bar, the chosen move.
2. **Then the swings, sized by the laptop first:** a `kz3` evaluator preset with km3's off switches on; shallow play-outs tested on their own (they weaken the simulated opponent); an offline fit of the evaluator's weights to the Gemini traces, with the human exam locked out of it.
3. **Not doing:** the outside review's bot deck tuner (32 deals per package is far below the 500 the Kaggle winner found necessary, and it is against your standing rule); no slow-report change, no per-card patches.

- **Gates kept:** each variant is its own pilot code; the 24 split deals are development, the other 104 regression; fresh deals and decks before "better".
- **Cost:** about 2 to 3% of the weekly meter per evening of laptop work, no Google or API credits, one laptop evening for step 1.

The next regular review is Sunday Nov 8 and will cover step 1's result.

## Sources (checked Nov 5)

- Upstream commits and PRs: https://github.com/bcollazo/deckgym-core (commits through 97b8787, Nov 2; PRs #440, #441, #442)
- Pocket Showdown: https://github.blesdmm.dns-dynamic.net/jiro-games/pocket-showdown (licence not confirmed)
- DeNA's official TCG Pocket AI talk (from Nov 1, unchanged): https://www.invenglobal.com/articles/24133/how-reinforcement-learning-ai-tackles-the-complex-rules-of-pok%C3%A9mon-trading-card-game-pocket
- Kaggle PTCG AI Battle Challenge write-ups (from Nov 1, unchanged): https://ptcg-abc.pokemon.co.jp/?lang=en
