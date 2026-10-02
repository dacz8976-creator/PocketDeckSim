# Appendix: evidence, options in detail, and past failures (the note's first draft, Oct 2)

This is the first draft of `DESIGN.md`, written and reviewed (three reviews) before the brief changed. Its recommendation (a fitted scoring formula after a weekend test) and its eight questions are superseded by `DESIGN.md`, which recommends the play-out chooser and asks one question. Its evidence stands: section 1 (what km3 can't do, from the code, with line numbers), section 1.2-1.3 (what the results show and don't show), section 2 (the options in detail), section 3 (measures and sizes) and section 6 (past failures). Two later corrections: speed is no longer reported as anything but a fact (Dustin, Oct 2), and km3 does pick a different attack from Dustin in 1 of 22 turns (`results/pause_games_decisions_2026-10-02/`).

---

# A pilot built for playing strength: design note (Oct 2, revised after three reviews)

For the coordinator, then Dustin. A read-only design: no game, build, git command or code change went into it. It
draws on four gather reports from earlier today and on the files they cite. Paths are relative to the repo root;
`rl/results/` is shortened to `results/`. VF = `engine/src/players/value_functions.rs`, EMM =
`engine/src/players/expectiminimax_player.rs`, REVIEW = `docs/REVIEW_2026-09-24_direction.md`. Numbers marked
[estimate] are mine and haven't been measured. Claims marked "gather" come from today's gather reports, which aren't in
the repo, so they're unchecked here. `rl/RUN5.md` is being edited today: its lines past about 550 moved twice while
this was revised, so those citations (723-line version) may drift a line or two.

The direction itself is recorded in `rl/RUN5.md:335-349`: Dustin's Oct 2 message, his approval ("Regressions on some
decks should be expected ... I want the realistic bot, not the bot that can pilot a bad deck the best", `:337`),
Astra's three requirements (`:342-345`: varied decks from the start, next-turn planning as a concrete design question,
development kept separate from the final test), and his word on speed (`:346-349`): "Do not reject an approach merely
because it is much slower than km3". So in this note speed is reported for him to weigh. It is never a reason to choose.

## In plain words

You're right, and the code says why. km3 judges every line at the end of its own turn, before the opponent hits back.
Its score pays mostly for the Active being ready to attack right now. An Energy on a Benched attacker is worth about a
third to a fifth of the same Energy on the Active. A ready backup attacker is worth nothing. Nothing charges the bot for
leaving a powered-up Pokémon in front of a knockout. So it tends to arm the Active and leave the Bench bare: the habit
you describe.

It doesn't do this everywhere. In quiz 2's seven positions on exactly this habit, kp3 played your way all seven times.
The failure shows up in particular positions.

Every fix so far added one hand-picked number for one hole and was judged mainly on the Limitless table. One big one got
through: kog, the discard-Energy credit, 15.5 → 14.0. Others were blocked, and not only because the table is thin:
several made particular decks play their own side worse.

I recommend a separate experimental pilot. It keeps km3's search but gets new scoring terms for the missing pieces: a
ready backup attacker, evolution lines priced by what they become, the cost of an exposed Active, and the race. It's
judged first on whether it beats km3 with the same deck on the same deals, and whether it plays the lines you'd play,
on decks it wasn't tuned on, your 15 included. The Limitless table is read afterwards and doesn't block it.

Before the full build, a cheap test this weekend: the backup-attacker term alone at three hand-set weights, on your
decks, plus a measure of how much better km3 could play at its key decisions. That answers "is there anything here" by
about Tuesday. If yes, the full build and the weight fit follow. A frozen version is about Oct 10-12, and the tested
result about Oct 13-14 [estimate].

It can fail. The closest earlier try, kpr3, changed its target habit and still played four decks worse. Better play
also won't close the gap to Limitless by itself: at central values even a perfect pilot reads about 7.5 real error on
these cells, against the 5.5 target. If it fails, the next options are a bot that looks through the opponent's reply
into its own next turn (3-8 times slower per game or more), or one that tries its top moves by short play-outs (about
60-120 times slower, roughly 10-20 minutes per 100 games) [estimates]. You've said slower is fine; the times are there
for you to weigh.

---

## 1. What km3 structurally can't do

km3 = `PublicPricingPlayer{ExpectiMiniMaxPlayer{max_depth 3, opponent_ply 0}}` (`engine/src/players/mod.rs:280-282,
682-711`, per the code read). It scores with `public_clock_effect_km_value_function` (VF:342-344): kog's flags plus
kta's switch 1 plus N2 (VF:476, 482, 488).

### 1.1 The code

| # | What it can't do | Where | What it causes |
|---|---|---|---|
| 1 | See its whole turn. The search is 3 actions, re-planned at each decision, and a turn averages about 7 decisions (69.4 per game over 2,000 km3 games, final turn 9.7; `results/draft_A_v_fire_2026-10-02/games/*.jsonl`) | EMM:323 (root uses `max_depth - 1`), EMM:940-960 (attach/target picks cost a ply) | At the first decision it sees under half the turn. In Poké Ball → bench → evolve → attach → attack, the attack is past the depth. Deeper own-turn search (k4-k6) didn't move the misses (`rl/RUN5.md:197-198`). |
| 2 | See the opponent's turn at all | `opponent_ply: 0` (`mod.rs:706`). EMM:773-777 returns the static score once the opponent holds Unknown cards, which under km is always (EMM:586) | Every line is scored before the opponent attacks. A knockout on my Active next turn is invisible unless it ends the game. The reply search was found inert (`rl/RUN5.md:199-200, 259-261`). |
| 3 | Value a ready Bench attacker | Readiness, weight 500 (VF:52, 783-784), reads the Active only. kq's Bench term is weight 0 for km (VF:395, 476-488; VF:811-819 skipped) | A [W] on an Active Vulpix is worth 310. On a Benched Ninetales ex it's worth 150 (`results/draft_A_v_fire_2026-10-02/BENCH_ENERGY_CODE_READ.md:26`). The code read's bottom line: Bench Energy is undervalued about 3-5x (`:9`). |
| 4 | Price a Basic by what it evolves into | HP × (Energy + 1) is credited against the card's own attacks. km's call has value_aware off, so `evolution_potential` (VF:2573) never runs | Vulpix gets +60 for its first [W] and +0 for the second, though Ninetales ex needs [WW] (`BENCH_ENERGY_CODE_READ.md:23`). |
| 5 | Charge for an exposed Active | No position factor in HP × Energy. Safety is HP ÷ KO points at weight 1 (VF:53). Retreat is −1 per Energy (VF:51, 782). At setup there's no clock, and the Active is picked by HP per point minus retreat (per the code read, VF:694-733) | With the Active Ninetales ex facing a knockout next turn, a [W] on it scores +400. On a Benched Lapras it scores +110 (`BENCH_ENERGY_CODE_READ.md:20, 26`). "Leave it in front unpowered and arm the Bench" always gives up readiness credit. |
| 6 | Finish an attack's own Bench pick inside the search | Target picks are ordinary plies (EMM:940-960) | When Turbo Shark is the third action, its Bench pick falls past the depth, and the line is scored with the Energy missing (`BENCH_ENERGY_CODE_READ.md:33`). |
| 7 | Count a second threat | The clock picks one threat, uses its damage against every victim, and charges nothing to bring a Benched threat up (VF:1761-1765, per the code read and `BENCH_ENERGY_CODE_READ.md:27`) | A ready backup attacker behind the first is worth 0. Energy acceleration onto the Bench saves no turn unless it changes which Pokémon is the threat. |
| 8 | Plan against a Stage 2 it can see coming, or value fetching next turn's evolution | Opponent read from the board only; deck and hand count alike for readiness (per the code read) | Fetching the evolution is worth +1 hand / −1 deck, like any card (VF:780-781). |

