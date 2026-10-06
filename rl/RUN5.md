# Run 5: does a learned position score make k3's search better? (one matchup)

Written September 22, 2026. Owner: Dustin. Lead: Opus. Code review: Astra.
**Status (Sept 23, closed): step 0 GO; stage 1 finished (Weezing +3.2 over k3, averaged copy); stage 2 dropped. Plan after Run 5 at the end — revised Sept 24.; option B reopened Sept 24 evening (update at the end of the plan). Superseded Sept 25: the current plan is "The plan, revised Sept 25 (approved by Dustin)" at the end of this page.** History and every earlier result are in
`FEASIBILITY.md`. This page is meant to be read on its own.

## The question, and why this one first

Can the network's judgment, used as the score at the end of k3's own look-ahead, beat k3 in a
matchup where deeper search pays? Search comes first on purpose:
- It's the only lever with a chance of moving the decks that reward calculation. Weezing and Suicune
  were the two networks under k3 in run 4, and they're the decks where k3 gains most over k2.
- Calculation is a prerequisite for piloting those decks at all.
- The other big gap is facing unfamiliar decks (every run 4 network lost ground to k3 against
  Ninetales). That's a problem with the scorer's inputs, not with search. It's queued as the run 6
  question: describe cards by what they are (HP, type, attack cost and damage) instead of by card
  number. Per-deck networks keyed to card numbers won't survive new sets. Eight meta decks would
  need about 17M games at run 4's rate, and would still know nothing about the next set.

## Matchup (decided)

**The network pilots Weezing against k3 piloting Lucario.** On rules4 over 1,000 paired games, k3
piloting Weezing wins 46.9% and k2 wins 36.8%, so depth is worth 10.1 points here. In run 4 (old
engine) the Weezing network was 6.5 points under k3 in this matchup. Astra's chosen-pair checks on
this pair all passed on add-on 0.7.2: replays, hidden cards, forecasts with skipped counts, and
choice encoding (`results/astra-review/rules4-addon-recheck-2026-09-22/`).

Why Weezing [inference]: its Poison and Burn pay off over later turns. A hand-written position score
prices that roughly; a score learned from game results might not.

**Accepted rules limits for this pair.** They're reported with every result.
- Reverse Thrust's delayed knockout: the forecast was fixed in 0.7.1/0.7.2.
- Hoopa's self-knockout finish: the observed tie case is fixed. Broader simultaneous-finish variants
  are still unconfirmed.
- Open question #22: a Checkup on turn 30.
- Open question #24: how random deck searches are weighted.

**Fallback:** the network pilots Weezing against k3 piloting Suicune. There, k3 wins 38.0% and k2
18.9%, a 19.1-point gap. It's used only if stage 1 shows the plain network already clearly ahead of
k3 in Weezing vs Lucario, and it needs its own chosen-pair checks first.

## Step 0: regression pilot (no new code, about 1.2 h)

Run 4's pilot settings, unchanged: Blaziken vs Lucario, two networks, encoding v2.2, 300,000 games.
The only difference is rules4 and add-on 0.7.2, in a new run folder. Run 4's pilot confirmed
**+10.2** at 250k. This checks whether the new setup still learns; it isn't a strength claim, since
the rules changed and an exact match isn't expected.
- **Go:** Blaziken's confirmed margin is **+5 or better**.
- **Below +5:** find out why before stage 1.

## Stage 1: plain network on the corrected engine

- Same trainer and settings as run 4: two networks, one per side, learning from final results only,
  encoding v2.2, 20% of games against past versions. One pairing: Weezing vs Lucario.
- **One code change:** keep a running average of each network's weights over roughly the last 100,000
  games (exact setting recorded in the build). Evaluate it beside the live weights at every checkpoint,
  on the same seeds. It never feeds back into training.
- **Learning-rate decay stays out.** It changes training, and this run changes one training thing at a
  time: none.
- **Budget:**
  - a safety cap of 2M games (about 8 h plus evaluation, estimated);
  - checkpoints at 100k and then every 200k;
  - **runs to the 2M cap** (changed Sept 23, see below). Level-off is reported, not used to stop;
  - the draw gate as before.
- **Evaluation at each checkpoint:** 1,000 paired games against k3 per network (500 per seat), for
  live and averaged weights, plus 200 against random moves.
- **Confirmation:** Weezing's best checkpoint (live or averaged, whichever is higher), plus a runner-up
  within 2 points. Each is played on 2,000 fresh paired seeds from a new seed range, followed by the
  existing knockout audit.
- **What it decides:**
  - Plain Weezing margin **below +5** over k3: stage 2 runs on this matchup.
  - **+5 or more:** record it (the plain network already beats k3 here) and move stage 2 to the fallback.
  - **Dropped Sept 23, 6:05 PM, before the confirmation ran:** no switch to the fallback. See the decision below.
- **Averaging verdict** (descriptive, read from 400k on): does the averaged copy score higher, and does it move less
  between checkpoints than the live one? This decides whether averaging becomes the default later.

## Stage 2: the learned score inside k3's search

k3 looks ahead up to three of its own moves within the turn, then scores the resulting position with a
hand-written formula. It never searches the opponent's reply. Stage 2 replaces only that formula.

1. **Position scorer.** A separate small network that reads the Weezing player's own view and predicts
   the result.
   - **Training data:** games between stage 1's confirmed networks (with the usual 5% random moves),
     recorded at every decision point in the game, on both players' turns, with the final result.
     Stage 1's network is not changed.
   - **Finished games** score exactly +1 / −1 / 0, because k3 scores finished games through the same
     function and the scales must match.
   - **Hidden cards:** it reads only its own player's view, so k3's search over a guessed board can't
     leak the opponent's hand.
   - **Speed watch:** the view includes the v2 threat numbers, and each of those runs a small
     look-ahead. If that makes scoring each position too slow, the scorer drops them.
   - **Known risk** [inference]: it learns from network-vs-network games but is used in games against
     k3. Training it on games against k3 would be tuning to the exam, so it isn't done.
2. **Runs inside the engine** (Rust), not a Python call per position. It must match the Python version
   to within 0.00001 on sampled positions.
3. **Gate, connection test:** the new search with **k3's own formula** plugged in must reproduce k3 game
   for game, over 100 seeds in both seats, every decision and every final state. Any mismatch stops
   stage 2.
4. **Speed, measured before any evaluation:** positions scored per decision, and seconds per game
   compared with k3.
   - Target: at most 3× k3's time.
   - Over 10× after the simple fixes (batching, a smaller scorer): stop and redesign.
5. **Evaluation.** A fresh seed range, 2,000 paired games (1,000 per seat), all against k3 piloting
   Lucario. Three pilots of Weezing:
   - (a) k3;
   - (b) stage 1's plain network;
   - (c) k3's search with the learned scorer.

## What counts (fixed now, before anything runs)

- **Success:** (c) beats (a) by **+5 points or more**, with the paired 95% interval above zero. Next
  would be an unfamiliar opponent and a second matchup.
- **Helps, but not enough:** (c) beats (b) by 5 or more but doesn't beat (a) by 5. The learned scorer
  helps the network but isn't yet better than k3's formula. One follow-up is allowed (more scorer
  data), then decide.
- **Failure:** (c) is not better than (b). That rejects this implementation and budget, not learned
  search in general.
- **Why 2,000 games:** a paired margin at run 4's rate of games decided differently (about 40%) is
  roughly ±3 points at 95% [estimate].

## Lead's decisions after the build (Sept 23)

The build is in `results/run5_build/` (`BUILD_NOTES.md`). Step 0 runs on `train_v5.py` with averaging
off, because `train_v4.py` can't find add-on 0.7.2's single-file install. Its game lists, seeds and
game-playing code match run 4's pilot.

1. **Stage 1 runs to its 2M cap. It doesn't stop when the networks level off.** Run 4's level-off rule
   was set for checkpoints 500k apart. At this page's 100k/200k spacing it could stop the run at 400k
   games. That would leave the plain Weezing network undertrained, and stage 2's "beats the plain
   network" comparison would be too easy. Laptop time is cheap, so the cap it is. Level-off is still
   reported. (My spec error; one small setting and code change for the builder.)
2. **Step 0 keeps run 4's pilot seeds.** For a check of whether the new setup still learns, the same
   games with only the rules and add-on changed is the cleaner comparison. It isn't a fresh-sample
   strength claim.
3. **No held-out row in stage 1.** Unfamiliar opponents are run 6's question.
4. **The averaged copy starts at the untrained network** (my formula). The start still counts for 50%
   at 100k and 6% at 400k, so the averaging verdict is read from 400k on. No code change.
5. **If an averaged checkpoint is confirmed best,** it's stage 1's plain network for stage 2: it's
   baseline (b) and it plays the games the scorer learns from. It went through the same confirmation.
6. **Step 0 stays at +5 or better to go on,** read by the lead before stage 1 starts.

**Step 0 result (Sept 23, 11:07): GO.** Blaziken ckpt_250k confirmed at **+10.7** over k3 on 1,000 paired
games (58.1% vs 47.4%; runner-up ckpt_200k +8.7). Habits are close to run 4's pilot: attacked 88% of offered turns
(run 4 90%), skipped 26% of benching chances (22%), missed 4.5% of sure knockouts (3.5%), no sure wins missed.
Lucario's network confirmed at +3.5 (run 4's pilot: −1.5). Both lose to k3 against held-out Ninetales (−12.3, −13.0;
300 games each). Report: `runs/run5-step0-blaziken-lucario/REPORT.txt`. The new setup learns as before.

**Decided Sept 23, 6:05 PM, before stage 1's confirmation ran (lead, after the independent audit):**
- **No switch to the Suicune fallback, whatever the confirmation shows.** At 1.6M the averaged Weezing copy scored
  +5.8, right on the old line, and the confirmation is only accurate to about ±3. Stage 2's comparisons against k3
  and against the plain network stay meaningful at any plain-network margin. The switch would cost another round of
  Astra checks and a 9-hour run over half a point of noise. This is decided before the confirmed number exists.
- **The stage 2 build is on hold** until Dustin decides on the audit's proposal: measure whether better piloting moves
  the simulator's matchup table toward Limitless before building more against k3.

**Stage 1 result (Sept 23, 19:09): finished at the 2M cap.** Report: `runs/run5-stage1-weezing-lucario/REPORT.txt`.
- **Weezing:** best confirmed checkpoint **ckpt_1800k_avg, +3.2 over k3** on 2,000 fresh paired games (51.7% vs 48.5%;
  351 vs 287 games won only by one side). The runner-up ckpt_1600k_avg confirmed at +2.3. Both were +5.3 and +5.8 on
  their 1,000-game checkpoint scores; the confirmation took the usual 2–3 points off the best-of-many. Under +5, so the
  dropped fallback switch would not have fired anyway. Run 4's Weezing network was −6.5 here on the old engine.
- **Weezing habits vs k3 piloting Weezing:** attacked 86% (k3 92%), benched 66% (k3 95%), missed 45 of 999 sure
  knockouts (k3 58 of 893), missed 8 of 787 sure wins (k3 0).
- **Lucario:** ckpt_1800k_avg confirmed at **+25.6** (76.8% vs 51.2%). Benched only 54% (k3 92%), 3.2 checkup deaths
  per 1,000 turns (k3 0.5): a much better Lucario strategy than k3's exists in this matchup, with sloppy habits intact.
