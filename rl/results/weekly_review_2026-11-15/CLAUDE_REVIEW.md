# Claude-side weekly review, Nov 15, 2026

Read for this: the queue note, the tried-before index, this week's EVIDENCE.md (the only file in the week's folder; OUTSIDE_IDEAS.md, COMPETITIONS.md and DIAGNOSTIC.md do not exist in either place), main at 4fe43742 (local and GitHub match), the upstream PR list, and a fresh outside search. Weekly meter at the start of this review: 78%, 17 hours before the reset.

## A. Are we making progress towards your goals?

On the goal itself, no. You wanted a bot reliable enough to test unusual combinations. It does not exist, and nothing this week moved it closer.

- **One thing the bot can do now that it could not last week:** it counts random-target attacks (Draco Meteor and similar, 30 printings) instead of reading them as 0 damage (ledger C11). Worth about +2 points on the two lists tested, and nothing on lists without those cards.
- **Two repair attempts failed their own checks:** longer look-ahead did not fix the passed-up Mega Burst knockouts (C10), and setup play-outs changed 0 of 230 setups (C12).
- **Not progress by your rule:** the gap investigation, the ledger, the Match Log page. The Match Log is useful to you and to deckgym's creator, but it does not make the bot better.
- **Upstream:** no new fixes this week. The total stays at 26 merged, none open, and upstream's code has not changed since Nov 2.
- **Your own games were the best deck evidence of the week:** 12-3 with the Magnezone / Miraidon ex list. That is your play, not the bot's.

## B. Is the bot as built the right way to get there?

No, and this week made that clearer. The gap investigation showed a bot score of 55 goes with a real record of about 48-51 (J11), and the two most reasonable remaining repairs failed. More switches on this bot have no credible reason to work (your Nov 14 conclusion; the ledger agrees for families A, B, C and E).

The alternative I was told to weigh, the deckgym creator's play-every-card AI, is not a way out yet either. His words on Nov 15: "Its still not ready... Full generalist and strong is fairly hard and might need compute." That says his is not ready. It does not say it is impossible.

What is worth keeping: the engine (26 accepted fixes), the records, and the narrow jobs the bot can do (telling clearly weak lists from established ones, counting how often a situation comes up, one named question on one deck). What is worth your time now: real tournament data and your own games.

## C. Outside ideas (searched today; pages opened by me)

Nothing new plugs in. What I checked:

- **DeckGym's new connector (new this week, and it works).** I called it: 2,353 tournament lists from the last 7 days; Magnezone / Miraidon ex is 4th at 4.4% of the field, 53.5% wins, 103 lists from 16 events. It also gives the common 20 cards, which cards every list plays, and the slots that vary. Already tried: Codex's Nov 8 library (160 lists from 20 events). What is different: it is current and about 15 times larger, but it gives no event names or dates, so the dated library stays. **Small cheap comparison, already run on your list:** your 20 differ from the common list by two cards. You play Pokémon Center Lady and Eviolite; the common list plays Serena's Choice (the tool marks it as in every list's core) and Giant Cape (47% of lists). Pokémon Center Lady is in 34%; Eviolite is not among the common choices. This is a lead from other players' lists, not advice, and I have not checked how the tool defines "core". https://www.deckgym.com/mcp
- **pocket-zero** (ledger N5/N6): only automatic list updates since Oct 16; the published network is still the Oct 14 one, and its page does not mention Dual Fusion cards. Unchanged: needs your yes, and would need current cards added before it could play your decks. https://github.com/Undi95/pocket-zero
- **The Pokémon Company's Kaggle contest (main card game):** the final round is still listed as "later in 2026", not held; the winner's code is still "available after the second round". https://ptcg-abc.pokemon.co.jp/ and https://github.com/yijieyuan/kaggle-pokemon-tcg
- **deckgym-core:** no release, no public learning code, last change Nov 2. The creator's other public projects show nothing new.
- **Papers:** two searches found nothing from October or November on judging decks or planning in games like this. sethkarten/tcg, which EVIDENCE.md describes, still returns "not found" when opened, so that description is unchecked.

## D. Is this asinine and impossible for a student with one laptop?

The goal is not asinine. But a bot that reliably judges unusual decks is, on this week's evidence, out of reach for one laptop right now: three months of our attempts are in the ledger, and the person best placed to build one says his is not ready and may need more computing power. What one laptop can do today is the smaller set of things in B. Scaling down to that is the honest answer for now, with the weekly search watching for the thing that changes it (a public model that plays current cards).

## Verdict: low-cost maintenance week

**One next step:** look at the two cards where your Miraidon list differs from the 103 tournament lists (Serena's Choice and Giant Cape, against your Pokémon Center Lady and Eviolite). I can pull which real lists play each and how they did, and you decide whether to try either in your own games. No bot test: the bot under-rates this deck more than any other, so its numbers would be weak evidence. The decision it changes: whether those two slots are worth your playing time. Cost: under 1% of the weekly meter, no API credits, no laptop time.

## Astra's review: where we agree and differ

Astra's weekly note (Nov 15, noon) was read after the above was drafted.

- **Agree:** the reliable evaluator is not delivered; the random-target repair is real but small; C10 and C12 close those setups only, not planning in general; more switches on the same bot are a weak investment; nothing outside is ready to install; DeckGym's connector is useful but lacks event dates (I confirmed that from its answers).
- **Differ on the verdict.** Astra says redirect: write one costed proposal to replace the bot's judging part with one that sees individual cards and learns from better consequence labels, with a small first prototype. I say maintenance. The files support caution: Astra's own note says the missing ingredient is a trustworthy source of those labels, and the ledger (D6-D9) shows four attempts that lacked exactly that. Until someone names that source, a proposal has nothing new to stand on. If you want to keep investing in the bot, Astra's is the right shape for it, and writing the proposal would cost roughly 1-2% of the meter. My verdict does not change.
- **Astra caught, and I checked:** EVIDENCE.md's "no outside generalist bot exists" overstates the creator's message; he said his own is not ready. I worded B accordingly.
- **Astra caught, not rechecked by me:** the "19.5 points" Magnezone gap shorthand in the queue and EVIDENCE.md does not carry the later exact-list correction (J12). The ledger still shows 19.5 under J11; I did not re-derive it.
- **pocket-zero:** Astra counted its card file (4,317 printings, none from Dual Fusion). I only read its page, which fits that.