None of this is a bug. It's the shape of the formula: 13 hand-set round numbers (VF:45-61), two of them computed and
multiplied by 0 (`online_pokemon_count`, `energy_distance_to_online`, VF:57-58).

### 1.2 Evidence that it costs games

- **Detector networks, same deals, paired.** Like for like against kp3, each is one cell, and both cells are against
  Lucario.
  - Hydreigon's network beats kp3 by +25.2 ± 2.6 (`results/hydreigon_network_readout/READING.md:41`). Its +40.8 is
    against k3 and includes +13.9 of pricing that kp already has (`:40`).
  - Its main habit: Hyper Ray without a knockout on 99% of the turns it could, against 3% for k3 and kp3 (`:18`).
  - Hyper Ray's chip is a readiness-horizon blind spot: the bot can't see Roar in Unison refilling the Active next turn
    (`:24-27`). The source says the +25.2 is "consistent with" the chip being most of the edge, "but not proven" (`:43`).
  - Altaria's network: +15.8 over kp3. About half of it is the opening Active. Where the openings differ, the network's
    choice is worth +19.4 ± 4.6 (`results/altaria_network_divergence_2026-09-26/RESULT.md:4-6`).
  - "The two moves leave different Pokémon Active" is worth +12.56 per game (`:23`).
- **Lucario's network (B2c).** Its three clear gains are Dustin's complaint exactly (`results/lucario_network_divergence_2026-09-25/README.md:27-51`):
  - attack with Bonsly instead of retreating into Riolu: +23.5 ± 10.0;
  - Energy on a Benched Pokémon instead of the Active: +13.1;
  - power the main attacker on the Bench: +6.7 ± 3.7.
  - The file's summary: "a sacrificial front Pokémon while building the real attacker behind it" (`:51`).
- **Today's draft A test.** km3 on both sides (`results/draft_A_v_fire_2026-10-02/RESULTS.md`):
  - The plan's line (Turbo Shark arms Vulpix, Ninetales ex attacks by own turn 3) happened in 17 of 1,000 games (`:10`).
  - The draft lost to deck 13 by −10.9 (−14.85 to −6.95) on the same deals (`:5, 24`).
  - The bot does arm the Bench when Turbo Shark fires, 912 of 955 times, because the attack has no "decline" option. But it picks targets in HP × Energy order: Ninetales ex 321, Lapras 209, Vulpix 114 (`BENCH_ENERGY_CODE_READ.md:32, 38-48`).
- **Dustin's own games.** In his five draft A games, Turbo Shark arming the Bench was the engine of games 1, 3 and 5 (`results/pause_games_2026-10-02/README.md:22, 50`). These are five random testers, not a rate.
- **Quizzes.**
  - Quiz 3: "This deck wants darkrai on the bench and loses when darkrai is active" (`results/blind_quiz3_2026-10-01/RESULTS.md:122`).
  - Quiz 3: "the bot had screwed up by leaving muk active" (`:128`).
  - Quiz 2: his notes keep budgeting next turn's retreat cost, which kpf's fix B, as written, didn't (`results/blind_quiz2_2026-09-27/RESULTS.md:16`).

### 1.3 What the evidence does not show (to keep this honest)

