# Setup tester: build spec (Kingambit first)

## Purpose
For one deck and many versions of it, the tester shows how often the cards let the deck carry out its opening plan: which Pokémon are in play by each of its own turns, how soon the evolutions land, how often a turn does nothing for the setup, and, for Kingambit, how often it attacks with a big Overlord's Blade before the opponent takes 3 points. It uses exact formulas where they exist. Everywhere else it runs a seeded simulation of our own cards under a fixed, written-down script, on the same deals for every version. It answers "what does this change do to my setup, and what does it cost?" It does not say who wins, and it does not search for the best list.

## Inputs
- **Deck files** in the repo's format. Each version first passes `lib/deck_check.py` (20 cards, at most 2 per id and 2 per printed name, a Basic). The 4 Pawniard printings share one name limit.
- **A versions file** (JSON): `base`: a path. `versions`: each a path, or a diff on the base such as `["-1 Copycat B1 225", "+1 Juliana B3a 071"]`. `swap_pool`, optional: adds every one-card swap of a non-plan card for a pool card (one swap per version). At most 100 versions per run. `plan`: the plan config.
- **The plan config** (JSON, one per deck): key Pokémon, main attacker, lead order, promote order, Blade target, Copycat rule, the opponent's hand size for Copycat (4), the Bench slots kept for plan Basics (Pawniard), and the horizon (8 own turns). Card facts come only from `lib/card.py`.
- **Seeds**: a new block, proposed as 24,700,000,000–24,709,999,999, above every block in START_HERE's table. The laptop records it there before the first counting run. Deal i uses seed base + i in every version; deals 0–99,999 are the standard set.
- **The first run**: the base is his list `73dfed58d1d6` (`rl/results/pause_games_new_2026-10-13/decks/KW261012_203719000.txt`). Pick lists by card-list id, never by file name: 2 of the 14 KW files are a Haxorus deck. Deck 01 (`35d98d0dcaf2`) runs beside it, because every Kingambit bot number so far was played on its list.

## Exact part (no simulation; pinned rules-switch-2 engine, main 70319c3d, engine unchanged since c045ede)
**The deal** (`deck.rs:129-153`): the top 5 cards are the hand. If none is a Basic, one random hand slot is swapped for a random Basic from the other 15, and those 15 are reshuffled. No mulligan.

**Formulas**, with b Basics in 20 cards: P0 = C(20−b,5)/C(20,5). A 1-copy Basic is in the hand with chance 5/20 + P0/b; a 1-copy non-Basic with 5/20 − [C(19−b,4)/C(20,5)]/5. Other cases: enumerate what the random 5 hold, then apply the swap (`consistency.opening_exact` already does this for single cards).

**Also exact** (natural draws only: no Supporters, Items or Mesagoza): **cards seen by own turn N** = 5+N in both seats, because the first player draws on turn 1; the 15 cards left after the deal are in uniform order, so draws are hypergeometric. **Basics in the opening hand** (1, 2, 3 or more) and each Basic's chance of being the only one. **Energy by own turn N**: N−1 going first, N going second. **Kingambit's earliest attack**: with Rare Candy, own turn 2 going second or own turn 3 going first; through Bisharp, own turn 3 in either seat.

**Anchors** (deck 01 and his list both have 5 Basics; all rechecked by exact enumeration, Oct 15):

| Quantity | Exact |
|---|---|
| P0 | 0.19369 |
| Pawniard in hand | 0.28874 |
| Kingambit in hand | 0.23709 |
| Rare Candy in hand | 0.23709 |
| Pawniard, Kingambit and Rare Candy all seen in 7 cards | 0.03373 |
| The same three, all seen in 8 cards | 0.05246 |
| Pawniard the only Basic (forced Active) | 0.12678 |

