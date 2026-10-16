# A look at the "Cliff" fork (IncredibleAloeVera/deckgym-core), Oct 16

Read-only. I read the clone at `/home/dacz8976/credit_work/cliff_src` (HEAD e69eea3, Aug 13 2026) and ran nothing from it. The only
code I ran was a small card-id checker of my own that reads its `database.json` and `auxiliaries/card_status.txt` as data.

## Short answer

**Not worth a trial run now. Worth a polite message to its author.** Cliff cannot play Dustin's Kingambit deck today, because the four cards that carry
the plan (Alolan Muk, Glimmora, Kingambit, Regigigas) are listed as not implemented in its engine. It also has no card from B4 onward, so nine of the ten decks I checked cannot be loaded as written. Its published evidence of strength is one rating number with no named opponent. Its engine
is about 7 weeks behind ours, and bringing it in would be a port of its RL code (about 48 files), not a swap of a bot.

## (1) Could Cliff play his decks' plans, and are his cards in its pool?

**Design.** The agent is a 1.26-million-parameter transformer (Burn framework) that sees only what a human sees (`RL_ARCHITECTURE.md`
§1.2): its own hand and deck contents, both boards, both discards, both Energy Zones. Of the opponent's hidden cards it sees counts, the
energy types it has watched, and whatever a reveal effect showed. The last 20 opponent choices are an ordered history token. The reward
is **win +1, loss -1, tie 0, nothing else**, with no discounting (γ=1, GAE λ=0.95) (§1.5.1). Training is self-play against past copies plus a
panel of the repo's simple bots, with the stated goal (§1.1.3) of piloting *anything well enough that results are about the deck*, "not to be
the best".

**Could it value a long-term sacrifice?** In principle yes. A terminal-only reward with no discounting lets "let Glimmora fall so
Overlord's Blade grows" pay off later. In practice there is no evidence it learned that. Three reasons:
- It trains on about 120,000 tournament lists drawn uniformly. Nothing in the data rewards a deck-specific plan like "hold Pawniard until
  a first knockout".
- The model is small and its design goal is uniform competence, not deck specialisation.
- No game of it playing a Kingambit-style deck is published. This is the same pattern as our September per-deck networks, only
  more general: that kind of agent plays a deck's plan only if it has trained on that deck.

**Pool check.** Its `database.json` has 3,520 cards, stopping at B3b plus P-A/P-B promos. Ours has 3,879.
The card status file lists 364 cards that exist but cannot be played (no logic).

| deck | not in its pool | in pool but not playable (no logic) |
|---|---|---|
| `01-kingambit-as-played` (all 15 lines) | none | **Alolan Muk B2 097, Glimmora B3a 045, Kingambit B3a 043, Regigigas B3 134**: every card the plan hangs on |
| brew 07 | Hoopa ex B4 103, Deceptive Needle B4 148 | none |
| brew 08 | Rainbow Cave B4 155 | none |
| brew 09 | Galarian Zigzagoon B4 095, Deceptive Needle B4 148 | none |
| brew 10 | none | none |
| deck 12 | Team Rocket's Goo-zooka B4a 068 | none |
| deck 13 | Team Rocket's Rattata B4a 058, Raticate ex B4a 059, Soothing Shore B4 154 | none |
| draft A (both files) | Carvanha B4 034, Mega Sharpedo ex B4 035 | none |
| draft D | Mega Houndoom ex P-B 080, Rainbow Cave B4 155 | Victini B3 025 |

Only **brew 10** (and draft C, which is not on the sheet) is fully inside the pool and playable. That is one of the ten decks checked.
(My first pass used a card-number pattern that skipped B4a lines; the table above is the corrected one.) B4 and later cards are absent
by design: "the freeze is what makes per-card embeddings affordable" (README).

## (2) What bringing it in would take