- **The headroom over km3 hasn't been measured.** The +15.8 and +25.2 were against kp3, on one cell each. km3 already
  took part of it (koa's opening switch is in km3, VF:476).
  - Expect lift against km3 to be a fraction of those. Both translations were built, and each recovered a third or
    less. kpr recovered +7.8 ± 4.4 of the +25.2; the other two thirds are "other habits, not yet named"
    (`results/table_readings_2026-09-24/kpr3_paired_reading.md:7-9`), and kpr3 wasn't adopted. koa recovered
    +2.00 ± 2.54 on Altaria v Lucario, against a predicted +5.5 (`results/koa_2026-09-26/reading/READING.md:46`).
  - The networks weren't trained against k3. They were trained against each other, with 20% of games against past
    versions (`rl/RUN5.md:53-54, 556`); k3 and kp3 were only the evaluation opponents. Lucario's own pricing takes
    4.8 ± 1.9 off the Hydreigon network, and the source reads that as "not mainly exploiting" a blind Lucario
    (`hydreigon_network_readout/READING.md:45`).
- **The bot doesn't always fail this.** In quiz 2's seven positions on exactly this habit, Dustin kept the cheap
  attacker in front and built on the Bench, and **kp3 did the same** (`blind_quiz2_2026-09-27/RESULTS.md:12`). It was
  kpf's projection that moved attackers up early.
  - Quiz 1 had the bots within chance at the decision point (`results/blind_quiz_2026-09-25/RESULTS.md:9-12`, gather).
  - So the failure is real, but it shows up in particular positions, not everywhere.
- **A stronger bot isn't automatically a more accurate simulator.** kq3's Bench-readiness term made the
  build-behind-a-wall decks play better (Lucario v Weezing +10.0). But it fit Limitless worse: mean squared miss 147.3
  against kp3's 112.2 (`results/kq_2026-09-25/README.md:1, 41-45, 85`).
  - At central values a perfect pilot would read about 7.5 real error on these 45 cells. That's not a bound: the
    perfect-pilot range is about 4.5 to 9.5 depending on the list assumption
    (`results/error_attribution_2026-09-29/README.md:31`). The 5.5 is the project's target (`rl/RUN5.md:355`), not a
    Limitless figure.
  - "Strength first" is a different target from "real error down". This note doesn't claim one gets you the other.
- **The real-error numbers, corrected.**
  - km3 reads 13.875 (`results/km_tables_2026-09-30/second_reader/SECOND_READER.md:37`), printed 13.8 → 13.9 in the
    reading (`results/km_tables_2026-09-30/READING.md:28`). The "about 13.8" is kta3's (13.836).
  - From kp3 that's 15.5 → 13.9; from k3, 15.3 → 13.9 (`rl/RUN5.md:355`).
  - Nearly all of the drop is one switch: kpg's discard-Energy credit, 15.5 → 14.0 (`results/kpf_2026-09-26/reading/READING.md:19`), adopted inside kog (`rl/RUN5.md:673`).

---

## 2. Candidate architectures

Every time below is reported for Dustin to weigh, not used to rank (`rl/RUN5.md:346-349`).

| | What changes | Cost per game v km3 | Build | First honest result | Main risk |
|---|---|---|---|---|---|
| **(a) Fitted planning evaluation** | km3's search, new scoring terms, new weights fitted on simulator strength | about 1.2-2x [estimate] | about 1,200-2,000 lines Rust + Python fit harness, 2-3 build days [estimate] | weekend test by about Tue Oct 6; frozen about Oct 10-12; examined about Oct 13-14 [estimate] | the terms as written may not express the plan; kpr3's precedent (moves the habit, loses strength) |
| **(b) Two-turn plan search** | km3's own-turn search, then a modelled opponent reply, then my next turn | 3-8x is b3o3n1's figure (REVIEW:31), which has no second own turn; a second own turn "would multiply cost by the full branching factor" (EMM:931-934), and b3o3n4 ran 16-17x (REVIEW:31). So likely above 8x [estimate] | about 500-900 lines Rust [estimate] | about 10 days [estimate] | opponent model wrong gives wrong plans; pending-choice frames are a known bug source |
| **(c) Learned evaluation network** (card-description features, B7 / run 6) | km3's search, network as the leaf score | target ≤3x k3 (`rl/RUN5.md:102-103`) | 1,000+ lines (encoder, trainer, Rust inference) [estimate] | 2-3 weeks [estimate] | the project's networks have never transferred to unseen decks |
| **(d) Play-out chooser** | at 1-2 key decisions per turn, km3's top moves are compared by short play-outs with km3 | about 60-120x [estimate, below]; about 10-20 min per 100 games on 14 threads | about 300 lines on `engine/examples/net_divergence.rs`'s play-out code [estimate] | 3-4 days as a diagnostic | needs the opponent's hidden cards sampled; it still plays km3's move everywhere else |

### (a) Fitted planning evaluation (recommended, after the weekend test)

**What it is.** A new player code (working name kx) on km3's search, reading its weights from a file. Terms:

- **The 13 existing terms** (VF:45-61) stay at km3's values in the first version, with points and is_winner as the
  scale. The two dead terms (VF:57-58) stay at 0. Fitting them too is what makes the fit too noisy to read (below).
- **F1, ready backup attacker.** kv's registered formula (REVIEW:108): 250 × the best eligible Pokémon's readiness ×
  min(1, strength ÷ 150), the weight to be fitted.
  - It reads at the target form, so it starts from `best_benched_attacker_online_score` (VF:3099).
  - The credit belongs to the Pokémon, and a ready Active at target form counts too, so promoting a ready attacker
    doesn't lose it. That fixes kq's flaw (1), found by code read (REVIEW:108). Whether that flaw caused kq3's loss is
    unmeasured: "The promotion counts were not included" (REVIEW:114).
  - It excludes Pokémon whose discard is a priced effect (Chase Order's Basic [G]), the caution recorded for any bench
    term (REVIEW:114). Chase Order's own census then found no measurable tax under kq3 (Combee discards 12.7% against
    13.1%; REVIEW:123), so this is a cheap precaution, not a known cause.
  - kv was registered Sept 24 and never built (REVIEW:114: "kv is not built"; no kv code in `engine/src/players/`).
- **F2, evolution lines priced by what they become.** `evolution_potential` (VF:2573) exists and is off in km.
- **F3, exposure.** Will my Active be knocked out next turn by the opponent's visible best threat after one attach? If
  so, charge the points it gives up plus the Energy on it.
  - Split into "main attacker in front" and "cheap wall in front".
  - The opponent is read from the board only, as km already does. kd's per-victim damage arithmetic exists.
- **F4, the race.** The clock difference (VF:788-789, weight 100 at VF:56) split into a "mine" weight and a "theirs"
  weight, plus turns until the best line's first attack.
- **F5, the opening Active.** The setup-phase choice (HP per point, retreat, koa's term), plus "main attacker in front
  with no Energy".
- **S1, one search change.** An attack's own Bench target pick costs no ply, as queued damage already doesn't
  (EMM:663-717; `BENCH_ENERGY_CODE_READ.md:54`).

**The weekend test first (kx-lite).** F1 and S1 only, with F1 at three hand-set weights (for example 125, 250, 500), on
Dustin's 15 decks against km3 on the floor's deals, with the line rates. 3 × 28,800 games is about 2.5 laptop hours at
the floor's 9.7 games/s (`results/floor_dustin_2026-09-30/timing.txt`), more with kx's slowdown. Beside it, if built in
time, (d)'s headroom probe: km3's top moves at its key decisions, compared by play-outs (the B2c method; Altaria's took
1,781 s on 14 threads, `altaria_network_divergence_2026-09-26/RESULT.md:14`).
- **Go/no-go, written before the run:** build F2-F5 and the fit if kx-lite's pooled lift on Dustin's decks has its 95%
  interval above zero at any of the three weights, or the probe shows km3 gaining at least +3 at its key decisions on
  several decks. If both are flat (or kx-lite is flat and the probe isn't ready), stop the full build and report;
  the question moves to (b) or (d).
- A flat kx-lite is a verdict on F1 at hand-set weights, not on a fitted (a). The page says so.

**How the weights are set (full build).**
1. **Texel warm start:** feature dumps at every decision of km3 self-play, labelled with the result, logistic fit,
   folds by game. Its values for the new terms are the starting point only.
2. **Strength fit over the new terms only** (F1, F3a/b, the F4 split: 3-5 weights), on a log scale around Texel's
   values. Fitness is the mean own-side lift against km3 over a rotating fit pool, same deals for both arms, at least
   4,000 paired deals per candidate.
   - Why that size: at 600 deals one evaluation's standard error is 0.62 ÷ √600 ≈ 2.5 points. The best of 12 equal
     candidates then reads about +4.1 by luck alone, which is above the +3 bar in section 3. At 4,000 deals it's about
     1 point.
   - The chosen point is re-scored on fresh development deals before anything is reported, since the best of a
     population is always flattered.
   - A CMA-ES over all of about 22 weights at that precision would be about 12 × 20 × 3,844 ≈ 920k games: 14-28
     laptop hours per run at 9-18 games/s. Not proposed.
   - deckgym-evalbot's tuner is weak support: its 63% was at depth 1, against a hand-set baseline (REVIEW:82).
   - Upstream's `engine/examples/value_function_grid_search.rs` isn't a usable starting harness: it plays a
     plain-baseline mirror with the variant always in seat B, unpaired, without km's scoring (`:128-166`).
- Fitting to Limitless cells stays banned (`rl/RUN5.md:245, 574`).

**Cost** [estimates].
- 20k self-play games for Texel: about 35-40 min at km3's 9-10 games/s on the 8-cell rows
  (`results/engine_switch_rules_2026-10/timing.tsv:31-33`), plus the dump overhead.
- One strength fit, for example 8 candidates × 10 generations × 4,000 deals = 320k games: 5-10 laptop hours at
  9-18 games/s, up to about 16 with wall decks in the pool (deck 03 ran at 5.4 games/s and deck 01 at 6.2,
  `floor_dustin_2026-09-30/timing.txt`), times kx's slowdown. One to two nights.

**Risks, bluntly.**
- kpr3 is the closest precedent and it failed this note's own primary measure. It was a readiness-one-turn-ahead
  scoring change built from a detector network. It moved its habit (Hyper Ray chips 1% → 91%), but with kpr3 on one
  deck at a time against kp3, Hydreigon gained +3.8 and Weezing, Lucario, Altaria and Vespiquen were piloted worse;
  head to head it scored 48.8% against kp3 (`kpr3_paired_reading.md:4-5, 18`).
- Texel learns what goes with winning under km3's own play. km3 rarely arms the Bench or sacrifices the front, so F1
  and F3 are the worst-identified weights. That's why the strength fit sets them.
- evalbot added a Bench-evolution feature in v6 and got 50.24% [48.98, 51.51] against v5: nothing (gather 4).
- The weights fit depth 3 and won't transfer to other depths (evalbot's own caveat, gather 4).
- If the fit sets F1 and F3 near zero at 4,000 deals per candidate, the terms as written buy less than about 2-3 points
  [estimate]. It can't rule out a smaller gain. Then (b) or (d).

**Why it fits here.**
- It aims at the holes the code read found (items 3, 4, 5, 7).
- It stays within km's information: the opponent is read from the board only, so there's no new information decision.
- Most parts exist, though the build is larger than one term (one term alone ran to about 400 lines:
  `engine/src/players/fuel_credit.rs` is 422 lines, `opening_class.rs` 428; km's single N2 switch took two build
  rounds, `results/km_build_2026-09-29/`, `results/km_build_2026-09-30/`; kq's two-term build drew 3 spec flaws and 13
  upheld review findings, REVIEW:108).
- It's the B3 step the plan approved on Sept 25 (`rl/RUN5.md:564-565`) and never ran. That approval was "judged by the
  adoption rule ... then left alone". This design suspends that rule on the branch, so it needs Dustin's word (Q3).
  "Texel" appears only in `.md` files (gather 3).

### (b) Two-turn plan search

**What it is.**
1. km3's depth-3 own turn keeps its top 4-6 lines.
2. Each line's end state gets a modelled opponent reply.
   - Default: board-only, staying blind. Their visible Pokémon take one attach and use the best damaging attack, or retreat when a knockout threatens.
   - Option: 2-4 sampled worlds from their list, as in `engine/src/players/list_aware_player.rs:1-9, 48-50` (option B's information).
3. Then my next turn: promote or retreat, attach, attack, at depth 1-2, scored by the evaluation.

This needs a flag lifting the stop at EMM:931-938 ("continuing would multiply cost"), a second own-turn budget, the
reply policy and root pruning.

**What it buys.** "Take a hit, prepare an attacker, attack next turn" pays off inside the search window as knockout
points, with no new value term. This is Astra's concrete question (`rl/RUN5.md:344`).

**Risks.**
- The reply is not a hard minimum: a hard minimum made x3 retreat rather than race (EMM:88).
- A wrong reply model gives wrong plans.
- b3o3n4 moved real error 11.5 → 10.1, with an interval crossing zero, by shuffling decks, at about 16-17x k3's time
  (`results/table_readings_2026-09-24/option_b_table_2026-09-24_reading.md:24-31`; REVIEW:31). That reading was
  unpaired (`:16`).
- The leaf is still km3's formula, with holes 3-5 intact two turns later. (b) works best on top of (a). That, and its
  larger build, is why it's second. Its cost isn't.

### (c) Learned evaluation network

Run 6's design (`rl/RUN5.md:237-244`): card-description features, the network as the scorer inside the search, whole
decks held out.

**What exists.** A DMC trainer on final results only, and a card-number encoder (gather 4).

**What doesn't exist.** A description encoder, Rust inference, or any result on an unseen deck.

**Risk: the project's record.**
- Run 3's shared network plateaued at −12.4 against k3 (`rl/FEASIBILITY.md:8`).
- Run 3 was 5-33 points under k3 against held-out decks (`:709`).
- In run 4, every per-deck network lost to k3 against held-out Ninetales (`:881-888`).
- A policy network as the pilot is on "Not doing" (`rl/RUN5.md:573`). A network as the evaluation inside the search isn't.

Too uncertain to start with: no network here has transferred to an unseen deck. It may be the right long bet once (a)
has shown which features matter.

### (d) Play-out chooser

**What it is.** At the Active choice, the attach target, and attack-or-retreat, compare km3's top 3-4 moves. Each is
played out to the end of my next turn, with km3 on both sides and the opponent's hidden cards sampled (it must never
read the real ones; `list_aware_player.rs:7-9`).

**This has been done before, as a diagnostic.** B2c's play-outs found the gains in section 1.2. Altaria's run did
3,025 positions × 16 play-outs in 1,781 s on 14 threads (`results/altaria_network_divergence_2026-09-26/RESULT.md:12,
14`). That's about 0.5 thread-seconds per full play-out [derived].

**As a pilot** [estimates]. About 5 own turns × 1-2 decisions × 4 moves × 8 play-outs is 160-320 play-outs per game,
about 80-170 thread-seconds. km3 takes about 1.4 thread-seconds a game (about 10 games/s, assuming 14 threads), so
that's about 60-120x km3, or about 6-12 s a game on the laptop.
- One deck question at 100 games: about 10-20 minutes.
- Dustin's 15 decks at the floor's size, (d) on one side: about 2-4 days. A 45-cell table with (d) on both sides:
  about 3-6 days.
- These assume full-length play-outs, as Altaria's were. Stopping each play-out at the end of the next turn would cut
  them by an unmeasured amount.

**Use.** First, a cheap honest way to measure the headroom over km3 and to label positions for (a)'s fit. If (a)
falls short, it's a real candidate pilot for deck questions at the times above, which Dustin said can be worth it
(`rl/RUN5.md:347-349`).

### Recommendation

**Run the weekend test, then (a) with S1 if the test clears its go/no-go, judged by section 3.** Reasons:
1. The code read pins Dustin's complaint on the scoring, not the search depth. Deeper own-turn search already failed
   (`rl/RUN5.md:197-198`). kpr's scoring change took Hyper Ray chips from 1% to 91% (`kpr3_paired_reading.md:4-5`),
   so scoring is the lever for habits. But kpr3 also shows that moving a habit isn't gaining strength
   (`:18`). That's the main risk, and the weekend test is aimed at it.
2. The weekend test answers "is there anything to fit" in about 3 laptop hours, before 1,200-2,000 lines are built.
3. No weight in this project has ever been fitted, so it's the one big lever not yet pulled.
4. It stays within km3's information, so there's no new information question.

Speed is not among the reasons. (b) is second because its leaf keeps km3's holes and its build is bigger; (d) is the
headroom probe first and a candidate pilot second.

---

## 3. How to judge it fast and honestly

**Development and examination are separate** (Astra, `rl/RUN5.md:345`).
- Development: the weekend test, the fit and any tinkering, on its own new seed block, on a fit pool of decks.
  (The weekend test uses Dustin's decks on development seeds; the examination uses fresh deals.)
- Then **freeze**: commit the weights file and the build hash.
- Then the examination: on deals the fit never saw, including decks it was never developed on. Nothing is changed after the examination starts.
- Runtime is printed on every run.

**The decks.**
- **Fit pool, varied from the start** (Astra, `:343`). The 10 scoreboard decks (the 8 panel lists, Rayquaza, Altaria/Greninja) plus the coverage lists (Scizor, second lists).
  - Labelled fast or slow so the fit sees both early aggression and build-behind-a-wall decks. `lib/deck_classifier.py` and the A1 tempo metric can label them.
- **Held out from the fit:**
  - Dustin's 15 decks (`decks/dustin/`);
  - B2e's 6 held-out archetypes;
  - draft A and deck 13.

**The measures, in order of weight.**

1. **Own-side lift against km3 (primary).** For each deck: L = (the new pilot on this deck wins v km3) minus (km3 on this deck wins v km3), on the same deals. This is the detectors' D.
   - **Panel.** The 45 cells' deals 0-499. km3's side is already played (`results/km_tables_2026-09-30/1f6319e_km3_table.jsonl`, `1f6319e_km3_new17.jsonl`). New games: 45,000.
   - **Dustin's 15 decks.** The floor's 1,920 deals per deck. km3's games for 14 of them are in `results/floor_dustin_2026-09-30/*_games.jsonl`. Deck 07's page was reused from the Sept 30 re-check (`floor_dustin_2026-09-30/README.md:48`), so its km3 games need checking or re-running (1,920 games). New games: 28,800.
   - **Held-out archetypes:** B2e's rows, same pattern: 96 pairings × 500 = 48,000 new games (`results/engine_switch_rules_2026-10/5a18d31_cov_b2e_km3.run`).
   - **Mirror smoke first:** the new pilot v km3, same deck, seats swapped, 10 decks × 500. It reads 50% if nothing changed.
   - **Exploit check:** a subset with k3 and kp3 as the opponent, where the sign must hold, as was done for the
     Hydreigon network (`READING.md:45`). It needs new km3-v-k3 and km3-v-kp3 baselines. It's weak: k3 and kp3 share
     km3's formula family and its blind spots, so a fit that exploits km3 will likely exploit them too, and the
     Hydreigon check tested one blind spot only. An opponent from outside the family would help: the saved detector
     networks on their own pairings, if their checkpoints still load [unchecked]. Without one, the claim is only "the
     sign holds against km3's relatives".
2. **Line rates from traces: footprint only.** They show whether the habit changed. They never count as a gain: kq3's
   features "do what they were built to do" and still failed (`results/kq_2026-09-25/README.md:85`), kpr3 chipped 91%
   and was weaker (`kpr3_paired_reading.md:4, 18`), and Dustin's own words for this are "a footprint, not a gain"
   (`rl/RUN5.md:376`). Fixed before play, in `results/draft_A_v_fire_2026-10-02/README.md`'s analyze.py pattern, km3 and
   the new pilot on the same deals.
   - **Exposed Active (card-agnostic).** An own turn ends with a 2- or 3-point Pokémon Active that can't attack next turn even with one attach, while a Benched Pokémon could have been in front.
   - **Ready backup (card-agnostic).** At each forced promotion, can a Benched Pokémon attack that same turn?
   - **Named lines:**
     - Turbo Shark's plan line, km3 at 1.7% (`RESULTS.md:10`);
     - Eevee's Boosted Evolution from the Active;
     - Hyper Ray without a knockout, km3-era bots at 3% (`hydreigon_network_readout/READING.md:18`).
   - Every rate is printed per deck. A generic setup rule has hurt a deck before: kor cost Suicune −3.33 ± 0.92 (`results/koa_2026-09-26/reading/READING.md:101`, gather).
3. **Agreement with Dustin.**
   - **The 55 graded quiz positions** (33 + 10 + 12). Each key holds seed, seats and deal, so the new pilot can be asked
     at the same point of the same game (`results/blind_quiz2_2026-09-27/BUILD_NOTES.md:10`, gather). Descriptive only:
     kx and km3 will agree on most of them, and quiz 2 can't show much (kp3 already matched him 7 of 7,
     `blind_quiz2_2026-09-27/RESULTS.md:12`).
   - **One new blind quiz** on positions where km3 and the frozen pilot disagree on exactly this habit. Its size and
     its threshold are fixed before any play. On 10 positions, 7-3 for the new pilot is chance-level (two-sided sign
     test p = 0.34); only 9-1 or better reaches p ≈ 0.02. So 10 positions is descriptive; a real test needs about 20
     or more, which is twice his time (Q8). The standing rule allows building it without asking.
4. **Limitless, afterwards.**
   - Run the 45-cell table with the new pilot on both sides (22,500 games).
   - Print ΔMSE, the detectable size and the per-deck rows.
   - It's read after the decision and doesn't gate it.

**Sizes** (per-deal sd about 0.62, anchored on draft A's 0.637, `RESULTS.md:24`; Hydreigon's ± 2.6 on 2,000 deals
implies 0.59):

| Paired deals | 95% ± | Gain detected 80% of the time |
|---|---:|---:|
| 600 (one fit candidate, rejected size) | 5.0 | 7.1 |
| 1,920 (one Dustin deck) | 2.8 | 4.0 |
| 4,000 (one fit candidate) | 1.9 | 2.7 |
| 4,500 (one panel deck, 9 cells) | 1.8 | 2.6 |
| 28,800 (Dustin's 15 decks) | 0.7 | 1.0 |

**Proposed reading rule, written before the examination.**
- "Stronger" means the pooled lift's 95% interval is above zero on the panel and on Dustin's decks separately, with a point estimate of at least +3.
- Every deck's row is printed.
- A deck worse beyond its noise goes to Dustin as a finding, not a veto. He expects some (`rl/RUN5.md:337`). With about 25 decks, about one will read "worse" by chance.
- **"Realistic" is a second, separate line:** the new blind quiz meets the threshold fixed before play, and the 55 old
  positions don't drop below km3's, read descriptively. The line rates are printed beside it as footprint.
- A pilot that is stronger but not more realistic is reported as such. Dustin asked for the realistic bot (`:337`), and the plan has long said a pilot equally competent with every deck matters more than a stronger one overall (`:206-207`).

**Cost** [estimate]. The examination is about 127k games or more: 45,000 (panel) + 28,800 (Dustin's decks) + 48,000
(B2e) + 5,000 (mirror) + the exploit check and its new km3 baselines. At 9-18 games/s on most decks and 5-6 on wall
decks, that's about 3-6 laptop hours, times kx's slowdown. (B2e alone ran 48,000 km3 games in 2,865 s, `timing.tsv:37`.)

---

## 4. What to keep, and what to suspend on the experimental branch

| Keep (unchanged) | Why |
|---|---|
| The official engine main-8626a35 (`rl/RUN5.md:350`). The new pilot touches only `engine/src/players/` plus a weights file | rules and pilot changes never mix |
| Identity: the branch build replays k3, kp3 and km3 game for game before any comparison. kx with F1-F3 and S1 off, and F4 and F5 at km3's values (the clock's single weight 100, VF:56; koa's term on, VF:476), reproduces km3 (the connection-test pattern of `rl/RUN5.md:97-99`) | otherwise no number means anything |
| km3 as the reference and the screen/floor pilot; k3 as the reproduction reference (`rl/RUN5.md:340, 354`) | the branch replaces nothing until Dustin says |
| The seed registry: new blocks above 23,200,999,999, claimed in START_HERE before play (`START_HERE.md:143`). Proposed: 23.3B for development, 23.4B for the examination | pairing and no reuse |
| No fitting to Limitless (`rl/RUN5.md:245, 574`) | the table must stay an outside check |
| The post-freeze read of kog/kta/km goes ahead as planned (`rl/RUN5.md:468`) | separate question |
| One code review per build. A second reader on the examination numbers (`rl/RUN5.md:717-718`) | cheap insurance |

| Suspend, on the branch only | Replaced by |
|---|---|
| The ΔMSE entry gate and the mixed-row vetoes as gates (`rl/RUN5.md:580-588`) | section 3: lift first; Limitless and per-deck rows reported to Dustin. Own-side losses like koh's Hoopa/Absol −10.4 ± 1.5 (`rl/RUN5.md:362`) become reports, not vetoes |
| B3's "judged by the adoption rule ... then left alone" (`rl/RUN5.md:564-565`) | section 3 (Q3) |
| One switch per candidate, composition checks (`:665-672`) | the pilot is judged whole; switching terms off one at a time is a diagnostic afterwards, never a gate |
| The fallback's four tests and the reserve route (`:646-650, 692-694`) | as above |
| Full registration documents (km's ran to 828 lines, gather 5) | this page, plus a half-page examination plan committed before the examination's first game |
| "Not doing: ... the kq/kv bench-credit line" (`:575`) | lifted on the branch only, with Dustin's word (Q2) |
| Hand-set "pre-set before any A/B" weights (VF:346-348) | fitted weights, recorded with their fit run (the weekend test's three hand-set values are a probe, not a candidate) |

The rules switch stays parked (`rl/RUN5.md:341`).

---

## 5. The first week (Sat Oct 3 to Fri Oct 9), then the freeze

Laptop heavy runs only overnight and at home. Wednesday has no class (`rl/RUN5.md:409`). Release builds, long
replays and tables go to the laptop; code changes, unit tests, the review and short smokes go to the cloud
(`rl/RUN5.md:544-545`). Cloud messages go as paste blocks via Dustin. Owners: the cloud writes the Rust; a Sonnet
agent owns the Python fit harness (Texel fitter, strength-fit driver, paired-lift evaluator), reviewed with kx.

| Day | Laptop (overnight unless noted) | Cloud (Opus) | Sonnet |
|---|---|---|---|
| Sat 3 | idle, or km3's line rates on the floor's games once the definitions are in | writes kx-lite: weights file, F1 (with the priced-discard exclusion), S1, unit tests, the km3-reproduction test | fixes the two card-agnostic rate definitions and the trace extractor before any play; the fit/held-out deck lists with fast/slow labels; the paired-lift reader; the go/no-go rule committed |
| Sun 4 | release build; identity replays (k3, kp3, km3); kx-lite reproduces km3; then kx-lite at three F1 weights on Dustin's decks (about 2.5 h or more) | one review of kx-lite, fixes; then (d)'s headroom probe tool (about 300 lines [estimate]) | independent read of the review findings; the quiz replay tool (55 positions) |
| Mon 5 | daytime: read kx-lite (lift per deck, footprint); overnight: the headroom probe, if built | review of the probe tool | reads kx-lite's results (development only) |
| Tue 6 | **go/no-go** (daytime, by the rule committed Saturday); overnight: the probe's second night if it needs one | if go: F2-F5 and the feature-dump hook | if go: Texel fitter, strength-fit driver |
| Wed 7 (no class) | daytime: Texel dump (20k games, about 35-40 min) and fit | finishes F2-F5; one review | fit harness tests; the examination reader script, committed before any examination game |
| Thu 8 | strength fit, night 1 (320k games, 5-16 h [estimate]) | fixes | the half-page examination plan |
| Fri 9 | fit night 2, then re-score the chosen point on fresh development deals | — | a plain-language interim page for Dustin: kx-lite, the probe, the fit so far, runtimes |

**Then.** Freeze about Sat Oct 10 to Mon Oct 12. The examination (about 127k games) the night after the freeze, the
Limitless table the next night, and the reading with a second reader and the new blind quiz about Oct 13-14
[estimate]. If the go/no-go reads "no", the week stops at Tuesday and the page says so, with (b) and (d)'s times.
If the laptop loses a night to travel, everything slides a day. The freeze doesn't move earlier to make up for it.

---

## 6. What failed before, and why this would differ

- **kq3 (Sept 25).** Two ideas bundled (the next-attack clock cut, and a Bench term at a hand-set 250).
  - The credit sat on the Bench slot, so promoting a ready attacker cost 250 (REVIEW:108). That flaw was found by code
    read; its effect was never measured (REVIEW:114).
  - Against kp3, on the decision set of 27, ΔMSE +36.5 (+13.2 to +59.9), wholly on the worse side
    (`results/table_readings_2026-09-24/kq3_paired_reading.md:23`; REVIEW:114).
  - The Vespiquen bench-tax explanation was a hypothesis (REVIEW:114) that Chase Order's census didn't support (REVIEW:123).
  - The single-feature follow-up was never run (`results/kq_2026-09-25/README.md:90`), and the line was banned (`rl/RUN5.md:575`).
  - **What differs, honestly:** two of the three differences are old plans. The per-Pokémon credit is kv, registered
    Sept 24 and never built (REVIEW:108, 114), and a fitted weight was B3's plan for kq's features (REVIEW:114). What's
    new is that Limitless no longer gates the decision, and that kv finally gets measured.
  - **It doesn't differ** in that if a stronger Lucario or Hydreigon reads further from Limitless, it still will.
- **kpr3 / kpf (Sept 26).** kpr3 moved its behaviour: Hyper Ray chips went from 1% to 91%. It failed on strength too:
  with kpr3 on one deck at a time against kp3, Hydreigon gained only +3.8, Weezing, Lucario, Altaria and Vespiquen were
  piloted worse, and head to head it scored 48.8% against kp3 (`kpr3_paired_reading.md:18`). Under this note's primary
  measure, kpr3 fails. On accuracy it read +74.7 worse on the 27-cell decision set
  (`results/fable_reviews_2026-09-26/kpr_readout_review.md:11`) and −84.7 on 45 cells (`kpf_2026-09-26/reading/READING.md:18`).
  - kpf read −84.2 (−149.9 to −21.3) on 45 cells, blocked by vetoes on Altaria and Vespiquen (`results/kpf_2026-09-26/reading/READING.md:7-10`).
    That gain is in-sample, as koh's is: it sits in Rayquaza's cells, which were used to design kpf (`rl/RUN5.md:691`;
    `error_attribution_2026-09-29/README.md:26`). On the 28 panel cells kpf3 reads 136.7 per cell and kpr3 135.2,
    against kp3's 75.7 (`README.md:131, 138-139`). The panel is worse in both frames.
  - Quiz 2 then showed kpf moving attackers up early where Dustin and kp3 didn't (`blind_quiz2_2026-09-27/RESULTS.md:12`). So the harm was real play, not just a reading artifact.
  - **What differs:** F3 charges for an exposed Active, which kpf lacked, and the quiz is part of the judgment. **What
    doesn't:** kpr3 is the same kind of change, and nothing here proves the fit avoids its fate. The weekend test is
    the first check.
- **koh (Sept 28).** Real error 14.0 → 12.3, interval crossing zero, Altaria vetoes, and its own side played worse on
  Weezing's second list (−3.8 ± 1.6) and B2e's Hoopa/Absol (−10.4 ± 1.5) (`rl/RUN5.md:357-365`).
  - Its gain was in-sample on Rayquaza's 9 cells, and on the 28 panel cells it was a net cost of −1,216 (`error_attribution_2026-09-29/README.md:26-27`).
  - Blunt: koh was a hand-tuned fix designed on the cells it was scored on.
  - **This differs:** the weights come from a self-play fit, and it's examined on held-out decks and fresh deals after a freeze.
- **kd3.** A bundle that priced a sniper as the threat and piloted Lucario worse, −2.2 ± 1.4 (`results/kd_2026-09-25/README.md:6`). A reminder that a sensible term at a hand-set weight can make a deck worse.
- **The networks.**
  - The shared run 3 network plateaued at −12.4 against k3 (`rl/FEASIBILITY.md:8`).
  - Run 4's per-deck networks all lost to k3 against held-out Ninetales (`:881-888`).
  - Run 5 found that a network's margin over k3 didn't predict its head-to-head result (`rl/RUN5.md:183-184`).
  - They read card numbers and learned from millions of games with no search. They memorised matchups.
  - **This differs:** (a) fits 3-5 weights on card-agnostic terms inside km3's search, so there's little room to memorise a deck. It's still tested on decks it never saw.
  - The detector networks succeeded as detectors. Both translations were built and each recovered a third or less:
    kpr +7.8 ± 4.4 of Hydreigon's +25.2, not adopted (`kpr3_paired_reading.md:7-9`); koa +2.00 ± 2.54 of a predicted
    +5.5 on Altaria v Lucario, now in km3 (`koa_2026-09-26/reading/READING.md:46`).
- **b3o3n4 (option B).** Moved real error but not reliably, on an unpaired reading, at about 16-17x k3's time
  (`option_b_table_2026-09-24_reading.md:16, 24`; REVIEW:31).
- **The process itself.**
  - Not everything adopted was small: kog went through at ΔMSE −43.1, real error 15.5 → 14.0 (`rl/RUN5.md:673`;
    `error_attribution_2026-09-29/README.md:142`). km went through at ΔMSE +1.1 (−7.0 to +10.1) (`rl/RUN5.md:396`).
  - Big movers are hard to see on thin cells (about 2.1 points of real error is the smallest gain a big mover shows
    half the time, `rl/RUN5.md:642`). But the big candidates were also blocked because decks played their own side
    worse: koh's Hoopa/Absol and Weezing rows, kd3's Lucario, kq3's +36.5 against kp3 (above).
  - Under Q3, own-side losses like those become reports to Dustin, not vetoes. That's the real change, and it means the
    branch will carry pilots the old rules blocked for real reasons. The per-deck rows are how he sees them.

**Where this is not different, said plainly.**
- (a) is still a formula with features a person wrote. If "build behind a wall" needs a two-turn plan that no static term captures, the fit will find little. That's the case for (b) and (d).
- Strength against km3 can rise while realism doesn't. Section 3 keeps those apart, but they could disagree, and then it's Dustin's call.

---

## 7. Questions for Dustin

1. **Run the weekend test (the backup-attacker term alone at three hand-set weights on your decks, plus a measure of
   km3's headroom), then build the fitted scoring formula (a) if it clears the go/no-go, rather than starting with the
   two-turn search (b), the play-out chooser (d) or a network (c)?**
   Recommend: yes. It goes straight at the holes the code read found (no value for an armed Bench, no cost for an
   exposed Active), most parts exist, and the test answers "is there anything here" by about Tuesday before the big
   build. Speed isn't the reason: (b) is likely above 8x per game and (d) about 60-120x, about 10-20 minutes per 100
   games [estimates], which you've said can be fine. The main risk is kpr3's: a scoring change that moves the habit
   and still plays decks worse.
2. **Lift "Not doing: the kq/kv bench-credit line" (`rl/RUN5.md:575`) on the experimental branch only?**
   Recommend: yes, branch only. km3 stays as it is.
3. **Judge the branch on its own-side lift against km3 and on quiz agreement, with line rates as footprint, Limitless
   read afterwards and not gating, and per-deck regressions reported to you rather than vetoing?** This also sets
   aside B3's "judged by the adoption rule" (`rl/RUN5.md:564-565`) on the branch, and a loss like koh's Hoopa/Absol
   −10.4 becomes a report, not a block.
   Recommend: yes. That's the change you asked for, with the table and every deck's row still printed every time.
4. **Keep your 15 decks (and draft A, deck 13, B2e's six) out of the fit, as the decks the frozen pilot is examined on?**
   Recommend: yes. It's the strongest test that it learned to play, not to play these decks. The weekend test uses your
   decks on separate development deals, which is a lesser use; say if you'd rather it used the fit pool.
5. **Keep the new pilot "blind" this week (the opponent read from the board only, as km3)?**
   Recommend: yes. Guessing the opponent's hand from their list (option B's information) only matters if (b) or (d) is built, and would be its own question then.
6. **If the frozen pilot reads "stronger" and "more realistic", does it replace km3 on the screen and the floor?**
   Recommend: not automatically. You see the per-deck page and the new quiz first. km3 stays the reference until you say.
7. **Laptop time: overnight Saturday to Friday, plus Wednesday daytime, then about two more nights to the examination
   (about Oct 13-14). Any travel nights we should plan around?**
   Recommend: plan overnight-only, so a lost night just slides the schedule a day.
8. **The new blind quiz: 10 positions, read as description only (7 of 10 is chance-level), or about 20, which can
   actually test agreement but takes twice your time?**
   Recommend: 10, labelled descriptive, unless you want the stronger test.

---

## 8. Changes after review (Oct 2)

Three reviews (feasibility and cost; honesty about past failures; written for Dustin) were applied where they held.
Main changes: speed removed as a reason (`rl/RUN5.md:346-349`); a weekend kx-lite test and go/no-go before the full
build; the fit narrowed to 3-5 new weights at 4,000+ deals per candidate with a re-score; build 1,200-2,000 lines and a
freeze about Oct 10-12; the reproduction spec fixed; examination about 127k games; (b) and (d) costs corrected; line
rates as footprint only; quiz power stated; kpr3's strength failure added; the "only small changes got through" claim
corrected; detector numbers like for like; citations re-checked against the current `rl/RUN5.md`.
Declined or changed from the reviews: the claim that both translations "shipped" (kpr was built but not adopted); the
bench-tax exclusion is kept only as a caution, since REVIEW:123 found no measured tax; the 13 upheld findings belong
to kq's whole build, not its Bench term alone; (d)'s table time is re-derived (3-6 days, both sides) rather than the
review's 1-2 days; the Friday Oct 9 full result is replaced by an interim page, since the freeze moved. The third
review arrived truncated after its second point, so anything after that wasn't applied.
