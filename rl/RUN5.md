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
   stop-loss; A5 B4b as a data refresh with bit-for-bit reproduction of the k3 table plus a card-effect pass, and an
   upstream code-merge trial in the cloud before C1.
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
   fixes under the card-agnostic rule, each with a paired A/B and the sentinels; B6 done (skill explains under 0.6 of
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
  beyond chance are reported, never decided on. Candidates are confirmed on the holdout before adoption is permanent.
- Variants and process: whole table paired by deal, never the five worst cells; τ̂ margin E = 3 with the 90% interval,
  doubling deals to 2,000 when undecided; every experiment names the decision it changes; two review tiers (engine
  rules, the scoreboard tool and any pilot adopted or played by Dustin get a second reader; diagnostics none); one
  owner per results file; every brew number carries its coverage flag.

**Owners:** the WSL session runs on the laptop; the laptop session coordinates, second-reads tier 1 and owns the
readings; the cloud session does engine items and the B7 probe; the Cowork agent does Limitless data; Fable reviews
on request; Dustin decides, plays the quiz and the ladder.
