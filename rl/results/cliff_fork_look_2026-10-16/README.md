# A look at the "Cliff" fork (IncredibleAloeVera/deckgym-core)

Oct 16, 2026. Read-only: I read the fork's README, performance and design files, its file list, its card
list and its card-status list. I did not build or run any of its code, and nothing was posted anywhere.

## Short answer

**Not worth a trial run now.** Cliff cannot play the decks Dustin actually plays. Its card pool stops
one expansion before his ladder decks, and the four cards that carry his Kingambit plan do not work in
its engine at all. A few of its ideas and its tournament-deck archive are worth borrowing later (last
section); the bot itself is not.

## What it is

- A fork of the same upstream engine we started from, branched around Jul 22, 2026. The last change was
  Aug 13, 2026; there are no releases. The author's aim is stated in the README: a pilot that plays
  *any* deck well enough that a result belongs to the deck rather than the pilot. It is "not to be the
  strongest."
- "Cliff" is one trained neural-network player (about 1.26 million numbers, 5 MB, `models/Cliff/weights.mpk`,
  committed in the repo). It reads only what a human can read: its own hand, both boards, discards, and
  the opponent's hidden cards only as counts plus Energy it has watched arrive. No engine internals, no
  peeking at the opponent's hand.
- The deckbuilding half of the project is "not started" (their words).
- License: AGPL-3.0, the same as our engine folder, so copying code or weights is legally fine for us.
  I did not check the terms of the data behind its deck archive (see below).

## What I checked

**1. Can it play Dustin's plans? No.** Its card pool stops at expansion B3b (3,520 cards). I checked every
card of our decks against its card list and its list of cards whose effects the engine has not
written (364 of 3,520). Full output: `pool_check_output.txt`; the script is `pool_check.py`.

| Deck | Result in the fork |
|---|---|
| Kingambit as played (and the Muk/Glimmora/Regigigas file) | All cards exist, but **4 do not work**: Kingambit's attack, Glimmora's ability, Alolan Muk's ability, Regigigas's ability. The fork's deck databases drop every list that needs such a card, so Cliff never saw this deck type in training. |
| Brew 07, deck 12, deck 13-A (its Giant Cape and Big Malasada variants miss the same cards), brew 08, brew 09, draft A (both), draft D | **Not in the pool.** Each uses cards from B4 or B4a (Hoopa ex, Mega Sharpedo ex, Team Rocket's Raticate ex, Rainbow Cave and so on). Draft D also has Victini with an unwritten ability. |
| Brew 10 | The only ladder-sheet deck that fits. |
| The 8 panel lists | 4 fit (Altaria, Blaziken, Lucario, Sceptile); 4 do not (Hydreigon, Suicune, Vespiquen, Weezing each need a B4/B4a card). |

So: 1 of his 8 ladder-sheet decks and 4 of the 8 panel lists could even be dealt to Cliff, and Kingambit
cannot. Its multi-turn plan (hold Pawniard back, let other Pokémon fall to grow Overlord's Blade, wall
with Regigigas) is exactly the kind of thing I found no evidence for either way, since it never played
those cards.

**2. How strong is it?** The only strength number in what I read is a rating in `meta.toml`: 1767 on a
rating scale pinned to "EvolutionRusher", one of the fork's own simple built-in bots, over 576,316
games, which by the design document were played inside the training pool (its own earlier copies and the
fork's bots). If that pinned bot sits at the usual
1500, a gap of 267 points is roughly an 82% expected win rate against it. I did not find the pin value
written down, and found **no published results against the stronger search bots, against our pilots, or
against people**. The README gives speed only: about 1,050 decisions a second on an NVIDIA GPU, about 90
on a plain CPU (roughly one game per second or two). The training run that made it is not published, so
nobody can rerun or extend it.

**3. What would it cost to try?**

- *As-is, on a cloud worker (no GPU needed):* build the Rust fork, then play Cliff against the fork's own
  bots on decks inside its pool. About half a day of my time plus a few CPU-hours. It would only tell us
  how strong Cliff is in its own engine. It cannot be compared with our pilots (km3, kx3), which live in
  our engine, and it covers 1 of his 8 ladder decks.
- *Making Cliff pilot our engine:* port its ~48 model/training files and the hidden-information tracker
  onto our game state (ours has different mechanic names, trainers keyed differently, and our own rule
  fixes). The weights are tied to its frozen B3b card list, so every B4 deck needs a **retrain**, which
  the README builds for a CUDA 13 NVIDIA card (their reference machine is an RTX 3050 laptop GPU). Dustin's
  laptop has only an AMD integrated GPU. This is weeks and an unknown GPU bill; I do not recommend it.

**4. Its deck archive.** `decks/meta/` holds 9,579 archetype files, 18.6 MB: decklists actually played
in tournaments, pulled from the Limitless public API, **only from before B4** (cutoff is a setting).
They are real field data rather than ladder data, and a stale one for Dustin's season. The fetch script
(`auxiliaries/build_meta_decks.py`, standard library only) is resumable and rate-limited; a full fetch
is about 11 hours, so a fetch limited to B4-era tournaments would be far shorter. I did not check
Limitless's terms of use for bulk collection. That is the first thing to check before using it.

**5. Other things.** Their `tests/belief_test.rs` and `src/belief/` track what the opponent has revealed;
their `card_status` list names the cards the engine cannot run; the fork also lists a rating system
(Glicko-2 with a pinned reference bot) and a throughput table (`PERFORMANCE.md`: the simple search bots
run 230 to 740 decisions a second).

## Worth borrowing later (small, not now)

1. **A current tournament field as a matchup opponent set.** Run the fetch script with the cutoff moved to
   after B4 and keep the top lists per archetype. Gives the "bad matchups" tables something real to check
   against besides the 8 panel lists. Needs the Limitless-terms check first and a decision from Dustin on
   whether tournament lists stand in for ladder decks (we know ladder opponents are mostly unmapped).
2. **The rating idea:** put each pilot version on a scale pinned to one never-changing simple bot, so
   versions can be compared without re-running a shared panel. Only useful if we start training pilots.
3. **Nothing else** I would take: their pilot is a different design from ours (a neural network trained by
   self-play, not rule-and-search) and the part of it that matters to Dustin, playing his B4-era decks,
   is the part it does not do.

## Recommendation

No trial run. If Dustin wants one anyway, the cheap version is the first bullet of section 3 on a cloud
worker; it would tell us nothing about his decks and I would not spend on it before the Kingambit pilot
(ky3) review is done.