- **Averaging verdict (read from 400k on):** the averaged copy scored higher than the live one at all 9 checkpoints from
  400k, for both networks, and both confirmed winners are averaged copies. For Weezing it also moved less between
  checkpoints (about 1.5 points on average vs the live copy's 2.4); for Lucario about the same (1.5 vs 1.7 from 600k).
  The report's own 'average change' line counts the 100k–400k warm-up, when the average is still mostly the untrained
  start, so it overstates how much the averaged copy moves. Verdict: averaging helps; make it the default.
- **For the Limitless comparison (part 2):** use ckpt_1800k_avg for both Weezing and Lucario. The pair is lopsided
  (+3.2 vs +25.6 over k3), so network vs network will lean toward Lucario for pilot skill, not just the matchup.

## After Run 5: the plan (decided Sept 23 with Dustin)

The independent audit asked whether beating k3 makes the simulator more realistic. The Limitless check
(`results/limitless_check_2026-09-23.md`: 111 B4a tournaments, 25,143 matches) answered what it could:
- **k3 vs k3 on rules4 is a usable coarse filter:** favorite right in 23 of 28 top-deck matchups (15 of 16 clearly
  one-sided), typical real miss about 9 points, and 9 matchups off by more than chance. Altaria is underrated
  in four, Sceptile overrated, Vespiquen underrated.
- **Trained bots told us little:** bot vs bot ended closer to Limitless in Blaziken–Lucario (2.0 vs k3's 5.9 off) and
  further away in Weezing–Lucario (9.7 vs 6.4). k3 was already inside Limitless's range in both. The mixed rows
  show the Weezing–Lucario result is mostly Lucario's much stronger pilot, and a bot's margin over k3 didn't
  predict its head-to-head result.

**Decisions (Sept 23; items 3 and 4 are now done or dropped, see the Sept 24 revision below):**
1. **Stage 2 as designed is dropped.** A scorer trained on one matchup with card numbers doesn't serve the goal.
2. **The Limitless table is the scoreboard.** Any change to piloting or lists gets re-scored against it
   (about 1.5 h of cloud time, no Fable or Astra).
3. Multi-list check of the suspect decks — **done Sept 24:** list drift is ruled out (see `results/limitless_check_2026-09-23.md`).
4. Option B (k3 guesses the opponent's hand and searches their reply) — **dropped Sept 24, reopened the same evening** (see below).
5. **Run 6 is the long bet:** one bot that reads cards by what they are and plays every deck.
6. **Weight averaging is the default** in any future training.

## The plan, revised Sept 24 (Dustin, after reviews by Fable, Astra and Opus)

Since Sept 23: the list refresh ruled out list drift; the deeper-search table showed k4/k5/k6 don't move the
systematic misses (`results/deep_search_table/STATUS.txt`); the Hyper Ray count showed a k3 valuation blind spot,
not a rules error, and the d3 damage-weighted formula has the same blind spot; the existing reply search was found
to be inert (296 of 300 games identical with it on and off).

**How to read the table.** Observed average miss is 9.3; the floor for a perfect simulator, from Limitless's own
sample sizes, is about 4.0; the simulator's real error after removing chance is about 8.8. Errors don't subtract.
**Target: about 6 points observed and 3–4 pairings beyond chance** — roughly halving the real error, not chasing
the floor. The table is development data and a proxy (mixed BO1/BO3, tournament population); matching it is not
proof of human-level play. What matters for deck testing is a pilot that is *equally* competent with every deck,
not a stronger pilot overall. Whether the remaining misses come from play, from a card's engine behaviour, or from
who plays these decks on Limitless is **open** — nothing so far separates the three.

**Order of work.**
1. **Ladder games when time allows** (Dustin): a few a week, concentrated on one brew at a time until it has 20–30
   games, rather than spread across many decks. Each game plus recording takes about 15 minutes, so this is a slow
   signal, not a gate — nothing below waits on it. Brew-06 has never been played; the Ladder Log's last entry is Sept 16.
2. **Tonight: the Hydreigon network run** (lead). Read three ways: does it chip with Hyper Ray, does it gain over
   k3, and does the Hydreigon v Lucario cell move toward 54.4 real — including network v network, since a bot can
   gain over k3 and take a matchup further from reality (part 2 of the Limitless check).
   - **Setup:** run folder `runs/diag-hydreigon-lucario`; settings `diag_hydreigon_v5_settings.json` (stage 1's
     settings with Hydreigon in Weezing's place). Seeds: training 10,000,000,000+, evaluation 13.0–13.3 billion,
     clear of the 72M/73M Limitless-check games, stage 1 and the practice block (9.0–9.8 billion). The launcher
     files any folder outside Run 5 under its practice rule, which only means seeds of 9 billion or more.
   - **Rows:** the standard confirmation gives network Hydreigon v k3 Lucario, k3 Hydreigon v network Lucario and
     k3 v k3 on the same seeds. The auditor adds network v network and the Hyper Ray count afterwards, and runs the
     pair checks (his check, not Astra's); the result isn't read until they pass. Benching is in the report.
   - **Reading, set before it runs:** chips with Hyper Ray and gains 10+ over k3 → learning finds the play k3
     misses; chips but lands near k3 → check its benching before concluding; gains without chipping → the gain is
     elsewhere; neither → ambiguous, and only then is a forced-Hyper-Ray k3 build worth it.
3. **Cheap card check of Altaria, Sceptile and Vespiquen** (Opus first pass, discrepancies to Astra): engine text vs
   the Limitless card page for every card, then a **legality scan of the table's own games** for illegal offered
   moves — the run 4 Eevee/turn-1 Mega Altaria bug had no text mismatch and would pass a text-only check.
   Plus Sceptile v Vespiquen transcripts (sim 66–34, real 33–67) for Dustin to read, made the way the Hydreigon
   ones were. Fold in one look at *why* the existing reply search never changes a decision (dead code or a gate that
   never fires), on the Hydreigon cell. Building option B was dropped here and is reopened (update below).
4. **Two clerical tables** (cheap agent, no engine work): a BO1-only version of the 28 cells from the tournament
   API, with future events reserved for confirmation; and a top-finishing-players-only version. If the
   Altaria/Sceptile/Vespiquen misses shrink against top players, the population is the cause and those cells
   shouldn't drive bot design.
5. **Run 6**, only after 2–4, since they decide whether its accuracy case is real. Design: card-description
   encoding (HP, type, attack cost/damage, abilities, conditions, evolution links, delayed effects); train on a wide
   pool (the 8 meta lists, Dustin's 15 decks, the brews); hold out whole decks and test the bot **piloting** a
   held-out deck as well as facing one (run 4 only tested facing); use the network as the scorer inside k3's search,
   not only as a policy (networks miss sure knockouts and bench less than k3; k3's hand-written score is where it
   goes wrong); weight averaging on; an imitation-warm-start arm (from k3 games) as an A/B inside the pilot, not a
   design commitment. One design page, one review, run, one report; no side studies unless they decide something on
   the page. Headline number = the table score; margin over k3 is a side note.
6. **Dropped:** tuning k3's evaluation weights against the table (d3 evidence, overfitting 28 cells, no value for
   brews); k7 or a larger specialist run as an automatic next step. (Building option B was on this list; reopened below.)

**Until run 6 passes a held-out-deck test, the simulator does not screen brews.** (Brew screening and its cutoffs wait until the engine is trustworthy and realistic (Dustin, Sept 24).) Its brew job is "does the combo
fire"; the ladder is the screen. Positions Dustin annotates while reading transcripts are diagnostics for a specific
fix, not the yardstick.

## Update, Sept 24 evening (Claude Code; the repo is now the project's home)

- **Option B is back on**, by Fable's condition. The see-everything test (Cowork cloud, 500 deals per matchup, the
  table's deals, both sides given the same information): Hydreigon v Lucario goes from 30.8 with both blind to
  **44.7** when both see hands and 46.8 when both see everything (Limitless 54.4 ± 8.0). Seeing hands gives almost all
  of it, so a guess of the hand from the known list can capture most of the gain; knowing the next draw adds little.
  Blaziken v Sceptile moves +3.6 / +5.1 (noise). Altaria v Lucario, Altaria v Blaziken and Sceptile v Vespiquen don't
  move at all. One-sided arms: pending. Caveat: played blind, the reply search never runs (the opponent's cards are
  blank, so it stops at their draw), so the test measures information plus a working reply search, which is what
  option B would build. That also answers item 3's "why the reply search never changes a decision."
- **Item 3, card text:** all 29 cards in the Altaria, Sceptile and Vespiquen lists match Limitless in HP, type, stage,
  weakness, retreat, costs, damage and effect text (internet-side agent, Sept 24). Mega Sceptile ex's text is missing
  an "a"; the code discards one Grass Energy, as on the card. The legality scan of the table's games is still to do.
- **Sceptile diagnostics** (Claude Code; seeds 81.0M–81.07M and 20.0B+; not for any ranking). In the sim, Butterfree
  (Sunny Wind), not Mega Sceptile ex, wins Sceptile's games. Switching Caterpie's Quick Growth off moves all seven
  Sceptile cells 11–22 points (Sceptile's average 59 → 43; Limitless 48). But the ability behaves as its text and the
  published ruling say (Fable), opponents stop Caterpie before it evolves in only 1–35% of cases, and k5 opponents
  don't stop it more often. So Quick Growth isn't shown to be wrong; what inflates Sceptile is still open. Weakness
  (+20 against Grass) checked in play: correct.
- **Item 2, the Hydreigon run, moves to the repo.** `rl/run_training_v5.sh` now reads the add-on from
  `rl/addon-0.7.2/wheels/`; the wheel itself (SHA-256 56ca0bad…925b) still has to be added there.
- **Lead for Altaria, from reading the code (not yet tested):** k3's position score ignores Sleep and
  Paralysis. Its threat clock (`calculate_turns_until_opponent_wins_damage_aware` in
  `engine/src/players/value_functions.rs`) treats an Asleep or Paralyzed attacker as able to attack next
  turn, and no other term rewards putting the opponent's Active to sleep, so k3 prices Swablu's Sing at
  nothing. That would underrate the Sleep deck in every matchup, as the table does. Against it: the
  see-everything bot's reply search does see Sleep, and Altaria didn't move there. Cheap test: a
  diagnostic copy whose clock adds half a turn for an Asleep threat and a whole turn for a Paralyzed one,
  k3 on both sides, the four Altaria misses (Lucario, Blaziken, Suicune, Sceptile) plus two cells without
  Sleep as controls, 500 table deals each. **Tested Sept 25 and refuted** (Altaria's cells moved −0.2 to +1.0
  against gaps of 11 to 18; `rl/results/status_clock_2026-09-25/`; section 8 of
  `docs/REVIEW_2026-09-24_direction.md`, B2b). The Altaria gap stays open; see "The plan, revised Sept 25".

## Limits on every number from this run

- These are simulator results on rules4, and the open rules above are reachable in this pair.
- One matchup, one opponent. Nothing here says anything about unfamiliar decks.
- The play-time "take the win" rule stays off in experiments. It goes on only for a bot Dustin plays
  against.

## Order of work (Sept 22; history — stage 2 was dropped; the current order is "The plan, revised Sept 24" above)

1. Opus builds step 0's launcher for 0.7.2 and stage 1's averaging and settings, and practice-tests
   them in the cloud.
2. Astra reviews that build once.
3. Dustin starts step 0, then stage 1.
4. While stage 1 runs, Opus builds stage 2: the scorer, the in-engine version and the connection test.
5. Astra reviews that build once.
6. The connection gate and the speed check pass before any evaluation.
7. Side studies get one review pass from one reviewer.

## The plan, revised Sept 25 (approved by Dustin, Sept 25)

Consensus of Fable's Claude Code session and the laptop Claude Code session, with a second Fable session's independent
read agreeing. Objective for this month: the bot decides which brew gets Dustin's ladder games and improves a list
before he plays it; the Limitless table is the regression test for pilot quality, not the objective. Full record and
every number: `docs/REVIEW_2026-09-24_direction.md`, section 8. This section supersedes "The plan, revised Sept 24".

**Decisions taken Sept 25 (approved by Dustin):** scoreboard v2 rebuilt from pairings on the development half (done,
971901b; every Sept 23 cell within noise at v2's n); kp3 adopted as the screen's pilot on both sides and as the working
table pilot pending the holdout confirmation, by Dustin's override of the pre-registered rule (on v2 alone kp3's ΔMSE
interval crosses zero because v2 has half the matches; the point estimate is unchanged), k3 kept as the reproduction
reference, the vetoed cells (Hydreigon v Suicune, the Vespiquen deck; Blaziken v Hydreigon on a 24-match cell) on the
investigation list; the holdout spent once, on the pilot Dustin picks after kd's reading; the screen re-run with kp3 on
both sides and the A2 hold decided on it; kd read against kp3 on v2; the Sleep and Paralysis fix published upstream;
PR #1 and the laptop branch merged (cf78d02, bbd5d9d); and, Dustin's word on Sept 25 late morning, the merged-main
engine build becomes the official engine once the identity replay in `rl/results/engine_identity_2026-09-25/` passes on
its own conditions (k3 and kp3 on 28 × 500 matching the reference per-game files field by field), plus a direct CLI parity check
of the new `deckgym` program against the rules4 one (k3,k3 on the screen's seed 7100, four matchups × 30, identical
win and draw lines) and a kp3 smoke test on the new program; at which point the new `deckgym` and `legality_scan` are
copied into `rl/engine-2026-09-25/` with a README naming the commit, both hashes and the replay and parity results,
`project_manifest.json` moves rules4 into its historical releases and names the new build as the available release
(`current_engine.py` reads the manifest, so it needs no change), `run_screen.py` defaults its engine to the manifest's
build and its players to kp3,kp3 with k3,k3 still available, and START_HERE's engine line is updated; the 0.7.2 wheel
and its run identities are untouched; a failing replay or parity check leaves the manifest untouched and is reported
first. **Done Sept 25, 10:50 (61d773c):** k3 and kp3 replayed 14,000 of 14,000 each, field by field including the move
hash; `deckgym simulate` k3,k3 on seed 7100 identical to rules4; the kp3 smoke test runs; evidence in
`rl/results/engine_identity_2026-09-25/`. The official engine is now main-7fc6ccb in `rl/engine-2026-09-25/`
(`deckgym` f4d235e5…1034, `legality_scan` d5c0a952…bfbb); rules4 is in the manifest's historical releases with its hash;
`run_screen.py` resolves the engine through `current_engine.py`, refuses any other binary, and defaults to kp3 on both
sides with k3 still available; the 0.7.2 wheel and its run identities are untouched.

**Where things stand** (status; updated with each reading. START_HERE carries none since Sept 28)
- **Direction from Oct 2: a pilot built for playing strength, on an experimental branch.** Dustin's words, relayed by the Fable coordinator session (verbatim):
  - "a lot of decks perform poorly in the simulator, because the bot doesn't setup for the future. They often just put their strongest pokemon in the active spot when it doesn't have enough energy to attack, leaving it exposed. Sometimes the best thing to do is leave a pokemon active and not put any energy on them to arm the bench pokemon so when it is promoted to the active spot, it can actually attack. I don't feel like we are making any real progress towards the bot playing better even with all these rules fixes. This whole project has been so narrowly/carefully adjusting one thing and not moving the floor. That is a great plan when you have a good foundation, when your foundation is shitty, you sometimes have to break things to know how to fix them".
  - On approving the direction change: "Regressions on some decks should be expected with these changes. Not all decks will move in the same direction. I want the realistic bot, not the bot that can pilot a bad deck the best. Astra's suggestions with the same instructions and your recommendations".
  - So:
    - **The new pilot** is built for playing strength on an experimental branch (design: `results/planning_pilot_design_2026-10-02/DESIGN.md`).
    - **The reference stays** the official engine (main-8626a35) and km3.
    - **The next rules switch is parked:** its plan stays a draft, not scheduled.
  - **Astra's additions, adopted as requirements:**
    - varied decks from the beginning (early aggression and preparation decks), so the bot learns WHEN building the Bench pays;
    - next-turn planning as a concrete design question ("attack now" against "take a hit, prepare an attacker, attack next turn");
    - experimentation kept separate from the final examination: freeze a promising version, then test it on fresh games and on decks it wasn't developed around, with runtime visible throughout.
  - **On speed and game counts** (Oct 2, relayed by the coordinator; verbatim):
    - "I would much prefer a slow accurate bot to a fast inaccurate one. 100 simulated games of human level play tells me way more than 1,000,000 games of the current bot".
    - Then: "100 to a million wasn't literal. But at 10 minutes a game for me to play and then more time for me to record all the moves so you can learn from it, it costs me a ton of time experimenting with bad decks. That was the purpose of this whole thing. To help me find decks without wasting hours and hours myself testing them... Prioritize trustworthy playing quality. Report the time and cost needed to achieve it, and let me decide whether that tradeoff is worthwhile. Do not reject an approach merely because it is much slower than km3, and do not treat 100 games as a fixed limit."
    - So the goal, in his terms: the bot saves his hours by telling him which decks are worth his own 10-minute games. Trustworthy playing quality comes first. There is no game-count budget and no speed requirement. Each option's time and money to reach trustworthy play, and to answer one deck question, are reported for him to weigh. No option is rejected for being much slower than km3.
  - **The first prototype, approved Oct 2 (Dustin, relayed by the coordinator; verbatim):** "I approve the build now." It is the play-out chooser on top of km3 recommended in `results/planning_pilot_design_2026-10-02/DESIGN.md` (f81cc964). Adopted with it (the coordinator's amendments and Astra's points; DESIGN.md section 9):
    1. the candidates are every distinct legal first action where practical, not km3's top few;
    2. the pilot knows only what its side may know. Giving it the opponent's exact list is a labelled laboratory condition. Realistic brew testing needs uncertainty about the opponent's list, and the meta side is never handed the brew's exact list;
    3. no leak: every play-out starts from a state sampled from the pilot's permitted observation, never from the real saved state (`net_divergence.rs` starts from the real one);
    4. the first demonstrations include a plan that needs several coordinated decisions, to learn whether km3's later mistakes in the play-outs hide good first moves;
    5. the 34 pause-game positions are development examples, not an exam; agreement with Auto doesn't establish Auto-level strength;
    6. the report brings back improved decisions and remaining failures.
    - The cloud writes the code on `claude/playout-pilot`; the laptop reviews it once, builds it beside the pinned engine (km3 in that build must reproduce the pinned self-check and the official games), runs the development positions, then sizes and launches the unattended development run in the strength harness.
  - **The first results and the freeze, Oct 3-4.**
    - The development run (`results/strength_2026-10-03_kx3_dev/`, d513e37b): kx3 beat km3 by +16.6 ± 3.5 points on Dustin's 7 development decks against the panel, and every deck went up. kx3 games take about 4½ minutes; km3's take under a second.
    - The position examples (`results/playout_pilot_positions_2026-10-04/`) show little human-like change. kx3 overrides km3 on about 3% of decisions; one strong improvement; signs that km3's later play inside the play-outs hides good first moves, and none that the pilot sees them.
    - **Dustin approved a conditional freeze and the exam, Oct 4 (relayed by the coordinator; verbatim):** "yes approved". Astra's three tightenings are conditions of it.
    - The rule is recorded before the result, in `results/strength_2026-10-04_kx3_v_k3/PREREGISTRATION.md`'s addendum: kx3 − km3 against k3, 95% interval above zero → freeze d513e37b; crossing zero → hold.
    - The freeze is labelled "a promising experimental baseline, not the finished planning bot".
    - **The exam (Oct 6):** kx3 (d513e37b) v km3 on the 11 held-out decks: +21.3 ± 4.0 (53.0% v 31.7%), every deck positive (`results/strength_2026-10-05_kx3_exam/`; a second reader agrees).
    - **After the exam (Oct 6; Dustin: "Yes to the quiz"; Astra's review adopted as his input; relayed by the coordinator):**
      - (A) **Quiz 4** uses positions where kx3 (d513e37b) and km3 disagree: setup decks first (build-up situations), fast decks for the tempo ones. It hides which bot chose which answer. It offers "both reasonable" and "neither" beside the two choices, so planning disagreements separate from harmless move-order differences. The key stays private. The laptop builds it; Sonnet may assemble.
      - (B) **kx3 in the tools**, after gate 3 and the Tool-rule decision:
        - opt-in only; the defaults (screen and floor) stay km3;
        - the exact tested version, with both pilots named in every output;
        - a separate "slow report" with results and their uncertainty, NOT run through the floor's pass/fail cutoffs;
        - no prerequisite of passing km3's screen: any deck can go straight to kx3.
      - (C) The Tool filter becomes a within-noise **tie-break**, never a dropped candidate (Poncho on the Active can protect after a retreat). Gate 3 waits for that version and includes decks 05 and 03.
      - (D) The unfamiliar-opponent version stays separate until it is measured against out-of-pool opponents.
    - **Rules finding queued for the next rules switch (Oct 6):** return damage set up by an attack takes Weakness. Dustin, verbatim: "I know it is the case for sableye. It is from an attack the return damage is done, not from an ability."
      - It covers the 5 attacks with "During your opponent's next turn, if this Pokémon is damaged by an attack, do X damage to the Attacking Pokémon".
      - Tools stay flat. The Ability case is open (shot-list row T15).
      - The engine adds no Weakness today. See `rules/02_damage_knockouts_points.md` §2 and `results/new_pause_games_triage_2026-10-06/`.
    - **Deck dependence (Dustin, Oct 5, relayed by the coordinator; verbatim):** "It's deck dependent when building the bench is helpful. Some decks are meant to play fast. Some reward buildup."
      - So results are reported by deck group (fast v setup) and per deck, with how kx3 changes each deck's pace (turns per game, first-attack turn).
      - Build-up positions and quiz items come from the setup decks (Wailord, Muk, Indeedee/Stoutland, Skarmory), and tempo ones from the fast decks (draft A, Manectric, Xatu/Weezing).
    - **Laptop schedule (Dustin, Oct 4, via the coordinator):** Monday Oct 5 is a full school day. The laptop is away about 7 am-5 pm Central and closed at 7:15 with no warning. So the exam checkpoints game by game and starts no new game after 5:15 am. Anything still running at 6:30 is stopped (a cut-off game replays on resume). The run is committed and pushed with main = origin/main by 7:00, and resumes from 5 pm. The same rule applies on any weekday morning until he says otherwise.
  - **Token budget until the weekly reset (Mon Oct 5, 7:00 am CDT; usage 82% on Oct 2, coordinator's rule):** no multi-agent workflows or reviewer fan-outs (one agent, one pass); no subagents for images or re-verification; prefer compute over tokens (unattended runs); the token-heavy coding of the first prototype lands after the reset unless Dustin says otherwise.
- **Official engine:** `rl/engine-2026-10-02/`, main-8626a35 (pinned Oct 2; a rules switch: the Sept 30 engine plus Victory Star after a Confusion heads (A), coin-flip damage prevention with Chase Order (B), kd's follow-ons and F1-F7; `engine/src/players/` unchanged). kta3, km3, k3, kp3 and kog3 (and kq3, kpr3 and kd3) replay their recorded games game for game, k3 and kp3 on all 45 cells, and every changed carrier game is accounted for (`results/engine_switch_rules_2026-10/`). kt3, ktb3 and ktc3 are kog-based: diagnostic, no identity claim. The Sept 30 engine (`rl/engine-2026-09-30/`, main-d363ba8) and the Sept 28 engine (`rl/engine-2026-09-28/`, main-9b4df9b) are kept; the Sept 28 one's kp-based kt presets replay the Sept 26-28 kt records.
- **Pilot:** km3 = kta3 + N2 (the Stadium damage bonus in the clock); kta3 = kog3 + switch 1 (the Tool cut); kog3 = kp3 + koa's opening switch A + kpg's discard-Energy credit F.
  - km3 was adopted in the tables Sept 30 (`results/km_tables_2026-09-30/READING.md`), after kta3 (Sept 30, `results/kta_tables_2026-09-29/READING.md`) and kog3 (Sept 28, `results/kog_composition_2026-09-27/READING.md`). Each is "unconfirmed" until the post-freeze read; if that read drops km, the default goes back to kta3.
  - The screen and the floor use km3 on both sides since the Sept 30 engine switch. The floor's pre-use re-check under km3 is `results/floor_recheck_2026-10/` (planned and committed with the Oct 1 pin; if it fails, the floor isn't used until Dustin has seen the pages). Sept 30's: `results/floor_recheck_2026-09-30/`; the Sept 28 one, under kog3: `results/floor_recheck_2026-09-28/`.
  - k3 stays the reproduction reference.
- **The yardstick:** scoreboard v3, 45 cells (`results/scoreboard_v3_2026-09-27/`). Development real error: k3 15.3, kp3 15.5, kog3 14.0; the target is 5.5. Every 45-cell reading prints the by-event interval beside the match-level one.
- **Candidates:**
  - koh (kog + R′, kph's registration): **not adopted; coverage complete Sept 29** (`results/koh_2026-09-28/laptop_reading/READING.md`).
    - Real error 14.0 → 12.3, but the ΔMSE interval crosses zero.
    - Altaria's vetoes count (v Lucario −4.8 ± 3.8; deck −1.8 ± 1.4).
    - Under Dustin's coverage rule, koh plays its own side worse on:
      - Weezing's second list, −3.8 ± 1.6;
      - B2e's held-out Hoopa / Absol, −10.4 ± 1.5 (his own Hoopa file −5.1 ± 1.5, reported);
      - Whimsicott, −2.0 ± 1.3.
    - Lucario and Vespiquen are repaired, and Rayquaza's gain is kept.
    - The Altaria diagnosis (`results/koh_2026-09-28/altaria_diagnosis/`) finds the crossed Swablu/Eevee line mostly a reading problem. The deficit is small and spread: R's attack-skipping v Lucario, and fix B double-counting the fresh Zone Energy (a candidate repair, not registered).
  - kt (kog + Tool/turn-effect switches; amendment 2, Dustin's word): **not adopted, as registered, Sept 29** (`results/kt_tables_2026-09-28/READING.md`; two readers agree on every number; the outcome was audited against the text).
    - kt3 (all three switches, footprint 64.7%, ordinary rule) fails: ΔMSE +1.0 (−16.7 to +18.9), plus own-side harm on three B2e held-out decks and two second lists. The scoreboard points at switch 2, but not beyond noise (ktb3: real error 14.3, τ margin −0.30 (−0.75 to +0.23)).
    - kta3 (switch 1, the Tool cut, 2.5%, reserve route) passes every test:
      - τ margin +0.21 (90% interval +0.06 to +0.31), real error 14.0 → 13.8;
      - Rayquaza's (d) +1.00 ± 0.39;
      - no harm anywhere.
    - The registration's fixed outcome, "kt3 fails: nothing adopted ... the next candidate is registered afresh", decides.
    - **Dustin, Sept 29 morning:** "honoring a registered 'not adopted' while an encouraging sub-result sits right there is the process doing its job."
      - **"kta alone, kog stays."** Register kta as switch 1 alone, on kog, with the same clause (d) gate as before: Rayquaza per the registration, with Skarmory as the motivating deck and Suicune reported.
      - "The +8.5 on your Skarmory deck is real simulator evidence and it should be in the registration as the reason the candidate exists; it isn't the gate." (The A/B: deck 07, kta3 v kog3, +8.5, 95% interval +6.7 to +10.4.)
      - **km:** "Goo-zooka's switch separate from km" (D1: option A). "Two switches that could each be adopted or dropped alone get two decisions, and a candidate is never adopted because its other half improved a different deck." "The specific caution is right too: Goo-zooka being played more often is a footprint, not a gain, and the footprint alone doesn't confirm the switch."
      - "**2,000 deals for clause (d)'s Lucario rows, fixed before play**" (D2). Clause (d) is paired and simulator-only, so its noise is all simulator noise, and quadrupling the deals halves it. The scoreboard cells are the opposite case, so no reason to enlarge every cell.
      - **kta registered, Sept 29** (Dustin, verbatim): "kta: approved. Register the text with clause (d) at 2,000 fresh deals per row, the 20% Jasmine threshold and baseline guard, and the coverage shortcut. Start as soon as possible within the stated plan. For coverage, skip mixed rows only when every corresponding deal has matching complete move fingerprints, decks, seeds and seats. Matching winners alone is insufficient." (`results/kta_2026-09-29/REGISTRATION.md`)
      - **km's threshold procedure approved, Sept 29, with three corrections before registration** (Dustin, verbatim):
        - "km: approve the threshold-setting procedure with these corrections before registration: 1. Use the exact midpoint for comparisons. Round only for display. 2. Complete the counter tool's support for all named cells before measuring either pilot. No reduced-cell substitute. 3. Freeze the exact paired-noise calculation and its random seed before measuring."
        - "Use development deals 200–299 to set the thresholds and deals 0–199 for the mechanism test, as drafted. Record and independently check the resulting rates, intervals and thresholds before the registered evaluation. Only the procedure needs my approval. The calculated numbers do not need another approval if they follow it exactly. If the procedure says a mechanism cannot pass, record that result without adjusting the threshold or trying another sample."
        - **Roles:** "Local Opus owns registration and integration. Cloud Opus owns km's build, counter-tool extension, tests and identity checks. Sonnet continues its separate calibration reliability task."
      - **Two additions to readings (columns, not rules):**
        - the reading says which condition carried the verdict. "No harm with almost no changed games" is the reserve route working as designed, but it says little. The informative parts are the gain on the pre-named decks and the footprint.
        - a per-cell breakdown beside a pooled gain, "so a gain that is really one cell is visible as one cell".
  - kta (kog + switch 1, the Tool cut; registered Sept 29): **adopted as the working pilot, "unconfirmed", Sept 30** (`results/kta_tables_2026-09-29/READING.md`; two readers agree on every number that gates; the outcome audit found no blocker).
    - Reserve route (footprint 2.35%). ΔMSE −4.3, 95% −8.8 to +0.0 at the deciding 20,000 reps: spans zero, "inconclusive at this size", so the fallback.
    - The fallback's four tests held: no harm (τ̂ +0.16, 90% +0.02 to +0.25; no veto; no deck worse), coverage (Scizor −0.45 ± 0.65; B2e held-out and second lists unhurt), (d) +1.03 ± 0.18 over 8 × 2,000 with every row above zero (Vespiquen +2.85, a third of it), and Jasmine at 31.35% against kog3's 0.39%.
    - Held-out direction flat (3 closer, 2 further, 1 unchanged, mean +0.00). Deck 07 replicated: +8.1 (+6.2 to +10.0).
    - Joined the post-freeze list Sept 30. An engine switch must carry its presets (and settle the `kta3` name clash) before the screen or the floor use it. Dustin, Sept 30: the switch "must reproduce the adopted kog-based kta, not accidentally select the older kp-based version". So it carries `kta<N>` as ec7e1a8 defines it, under the name `kta`, and replays kta3 game for game against `results/kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl` and `ec7e1a8_kta3_new17.jsonl` and `results/kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl` and `ec7e1a8_fresh_kta3_new17.jsonl` before the screen or the floor use kta3 (km's Amendment 1, (d) item 6, in `results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`).
  - km (N2 alone, the Stadium damage bonus in the clock; registered Sept 29 on kog, cloud build 9c11b30): **re-issued on kta, Sept 30, before any threshold or evaluation game.** Dustin (Sept 30, in the "Second brain from GitHub repos" session, relayed to the laptop session; verbatim): "Choose B. Re-issue km on the newly adopted kog-based kta before measuring thresholds or starting evaluation. Local Opus owns the dated amendment, resolves the kta3 naming clash, and updates the runner and blind reader. Cloud Opus adapts km's Stadium pricing to that clock and performs the required tests and identity checks. I approve that preparation, including laptop identity checks and threshold measurement under the already approved procedure, followed by the independent check. Registered tables still require my separate go-ahead. Keep 9c11b30 as implementation evidence. Describe cross-machine verification as agreement on the tested games. Keep the Riolu and full-clock Cubone tests, and leave fresh Stiffen counts deferred."
    - What he was answering: km's base-change rule read (A) literally (the cloud's 9c11b30 identity games were km's first game, so km stays on kog) or (B) as km's evaluation, which hadn't started. No km program had been built or played on the laptop and no threshold measured.
    - Dustin, later Sept 30, to the laptop session (verbatim): "This follows choice B. The main remaining risk is carrying old kog assumptions into the reused scripts. Have the existing reviewers check three things: The new comparison is km versus the adopted kta. That must hold throughout threshold measurement, coverage, mixed rows and the reading. Turning km's Stadium change off should reproduce that exact kta preset. Keeping the name `kta3` is acceptable when it is tied to the correct build. Preserve the historical binaries and records. The future official-engine switch must reproduce the adopted kog-based kta, not accidentally select the older kp-based version. Reuse the old workflow's general code, without spending more time validating its obsolete baseline. Its final runner and reader need one consistent set of candidate, baseline, reference files and program hashes. The revised 'agreement on the tested games' wording is appropriate. The order is now sensible: commit the reviewed amendment, cloud builds and checks the revised candidate, laptop performs the approved identity and threshold preparation, then you authorize the tables. Nothing in this update calls for another separate review workflow."
    - The amendment is in `results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md` ("Amendment 1 (Sept 30)"), committed 3aed736. The screen and the floor stayed on kog3 until the official engine switch (Sept 30, main-d363ba8).
    - **Read Sept 30: adopted as the working pilot in the tables, "unconfirmed", replacing kta3** (`results/km_tables_2026-09-30/READING.md`; two readers agree on every number that gates; the outcome audit found no blocker). Build B 1f6319e; cloud identity 114,840 games and laptop identity 5,240, all agreeing; thresholds by Amendment 2 (e308a65), independently checked.
      - Reserve route (footprint 13.85%). ΔMSE +1.1, 95% −7.0 to +10.1: spans zero, so the fallback.
      - The fallback's four tests held: no harm (τ̂ −0.04, 90% −0.26 to +0.18; no veto; no deck worse), coverage (B2e held-out, Scizor −0.23 ± 0.42, second lists unhurt), (d) on Lucario +0.444 ± 0.418 (lower edge +0.026, carried by the Suicune and Weezing rows), M1 Arena 35.7% against T 27.6% and M2 Training Area 33.8% against T 32.1% (kta3's rates 22.4% and 28.5% below).
      - Held-out direction flat (2 closer, 3 further, 1 unchanged). Joined the post-freeze list Sept 30. The screen and the floor stayed on kog3 until the official engine switch carried kta and km (pinned Sept 30 as main-d363ba8; they use km3 since).
    - **The reader's three gaps, and score.py (Sept 30).** Both outcome audits (kta's, km's) flagged the same three gaps in the blind reader. Sonnet fixed them in `read_km.py` for the next reading (branch sonnet/read-km-fixes; km's own reading used a14014e unchanged):
      - the ΔMSE lower edge is read from the unrounded value;
      - the held-out direction goes beside the verdict;
      - the detectable size starts from the unrounded real error.

      The fix needs one new full-precision line printed by `rl/results/table_readings_2026-09-24/score.py`, the registered scorer.
      - Dustin, asked via the Fable coordinator session "Is editing the registered scorer by that one line acceptable?" (recommended only if no script reading the pages breaks), verbatim: "Yes".
      - The laptop's consumer check found that every number-reading script parses the same values, and existing lines stay byte-identical. But four reproduction checks that compare pages line by line would falsely report "does not reproduce" if re-run: `kpr3_reading/check_score_runs.py` and km's and kta's `second_reader/rc_score45.py` / `sr2_score45.py`. So the merge was held.
      - The fix: the new line is printed only on an opt-in flag. The default page stays byte-identical, and only the new `read_km.py` asks for it. Dustin, via the coordinator, verbatim: "Flag option is fine, go ahead".
    - **The official engine switch carrying kta and km (Dustin, Sept 30 morning, in the laptop session, answering the switch plan's four questions; verbatim):**
      - Preparation timing: "now is fine, I don't have class on wednesdays this semester".
      - The pin: "Yes, pin if all pass (Recommended)", meaning the laptop pins if every replay matches, and a mismatch stops and comes to him first.
      - The default pilot for the screen and the floor: "km3 (Recommended)".
      - Rules items (Victory Star/Confusion, upstream 09e964f, PR #383, B4b data): "Keep them out (Recommended)". This switch is players-only: main plus B's `engine/src/players/`. The rules items go in a later switch under the full procedure.
      - The plan followed: the build; kta3 replayed against ec7e1a8's committed fresh and development games; km3 against B's; k3, kp3 and kog3 against the pin's references; the extras reported beside; CLI and goldfish checks; then the pin, the km3 default with `floor.py`'s pricing-pattern fix, and the floor's pre-use re-check under km3. kt3, ktb3 and ktc3 are kept as B defines them, labelled diagnostic with no identity claim.
      - **Pinned Sept 30:** every replay matched (`results/engine_switch_2026-09-30/README.md`). The official engine is main-d363ba8 in `rl/engine-2026-09-30/`; the screen and the floor default to km3, with `floor.py`'s pricing-pilot pattern fixed and tested. The floor's pre-use re-check under km3 follows (`results/floor_recheck_2026-09-30/PLAN.md`).
      - **The floor's pre-use re-check under km3 passed (Sept 30, 20:06 UTC; `results/floor_recheck_2026-09-30/`):** the floor stays usable.
        - brew-06 reads "fail" (125 of 1,920) and brew-06b "fail" (262), km3 on both sides, and plain `run_screen.py` gives the floor's wins per opponent exactly.
        - The deck 14 k3 control reads "untrusted" (196), repeating Sept 28's games.
        - Reported beside: brew-05b clears (577; 584 under kog3); **deck 07 (Skarmory) clears at 1,098 of 1,920 (57.2%), against 903 under kog3**, the Tool/Jasmine fix acting on Dustin's deck.
    - **The next engine switch, the rules one** (`results/engine_switch_rules_2026-10/PLAN.md`, 0a68b0a): it carries the cloud's Victory Star / Confusion repair (A) and its coin-flip damage prevention + Chase Order repair (B), plus kd's follow-ons and the fixes F1-F7. It follows the full rules procedure, in two laptop sittings.
      - Dustin, Sept 30 evening, via the Fable coordinator session, answering the plan's questions 1-6 and 8-10 (put to him as nine items, each with the plan's recommendation; verbatim): "Sure go for all 9".
      - So, as recommended:
        1. a conditional go, "pin if all pass", where every changed carrier or scratch game must be explained by an exact counter or by a trace meeting both halves, and a judgment-call trace comes to him;
        2. the scope is A + B + kd's follow-ons + F1-F7, with 09e964f, PR #383 and B4b data left out;
        3. the per-thread heads-cut value is kept;
        4. real carrier lists, extracted by the cloud from the committed Limitless archive;
        5. km3's coverage baselines are replayed as a gate;
        6. kd3's identity is a gate;
        8. overnight laptop runs on Oct 1 and Oct 2 nights, pushed by 7:00 am Central with main = origin/main;
        9. if A fails its mechanic check, A is held and B + kd ship if B passes;
        10. 09e964f's fix 2 is recorded as not taken (it contradicts the JP ruling the fork follows, `rules/06_sources.md:124`, and would break `rules_repair_retaliation_timing.rs:136`), and fix 1 stays "unchecked" until F8 or a second reader settles it. F8 has (the cloud, Oct 1; `results/engine_switch_rules_2026-10/f8/F8.md` at 5a929c0 on `claude/pensive-ptolemy-spwc0b`): **covered**, the fork already handles fix 1's case.
      - Question 7 (the order against N1) was the coordinator's operational decision: Sonnet does F1-F7 tonight on sonnet/rules-fixes, cut from cae37a3 with no `players/` change; R is its head; the cloud stays on N1.
      - **Sitting 1 passed** (steps 4-7c, the night of Sept 30, record b55aad4):
        - candidate 5a18d31 (main c9f4224 + R f8cfa9c);
        - 151,240 identity games equal;
        - the table's counters right;
        - Dustin's floor pages equal.
      - **Sitting 2 passed** (steps 8-10, Oct 1 evening, record 78e51e8):
        - 8b and 8 played, with every all-zero-counter game identical. Of 24,000 carrier deals, 3,750 changed, and all are handed to 8c.
        - km3's coverage baselines (66,500) equal.
        - CLI, goldfish and the screen equal.
        - Details: `results/engine_switch_rules_2026-10/README.md`.
      - **Condition 3** (PLAN.md:95): it reads "no exact counter on the board and no trace meeting both halves". That is the coordinator's wording (Oct 1), consistent with his Q1 answer.
      - **Dustin's word on Victory Star smoke game 28 and the pin** (Oct 1 evening, in the Fable coordinator session, relayed; verbatim): "Accept Victory Star smoke game 28 as the specific documented judgment exception. State clearly that the Copycat explanation is supported by a possible sampled path, not a replay of the bot's exact original search. My conditional approval stands: pin the existing candidate once all remaining required trace checks pass. Account for every changed game, including all 297 flagged cases. This exception does not waive unexplained carrier games. Complete the planned checks after the pin. Bring me any new failure or judgment call; otherwise proceed."
        - So game 28 is the one documented judgment exception. Its Copycat explanation is a possible sampled path, not a replay of the bot's exact original search.
        - The pin goes ahead without a further word from him once 8c passes:
          - 0 unexplained;
          - no new judgment call;
          - every changed game accounted for;
          - the 296 + 1 CONDITION 3 games each with a trace meeting both halves;
          - the 63 8b rows agreeing with the cloud's.
        - The coordinator audits 8c before the pin. Steps 11-14 follow, then the floor re-check (15). Any new failure or judgment call stops and goes to him.
      - **8c and his acceptance of 8 games** (`results/engine_switch_rules_2026-10/8c_RESULT.txt`, `8c_DECISION.md`). Of the 3,813 changed games, Sonnet's traces put 2,414 on the board and 1,391 in lookahead with both halves; the CONDITION 3 rows were 297. The rule could not settle 8:
        - **2 prefix games:** a Victory Star offer with its exact counters at the extra tick.
        - **6 games** (5 promotions and i106): B's queued coin frame, resolved free at ply 3 inside the search, which the probe didn't count. Reverting just that one change brings back the old choice and scores. Sonnet's revert check over all 1,395 coin-Ability lookahead games had 0 failures (`8c_FIVE_LOOKAHEAD_opus.md`, `trace_8c_sonnet/`).
        - **Dustin, Oct 2 (about 1:30 am Central), in the laptop session; verbatim, his chosen answer:** "Accept all 8 and pin (Recommended)". The question put to him was whether to accept the 8 as explained and pin tonight.
      - **Pinned Oct 2** (early morning Central; `results/engine_switch_rules_2026-10/README.md`, "The pin"): 8c passed on his conditions and his acceptance of the 8, with game 28 the one documented exception. The official engine is main-8626a35 in `rl/engine-2026-10-02/`: the programs sitting 1 built from 5a18d31 and tested, never rebuilt. The repairs, kd's follow-ons included, act only with a Victini or a coin-Ability Pokémon in play, and every replay without one was identical (steps 7-10); the screen and the floor stay on km3. What the switch left open is `rules/09`'s open entry, for the next rules switch. The floor's pre-use re-check under km3 (PLAN step 15) follows (`results/floor_recheck_2026-10/PLAN.md`).
      - **The floor's pre-use re-check passed** (Oct 2, 07:36 UTC; `results/floor_recheck_2026-10/verdicts.txt`). The floor stays usable under km3 on the new engine.
        - brew-06 fail 125, brew-06b fail 262, the deck 14 k3 control untrusted 196, brew-05b 577, deck 07 1,098: Sept 30's exactly.
        - All 16 outputs are equal to Sept 30's but for the engine lines.
    - **Dustin's rule on card text** (Oct 1, in the laptop session; verbatim):
      - "I don't know why you have such a hard time with understanding the rules. The first coin of the next coin flip for an Attack, Ability, or Trainer will definitely be heads. Not a status effect. Same thing with meowth, why would gyarados's attack bypass it magically with discarding water Pokemon?"
      - Then: "I don't mind getting video for proof, but if there is a plain reading of the text, the engine build should go with that, unless there is contradicting evidence. Not the other way around".
      - So the engine follows the plain reading of a card's text by default, and only contradicting evidence overturns it. A case is never kept on the old path "until seen in the game".
      - The rules switch's two gated Victory Star cases go to the next rules switch on the plain reading. They are CoinFlipToBlockAttack, and Confusion with a pending Will. The four bugs from the Oct 1 recordings go there too (`results/rules_recordings_2026-10-01/READOUT.md`).
    - **The tables' go-ahead** (block item 9; Amendment 1 (g) step 5). Dustin, Sept 30 about 02:20 UTC, in the laptop session, after 3aed736 was pushed (verbatim): "The cloud has the message go ahead on the tables". The tables start in the laptop's queue as soon as the preparation has passed: the cloud's round at B committed as passed, the laptop's identity games and timing pair, the threshold sample, the independent check and the thresholds amendment, in (g)'s order. A stop in any of them holds the tables and goes to him.
      - **His confirmation of that reading** (Sept 30, after km's reading, given in the Fable coordinator session "Work delegation and task routing" and relayed to the laptop session; verbatim): "Yes, go ahead on the tables meant once preparation passes". This closes the outcome audit's N7 (`results/km_tables_2026-09-30/second_reader/OUTCOME_AUDIT.md`).
  - kph is not run (superseded by koh on the composed base).
- **Waiting on post-freeze data:** kpg's confirmation, koa's no-harm re-check, kog's own row, kta's and km's no-harm re-checks (`results/postfreeze_2026-09-27/README.md`). Read once, at 804 + 303 matches (about mid-October) or at the last pull before Mega Garchomp ex.
- **Holds:** deck ranking stays on hold (14.0 against 5.5; the ladder-weighted panel and calibration are unfinished). The floor check may be used under the A2 decision. The quick screen's ranking is on hold.
- **Finished, with where:**
  - kp3 was confirmed on the Sept 25 holdout, which is now spent (`results/holdout_kp3_2026-09-25/`).
  - Not adopted: kd3, kq3, and b3o3n4; kpr3 and kpf "not adopted, provisional".
  - kpg and koa were read (`results/kpg_2026-09-27/`, `results/koa_2026-09-26/`) and composed into kog.
  - The gauntlet: the 45 cells and the variation check (`results/gauntlet_runs_2026-09-26/`).
  - The blind quizzes 1 and 2 (`results/blind_quiz_2026-09-25/`, `results/blind_quiz2_2026-09-27/`).
  - The recordings and frame checks (`results/recordings_check_2026-09-25/`).
  - The engine switches of Sept 25, 27, 28 and 30, and the rules switch of Oct 1.
  - The Hydreigon and Altaria detector networks; B2c and B2e; the X Speed census; the brew pilot checks.

**Order of work.**
1. Scoreboard v2 is the table for decisions (development half); the holdout confirms, once.
2. Brew tools: A1 harness (one build kept, the other a fixture; coverage flag checked against kp's audited texts; the
   one pre-registered tempo metric, with the dated prediction that brews 07 and 08 are fastest and 10 slowest); A2
   screen readouts with kp3 on both sides (which needs PR #1 merged, an engine built from the merged main with its
   identity recorded, meaning its hash plus proof that k3 and kp3 replay all 14,000 table games move for move, and
   `project_manifest.json` and `decks/screen/run_screen.py` pointed at that build, since the verified rules4 program has
   no kp3 and the screen script hard-codes k3), a ladder-weighted panel, worst matchup and failure modes instead of an
   average, one-sided rows. **Dustin's decision, Sept 25:** the hold lifts for the floor check only; ranking stays on
   hold until the ladder-weighted panel and the held-out decks exist. The floor starts after the engine switch passes.
   Bar: 20% under kp3 on both sides; a result within the screen's own noise of 20% reads "borderline". Game count fixed by
   Dustin on Sept 25 before any floor game: 240 per matchup, 1,920 per floor run (band about ±1.8 at 20%). The 25%
   "small share" threshold stays, with the actual share printed beside every verdict; it is a flag for a human, and is
   revisited only if a case lands in the 25 to 45 gap. "Untrusted" keys on the coverage flag only (cards the bot is known not
   to price), not on "central" cards, which Dustin rejected on Sept 25 (every card has a use, and "used" is not one
   thing: Crobat's job is its ability, Comfey's is the bench, Regigigas's is to take hits). Each flagged card carries a
   role set by the page's author, printed beside its count: attacker (attack chosen when payable), activated ability
   (used when offered), bench piece or passive (benched when in hand and benchable), wall (kept Active when a switch was
   available), Tool or Stadium (played when playable); roles with no countable move are marked "not countable" and
   never feed "untrusted". No confirmation from Dustin is needed; he objects on the page when a role is wrong. A fail or
   borderline result shows the worst matchups, the failure modes and the coverage flag, recomputed under kp3. A result
   reads "untrusted" instead of "fail" only when a flagged card central to the list was used on a small share of the
   turns it was available; the page reports available and used counts for every flagged card. Check before use: both
   Payback lists must come out "fail", not "untrusted"; A3 per-game calibration from the Ladder Log; A4 one brew to 15 to 20 ladder games with a
   stop-loss; A5 B4b as a data refresh (B4b is reprint-only: its five "new" cards are new-art reprints, and the one new card
   in the window is Mega Garchomp ex, an October promo, `results/b4b_prep_2026-09-26/`; Dustin, Sept 28: B4b waits up to
   three days for upstream) with bit-for-bit reproduction of the k3, kp3 and kog3 tables (14,000 games each) and of kta3's and km3's recorded games (the Sept 30 switch's references) on the pinned engine `rl/engine-2026-10-02/` plus a card-effect pass, Mega Garchomp ex as its own small refresh when its text is published, and an
   upstream code-merge trial in the cloud before C1.
   - **Dustin, Sept 28 about 7:30 pm Central** (typed in the Fable session, relayed verbatim; recorded the same day):
     - **A4, which brew:** "Play the one you'll enjoy twenty games of — that's the only rule that matters, and the log's spread problem came from switching. But if it's a coin flip between 07 and 08, 08 is the better evidence ... it's an unchanged real Limitless list, so it's the first deck you'd play that has both a screen number and a real cell." Also: "the A1 prediction — 07 and 08 fastest to set up, 10 slowest — gets its first real test from whichever you play, so note setup speed when you log." The brew pages in `results/floor_brews_2026-09-28/` say what to note.
     - **A5, the merge trial:** "Trial it whenever the cloud has room, in isolation, off the official engine — a separate worktree, the full test suite and the identity replays against the current references, with the new cards' text checked against `card.py` as they come in. Don't pin it until two things are true: the current candidate queue (koh, kt) has its verdicts, and the mid-October read has been taken on the B4a meta it was registered against. The Garchomp release is the natural pin date."
     - **The Sleep/Paralysis pull request upstream: "yes, and first."** "If upstream merges the fix before you merge upstream's B4b, the new set arrives with the fix already in it and there's nothing to re-patch." The seven repairs from this week may follow, "but one clean pull request first". The laptop prepares it; Dustin opens it from his own account.
       - **Checked the same night: nothing to send.** Upstream merged the same fix on Sept 27 (commit `e38b77d`, PR #379, with its own tests), so the new set will arrive with it already in, which is what the ruling wanted (`../engine/UPSTREAM.md`). Which fork repair upstream still lacks is being checked for his choice of a first PR.
       - **Dustin's pick, about 9 pm Central Sept 28** (relayed verbatim by Fable): "Send the non-attack damage fix."
         - His reasons: "it's a rules error with the card text as the argument, so the maintainer doesn't have to trust our simulator to accept it"; "it copies a gate upstream already uses two lines away for Steel Apron and Metal Core Barrier, so it reads as consistency rather than opinion"; and "it touches a card you play", Heavy Helmet in deck 01.
         - His conditions before the branch goes up:
           - "Every one of the four cards' text — Heavy Helmet, Harden, Hide, Blocking Shell — quoted from `card.py` in the pull request body, with the phrase 'from attacks' shown";
           - "the rules reference for Poison, Burn and Bad Dreams damage not being attack damage cited from the project's `rules/` sources rather than asserted";
           - "one test per card plus one that shows Steel Apron and Metal Core Barrier unchanged, so the diff demonstrably doesn't widen."
         - "If this one is accepted, the thirteen small missing repairs become a sequence, one at a time, each with the same shape."
         - The list is in `results/overnight_2026-09-28/README.md`.
         - **Opened Sept 29 as https://github.com/bcollazo/deckgym-core/pull/383**, from his account at his word. It carries three in-game proofs (Heavy Helmet v Poison, Heavy Helmet v Water Shuriken, Harden v Water Shuriken), six tests, and fmt and clippy clean (`results/upstream_pr_2026-09-28/`).
     - **B4b and the size rule** (Dustin, Sept 28 about 11:15 pm Central, verbatim via Fable): "On B4b going live tomorrow: if RUN5's line is right that it's reprint-only, the meta doesn't shift and the post-Sept-24 confirmation window stays open, so nothing about the size rule changes — but 'reprint-only' should be confirmed against the card list when it lands, because if it isn't, the window closes tomorrow at an eighth of the data and that becomes a decision."
       - **Release time** (Dustin, Sept 29, from the app): B4b releases at 8 pm Central on Sept 29.
       - **Checked Sept 29, before the release: B4b is reprint-only** (`results/b4b_prep_2026-09-26/B4B_REPRINT_CHECK_2026-09-29.md`). Upstream's card data landed early, at main 9044ff6 "B4b", 1:57 am EDT.
         - Two agents checked every card, the second as an independent recheck. All 429 B4b cards and 8 of the 9 new promos are reprints, with game text identical to an earlier printing.
         - The one new card is P-B 099 Mega Garchomp ex, as this line said.
         - So, by Dustin's rule, the meta doesn't shift, the post-Sept-24 confirmation window stays open, and nothing about the size rule changes. No decision is needed.
         - The two later checks were cancelled.
         - The same upstream range also brings 09e964f, which fixes two knockout-promotion bugs. Fix 2 is not taken (Dustin, Sept 30: it contradicts the JP ruling the fork follows). Fix 1's case is already covered in the fork (F8, Oct 1), so there is nothing to port; F8 did not audit every path. `rules/09` records both.
       - **To do when the list lands**: check each B4b card against `lib/card.py` (a reprint is the same name and text as an earlier printing) and record the answer here.
       - If it isn't reprint-only, nothing is decided here. The consequence goes to Dustin as a decision, with the numbers from `results/postfreeze_2026-09-27/`.
     - **The B4b release-note defaults** (decided under his delegation by the Fable session and the fourth session, Sept 28):
       - B1: keep CRLF in `engine/` for this refresh.
       - B2: the version string is recorded, not changed.
       - B3: moot; the replay references are the Sept 28 tables.
       - B5: the 44 Pocket Deck Lab replay segments are not a condition; the full suite and the 14,000-game replays are the standard.
       - B6: Mega Garchomp ex is its own refresh.
       - B8: skip the QR catalog until a B4b card fails to scan.
       - B9 is still his: the merge trial's window.
   - **The cloud** (Dustin, Sept 28 about 7:30 pm Central, then revised about 7:50 pm, both verbatim via Fable):
     - First: "each candidate gets one cloud round — build, one review, identity check — before its table, with a second cloud round only after a table has asked a question ... The laptop is free and does the tables."
     - Revised: "I don't want a weekly cloud cap, but don't want things overlapping unnecessarily. As long as no one is stepping on one another, the cloud gives us two more cores to run/test things."
     - So there is no cap. The one-round shape is the default order. Before a cloud job starts, its plan names the laptop job it must not duplicate, and the other way round (Fable's practical rule). kt's cloud cross-check (`results/kt_kog_2026-09-28/`) is the one deliberate overlap.
     - **Where work runs (Dustin, Sept 30, in the "Second brain from GitHub repos" session, relayed to the laptop session; verbatim):** "Longer runs and builds should be laptop, parallel smaller jobs should be cloud". It came after he asked why the cloud was running km's 114,840-game identity (about 6½ hours by its log) when the laptop plays about 8.6 games a second (about 3¾ hours), with the laptop waiting on it.
       - **It supersedes** the part of the rules above that gives builds and identity replays to the cloud. From the next job: release builds, long identity replays and tables go to the laptop; the cloud takes smaller jobs that can run in parallel (code changes, unit tests, the one code review, short smoke checks, diagnostics). A candidate's cloud round is fitted to that. Laptop quiet hours still apply to the long runs.
       - **km's round at B** (started before the rule) finishes on the cloud, unless Dustin says to move it. The laptop's part is unchanged (km's Amendment 1 (g)).
   - **The shot list and blind quizzes: a standing rule (Dustin, Sept 30 evening).**
     - To the laptop session, verbatim: "if anything should be added to the shot list artifact or another quiz helps at any point, feel free to do either".
     - Then via the Fable coordinator session, verbatim: "quizzes or the shot list should be used to clear up things whenever helpful, so I don't have to specifically ask for it."
     - **So any session may add a Pocket Shot List row or build a blind quiz without asking.** It tells Dustin in one line what the row or quiz is evidence for.
     - An untaken quiz or an unrecorded shot is never a blocker.
     - **Extended Oct 2 to gameplay recordings** (Dustin, relayed by the coordinator, verbatim): "at any time, if more gameplay recording of certain decks helps, if capturing unclear things on the 'shot list', or making more quizzes helps improve the bot, I am available to do anything to help."
       - Each of his games costs him about 10 minutes plus recording time, and saving his hours is the point. So ask for the smallest targeted set: which decks, which situation, and what the transcript must capture (hand at each turn start, every drawn card by name, plays in exact order, opponent hand size).
3. Pilot quality: kd (the defender's Weakness and reductions in the clock) read against kp3 on v2; then, approved by
   Dustin on Sept 25 as optional and only after kd is read, **one Altaria detector network** on an otherwise idle
   laptop night: the Hydreigon recipe (two networks trained against each other, pair checks passed before anything is
   read), read afterwards against kp3 with the key comparison fixed before training as the network's Altaria against
   kp3's opponent minus kp3 against kp3, pairing Altaria v Lucario (Limitless ±4.9, kp3 62.4 against real 71.9), the
   same readout as Hydreigon's (attack and ability use rates against kp3 on the same deals, benching, the knockout
   audit, network v network), a new seed block, and no follow-up training whatever it shows: its value is the audit of
   what it does differently, not the bot; kpr (projected readiness for the Active) registered with its census
   footprint, read the same way; B2e held-out archetypes that
   are Dustin's own decks (card check, legality scan, k3 and kp3 rows; no fix may move one more than 2 further from
   Limitless); B3 features then a Texel fit (Weakness, status, the three B2c habits), judged by the adoption rule and
   the held-out decks, then left alone; B4 Dustin's one-hour blind quiz on decisive positions, then about ten saved
   games with the sequential stopping rule, the bot on the archetype's list and never his exact list; B5 blind-spot
   fixes under the card-agnostic rule, each with a paired A/B and the sentinels (queued classes, Sept 26: Tools and
   turn effects (`kt`); Trainer pricing, shown early by the gauntlet's variation check, where one swapped Trainer moved a
   deck 4 to 7 points on average, Team Rocket's Boss especially (also X Speed played with no retreat after it, 23% of
   its turns and 52% in Dustin's deck 12, `results/xspeed_census_2026-09-27/`; and, Dustin Sept 28 about 11:15 pm, verbatim via Fable: "Brew 03b's borderline through Goo-zooka at 2.1 percent use is the Trainer-pricing blind spot showing up again, which puts a fourth card on that candidate's list": 95 of 4,445 chances, `results/floor_brews_2026-09-28/`; the draft is `results/trainer_pricing_2026-09-28/`, not registered); discard-cost attacks and discard-pile Energy (`kpf`)); B6 done (skill explains under 0.6 of
   any gap; Sceptile v Vespiquen out of quarantine as drift-sensitive, Altaria v Sceptile in); B7 not now, gated by
   the cloud transfer probe or three card-patch entries in B5's log.
4. Not doing: policy networks trained on who won as the pilot (one network per mispiloted deck as a blind-spot
   detector is allowed, read the way the Hydreigon run was); k7 or depth tables; tuning to Limitless cells; new
   launchers, guards, gates or ledgers; five-worst-cell screens; "cheapest within noise"; the kq/kv bench-credit line.

**Rules.**
- PASS for the pilot: real error τ̂ at 5.5 or less; every cell's confident miss at 10 or less; every deck's
  7-opponent average within ±6; confirmed on the holdout.
- Adoption of a pilot: paired ΔMSE bootstrap with the whole 95% interval below zero; vetoes (a cell's miss grows more
  than 6, a deck's gap more than 2, a held-out deck more than 2 further) count only when mixed rows on the same deals
  show the changed pilot's own side got worse beyond the mixed row's paired noise (about ±4 at 500 games), and never
  on a cell whose Limitless band is wider than about ±15; otherwise they are investigation items (this refinement is
  pre-registered as of Sept 25 for tables read from now on). Correlation, average miss, favorites right and pairings
  beyond chance are reported, never decided on. Candidates are confirmed on the holdout before adoption is permanent, and confirmation needs size as well as
  direction (Dustin, Sept 25): on the holdout alone, the τ̂ margin must be at least half the development half's and its
  own 90% interval must lie above zero; the pooled interval and the sign are reported beside it but cannot confirm on
  their own.
- **Engine repairs: the switch procedure and the "reaches the mechanic" rule** (Dustin, Sept 26-27; worked example in `results/engine_switch_2026-09-26/`).
  - **Replays:** replay every repair on the table (k3 and kp3, 14,000 games each), and list the games each one changes.
  - **The mechanic check:** a repaired engine becomes official only if every changed game reaches that repair's mechanic.
    - A game reaches it either on the board, or **in the bot's lookahead**: inside a line the bot's search examined, where the changed outcome changed its choice.
    - "In lookahead" counts only with both halves present:
      1. a code path gated on the mechanic's condition, so the fix cannot run otherwise;
      2. a trace showing that condition reachable within the bot's search depth at the game's first divergence.
    - A fix without a gate, or a divergence with no reachable condition, fails. That engine waits.
  - **The standing template for every repair:**
    - the gate, read in the code;
    - watch-only instrumentation counting the mechanic per game, checked to change no play;
    - a move-by-move trace of each changed game without an on-board firing, to its first divergence.
  - **Worked example (Sept 26-27), the promotion fix (5bab907):**
    - 7,437 of its 7,461 changed games had an on-board end-of-turn or Checkup Knock Out.
    - The other 24 first split at a turn where a Checkup Knock Out was within the bots' reach: 22 plainly, 2 through an attack plus Burn. All were in the cells where its on-board changes are.
    - Its code runs only when a promotion is pending after the Checkup. So it passed.
  - **A refactor of a rules file** (Dustin, Sept 28; general, since it will recur; worked example `results/engine_switch_2026-09-28/`):
    - It is acceptable only when all three hold:
      1. the source equivalence is written down;
      2. the full test suite passes;
      3. games that reach the touched paths replay identically on the old and new builds.
    - The whole-table replay alone doesn't qualify when the table's lists don't reach the changed code: identical games that never execute the changed lines prove nothing about them.
    - It is the "in lookahead" rule from the other side: the check has to be where the change is.
  - **Baselines move with the engine.** k3 and kp3 on all 45 scoreboard cells at the new engine become the frozen table. Earlier tables stay as history with their hashes. Every reading uses baselines from the same engine as the candidate, with no exceptions.
- **Confirming a reserve-route (no-harm) fix** (Dustin, Sept 27; standing rule, not decided per candidate).
  - A no-harm fix can't show a gain of fixed size by design.
  - Its confirmation is a re-check of no harm on post-freeze Limitless events (after Sept 24): the τ̂ margin's 90% lower bound at −1.0 or above, and no veto, with the fix's own real cells reported.
  - Until then it is the working pilot, "unconfirmed".
- **When post-freeze data is read** (Dustin, Sept 27; standing rule; the pull is in `results/postfreeze_2026-09-27/`).
  - **Trigger:** read once, when the post-freeze pull reaches half the development half: 804 matches on the 28 panel cells and 303 on the 17 new cells. That is the smallest size at which the confirmation rule has meaningful power. Until then, re-pull and count sizes only, never results.
  - **The Mega Garchomp ex clause:** if its release (mid or late October) comes first, read at the last pull before it, with the size printed beside the result. That is a confirmation on the B4a meta, which the pilots were built against.
  - **One pull, every pending check.** Every check waiting on post-freeze data is read at the same pull. The list is pre-registered in the pull's folder before the data is opened. The data is looked at once, for everything, never once per candidate.
  - **Rolling freeze.** Once read, that pull becomes development data like everything before it. The next confirmation waits for events after its date. The post-Garchomp meta becomes the next confirmation set that way, once the table decks are refreshed for it.
  - **How a result reads:**
    - At this size the pass criterion is unchanged: direction, plus at least half the development margin, with the interval not crossing a loss (its own 90% interval above zero; for a no-harm re-check, the lower bound at −1.0 or above and no veto).
    - A failure reads **"not confirmed at this size"**, never "no better", as for the first holdout, and more strongly here.
- **The frame a candidate is read in** (Dustin, Sept 27).
  - A candidate's adoption verdict is read on the cells it was registered on. Changing the frame after the result is what the rules exist to prevent.
  - An "adopted" must also survive the coverage cells it touches: there they count for no harm only. A veto blocks the takeover; a gain is reported, not credited.
  - **How coverage rows count** (Dustin, Sept 28 about 6:40 pm Central, typed in the Fable session "Recommendations and advice" and relayed verbatim; recorded the same day): "coverage rows count for the mixed-row veto and are reported for accuracy."
    - The accuracy half needs real cells, and neither Scizor nor a second list has its own. Scizor's nine real lists can't anchor a cell. A second Lucario list shares Lucario's archetype cell with the first, and scoring both against it counts the same real data twice. So for accuracy they are reported, never vetoing.
    - The own-side half ("no deck's own side plays worse beyond noise in the mixed rows") is simulator-internal and needs no real cell, so it applies to them in full. A candidate that makes Scizor or a second list play its own side worse beyond paired noise has done harm, and that counts: "Coverage decks hurt is exactly the failure mode the gauntlet was added to catch."
    - So coverage rows (Scizor, the second lists, and B2e's held-out decks) get mixed rows every time, not only after a veto. This supersedes kph amendment 2's two-part tests, and the matching text of kt's amendment 2 (its R6).
  - **What koh's and kt's readings hinge on** (same message): "No verdict from me without the readings, but what each hinges on is fixed already."
    - koh: the 45 cells under the standard rule, "no coverage deck hurt, and the Hyper Ray census beside it".
    - kt: the reserve route, "the 15 percent trigger read first, no-harm with the −1.0 lower bound, no deck hurt", and the real gain.
    - "If the readings show those, the verdicts write themselves; if they show something else, that's the morning conversation."
  - **kt's clause (d) gates on Rayquaza, as registered** (Dustin, Sept 28 about 7 pm Central, relayed verbatim by Fable). "A registration written before the games and satisfying the rule outranks a reviewer's paraphrase after it."
    - Suicune is reported beside. The same direction as Rayquaza is supporting evidence; the other direction is "a finding to write down, not a gate that fired".
    - Fable's Suicune wording of Sept 28 was a misstatement and is withdrawn. His full words are in `results/kt_tables_2026-09-28/README.md`.
  - **Accuracy judges only what it can detect** (Dustin, Sept 29 morning, in the laptop session; adopted from the eval-power check, `results/eval_power_2026-09-29/`).
    - His words: "a candidate whose gain is below the detectable size is not judged adopt or reject on accuracy at all. It's judged on no-harm, the coverage decks, and its behavioural footprint (the census counts — did it chip, did it play the Tool, did Rayquaza attack), and 'not adopted' for a sub-threshold gain is recorded as 'undetectable at this size,' not as a negative. Otherwise the project keeps rejecting fixes it can't measure and calling that rigor."
    - **The detectable size.** Every ΔMSE reading prints the interval's own sd and the true gain it would detect: half the time (MDE50, 1.96 sd, which is the interval's half-width) and 80% of the time (2.80 sd), each also as real error.
      - The check found the size is set by the candidate. Big movers like koh are limited by Limitless's thin cells (about 80% of the variance): MDE50 is about 2.1 points of real error, 14.05 → 11.9. Small-footprint candidates are limited by the simulator's deals: MDE50 is about 0.7 points.
    - **The rule: an accuracy result has three outcomes** (corrected Sept 29 on Astra's catch; Dustin: "it should be written exactly that way"; the first transcription had sent every non-gain to the fallback):
      1. **Interval wholly on the improvement side** (ΔMSE, new minus current, wholly below zero): demonstrated improvement. The accuracy clause passes.
      2. **Interval wholly on the worsening side** (wholly above zero): demonstrated worsening. The candidate fails on accuracy "regardless of anything else — no fallback".
      3. **Interval spanning zero:** "inconclusive at this size". Only this case goes to the fallback, where the verdict rests on four things:
         - no harm: the τ̂ margin's 90% lower bound at −1.0 or above, and no mixed-row veto that counts;
         - the coverage decks, by "How coverage rows count";
         - the pre-named decks: clause (d);
         - the behavioural footprint.
         - Passing all four means adopted, "unconfirmed", with confirmation at the post-freeze pull as for a no-harm fix.
         - Failing any means not adopted, recorded by the test it failed, never as an accuracy negative.
    - **The footprint counts are diagnostic in the normal route and gating only in the fallback.** Even there they gate only as predictions written before the games, with a threshold attached: "Jasmine played on at least X percent of eligible turns", not "more often".
    - **Clause (d)'s gain stays required in both routes.** It is the paired, simulator-only test whose noise more deals actually reduce, "so it's the one place a small gain can be shown rather than assumed".
    - **More deals only where they help.** Where the simulator's share dominates a candidate's cells, the registration may fix more deals in those cells before the tables, on the cloud's spare cores ("cheaply, and only there").
    - **Scope.** It applies to candidates registered from Sept 29. Past verdicts are relabelled, not re-read:
      - koh's (−45.1, −100.4 to +10.4) and kt3's (+1.0, −16.7 to +18.9) accuracy intervals both span zero, so both read "inconclusive at this size";
      - both stay not adopted, on their vetoes and coverage harms;
      - a new reading needs a new registration.
  - **The held-out direction, reported beside every verdict** (Dustin, Sept 29 morning): "Report the held-out direction beside every verdict, as proposed, and revisit whether it should gate when the post-freeze data reaches the size rule — at that point it's a real test."
    - Every verdict prints how B2e's held-out archetypes (pairings 0-47) moved under the candidate: how many moved closer to their Limitless figure and how many further, and the mean change in miss.
    - It gates nothing. Blocking on "dev up, test flat" would reject at random, since "flat" is the expected reading for any sub-threshold candidate, real ones included.
    - Revisit when the post-freeze data reaches the size rule ("When post-freeze data is read").
  - Every candidate registered from Sept 27 is registered on the 45 cells, so the split doesn't recur. (koa: the 28 table cells for the verdict; its two new cells, where the panel's Altaria is the opponent, for no harm.)
- **Composing candidates into one pilot** (Dustin, Sept 27: "two pilots is the drift risk").
  - Candidates that pass separately and touch different things are combined into one pilot through a **composition check**, not a new candidate:
    - the combined code's identity checks;
    - one table on the 45 cells;
    - no veto;
    - accuracy no worse than the better component alone.
  - Each component keeps its own verdict and evidence, and the combined pilot inherits both.
  - First case: kp3 + koa's opening (switch A) + kpg's discard credit, run once kpg's held-out check is in.
    - **Passed Sept 28 as `kog`** (`results/kog_composition_2026-09-27/READING.md`): identity 14,000 of 14,000; real error 15.5 → 14.0 on the 45 cells; no veto; level with kpg3 (−0.01).
    - It is the working pilot, "unconfirmed" until the post-freeze read. The screen moves to it once the official engine carries its code.
- **Open causes** (cells whose remaining error has no named cause; each fix's reading adds to this list):
  - **Sceptile v Vespiquen:** sim about 66, real about 33.
  - **Altaria v Vespiquen and Altaria v Weezing:** koa's correct opening fix lifts Altaria past their real cells (52.0 v 37.6 and 40.3 v 33.0), so their remaining error has one less explanation (Dustin, Sept 27).
  - **Hydreigon's overshoot** under kpr/kpf.
  - **Altaria/Greninja's gap** (41-44 v 51-59).
  - **The Rayquaza v Lucario remainder:** 55 under kpf against a real 64-73.
- **A "not adopted" is provisional until the coverage decks are read** (Dustin, Sept 26 evening, registered as a rule).
  - It has happened twice:
    - kp3 was vetoed, then found to be the fix.
    - kpr3 was "not adopted" on the 28 cells on Sept 26. On the 17 new scoreboard cells it was then the best pilot by a wide margin and the only one that plays Rayquaza (`results/gauntlet_runs_2026-09-26/`).
    - Both times the meta table couldn't see what the fix did.
  - So a scoreboard "not adopted" stands only once the candidate has also been read on the gauntlet's coverage decks: the new scoreboard decks, the held-out archetypes and the coverage rows.
  - A candidate can be reopened by coverage evidence, and that does not count as moving the goalposts.
  - Reopening means a new reading under the rules in force. It never re-reads an old reading until it passes.
- **Development data, stated with each reading:**
  - Cells used to diagnose a problem or design a candidate are development data for that candidate.
  - For the 17 new scoreboard cells (used Sept 26 to diagnose Rayquaza and design `kpf`), the holdout is Limitless events after the freeze date, not a split of the 17.
- **Reserve route for a change the table can barely see** (Dustin, Sept 26: "approved as sharpened").
  - Its clauses (a) to (e) and the closure sentence are as fixed in section 8 of `docs/REVIEW_2026-09-24_direction.md` (line 130), including that the gain must show on at least one deck that isn't Dustin's.
  - The route is chosen by the footprint measured on the table, read before anything else; under 15% it applies, otherwise the ordinary adoption rule does.
  - A panel archetype whose real Limitless lists carry the relevant cards may serve as the non-Dustin deck (Dustin, Sept 26; covers Altaria for `koa` and Suicune for kt).
  - **Nothing is excluded from testing because it matches Dustin's decks** (Dustin, Sept 26: "if my deck matches a limitless deck, that doesn't mean you shouldn't test it. This argues for a broader test group after repairs, not restriction.").
    - Clause (d) asks only that the gain also show on a real Limitless list with known results, not on his own files alone.
    - An archetype he also plays still qualifies. "His decks" means the files he gave the project (`decks/dustin/` and the brews built with him).
    - So Dragonair Mega Rayquaza ex can serve for kt's switch 1, and his own files and the held-out archetypes that match them (B2e) are tested and reported too.
  - Registered under it so far: `koa` (`rl/results/opening_active_census_2026-09-26/REGISTRATION.md`).
- **Test groups** (Dustin, Sept 26: "Smaller tests for finding and repairing bugs, then a larger test for changes to the engine").
  - **Small tests find and repair bugs:** identity replays, spot replays, card checks, footage checks.
  - **The gauntlet is for engine and pilot changes.** It is the most-used Limitless decks, with at least one deck of every Energy type. It starts with the 8 table decks (28 pairings), plus the 6 held-out tournament archetypes against the 8 (B2e, 48 pairings, read in every candidate's reading, not only as the veto), plus Dustin's own files in those archetypes, reported beside and not counted for adoption. Archetypes are added until every Energy type is covered; the proposal is in `rl/results/gauntlet_proposal_2026-09-26/`, for Dustin's OK on the additions.
  - This is the standard after the engine repairs land, when kp3's reference is regenerated anyway (Dustin, Sept 26).
  - **Scoreboard rows and coverage rows** (Dustin, Sept 26 midday, on the additions proposal).
    - **The scoreboard** is the cells real Limitless results can check. It grows from 28 to 45 cells with Dragonair Mega Rayquaza ex and Mega Altaria ex Greninja: each against the 8, plus each other.
      - The 28 stay frozen. The 17 new cells have their own seeds (21,108,000,000+).
      - k3 and kp3 are run on them before any candidate is.
    - **A coverage row** is a deck with too few real results to check, played so the bot has met it. The Metal deck, Mega Scizor ex / Revavroom, is one. It is reported, but never counted toward accuracy.
    - Past about 10–11 decks (about 50 matchups), Limitless can't check the simulator. Further gauntlet decks are for brew realism and coverage, and are labelled that way. A 30-deck gauntlet is not a 30-deck accuracy claim.
    - **List variation:** a deck's second list joins the gauntlet when it moves that deck's opponent average by 3 points or more. Single cells don't count: they are about ±4 at 500 games, and the average is about ±1.5.
  - **Where the gauntlet is heading** (Dustin, Sept 26: "The more of the limitless percentage we include the more it mimics real life ladder play and decks I would likely encounter. That would be how we tests new decks once the engine is good enough to approximate the play").
    - The gauntlet grows toward covering most of real Limitless play by share. Once the pilot passes, it is how brews are tested: a usage-weighted gauntlet, the ladder-weighted panel of A2.
    - Each proposal states the share of Limitless play it covers.
  - **Decks aren't fixed lists** (Dustin: "the limitless decks cover variations of the same archetypes ... often recommendations/alternative cards you can use for the same deck. Usually just different trainers"). A test list stands for its archetype's usual list, and the proposal reports how much each archetype's Trainers vary. A result that hangs on one exact flex card is read with that in mind.
- Variants and process: whole table paired by deal, never the five worst cells; τ̂ margin E = 3 with the 90% interval,
  doubling deals to 2,000 when undecided; every experiment names the decision it changes; two review tiers (engine
  rules, the scoreboard tool and any pilot adopted or played by Dustin get a second reader; diagnostics none); one
  owner per results file; every brew number carries its coverage flag.

**Owners:** the WSL session runs on the laptop; the laptop session coordinates, second-reads tier 1 and owns the
readings; the cloud session does engine items and the B7 probe; the Cowork agent does Limitless data; Fable reviews
on request; Dustin decides, plays the quiz and the ladder.