## Simulation part
**Engine rules to follow** (the code cites the engine file and line for each): hand limit 10, extra draws skipped; empty deck, no draw; Bench of 3; one Supporter per turn (allowed on the first player's turn 1); one Stadium per turn. No evolution on your own first turn or on a Pokémon placed this turn; at most once per Pokémon per turn; Energy carries over. Rare Candy: not on your own first turn, needs a Basic in play since before this turn, matches by name (any Pawniard can become Kingambit with no Bisharp in the deck). Searches pick uniformly over cards. **Not yet checked in Pocket** (flag the measures they touch): Poké Ball over cards or over names (open question #24), Sightseer's missing hand-limit check, Communication's draw order.

**The script**, each own turn:
1. **Setup** (before turn 1). The Active is the first Basic in hand by the lead order. Proposed default, from his 12 games (`positions_all.json`, his turn 1, games where he placed 2+ Basics: Regigigas 3, Glimmet 2, Pawniard 1): Regigigas, Glimmet, Alolan Grimer, Pawniard. The other Basics go to the Bench, Pawniard first, up to 3.
2. **Draw 1**, the first player's turn 1 included.
3. **Repeat until nothing changes:** (a) **Items:** Poké Ball while the deck holds a Basic; Rare Candy when legal; Communication while a plan piece is in the deck, trading the Pokémon in hand earliest in the promote order, never a plan piece. Never Lucky Ice Pop or Heavy Helmet. (b) **Mesagoza:** play it if none is in play, use it every turn, assume it stays. (c) **Place Basics**, Pawniard first, but keep one Bench slot free while Pawniard is still in the deck or hand. (d) **Evolve** every Pokémon that legally can, except Pawniard into Bisharp (step 4). (e) **One Supporter**, the first that applies: Juliana, if Kingambit is in the deck. Lisia, if a Basic of 50 HP or less is in the deck and the Bench has room (in his list only Pawniard B3a 041; Glimmet has 60 HP). Sightseer. Professor's Research, if the hand has 8 cards or fewer. Copycat, if the hand holds no Kingambit or Rare Candy and our hand without the Copycat is smaller than the opponent's. The opponent's hand is the config value, 4 by default (his 12 games: median 4, range 1–8 at the start of his turns), the same under every clock. Never Ilima.
4. **End of the turn:** a Pawniard still in play evolves into Bisharp if one is in hand. (Done last so that a Kingambit found later in the turn can still use Rare Candy.)
5. **Energy** goes to the first that applies: Kingambit, if it has fewer than 2. Bisharp or Pawniard, if fewer than 2. Regigigas, if Muk is in play. Otherwise the Active.
6. **Attack:** Kingambit uses Blade if it is Active with [DD]. Nothing else attacks; our knock-outs of their Pokémon are not modelled.
7. **Opponent's turn** (clock measures only): apply the clock. A knock-out removes our Active. Promote Kingambit if it has [DD] and k is at least the target; otherwise in this order: Glimmora, Glimmet, Alolan Grimer, Regigigas, Muk, Bisharp, Pawniard, Kingambit. No retreats.

**Dustin confirms five choices:** the lead order, the promote order, the Copycat rule, the Blade target (2, or 3 for the 180 line), and what "a fast deck" means (C-fixed below). Each is a config value. One alternative of each is run once on the base, plus Poké Ball over names and the opponent's hand at 2 and 6, to show how much each matters.

**Why this is not a bot pilot.** It plays fixed priorities, looks no turns ahead, and never sees the opponent's board. It measures what the cards allow under a stated plan, not km3's or kx3's choices; km3 also values Blade only at its printed damage.

**It can represent:** draw, search, evolution and Energy timing; Rare Candy legality; the Bench, hand and Supporter limits; Mesagoza coins; the knock-out count and Glimmora coins under a given clock.

**It cannot represent:** disruption (Red Card, Iono, Mars, Item or Supporter lock, Evolution Jammer, Primeval Law, a Stadium replacing Mesagoza); Bench snipes or damage built up over turns; our attacks or a high-HP wall slowing their clock; retreats, his judgment, or win rates. Cards the script never plays (Lucky Ice Pop, Heavy Helmet, Ilima) count as blanks.

## Measures (each going first, going second, and pooled)
The setup measures (G, K1, K2, K6) run with **no knock-outs**, so no clock or deal end touches them. The clock measures (K3–K5) run once per clock.

| Id | Measure | How |
|---|---|---|
| G1 | Basics in the opening hand (1, 2, 3 or more), and each Basic's forced-Active chance | exact |
| G2 | Each key card in the opening hand, and seen by own turn 1–5 by natural draws | exact |
| G3 | Each key Pokémon in play at the end of own turn 1–5 | simulated |
| G4 | Each evolution done (Stage 1 or Stage 2 in play) by own turn 2–5 | simulated |
| G5 | Empty turns: own turns with no Pokémon placed or evolved and no draw or search card played. Share of games with one in own turns 1–3; mean number in own turns 1–5 | simulated |
| G6 | The main attacker in play with its full attack cost attached, by own turn 2–5 | simulated |

**Kingambit plan lines, PROPOSED.** Dustin confirms or rewrites each before any is reported to him.

| Id | Plan line | Definition |
|---|---|---|
| K1 | Pawniard in play | By setup (exact: 0.28874) and own turns 1–5 |
| K2 | Kingambit in play | By own turns 2–6 |
| K3 | Kingambit's first attack | The first own turn it is Active with [DD] and attacks; distribution by turn, plus the share that never attack. Its Blade is 60 + 40·k, k = all our knock-outs so far, Glimmora heads included; the k distribution (0, 1, 2, 3+) is shown with it |
| K4 | Big Blade in time | Blade ≥ 140 (target 2) or ≥ 180 (target 3) used while the opponent has fewer than 3 points, by the horizon. Opponent points = k minus Glimmora heads |
| K5 | Pawniard lost before evolving | Pawniard knocked out as our Active, under the clock, before it evolves; shown beside the exact forced-Active chance |
| K6 | Muk with Regigigas | Alolan Muk and Regigigas both in play by own turns 3–5 (Regigigas B3 134 can attack only while Muk turns off its Seal of Antiquity) |

## Opponent clock
Blade's damage and the opponent's points move on one counter, so the tester samples our knock-outs per opponent turn, not points. It works out the points from its own victim: a knocked-out Glimmora flips its coin, and heads gives 0 points. At the start of our own turn t, k counts knock-outs on opponent turns 1 to t−1 if we went first, 1 to t if we went second. A deal ends when the opponent reaches 3 points or our last Pokémon in play is knocked out.

**Clock sources.** Every table header names the one it used and its games.
- **C-his**: his 12 Kingambit games in `rl/results/pause_games_new_2026-10-13/v2/positions_all.json` (positions v3, main 358562b2): 9 going first, 3 going second. Knock-outs on an opponent turn = the rise in `me.knockouts` between his consecutive turns. Each timeline stops at his last recorded turn (015011 at turn 2); the packet's outcome says whether the opponent's third point came next (one more knock-out, then complete) or the game is cut off (undecided from there). A rise across a missing turn (015659 has no turn 6) is undecided for those turns. The headline samples all 12 games by the opponent's own turn number; the seat-matched reading (9 and 3 games) is shown beside it.
- **C-bot**: the 64 deck-01 rows of `rl/results/kx3_on_rules2_2026-10/replay_b/games.jsonl` (the file has 192 rows over 3 decks; 42 deck-first, 22 opp-first), km3 and kx3 against km3 on the 8 panel lists. Only decisions with 2+ choices are logged, so forced promotions are missing as well as Bench knock-outs. Per opponent turn (game turn `t`), k = the larger of the logged `Promote` with an empty Active and the opponent's points `p` at the next logged decision. A lower bound. Older-engine runs are a labelled check only.
- **C-fixed**: set paces, no sampling. Fast: one knock-out on each opponent turn from their turn 2. Medium: the same from their turn 3. Slow: their turns 3, 5 and 7. "Fast" is the proposed reading of "a fast deck"; Dustin confirms it.

**Sampling.** Deal i draws one recorded game by a random stream keyed by i alone, so every version meets the same clock on the same deal. If the record ends before a measure is decided, the deal is undecided, and the number is shown twice: undecided counted as no, and as yes.

**What the independence assumption costs.** The clock is treated as independent of this deal's draws and board:
1. Real opponents slow down when we hit back and speed up when we stall, so differences between versions that change setup speed are probably understated (reasoned, not measured).
2. Every knock-out lands on our Active, whatever its HP; in real games which Pokémon falls, and when, depends on what we expose.
3. C-his carries his own fodder choices and walls (he led Regigigas in 3 of 6 games with a choice).
4. C-bot is km3 and kx3 on deck 01 against km3 on fixed lists, not ladder players.

**Width.** For C-his and C-bot, a bootstrap over the recorded games (1,000 resamples) gives the real width. Each deal's results are kept by the game it drew, so a resample only reweights those per-game tallies; nothing is re-simulated. Differences between versions under a clock use the same bootstrap.

## Output
Each run writes to `rl/setup_tester/runs/<date>_<deck>/`:
- **`results.json`**: every measure's x, n and Wilson 95% range, per version, seat and clock.
- **`RESULTS.md`**: **a table per version** (measures in rows; going first, going second and pooled in columns, each "p% (lo–hi)"). **A paired comparison against the base** on the same deals: mean per-deal difference ± 1.96·sd/√n (`paired()` from `rl/results/draft_A_v_fire_2026-10-02/analyze.py`, copied, since that file imports `decks/screen/floor.py`); bootstrap ranges for clock measures. A difference is flagged when its range excludes 0 **and** it is at least 1 percentage point. **A plain summary per version**: what it gains, what it gives up (flagged losses only), the clock used, and "not valued here" for every changed card the script never plays. **The run record**: the code's sha256, the engine commit, the seeds, the deal counts, the clock source paths, and the wall time.

**Pairing.** Every Pocket deck has exactly 20 cards, so one shuffle of 20 slots serves every version. A version's cards take the base's slots: same id first, then same name, then the rest in sorted order; a one-card change alters one slot in every deal. Searches take the found card and leave the rest of the deck in place (the same odds as the engine's reshuffle, because the order was already random); cards that go back into the deck (Copycat, Sightseer, Communication) go to random places. Each random choice (shuffle, search pick, coin, clock) comes from its own stream keyed by deal, purpose and count, so versions stay on the same cards while their play is the same.

## Tests to write first
1. **Exact formulas** match the anchors to 5 decimals. With searches off, the simulation agrees within 4 standard errors at 400k deals.
2. **Hand-checked fixed-order decks:** Rare Candy refused on own turn 1 and on a Pawniard placed that turn. With Pawniard the only Basic (so Active), Kingambit's first attack is on own turn 2 going second and own turn 3 going first. Bisharp, Juliana and Rare Candy in hand on own turn 2 give Kingambit that turn. Pawniard always finds a Bench slot. One Supporter per turn; Bench cap 3; hand cap 10; Energy N−1 going first. Blade 60, 100, 140, 180 at k = 0–3 under a fixed clock. A forced Glimmora heads gives 0 points, tails 1. Losing the last Pokémon in play ends the deal.
3. **Reproducibility and pairing:** the same seed gives byte-identical output; reordering the versions file changes nothing; a printing-only version gives identical numbers; swapping one never-played card for another (Lucky Ice Pop for Heavy Helmet) gives identical per-deal results; searching without the reshuffle matches an explicit reshuffle within 4 standard errors at 400k deals.
4. **Direction, on his list:** −1 Copycat +1 Juliana raises K2 at own turns 2–3. −1 Rare Candy (no Bisharp) gives K2 = 0. +1 Bisharp B3a 042 (the Darkness one) in place of a Lucky Ice Pop raises K2 at own turn 3 and, with the Mesagoza coin forced tails, leaves K2 at own turn 2 identical deal by deal in both seats. +1 Lisia in place of a Lucky Ice Pop raises K1 at own turns 1–3.
5. **Clock and Copycat:** C-his reproduces `me.knockouts` at every recorded turn of the 12 games; Copycat draws 4 under every clock.
6. **Against `lib/consistency.py`** on deck 01 (Kingambit in play by own turn 2/3/4/5 going first: 8/15/24/34%): every gap is explained by a named difference in the script. A gap is not a failure.
7. **Against the bots** (once, deck 01, C-bot): K3 printed beside the first Overlord's Blade turn in the 64 games. A gap is printed, not a failure.

## Run size and speed
Per version: 100,000 deals with no knock-outs, and 20,000 per clock (the recorded games, not the deals, limit those). Exact measures once per version. Target: at least 2,000 deals per second per process in standard-library Python, `multiprocessing` one version per task; the builder reports the measured rate. 30 versions are then about 6 million deals, about an hour on one process. Long runs go detached on the laptop, outside its quiet hours.

## Out of scope
Win rates, matchups, opponent decks, searching for the best list, bot piloting, and anything that needs the engine binary. Bot numbers stay in their own reports and in the version journal.

## Build rules
A Sonnet credit worker builds it in standard-library Python, tests first, and the laptop reviews. It reads `lib/`, `engine/src` and the data files above, and writes only to `rl/setup_tester/`. It imports `lib/consistency.py` helpers (`read_deck`, `classify`, `opening_exact`; the import has no side effects) but never calls that file's `build()` or `main`, which write into `decks/`. Cards come only through `lib/card.py`.