- **Engine distance.** Its tree branched from upstream around Jul 22 (last upstream merge #335); our merge-base with upstream is Jul 30
  and our notes cover upstream through Aug 30 and B4b. It lacks: B4, B4a and B4b cards (359 cards by database size: 3,879 vs 3,520); both of our rules switches (Oct 2 and
  Oct 12: coin-prevention round 2, Fossils as Item cards, Weakness on return damage); the Sleep/Paralysis fix (upstream #379); our PR
  #383 (Heavy Helmet and Harden limited to attack damage); and our players, `observation.rs` and `public_reply_evidence.rs`. A port
  means carrying its `src/rl/` (48 files, 366 tests), `src/belief/`, `models/` and the frozen text-embedding tables into our engine. Its
  tables are keyed to its 3,520-card pool, and the model's schema fingerprint (`0x4caea8b7fd0b4e2c`) would break if the card list
  changes. So running Cliff on our B4+ cards means retraining, not loading. That is a large job, not a trial.
- **Build needs.** Plain Rust builds the simulator. The model needs the `rl-model` feature (Burn 0.21, CPU). CPU play is about 90
  decisions/s (one game of about 70 decisions takes close to a second). The GPU path needs CUDA 13.3 and an NVIDIA card (about 1,050
  decisions/s). Training needs a GPU. I did not check whether Dustin's machine has a CUDA card.
- **Weights: yes, in the repo.** `models/Cliff/weights.mpk` (5.0 MB) plus `meta.toml`. It is the final model of an unpublished run, so
  there are no checkpoints and the run cannot be reproduced.
- The training code is in the repo and documented (`config/default.toml`, `train_player` example), but its cache of Limitless
  responses (334 MB) is not.

## (3) Evidence of strength

Almost none. `models/Cliff/meta.toml` gives a Glicko-2 rating of **1767 ± 5 after 576,316 games**, on a scale pinned so that the repo's
`er` (EvolutionRusher, a simple scripted bot) is the fixed origin. No one's rating for `er` is stated in the repo and the opponents of those
games are the author's own training pool, so the number says "it beat its own earlier copies", not how it compares with our k3/km3 or with
people. `PERFORMANCE.md` is a speed table only (15 games/s on GPU). There is no win rate against the repo's expectiminimax bots, against
any human, or on the ladder. The author's own design note says no absolute threshold like "40% vs expectiminimax" is interpretable.
The "intermediate levels" description comes from the Discord, and I found nothing in the repo that backs it.

## (4) The deck database

- **Format:** one text file per list in `decks/meta/` (9,579 files, one per archetype name; a list has `Energy:` plus `count set number`
  lines) and `decks/tutorial/` (four tier files). The code says the meta DB holds 120,444 lists in 8,849 archetypes; the files are
  the deduplicated and compiled form.
- **Source:** the Limitless API, every list played in a POCKET event **before B4 (Jul 30 2026)**. It is real tournament play, not tier-list
  guesses. Fetching takes about 11 hours and is rate-limited; the cache is not shipped. (The ~11 h figure is from its README.)
- **Freshness:** stops at the B3b era (mid-July). Nothing from B4, B4a or B4b.
- **Coverage:** wide for the old meta, but only lists whose cards the engine can run are kept. There are **zero lists with Kingambit**
  (B3a 043). Regigigas appears only as the A2 version (a different card from the one in Dustin's list).
- **Homebrew-style lists:** tournament lists are mostly established archetypes; they are not ladder-style brews and there are no
  ladder opponents. Our own ladder counts (29 of 40 opponents on established decks, 1 homebrew, 10 unidentified) are the better picture.
- **License of the data:** none stated. Limitless's terms govern its API data; I would not redistribute the lists without asking.

## (5) License and what else is worth taking

- **License:** GNU AGPL-3.0 (`LICENSE.txt`), the same as upstream and ours (`engine/LICENSE.txt`). Taking code is allowed if the
  result is also AGPL and carries its notices. Network use (a hosted service) requires offering the source.
- **Ideas worth taking:**
  - The **belief overlay** (`src/belief/`, `tests/belief_test.rs`): tracking what an opponent's hand can still hold after reveal effects,
    with tests. It is close to what our hidden-information boundary does, and a comparison could find gaps either way.
  - The **history token** idea: a pilot that reads the last 20 opponent choices to infer a plan.
  - The **ranking method**: Glicko-2 ratings with a fixed origin bot, selection on `rating - 2*deviation`. It is a cleaner way to compare
    pilots than raw win rates, and it is for pilot-vs-pilot, so it fits our Kingambit A/A1/A2 comparison.
  - **Card-status audit** (`card_status` binary, `auxiliaries/card_status.txt`): one list of unplayable cards.
  - The **tournament-list pipeline** (`build_meta_decks.py`): a path to a refreshed, post-B4 meta set if Dustin wants a broader deck panel.
  - Its commits are the work of several authors, including a Hisuian Goodra implementation from our own account (#335).

## (6) Recommendation

**No trial run of Cliff on Dustin's decks now.** It would fail at the first step (Kingambit's four key cards have no logic in its
engine), nine of ten checked decks are outside its pool, and a port plus a retrain is weeks of work for an agent with no measured strength.

What I would do instead:
1. **Message the author** on the upstream Discord, since Dustin wants to collaborate: say we run B4+ and a rules-corrected engine,
   offer our Muk, Glimmora, Kingambit and Regigigas logic if the author wants it, and ask what Cliff was measured against. The author is on a break, so
   expect no quick answer. Cost: a few minutes of Dustin's time.
2. **A cheap, safe trial, if Dustin wants one:** run Cliff on **brew 10** (the only checked deck fully in its pool)
   against our own tournament-list panel, **in its own engine, on CPU**, as a pilot vs `km3` and `er`. Cost: about 1-2 hours of a
   laptop for around 500 games, no change to our files. Build it in its own empty directory, away from our files. It would tell us
   whether it is strong at all, and nothing about Kingambit. The cost estimate is a guess from its speed table (about 1 s per game on CPU), not a measurement.
3. Keep our Kingambit work as planned (SPEC_AMENDMENT_1 / ITEM7). Cliff does not help there.
