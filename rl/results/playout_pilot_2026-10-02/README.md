# The play-out chooser, first prototype (the cloud, Oct 2)

Set by the Fable coordinator via Dustin, Oct 2. The design is `rl/results/planning_pilot_design_2026-10-02/DESIGN.md`,
sections 5 and 9 (the addendum's amendments win). Branch `claude/playout-pilot`, cut from main (551a348). Not merged.
- The official engine's behaviour and km3 are unchanged. The new code is only under `engine/src/players/`, plus its tests and
  an example.
- The laptop reviews it once, builds it beside the pinned engine, and runs the development comparison.
- No table game was played.

## In short

- **What it is.** `kx3` plays as km3 does, except that at each decision it plays every distinct legal move out to the end of the
  game 16 times, with km3 on both sides. It switches away from km3's move only when another move wins clearly more often.
- **km3 is untouched.** km3 built from this branch plays the official program's games exactly: 240 of 240, field for field. The
  strength harness built from this branch prints the pinned km3 self-check digest. The full suite passes.
- **It works through both harnesses.** It ran through the strength harness (`--pilot kx3...`) and Sonnet's position runner
  (`run_pilot.sh`), and gave the same result twice.
- **The smoke** (venusaur-exeggutor v weezing-arbok, 20 deals, both seats, 40 games):
  - The pilot scored 0.875. km3 on the same deals scored 0.850. The paired difference is +0.025 ± 0.111. That is no
    evidence either way, as 40 games can't be.
  - It changed 31 of 1,097 decisions from km3's move (2.8%).
- **It is slow.** About 7 seconds a decision and 3½ minutes a game on 4 cores, against well under a second for km3.
- **Its main weaknesses.**
  - km3 plays every later turn of every play-out, so a plan needing several coordinated moves can go unseen.
  - At 16 play-outs only big differences show.
  - Against an opponent whose list is not in the pilot's pool of 16 meta lists, its picture of that opponent is poor. That
    covers every position in the position runner. See "What to expect to go wrong".

## What it does

The pilot's code is `kx<N>`, for example `kx3`. It is a new player on top of km<N>.

At each decision with two or more distinct moves:
1. It asks km<N> for its move, with the same per-decision randomness km<N> would get in the game, so km<N>'s move is exactly
   km<N>'s.
2. It takes every distinct legal move as a candidate, km<N>'s first, up to a cap.
3. It plays each candidate out to the end of the game R times, with km<N> on both sides.
4. Each play-out starts from a world sampled from what the pilot may see, so its own deck order, the opponent's hand and deck,
   and every coin are fresh each time.
5. It scores each candidate by its play-outs: a win is 1, a tie ½, a loss 0.
6. It plays the best-scoring move only if that move's lead over km<N>'s move is beyond the noise. Otherwise it plays km<N>'s.

**Common random numbers.** Play-out j of every candidate starts from the same sampled world and the same game seed. So the
coin stream is the same, and so are km<N>'s decision seeds, for as long as the games run alike. The comparison is paired:
for each candidate the pilot takes the difference d_j = score(candidate, j) − score(km's move, j) and its mean and standard
error (sample sd / √R). It switches only if the best candidate's mean d > z × SE. Ties go to km's move.

**The cap** (default 12).
- km's move is always kept.
- The others are ranked by km's own score of the position right after the move, on the first sampled world. The rest are
  dropped, and each drop is named in the trace with that score and the reason.
- Most decisions have fewer distinct moves than the cap. In the smoke the mean was 5.3 and the cap was hit 3 times in 1,097
  decisions.

## What it can see, and what it can't

It sees only its `PlayerObservation`, exactly what km3 sees:
- its hand and board;
- the public board, discards, points and counts;
- its own deck as an unordered set.

It never reads the real game state. The opponent's hidden cards come from a list:
- **REALISTIC** (the default). For each play-out a list is drawn from a candidate pool: the 8 lists under
  `decks/screen/opponents` and the 8 under `decks/research`, embedded in `engine/src/players/playout_pool.rs` with each
  file's sha256.
  - The draw is uniform among the lists consistent with the opponent's cards seen so far, matched by name. A card counts as
    seen if it is in play, under an evolution, attached, discarded, their Stadium, or revealed.
  - The unseen cards come from the drawn list.
  - With no list consistent, it takes the closest one: the list missing the fewest of the seen cards. On a tie it takes the
    first list in the pool's order, which is t-altaria. The trace says "closest; no list consistent". This is a weakness; see
    below.
  - The opponent's real list is always consistent when it is in the pool. So against the strength harness's 8 panel lists,
    which are all in the pool, the fallback never happens.
  - The pool holds no brew and none of Dustin's lists.
- **LAB** (`_lab`, a laboratory condition, labelled as such in every output).
  - The opponent's exact 20-card list is used, but only when it is one of the pool's meta lists.
  - **The meta side is never handed a brew's exact list.** If the opponent's list is not a meta list, LAB falls back to
    REALISTIC and the label says so.
  - In the strength harness, with the pilot on Dustin's deck against a panel list, LAB gets the panel list.
  - In the position runner the opponent is a filler list, so LAB acts as REALISTIC there.

Never seen in either mode: the opponent's hand, the order of either deck, and coins not yet flipped.

**The no-leak test** checks this. It takes a game state, swaps a card between the opponent's hand and deck, and reverses both
decks. The pilot's observation is then the same.
- The test checks that the pilot's whole evaluation (every candidate's play-out score and difference) and its move are
  identical, in both knowledge modes, directly and through `Game::from_state(...).play_tick()`.
- A pilot that read any hidden card would see different worlds and get different play-out scores.

## Parameters

All are in the code: `kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<seconds>][_trace]`.

| part | meaning | default |
|---|---|---|
| `<depth>` | km<depth>: the move it proposes, and both sides in every play-out | (required; 3) |
| `_r<R>` | play-outs per candidate | 16 |
| `_c<cap>` | at most this many candidates (km's move always one of them) | 12 |
| `_z<z>` | the noise threshold, in standard errors of the paired difference | 2 |
| `_lab` / `_real` | knowledge mode | `_real` |
| `_t<seconds>` | time budget per decision: stop after the rounds finished in time (at least 2). Off by default, because it makes the result depend on the machine's speed | off |
| `_trace` | one `KX_TRACE` JSON line per decision on stderr | off |

- The first decision of each game prints `KX_PARAMS` on stderr: every parameter and the knowledge label. Every trace line
  carries the full code and the label too.
- **Deterministic given seeds.** All sampling and play-out seeds come from the decision's own randomness, the engine's
  per-decision search seed (game seed, seat, decision count).
  - Play-outs run in parallel on rayon's threads but are collected in order.
  - With no time budget, the same deals give the same games. This is tested, and was checked again across a container
    restart (below).

**The trace** (`_trace`, or the smoke example's `--trace-out`). Each decision line has:
- turn and seat;
- the rounds run, and any failed;
- the opponent lists drawn;
- the milliseconds the decision took;
- km's move, the move chosen, whether they differ, and the reason;
- every candidate with its play-out score, its paired difference from km's move and that difference's standard error;
- the dropped moves with their reasons.

So any of the pilot's decisions can be shown with its evidence (examples below).

**Not covered; these keep km's move, and the trace says so:**
- a setup choice made after the opponent's hidden setup, since their placed cards can't be sampled yet. When the pilot sets
  up first, which is half the deals, its setup choices get play-outs;
- a decision with a hidden stack frame of the opponent's.

In the smoke, 23 of 1,120 decisions kept km's move this way.

A play-out that panics (an engine bug in a sampled world) drops its whole round for every candidate, so the rest stay paired.
It is counted as `failed_rounds`. The smoke had none in 17,552 rounds.

One such bug was found and fixed while building. A sampled opening hand for an opponent still to set up could hold no Basic
Pokémon, which the engine's own deal never allows, and the opponent then had no legal move. The sampler now swaps a Basic into
such a hand, as the engine repairs a real one.

## Checks

### km3 and the official engine are unchanged

- **The engine's diff from main-8626a35:**
  - `engine/src/players/mod.rs` gains 12 lines: the two module lines, the `KX` code, its parse and its player. The file keeps
    its stored Windows line endings.
  - The new files are `playout_player.rs`, `playout_pool.rs`, the test file and the smoke example.
  - Nothing else in `engine/` changes. No other code reaches the new player.
- **km3 game for game.** `deckgym` built from this branch and the official program `rl/engine-2026-10-02/deckgym` both ran
  step 10's command here: km3 v km3, 240 games, research Altaria v Blaziken, seed 7,100, `--seed-stream`.
  - They agree on every field of all 240 per-game results: winner, points, turns, plies, actions per player and both search
    seeds. The games' digest is 9dde28db2de6c9bc for both.
  - Both equal the pinned record `engine_switch_rules_2026-10/5a18d31_10_cli_km3.txt` on every line but the wall time:
    149-91-0.
  - Files: `harness/simulate_km3_7100_*.txt`.
- **The pinned self-check.** The strength harness, built from this branch's engine, prints the pinned km3 digest:
  `strength selfcheck --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12`
  gives `digest=81b572198c04d5d1` (8-4, 127 turns), as `strength_harness_tests_2026-10-02/TESTS.md` records.
  - File: `harness/strength_selfcheck.txt`.
- **The full suite.** `cargo test --release --features test-utils` on the final code: 2,025 passed, 0 failed, 0 ignored. The play-out tests take about a minute of that.
  - File: `suite.log`.

### The tests (`engine/tests/playout_pilot_test.rs`)

Written and committed before the player (a3612b71): `tests_before.log`, where they fail to compile with no `kx` code and no
`playout_player`. After the player, all 7 pass:

| test | what it checks |
|---|---|
| `the_code_parses_with_defaults_and_parameters_and_leaves_the_other_codes_alone` | the code's grammar, defaults and errors; `km3` and `k3` parse as before |
| `an_immediate_win_is_taken` | Mega Absol ex's Darkness Claw knocks out the opponent's only Pokémon: chosen in both modes, every play-out a win |
| `within_the_noise_km3s_move_is_kept` | at an unreachable threshold km3's move, exactly km3's own choice, is kept; at 0 the best score, km3's on a tie |
| `a_capped_candidate_list_keeps_km3s_move_and_names_the_drops` | at cap 2, km3's move is kept and every other distinct move is a named drop |
| `the_choice_cannot_depend_on_the_opponents_hand_or_either_decks_order` | the no-leak test (above), both modes, directly and through `Game` |
| `the_same_seeds_give_the_same_moves` | 12 ticks from a position, twice, the same moves |
| `a_whole_game_plays_to_the_end` | a whole game from `Game::new`, setup included, with no panic |

### The smoke (`smoke/`)

`engine/examples/playout_smoke.rs`: the pilot (`kx3` at its defaults, REALISTIC) on `example_decks/venusaur-exeggutor.txt`
against km3 on `example_decks/weezing-arbok.txt`. 20 deals (seeds 24,200,000,000 to 24,200,000,019, registered in
START_HERE), each with the pilot in both seats. Each deal was also played km3 v km3, which is the pairing. The cloud ran it on
4 threads (rayon), one game at a time, from 21:30 to 23:56 UTC.
- **A restart.** The container restarted after 19 games. The example gained `--resume`, which skips the games already in the
  file, and the run went on from game 20. Since every game is seeded and the pilot is deterministic, a resumed run gives the
  games an unbroken one would.
  - Checked: two games of the first run, replayed afterwards by the resumed run's program, are equal in every field but the
    times. So is every traced decision: each candidate's score, difference and standard error, the lists drawn and the
    choice. (`smoke/replay_check.txt`: both games equal; 24 of 24 traced decisions equal.)
- **Results** (`smoke/summary.txt`, from `smoke/summarize.py`):

| | games | pilot | km3 on the same deals | paired difference (95%) |
|---|---|---|---|---|
| all | 40 | 0.875 | 0.850 | +0.025 ± 0.111 |
| pilot in seat 0 | 20 | 0.900 | 0.800 | +0.100 ± 0.196 |
| pilot in seat 1 | 20 | 0.850 | 0.900 | −0.050 ± 0.098 |

- **The changes.**
  - 5 deals' results differ between the arms: the pilot won 3 that km3 lost and lost 2 that km3 won.
  - 21 games had at least one changed decision. 16 of them ended as km3's game did.
  - The decisions: 1,120 asked; 1,097 with play-outs; 31 changed from km3's move (2.8%), all listed in `smoke/summary.txt`.
  - In the 294 kept decisions where some other move led km3's, the lead was a median 1.0 standard error. 9% of those leads
    were 1.5 or more.
- **Time** (4 threads):
  - ms per decision with play-outs: mean 7,417, median 6,217, p95 17,599, max 32,001;
  - seconds per pilot game: mean 204, median 176, max 381. That is 28 decisions and 14 turns a game. The pilot in seat 0
    averaged 219 s and in seat 1 189 s;
  - the km3 v km3 game of the same deal takes well under a second.
- **The opponent lists drawn.** Weezing-arbok is not in the pool, so after its first cards were seen no pool list was
  consistent. 85% of the play-out rounds used t-altaria as the "closest", 10% t-lucario and 4% t-vespiquen. That is a poor
  model of a Weezing-Arbok opponent (below).

**Three decisions from the trace** (`smoke/trace.jsonl`; the score is the share of 16 play-outs won):
- **Deal 10, pilot in seat 0, turn 17, changed.** The opponent played Sabrina, and the pilot chose its new Active.
  - km3 chose the Pokémon in slot 1: 0 of 16 play-outs won.
  - The pilot chose the one in slot 3: 14 of 16 won, a lead of +0.875 ± 0.085.
  - It took 0.7 s. That game the pilot won, and km3's game of the same deal was lost.
- **Deal 7, pilot in seat 0, turn 19, changed.** km3 played Professor's Research: 0.31.
  - Attaching the turn's Energy to the Active scored 0.94, a lead of +0.625 ± 0.125. X Speed scored the same. The pilot took
    the attach, the first of the two in the engine's order.
  - Ending the turn scored 0.00. Three other moves scored exactly km3's 0.31, with no spread: their play-outs went alike.
- **Deal 1, pilot in seat 0, turn 2, kept.** km3 played Poké Ball: 0.69.
  - The attach to the Active and Professor's Research each scored 0.88, a lead of +0.188 ± 0.101, which is 1.9 standard errors.
  - That is just under the threshold of 2, so km3's move was kept.

### Through the strength harness (`rl/strength/`)

- **Build** against this branch's engine: `rl/strength/build.sh <this checkout>/engine <out>`. The harness then knows the `kx`
  codes. A pilot is any code, for example `kx3`, `kx3_lab` or `kx3_r32_z2.5_lab`.
- **Runs here:**
  - km3's self-check prints the pinned digest (above).
  - `strength selfcheck --pilot kx3_r2_c3_lab --games 2` (kx on both sides, t-altaria v t-suicune) gave `digest=3a2eb43bd9053639`
    three times: twice before the container restart and once after, on a fresh build of the final code. Each took 2 to 2½
    minutes. Its stderr carries `KX_PARAMS` with the LAB label.
- **LAB applies there.** The 8 panel lists are all in the pool, so `_lab` gets the exact panel list, and `_real` always finds the
  real list among the consistent ones.
- **Threads.** The pilot spreads its play-outs over all cores itself, so `--threads 1` or `2` is enough. More harness threads
  only make the pilot's decisions wait on each other.
- **Pre-registration.** `strength_prereg.py` runs a 12-game self-check of every engine pilot, with that pilot on both sides.
  For `kx3` at its defaults that is about 12 games of twice the smoke's decisions. Expect roughly an hour and a half on 4
  threads, and proportionally less on more. That is an estimate; it was not run here.

### Through the position runner (`rl/results/pause_games_decisions_2026-10-02/harness/run_pilot.sh`)

- **Build** a kx-aware runner against this branch's engine, as that README says:
  `PGD_ENGINE=<this checkout>/engine PGD_TARGET=<dir> PGD_BIN=<dir>/pg_pos_kx harness/pgd_build.sh 8`. The print-only patch
  finds its anchors, because `expectiminimax_player.rs` is unchanged.
- **Run:** `run_pilot.sh kx3_trace 1,2,3,4,5,6,7,8,9,10,11,12 <dir>/pg_pos_kx`. With `_trace`, each decision's evidence goes to
  `err_<position>.txt`.
- **Run here:** one position (A-115323-t03, draft A, seeds 1 and 2) in 33 s, with 3 traced decisions. Every one kept km3's
  move: Misty's lead of +0.188 had a standard error of 0.136 (`harness/pg_pos_kx3_trace_*`).
- **No root-score dump.** The pilot silences `PG_DUMP` during its own decisions; otherwise every play-out's km search would
  print its root scores. So there is none for kx, and the runner prints "(no Turbo Shark tables: that pilot printed no root
  scores)". The choices table is produced as for any pilot.
- **Time:** 29 positions × 12 seeds at about 16 s each comes to roughly 1½ hours on 4 threads.
- **The opponent lists.** None of the positions' opponents (Snorlax, Teal Mask Ogerpon ex, Chingling, Shaymin, the fossils,
  Meowscarada ex, Chandelure, Flygon ex) is in the pool. So REALISTIC uses the "closest" fallback at every position (below).

## What to expect to go wrong

- **km3 plays the later turns of every play-out.** A move that only pays off if the next several decisions follow it up can be
  undervalued: charging a Benched attacker that km3 then never promotes, or a sacrifice km3 then doesn't make. Its play-outs
  score no better than km3's own move, and the pilot keeps km3's move.
  - **How the trace shows it:** the plan's first move has a score about equal to km's move (a difference within the noise),
    and km's move is kept, at a position where Dustin or a human sees the plan.
  - The test is DESIGN.md's amendment 4: run the pilot's trace on a position built for a coordinated plan (charge a Benched
    attacker, keep a sacrificial Active, promote at the right time).
  - If the plan's first move doesn't stand out there, km3's later play inside the play-outs is hiding it. A cure would be a
    play-out policy that follows plans, or two-move candidates.
  - The same cause works the other way. In the deal 7 example, Professor's Research lost to the Energy attach, probably
    because km3 didn't follow up with the attach after the draw. The pilot exploits km3's weaknesses as well as finding real
    improvements, and the trace alone can't tell the two apart.
- **An opponent whose list is not in the pool.**
  - **The problem.** Once such an opponent shows a card no pool list holds, no list is consistent. The "closest" then ties
    across many lists, and the tie goes to the first in the pool's order, t-altaria. The play-outs model that opponent holding
    t-altaria's remaining cards.
  - **The smoke.** 85% of the rounds against Weezing-Arbok were like that.
  - **The position runner.** It is like that at every position.
  - **The strength harness.** It never happens there.
  - **Repairs, not made here** (the smoke measured the code as it stands):
    - break the tie at random among the closest lists (small);
    - widen the pool. Which lists to add is the coordinator's or Dustin's call; the gauntlet lists and the scoreboard's
      Limitless lists are candidates;
    - build the unseen part around the seen cards.
- **Noise.** At R = 16 the standard error of a paired difference is often 0.08-0.15 (8-15 points of win rate). So only large
  gains switch the move, and small real gains are lost. Raising R costs time in proportion.
- **Many candidates, one winner.** The best of up to 11 rivals is chosen after seeing their scores, so its lead is biased
  upwards. At z = 2 some switches are noise.
  - If no move were really better, each rival would pass the bar about 3% of the time; with about 4 rivals a decision, that
    makes up to about one decision in eight. Many rivals' play-outs run identically, which lowers that.
  - The smoke's 2.8% of decisions switched is inside that range. So the smoke can't tell real gains from lucky switches; the
    development comparison can.
  - With equal moves a lucky switch costs nothing on average; with a truly worse move it costs. A higher z reduces it.
- **REALISTIC early in a game.** Few of the opponent's cards are seen, so the drawn lists are a mixture of all 16 meta lists.
  The play-outs then model an average opponent, not this one.
- **Speed.** About 7 s a decision and 3½ minutes a game on 4 threads. That is several hundred times km3's time: a km3 game of
  these decks takes well under a second. The work per decision is about 85 play-outs (5.3 candidates × 16) and spreads over
  cores, so a machine with more cores is faster in proportion.
- **The opening.** Setup choices made second keep km's move (above).

## Time for the laptop's runs

On 4 threads the smoke averaged 204 s per pilot game. The play-outs spread over the cores, so on T threads expect about
204 × 4 / T seconds; that is roughly 50 s at 16 threads. The reference arm's km3 game is negligible.
- **A development comparison** of D decks × 8 panel lists × N deals × 2 seats is 16 × D × N pilot games. For example, one deck
  at 25 deals is 400 pilot games: about 23 hours on 4 threads, or about 6 at 16.
- **The pre-registration's kx self-check:** about 1½ hours on 4 threads (estimated).
- **The position runner** (29 positions × 12 seeds): about 1½ hours on 4 threads.
- Raising R raises all of these in proportion. `_t<seconds>` caps a decision's time, but its results then depend on the
  machine's speed.

## Files

- `engine/src/players/playout_player.rs`: the player, its parameters, sampler, play-outs and trace.
- `engine/src/players/playout_pool.rs`: the 16 pool lists, embedded, each with its path and sha256 (generated from the deck
  files).
- `engine/src/players/mod.rs`: the `kx` code (12 lines).
- `engine/tests/playout_pilot_test.rs`: the 7 tests.
- `engine/examples/playout_smoke.rs`: the smoke (`--resume` included).
- Here:
  - `tests_before.log`, `tests_after.log` and `suite.log`;
  - `smoke/`: `games.jsonl`, `trace.jsonl`, `summarize.py`, `summary.txt`, `replay_check.txt`, `run_times.txt`, and the
    stdout of both parts of the run;
  - `harness/`: the km3 replay (`simulate_km3_7100_*`), the self-checks (`strength_selfcheck.txt`) and the position runner's
    traced run (`pg_pos_kx3_trace_*`).
