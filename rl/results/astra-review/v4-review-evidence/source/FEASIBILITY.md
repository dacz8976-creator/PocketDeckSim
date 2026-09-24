# Can a self-play bot be trained on this engine? — feasibility, 2026-09-18

**Short answer: yes. The setup works, and it learns from game results alone.**
- **Run 1 (brew-03a mirror) PASSED:** ckpt_1500k won 55.5% of 1,000 fresh games against k3, after 2.2 h of training on the laptop.
- **But it didn't carry over:** 1–3% against Lucario, Weezing and Skarmory.
- **Run 2 PASSED on the laptop (Sept 19).** It's a specialist for Dustin's Mega Blaziken against Mega Lucario, with an encoding that shows what each move does and what the opponent can hit back for. After 1M games (3.4 h), it won **62.3%** of 1,000 games where k3 piloting the same deck won **47.6%** of the same games (p ≈ 1e-13). It never missed a sure win. Against unseen decks it's close to k3's level, but poison and burn defence is still weaker than k3's. See "Run 2" below.
- **Before that, the cloud pilot PASSED by run 2's own rules.** It matched k3 within 25,000–50,000 games and leveled off at 250,000 (2.4 h on 2 cloud cores). Its best checkpoint then won **57.2%** of 400 games against k3's **45.8%** on the same games (p ≈ 0.0002). It also carries over to decks it never trained on (see the transfer table).
- **Run 3 (one network for a five-deck pool) FAILED, and the reason is now known.** It stopped at its 1M floor and its continuation to 2M leveled off at −12.4 with no head-to-head gain: a plateau, not a slow climb. Blaziken sits at k3's level; Weezing, Altaria and Suicune are 20–36 points under. The shared network is worse at everything it does than run 2's specialist: it misses sure knockouts, doesn't bench, and often doesn't play out its turn at all. See "Run 3 result".
- **Run 4 is decided, not built:** one network per piloted deck, trained against the whole pool, plus two new per-move numbers for benching. See "Run 4 design"; it waits for Fable's sign-off on the open points.
Tags: **[measured]** = actually run; **[estimate]** = my reasoning, not run; **[check]** = needs Astra or you. Revised the same day after Fable's review.

## What was built (nothing under `deckgym-fork-s193/src/` was touched)
- `pdl_rl_env/` — a small Rust add-on that sits on top of the engine at tag `pdl-unified1-release` (commit 237b0f8; exact source in `engine-pdl-unified1-release.bundle`). The engine's own Python bindings can run whole games but can't hand over the legal moves or take a chosen move, so the add-on calls the same engine functions the engine's own game loop uses.
- `pdl_env.py` — `reset(deck_a, deck_b, seed)`, `observe(player)`, `legal_actions()`, `step(i)`, `reward(player)` (+1/−1/0). Moves with only one option are played automatically, as the engine does.
- `model.py` — the network: 419,000 parameters, plain numpy (no torch, no GPU).

## What the network sees
Everything is built from the engine's `PlayerObservation`, never the full game state. Cards are identified by set and number. The card list is the cards in the decks being played (13 for brew-03a) plus two extra slots: "hidden card" and "any other card". That's fine for one fixed matchup. Moving to other decks later needs either a shared card list across all decks or describing cards by what they are (HP, type, attack costs).
- **16 single numbers:** turn number, whether it's my turn, both players' points, both hand sizes, both deck sizes, both discard sizes, "opponent's starting Pokémon still face-down", "a multi-step choice is in progress", "a coin or target choice is pending", whose Stadium is in play, and how many opponent hand cards are known.
- **10 card lists** (a count per card): my hand; my remaining deck, unordered; my discard; their discard; their hand cards that have been revealed; my Pokémon in play; theirs; my Active; their Active; the Stadium.
- **8 board slots** (my Active + 3 Bench, then theirs), 26 numbers each: occupied or not; HP left and printed HP; attached energy by type and in total; number of Tools; Poisoned, Asleep, Paralyzed, Burned, Confused; ex or not; stage; retreat cost; played this turn; ability used this turn; has attacked since it was played.
- **Energy Zones:** current and next type for me and for them.
- **Each legal move** (143 numbers): what kind of move it is and its details (attack name, damage, which Bench slot, and so on), hashed into 128 slots, plus a count of the cards the move names. Two different details can share a slot. I haven't checked how often that happens in this matchup.
- **Not included:** move history (DouZero feeds past moves to an LSTM; here the discard piles are the only history); the opponent's deck list; the "already played a Supporter / already retreated this turn" flags, which the engine keeps private (they still show up indirectly, because those moves stop being offered); discarded energy.

## Step 1 — interface check: passed [measured]
- 1,000 seeded random-vs-random brew-03a mirror games: seat 0 **14 wins, 15 losses, 971 draws** at the turn-30 limit. Every result matched the engine's own record. The same seeds run again gave identical games, move for move. Illegal moves raise an error.
- The add-on driving the engine's own random bots matched the engine's own game loop on all 1,000 seeds.
- **Same k3 through the add-on** (Fable's question): I played 50 k3-vs-k3 games in the engine's own loop and recorded one seat's moves. Then I replayed them with that seat going through the add-on's `step` (the network's path, which skips the decision counter) and k3 on the other seat. The final game state matched exactly in **100 of 100 replays** (50 per seat). Control: with k2 in place of k3 on the other seat, only 24 of 100 matched, so the check can tell two bots apart. The reason, from the code: that counter is kept separately per seat, and k3's own counter still advances inside the engine's loop. (`step1b_k3_replay_check.py`)
- **Same legal moves and same observation** (Fable's follow-up — a matching final state alone doesn't prove the network was offered the right moves). At every one of the **2,606 replayed decisions**, the check compared three things between the add-on and the engine's own loop at that same decision: the full legal-move list the network is offered (every move, in order), the game state, and the `PlayerObservation`. **0 mismatches on all three.** Sensitivity: a decision's fingerprints matched the next decision's in only 1 of 2,506 pairs for the move list and never for state or observation, so the check does see changes.
- Hidden-card check: shuffling the opponent's hand and deck (and our deck order) left our observation unchanged at all 17,391 decisions tested. The control — shuffling our own visible hand — changed it 12,741 of 12,741 times, so the check can catch a leak.

## Step 2 — speed [measured]
| Machine | Workers | Games/sec | Hours per 1M games | Memory (all workers) |
|---|---:|---:|---:|---:|
| **Your laptop, WSL (8 cores / 16 threads), other work running** | 1 / 4 / **8** | 44.0 / 131.2 / **162.9** | 6.3 / 2.1 / **1.7** | 65 / 259 / 517 MB |
| Your laptop, 2 cores via the Cowork sandbox | 1 / 2 | 31.3 / 62.6 | 8.9 / 4.4 | 51 / 102 MB |
| Cloud machine, 2 cores, Xeon 2.1 GHz | 1 / 2 / 4 / 8 | 29.7 / 59.4 / 57.1 / 56.8 | 9.4 / 4.7 / 4.9 / 4.9 | 53 MB per worker |

- **What was playing in every row:** the network itself, untrained, picking every move for **both** seats (10% random moves, as in training), in the brew-03a mirror.
  - Each worker has its own copy of the network (419,000 parameters) and scores one position at a time. There is no batching across workers.
  - Every decision was also saved as a training row, then thrown away. No bots were involved and nothing was learned.
  - So these are training-game speeds with the network in the loop, not the bare engine's speed. k3 appears only in the separate 0.2–0.4 s/game figure below.
- **Laptop, 8 workers: 163 games/sec, 1.7 hours per million games.** This is the number to plan with.
  - It was measured with other work running on the laptop: Astra's k3-vs-k3 baseline was writing results in this folder at the same time.
  - You'll be using the laptop during a real run too, so it's a fair planning figure. A quiet machine would likely be somewhat faster [estimate].
  - 8 workers gave 3.7× one worker, not 8×, because all cores running flat out clock lower and the other job was competing for them.
  - 16 workers (using the extra threads) is untested.
- **Not measured yet** [estimate]: what a real run adds on top — the trainer taking a core, and shipping rows to it and fresh weights back.
  - The trainer needs about 3 core-hours over 5M games, roughly 0.35 of a core during a 9-hour run. Shipping rows is about 25 MB/s.
  - I'd expect 5–15% slower, not several-fold. The first 250,000 games of the real run will show the actual rate.
  - Game length also changes as the network learns (67 moves per game now), and speed moves with it.
- My earlier estimate for 8 workers was 155–220 games/sec. The measurement landed near the low end, as expected.
- Two workers exactly doubled one on both 2-core machines, so the worker processes don't slow each other down. The cloud's 4 and 8 are flat because it only has 2 cores.
- Training costs almost nothing next to playing: about 30,000 decisions/sec on one core. For a 5M-game run that's about 3 core-hours, spread across the whole run. A game against k3 takes 0.2–0.4 seconds.

## Step 3 — does it learn? Yes, for a clear-cut decision [measured]
- 778 real positions where one move wins on the spot and at least one doesn't. 632 to train on, 146 held out, split by game. The network only ever sees final results.
- It starts at chance (12.1%, because the untrained network scores every move the same) and reaches **91.8% after 192 practice games**, holding at 91–94% through 20,000. Attack-to-win positions: 98–100%. With the results scrambled it stays at chance (average 10%), so the results are what it learns from.
- Not learned: "end the turn and let poison take the KO." In those positions the best non-winning move still wins 97% of the time, so there was almost nothing to learn. Small edges will take many games.

## The draw problem, and the fix to build in before the run
- Random play draws 97% of games at the turn cap. The untrained network with ordinary starting weights draws much less: **28% of 36,719 self-play games** [measured, all three setups in the step 2 table]. That's because it happens to lean toward attacking — the same quirk that spoiled the first try of step 3. So DMC won't start from a 97%-draw desert, **as long as the run uses ordinary starting weights, not the "no preference" start step 3 used.** That start would bring back random play and 97% draws.
- That lean comes from how moves are encoded and helps here by luck. Nothing should depend on it beyond getting the first games to finish. The fix below is insurance, not a blocker, but it goes into the code before the run:
  - **Temporary shaping at the turn cap:** a game that hits the cap scores 0.25 per point ahead (at most ±0.5) instead of 0. A real win is still +1.
  - The risk: the bot learns to take a one-point lead and stall. So remove the shaping once cap draws are under 5% of self-play games at two checks in a row.
  - Evaluation games never use shaping: a draw is a non-win.
- **Draw gate at 250,000 games** (~26 min on the laptop): cap draws in the latest 20,000 self-play games must be under 10% and lower than at the start. If not, stop and rethink before spending the rest of the budget. It catches both failures: nothing finishing, and a bot stalling to the cap with a lead. Measured on self-play games only. The draw rate in the k3 evaluations is reported separately.
  - **Why 10%:** self-play starts at 28% draws (measured), and two competent bots draw 2.8% (k3 vs k3). Under 10% at 250,000 games means it's covered most of the distance to that floor, without demanding it be there already. The "lower than at the start" part checks the trend.

## Kill criterion for the brew-03a run (final numbers set with Fable)
- **Budget: 5,000,000 self-play games.** For reference only: about 8.5 hours with 8 workers on the laptop at the measured 163 games/sec, closer to 9 counting training and checkpoint games. The 250,000-game draw gate comes at about 26 minutes.
- **Every 500,000 games, three opponents, win = win (draws count as non-wins):**
  - 400 games vs k3 (200 per seat, the same seeds every time; 1–3 min)
  - 200 vs random moves
  - 400 vs the previous checkpoint. Scoring under 50% against its own earlier self at two checks in a row is a flag, not a stop: it means the latest checkpoint isn't the best one.
  - Report the win, loss and draw rate for each seat separately.
- **Stop early:**
  - at 250,000 games, if the draw gate fails
  - at 1,000,000, if it wins under 90% vs random or under 5% vs k3
  - at 2,500,000, if it wins under 25% vs k3
- **Hand check at 1M and 2M, set by Fable while the run was live:** the coded 5%-vs-k3 floor at 1M is below the untrained network's own 6%, so it can't catch a run that isn't improving. Whoever reads STATUS at 1,000,000 games applies this by hand: **12%+ against k3 → carry on; under 8% → stop; 8–12% → flag, and it must reach 15% by 2,000,000.** (The live run's settings can't be changed without a restart, so this isn't in the code.)
- **Reading the draw check:** 'started at' is the run's own first 20,000 self-play games, played while it's already learning — not the 28% from the speed test. If that start is already under 10%, the check effectively becomes 'draws must not rise'. That's intended, not a problem.
- **Pass:** always tested on the **best checkpoint by k3 win rate, never automatically the latest**. It needs 55%+ vs k3 over its 400 checkpoint games. Then a confirmation on **1,000 fresh seeds, 500 from each seat**: **55%+ overall, and neither seat below 45%** → Phase 2. A seat between 45% and 50% is flagged in the report but doesn't fail the pass. The confirmation takes 3–7 min.
- **Why a flat 45% floor (set by Fable after Astra's baseline):** in 1,000 k3-vs-k3 mirror games, k3 won 48.8% from seat 0 and 51.4% from seat 1, with 2.8% draws. That gap is within noise (±4.4 points per seat), so there's no real seat advantage to adjust for. 45% is k3's own per-seat rate minus that noise margin. The floor means "not meaningfully worse than k3 from either seat."
  - The 29–19 split in my 50-game sample was chance, as its wide interval allowed.
  - Astra's 1,000 games are kept in `results/astra-review/mirror_games.jsonl`. Each is replayable from its seed, since both sides are k3. They're the baseline games to read first when transcripts exist.
- **How reliable the checkpoint pick is:** each checkpoint is scored on 400 k3 games, about ±5 points.
  - Two checkpoints less than ~7 points apart can't be reliably told apart. If the runner-up is that close to the best, run the confirmation on both.
  - The fresh seeds matter too: picking the best of up to 10 checkpoints flatters its 400-game score, and the confirmation removes that luck.
- **Otherwise:** stop at 5M and write down the curve. No extension without a new reason. For scale: Jev beat k3 once in 78 games, and random moves won 0 of 100.

## What's done, what's open, what's next
- **Astra's review is done** (`results/astra-review/ASTRA_REVIEW.md`):
  - It found no legal-move or observation problem in the add-on.
  - It explained from the engine code why the skipped counter can't touch the move list or first-turn rules.
  - It independently reran the replay check (100/100, 2,606 decisions, 0 mismatches) and ran the 1,000-game k3 baseline.
  - The WSL speed run is done (163 games/sec with the network playing).
- **Energy Zone, settled by Dustin from a real match:** both players see the current energy and the next energy for both sides. The engine exposes the same thing, so the observation is right and nothing changes.
- **Hidden cards in the move list, closed** [measured]: at 19,805 decisions (200 random-vs-random games, 100 against k3), I rebuilt the position with the opponent's hand and deck reshuffled and our own deck reordered, then asked the engine for the legal moves again. The list never changed (0 of 19,805), so the moves on offer never depend on the opponent's hidden cards or on deck order.
  - Control: reshuffling our own visible hand changed the list 13,113 times, so the test notices a change when there is one.
  - Checking card names alone can't settle this in a mirror match, because both decks hold the same cards. The reshuffle test is the stronger version. (`step1c_move_list_leak_check.py`)
- **Now (Sept 20):** runs 1 and 2 passed; run 3 failed and its continuation confirmed a plateau. Run 4 (one network per deck) is designed and waiting for sign-off; nothing is running.

## Training program design (approved by Fable; built as `train.py`)
**What it learns from.** Each decision's target is the final result of that game, from the view of the player who made it: +1 win, −1 loss. It's pure Monte-Carlo (DMC), with no bootstrapping from the network's own estimates. Games are short (~67 decisions), so that's the standard choice for card games, and a wrong target can only come from the game itself, not from the network feeding back on its own guesses.
- A game that hits the turn-30 cap gets 0.25 per point ahead, capped at ±0.5, until the shaping switches off (then 0).
- **The draw gate still counts every turn-limit game as a draw**, whatever the tiebreak gave it. The tiebreak only changes the training target; it never changes how a game is counted.
- No discounting: every decision in a game gets the same target.
- It uses the same 419,000-parameter network with normal starting weights, trained on squared error with Adam: learning rate 1e-4, batches of 512 [a starting choice, not tested].
- **How it picks moves in training games:** at every decision, with probability 10% it plays a uniformly random legal move. Otherwise it plays its highest-scored move, with exact ties broken at random. The 10% drops to 5% after 1M games.
  - That's about 6–7 random moves per game, spread through the game, so games keep branching even between two copies of the same network. Coin flips and draws add more variety on top.
  - Past checkpoints used as training opponents follow the same rule.
  - **Evaluation games are greedy: yes.** No random moves, no tiebreak shaping, draws count as non-wins.

**Who it plays while training.**
- **80% of games: the latest network against itself.** Both sides' decisions become training rows.
- **20%: the latest network against a randomly drawn earlier checkpoint.** Only the latest network's decisions are used. This guards against forgetting, and against "A beats B beats C beats A" cycles.
- **k3 is never a training opponent.** A k3 game costs about 13× a self-play game (0.31 s vs 0.023 s on one laptop core), so even 10% k3 games would roughly double the run time. And k3 is the exam: training against it risks learning k3's quirks, which would make "55% against k3" mean "exploits k3" rather than "plays well".
- The cost of that choice: self-play alone could settle into a style k3 happens to beat, and the checkpoint scores would show that. **This is the biggest judgment call on this page.**

**Moving data around.**
- 8 worker processes play. One trainer process learns. The main process runs checkpoints and evaluations.
- Each worker sends a finished game's decisions to the trainer in one message (~150 KB).
- The trainer keeps the **200,000 most recent decisions** (~18 seconds of play, ~0.45 GB) and drops the oldest first.
- **163 games/sec is an upper bound for a real run.** It was measured without the trainer running, and the trainer will take CPU from the workers.
- **The trainer is light, though** [measured inputs, inferred result]:
  - 163 games/sec produces about 10,900 moves/sec. The trainer handles about 30,000 moves/sec on one free core.
  - Training on every move once needs only about 37% of one core. A full core would train on each move about 2.7 times.
- **Target: each recorded move trained on 2 times on average before it leaves the buffer.** The trainer is capped there so it doesn't over-fit to the newest games.
  - `STATUS.txt` reports the actual number at every checkpoint.
  - This is an average from random sampling, not a guarantee that each individual move is used. If it falls below 1, the trainer is falling behind; try 7 workers instead of 8. Restarting discards old replay credit along with the old buffer.
- **Fresh weights are published every 50 training steps** (about every 1–2 seconds). Each worker picks them up at the start of its next game, so it's never more than a few seconds behind. Live weights are copied through shared memory under a lock, so no worker reads a partial update. Saved checkpoint weights use complete files followed by an atomic rename.

**Checkpoints and evaluation.**
- A checkpoint every **500,000 self-play games** (~51 min at 163/sec): 10 in the 5M budget.
  - Plus **checkpoint 0**, the starting network, evaluated before training begins, so there's a baseline to compare against.
  - Plus **an early checkpoint at 100,000 games** (~10 min). A run that isn't learning shows up as no gain over checkpoint 0.
  - The 100,000 checkpoint is reported, not an automatic stop. The first automatic stop is still the draw gate at 250,000.
- At each checkpoint, self-play pauses and all 8 workers evaluate. That's about 1–2 minutes each time.
- **Three opponents, 1,000 games in all**, with the network playing greedily (no random moves, no shaping, draw = non-win) and results recorded per seat:
  - **400 vs k3** (200 per seat, the same seed list at every checkpoint)
  - 200 vs random moves
  - 400 vs the previous checkpoint
- Sample size: 400 k3 games is ±4.9 points. The best checkpoint is chosen by its k3 score, and if the runner-up is within 7 points, both get the confirmation.
- The confirmation (1,000 fresh seeds, 500 per seat) runs automatically once a checkpoint reaches 55% against k3.
- Seeds come from three ranges that never overlap: training, the fixed evaluation list, and confirmation.

**Recording, for transcripts later.**
- Every evaluation game is one line in `eval_games.jsonl`: checkpoint name, opponent (k3 / random plus its seed / checkpoint name), game seed, the network's seat, every move choice (as positions in the engine's sorted legal-move list, for both sides when both are networks), result, points and turns.
- Checkpoints are saved as weight files. Any evaluation game can then be rebuilt exactly, and the network's score for every legal move recomputed from its checkpoint. k3's side regenerates on its own, as the replay check proved.
- One self-play game in 1,000 is also recorded (seed and moves), so draws and stalling can be read. Those can't show the network's scores, because training weights between checkpoints aren't kept.

**Running it.**
- All the stop rules in the kill criterion are automatic: the 250,000-game draw gate, the 1M and 2.5M floors, the 5M budget, and a pass triggering the confirmation.
- A plain-language `STATUS.txt` is rewritten at every checkpoint: games played, hours, self-play draw rate, and win/loss/draw per opponent and seat. On any stop it says why in one line.
- If interrupted, the run resumes from the last complete saved state and its matching weights. Work since that save is lost. The buffer isn't saved; it refills in seconds. Changing worker count is allowed; changes to learning settings, source, deck, or engine are refused on resume.

## The training program as built
- **Files:** `train.py` (the whole program) and `run_training.sh` (the one line to start or resume it in WSL). It uses the same add-on, network and observation as steps 1–3, and nothing under the engine's `src/` changed.
- **Everything in the design is in it:**
  - 8 workers, 80/20 self-play vs past checkpoints, 10%→5% random moves
  - 200,000-move buffer, capped at 2 uses per move, weights shared every 50 training steps
  - checkpoint 0 and the 100,000-game checkpoint, then every 500,000
  - three-opponent greedy evaluation with results per seat
  - the draw gate at 250,000 (turn-limit games always counted as draws), the tiebreak switch, the 1M and 2.5M floors, and the 5M budget
  - automatic confirmation on the best checkpoint (and a runner-up within 7 points)
  - `eval_games.jsonl`, one self-play game in 1,000 recorded, `STATUS.txt`, and resume after an interruption
- **Smoke tests** (a scaled-down copy on the 2-core cloud machine; this tests the program, not the bot) [measured]:
  - **Real thresholds, scaled down, run twice.**
    - First run: the draw gate stopped it (11% draws; the gate needs under 10%).
    - Second run: it passed the gate at 5%, then was stopped by the last floor (15% against k3, needed 25%).
    - So both stop paths work. `results/smoke_status_A.txt` is the STATUS file that second run wrote.
    - The difference between the two runs is expected. Worker timing makes training runs not repeat exactly, even though every recorded game can be replayed exactly.
    - Its checkpoint scores (0% → 15% against k3, 30% → 100% against random) come from 10–20-game evaluations after 3 minutes of training. They show the program trains; they say nothing about how good the bot gets.
  - **Thresholds relaxed so it runs to the end:** it was deliberately crashed mid-run, restarted with the same command, resumed from the last save, and finished at its budget. Every checkpoint was evaluated and the resume was flagged in STATUS (`results/smoke_status_B.txt`). No stray processes were left behind.
  - **Pass threshold set to zero:** the confirmation ran and the run stopped as PASSED. Running the same command again refused to restart a finished run.
  - **Two bugs found and fixed in testing:** after a crash, workers could hang forever waiting to hand over games nobody would read; and STATUS showed the trainer's uses per move as 0 right after a checkpoint.
- **Not tested:** a full-size run. The first real numbers — actual speed with the trainer running, uses per move, whether the 100,000-game checkpoint beats checkpoint 0 — come from the laptop's first `STATUS.txt`.
- **Starting it** (after Astra's review): laptop plugged in, Windows set to never sleep while plugged in, no other heavy jobs. In Ubuntu run `bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training.sh"` and leave the window open.
  - Progress is in `runs/brew03a-01/STATUS.txt`.
  - If it's interrupted, run the same line again.
  - If STATUS says moves are being trained on less than once each, restart with `--workers 7` added to the end of that line.

## Transcripts (built while run 1 trained)
- **Files:** `run_transcripts.sh` (in WSL; add `--ckpt ckpt_500k` for a checkpoint other than the latest) and `transcripts.py`.
- **What it writes:** for one checkpoint, `runs/brew03a-01/transcripts/<checkpoint>/INDEX.txt` plus one text file per game:
  - games against k3: 5 losses, 5 wins from the first seat, the 5 longest, and up to 5 draws
  - 3 k3-vs-k3 games from Astra's baseline, to read first
- **At each bot decision, a transcript shows:**
  - the board exactly as the bot saw it
  - every legal move with the bot's predicted result (-1 sure loss, +1 sure win), and the move it picked
  - a marked referee line with the cards it couldn't see
- **Separate setup, so the training run is untouched:**
  - It uses its own add-on build (`wheels/transcripts/`, version 0.2.0). That build only adds read-only recording and board description.
  - It runs in its own Python setup.
  - The training run's 0.1.0 build and setup are unchanged; the run refuses to resume if its inputs change.
  - Encoding check: 60 test games gave byte-identical observations, move features and results in both builds.
- **Every game is checked on replay:** the recorded move must be the checkpoint's top-scored move, and the final result must match the saved one.
- **First real run:** checkpoint 1,000,000, 20 bot games plus 3 baselines, 0 problems, 21 seconds.
- **Finding:** draws against k3 are almost all both players reaching 3 points on the same action, not turn-limit stalls.

  | Checkpoint | Draws vs k3 | Turn limit | Both reached 3 points |
  |---|---:|---:|---:|
  | 100,000 | 16 | 0 | 16 |
  | 1,000,000 | 10 | 1 | 9 |

  **Open rules question for Dustin:** is that a draw in the real game? The engine scores it as a tie.

## Knockout audit of the passing checkpoint (ckpt_1500k), run the night of Sept 18
**What was measured** (`audit_knockouts.py`, results in `results/ko_audit/`):
- **Games:** 1,400 saved bot-vs-k3 games, replayed exactly, plus 400 k3-vs-k3 mirror games as a baseline. 0 replay problems.
- **How:** at every real decision, the engine applied each legal option to copies of the true game under 4 chance seeds. This is analysis only; the bot never sees it.

| Per player-turn | Bot | k3 (same games) | k3 mirror |
|---|---:|---:|---:|
| Turns with a sure KO on offer / missed | 1,992 / 44 (2%) | 1,584 / 32 (2%) | 1,132 / 25 (2%) |
| Turns with a sure game-winning move on offer / not won that turn | 795 / 19 (2%) | 525 / 0 | 386 / 0 |
| Attacks that hand the opponent sure points (e.g. into Rocky Helmet), per 1,000 turns | 13.8 | 3.2 | 4.6 |
| …of which hand the opponent the game outright | 21 | 0 | 0 |
| Turn ended with no attack and own Pokémon then knocked out at checkup, per 1,000 turns | 9.0 | 0.4 | 0 |

**What it says** (the last row is the least clean: it partly reflects the bot ending turns without attacking more often):
- **Offensive knockout math is not the weakness.** The bot takes sure KOs exactly as reliably as k3.
- **Wins: it doesn't always take a sure win right away.**
  - In 16 of the 19 missed-win turns it played Sabrina first, which swapped out the target it could have knocked out for the win.
  - It scored Sabrina and the winning attack almost equally: every gap was under 0.09.
  - Cause (inference): the training target has no preference for winning sooner. A win now and a win three turns later both count +1.
  - Candidate fixes for run 2: a small discount for later wins, or a "take the win now" rule.
- **Defense is the weakness: it hands points away 4–20× more often than k3.**
  - It attacks into Rocky Helmet with a low-HP attacker. 21 of these self-knockouts handed k3 the game.
  - It lets poisoned Pokémon die at the checkup.
  - Two encoding gaps fit this. Tools are counted but not identified, so it can't tell a Rocky Helmet from a Giant Cape. And it sees "poisoned" but not how much damage the poison does.
- **Answer to Fable's question:** on offense it has the information and uses it. On defense it's missing information. The wins issue is the training signal.
- **Example games:** `runs/brew03a-01/transcripts/audit_examples/`
  - `20000249` (seat 1, turn 11): fatal Rocky Helmet trade
  - `20000365` (seat 1, turn 12): Sabrina instead of the winning attack
  - `20000192` (seat 0, turn 9): poisoned Nihilego left to die when attaching to it and retreating was available

**Rules check: both players reaching 3 points on the same action**
- GameWith's rules guide says that's a draw, and the engine does the same.
- A Dexerto report says that if only one player still has a Pokémon on the bench, that player wins. The engine doesn't do that.
- It matters in 2 of the 97 simultaneous-3-point draws against k3, so it's negligible here.
- **Dustin confirmed (Sept 18):** both players reaching 3 points at once is a draw in the real game, as the engine has it.

## Run 2 — a specialist on Dustin's Mega Blaziken: PASSED (laptop run, Sept 19)
**Result in one line:** after 1M games (3.4 h on the laptop), the bot piloting Blaziken won **62.3%** of 1,000 games against Lucario, where k3 piloting the same deck won **47.6%** of the same games. That's a pass under the signed-off rule. Full results in "Run 2 results" at the end of this section.

**Status before launch, Sept 18 night.**
- **Fable signed off** the design, the pass rule and the stop rules.
- **Astra's code review** (`results/astra-review/V2_REVIEW.md`) found four problems and one small one. All are fixed; see "Fixes after Astra's review" at the end of this section.
- The corrected encoding is named **v2.1** (add-on **0.5.0**). The pilot below ran the uncorrected **v2** (0.4.0), so its result is evidence for the design, not for the fixed code (Fable). The laptop run is the test of the fixed build.
- If its first two checkpoints come in below the pilot's at the same point, something regressed.
**Why a second run.**
- Run 1 passed in the brew-03a mirror, but it doesn't carry over: 1–3% against Lucario, Weezing and Skarmory.
- The knockout audit found two problems:
  - **It doesn't always take a sure win right away.** The training target has no preference for winning sooner.
  - **It gives points away on defence:** Rocky Helmet trades, and Pokémon left to die from poison. Tools are counted but not named, and damage only appears as a hashed label.
- On top of that, nothing in the v1 encoding says what the opponent can hit back for next turn. That's the kind of number that should carry over to decks the bot hasn't seen (Fable).

**Deck and matchup, from the k3 screen** (`results/k3_screen.txt`: every deck in dustin/ and brews/ against the 8 Limitless study decks, 100 games each, k3 piloting both sides; ±10 points, a screen, not a ranking).
- Dustin's three candidates against Lucario, the most common Limitless deck (8.6%): **Mega Blaziken 52%**, Mega Manectric/Heliolisk 37%, Indeedee/Stoutland 30%.
- **Chosen: Mega Blaziken (06) vs Mega Lucario ex.** It's the most even of the three against the deck Dustin meets most.
  - On 400 more games (the cloud pilot's baseline), k3 won 45.8%.
  - Runner-up: Manectric, 37% against Lucario, which leaves more room for the bot to beat k3.
- **Transfer test matchups:** Blaziken vs **Altaria** (46% under k3, 5.1% on Limitless) and vs **Suicune** (47%, 4.8%). These are the next most common decks where k3 is roughly even.
  - Sceptile (65%) and Vespiquen (80%) are more common, but too lopsided to measure a difference.

**Encoding v2 / v2.1** [built and checked in the cloud; `pdl_rl_env/src/v2.rs`; v2 = add-on 0.4.0 (the pilot), v2.1 = 0.5.0 (the laptop run)]
- The bot now sees, **for every move on offer**, what that move does. It's worked out exactly the way k3 looks ahead:
  - It starts from the engine's `search_state`, the player's own view. The opponent's hand and deck are unknown cards; our own deck is one sampled order of the cards we know are in it.
  - It runs the engine's exact forecasts.
  - Anything the engine flags as depending on hidden cards (`hidden_continuation_reason`) is refused: all zeros, with a "not worked out" flag.
- **Per move (16 numbers):**
  - points I'd gain; points they'd gain; chance I win now; chance they win now
  - damage to their side; damage to my side (Rocky Helmet, recoil, poison at the checkup when ending the turn)
  - whether the turn passes
  - after the move:
    - the best my Active can still hit their Active for this turn, and the chance it knocks it out
    - the best their Active can hit mine for next turn, with their next energy attached; the chance it knocks mine out; the chance that wins them the game; and how much of that could be worked out
  - asleep/paralysed or poisoned/burned left on their Active
- **Per position:**
  - the same "my best hit now" and "their best hit next turn if I end my turn now"
  - the knockout points my Active and theirs are worth (1/2/3)
  - which tools are attached on each side, named by card (Rocky Helmet is no longer just "one tool")
- **Everything from v1 is kept unchanged.** Same card-count blocks, board slots and hashed move tokens.
- **Fable's four items, and where each one is:**
  1. **Damage and HP as numbers.** HP was already a number per board slot; each move's damage dealt and taken is now a number too.
  2. **What they can hit me for next turn:** the threat numbers. They're worked out from the opponent's face-up Active: its attacks, costs and damage, plus weakness and effects through the engine. So they work even when the card is an unfamiliar "other card" to the network.
  3. **Which Tool is attached:** the tool blocks, named by card. Rocky Helmet's effect also shows up directly on each attack row, as damage to my side and points they'd gain.
  4. **Poison damage due at checkup:** on the End turn row, as damage to my side (and points they'd gain if it knocks the Pokémon out). It's not a separate per-slot number, because the engine keeps the poison amount private. The checkup result is the part a player acts on.
- **Checks** [measured, `v2_checks.py` → `results/v2_checks.txt`, 80 s]:
  - **v1 is untouched.** The 60-game encoding hash equals 0.1.0's (18e818dfef01e2ca1caa), so run 1 and its tools can use the new add-on.
  - **Hidden-card probe extended to everything v2 adds**, over 40 games and 23 decks. Each position was rebuilt with the opponent's hand and deck reshuffled and our deck reordered, then the observation and every move's v2 numbers were compared.
    - Identical in 4,666 of 4,666.
    - Control, reshuffling our own visible hand: noticed 1,628 of 1,628.
  - **Agreement with the real game.** For each move v2 worked out (6,698 of 7,045 offered over 60 games), its points and win numbers were compared with what the engine gives applying that move to the true game under 4 chance seeds. Agreed in 6,698 of 6,698. The 347 refused are mostly draw and search cards.
  - **Threat vs what k3 actually did next turn** (598 turn ends):

    | v2 predicted | Turn ends | k3 scored next turn | k3 won next turn |
    |---|---:|---:|---:|
    | They win for sure | 96 | 100% | 100% |
    | Sure knockout | 80 | 98.8% | — |
    | No knockout | 406 | 23.6% | 11.3% |

    The last row comes from hidden-hand plays (evolving, supporters, switching in a benched attacker), which the player's view can't price. So **"no threat" is not "safe"**; the network gets the numbers, not a promise.
  - No engine errors in play. 1–4% of forecasts are refused as depending on hidden cards.
- **Known gaps:**
  - The threat only considers their current Active attacking. It doesn't cover a benched attacker retreating in, or evolutions and supporters from their hand.
  - The threat measures damage, knockouts and wins only. Effects their attack leaves behind aren't in it, such as Bonsly's "−30 to your next attack" or a status condition. The same goes for our own next turn: its attack isn't projected. (Fable: this belongs here whatever the Bonsly retreat turns out to be.)
  - When a knockout forces a promotion, the defender is assumed to pick the safest Pokémon and the attacker the most dangerous.
  - When the opponent chooses in the middle of our turn (which Pokémon Sabrina brings up), v2.1 assumes they pick the one that leaves our attack weakest.
- **Cost** (measured on 2 idle cloud cores): v2.1 takes 1.2–1.4 ms per decision against 0.9–1.0 ms for v2, because the "after" numbers are now always recomputed. I'd expect about 70–90 games/sec on the laptop; the first STATUS update will show the real number.
- **Coin flips** are priced as chances, never as the worst case. Each number is averaged over the engine's own forecast branches (up to the 8 most likely per move; up to 4 for the end-of-turn step inside the look-ahead).

**Training changes (`train_v2.py`, built from Astra's reviewed `train.py`; everything not listed is unchanged)**
- **Two decks.** In self-play the network plays both sides, with Blaziken in a random seat. The card list is both decks' cards together. Evaluation always has the network piloting Blaziken.
- **A sooner result counts more.** Each move's target is the result × 0.97 per game turn left until the end, so a win this turn beats a win next turn by about 6%.
  - **Fable's caution:** the same discount makes a later loss hurt less, so a losing bot gets a reason to stall. The draw gate stays exactly as it is, as the tripwire for that.
  - **Pilot evidence, no stalling** [measured]:
    - Turn-limit draws in self-play fell from 11% to 0.1%. Of 1,800 evaluation games against k3, one hit the turn limit, and that was the untrained network.
    - Bot games run slightly longer than k3's on the same seeds: losses +0.5 turns, wins +0.9. Since wins are longer too, that's not loss-specific delaying.
  - **Fable: the discount stays as piloted.** The pilot showed no stalling. "Discount wins only" (a loss is −1 whenever it happens) is the ready fallback if a slower deck ever shows the pattern.
  - A hand-written "take the win if it's there" rule isn't needed: the bot now misses 1 sure win in 299.
- **Same settings as run 1:** network size, learning rate, batch, buffer, "2 uses per move" target, random-move rate, 20% games vs earlier checkpoints, draw gate at 250k with tiebreak shaping.

**Evaluation and stop rules (Fable's)**
- **The bar, measured first:** k3 piloting Blaziken vs k3 piloting Lucario, 1,000 games on the confirmation seeds.
- **Checkpoints** at 100k and 250k, then every 250k, up to a budget of 4M games or `HOURS` of training and evaluation (Dustin sets it; the default is 6; it can change on resume). Each one plays:
  - 500 games vs k3 (the network pilots Blaziken)
  - 200 vs random
  - 400 vs the previous checkpoint. The two networks swap decks every two games, so 50% = no change.
- **Floor at 1M games:** at least 90% vs random, and at least half of k3's own win rate vs k3. Otherwise the run stops.
- **Leveled off:** 3 checkpoints in a row within 5 points of each other vs k3, each at or under 55% vs its previous checkpoint. Training stops there, or at the budget.
- **Confirmation:** the best checkpoint (by the k3 column), plus the runner-up if it's within 7 points, then plays 1,000 fresh games, on the same seeds and seats as the bar, so the two are paired.
  - A checkpoint crossing the bar mid-run is only a milestone; the run keeps going.
  - **PASS** = at least k3's rate + 5 points, and neither seat more than 5 points below k3's result in that seat.
  - Otherwise: FINISHED, not a pass. [Signed off by Fable. With 1,000 games per side, ±3 points on each rate.]
- **Two report lines on the final checkpoint** (not gates; `run_training_v2.sh` runs both when training ends):
  - the knockout audit (`audit_knockouts_v2.py`): give-aways and missed sure wins next to k3's, in the same games
  - **the defensive test** (Fable), `audit_knockouts_v2.py --vs weezing,blaziken`: fresh games against two decks it didn't train on, with k3 piloting Blaziken on the same seeds for comparison
    - Weezing poisons and burns (Boiler Smog, Deceptive Needle).
    - The Limitless Blaziken list is the only study deck that runs Rocky Helmet.
  - the transfer test (`matchup_test_v2.py`): the same floor/ceiling/bot rows as run 1, on Lucario (trained on), Altaria and Suicune, 400 paired games per row
- **Time:** at about 80 games/sec, 4M games would be about 14 h. The pilot leveled off at 250k, so the laptop run will probably take an hour or two.

**Tested so far (cloud; 2 cores, so small samples; the uncorrected v2 build, add-on 0.4.0)**
- **Smoke test** (a scaled-down 12k-game run): every path worked.
  - bar measured → draw gate passed → shaping switched off → checkpoints → leveled off → confirmation → FINISHED
- **Pilot** (`runs/pilot_v2_blaziken_lucario` in the cloud):
  - the real program, 2 workers, checkpoints at 25k/50k/100k then every 50k, 200 k3 games per checkpoint (±7 points)
  - The bar, on 400 games: k3 piloting Blaziken wins **45.8%** against k3 piloting Lucario (44.0% / 47.5% by seat).

  | Checkpoint | vs k3 (seat 0 / seat 1) | vs random | vs previous |
  |---|---:|---:|---:|
  | ckpt_0 | 0% (0% / 0%) | 0% | — |
  | ckpt_25k | 44% (47% / 40%) | 96% | 98% |
  | ckpt_50k | 50% (55% / 44%) | 96% | 55% |
  | ckpt_100k | 45% (41% / 49%) | 95% | 54% |
  | ckpt_150k | 56% (60% / 52%) | 98% | 55% |
  | ckpt_200k | 52% (54% / 51%) | 97% | 55% |
  | ckpt_250k | 57% (59% / 56%) | 99% | 53% |

  - **The bot reached k3's own level after 25,000–50,000 games (13–25 minutes of training on 2 cloud cores).** For comparison, run 1 was at 39% after 100,000 games, in a mirror where k3's bar was about 50%.
  - **At 150,000 games (84 minutes) it went past k3**, and it kept that level. I checked ckpt_150k on the bar's own 400 games: 56.2% vs k3's 45.8%, p ≈ 0.001.
  - **The pilot ended by its own rules: PASSED.**
    - Leveled off at 250,000 games: the last three checkpoints were 56%, 52% and 57%, within 5 points, each 53–55% against the one before.
    - Its best checkpoint, **ckpt_250k**, then won **57.2%** of the 400-game confirmation (seat 0 53.5%, seat 1 61.0%) vs k3's 45.8% (44.0% / 47.5%) on the same seeds and seats.
    - Game by game: the bot won 95 that k3 lost; k3 won 49 that the bot lost (p ≈ 0.0002).
    - 2.4 h of training on 2 cloud cores. The cloud machine restarted once, somewhere between 150k and 200k games. The run resumed from its 150k save, which also tested the resume path with v2.
    - It's still a pilot: 400-game confirmation, 200-game checkpoints. The laptop run (1,000-game bar and confirmation, 500-game checkpoints) is the real test.

- **Knockout audit of the pilot's ckpt_250k** (`audit_knockouts_v2.py`, same method as run 1's). 600 bot-vs-k3 games and the 400 bar games (k3 piloting Blaziken on the same seeds), replayed exactly, with 0 replay problems:

  | Per player-turn | Bot piloting Blaziken | k3 piloting Blaziken | Run 1 bot (mirror, for reference) |
  |---|---:|---:|---:|
  | Sure game-winning move on offer / not won that turn | 299 / 1 (0.3%) | 149 / 0 | 795 / 19 (2%) |
  | Sure knockout on offer / not taken | 583 / 28 (5%) | 381 / 4 (1%) | 1,992 / 44 (2%) |
  | Sure points handed over (attack / end turn / other), per 1,000 turns | 0 / 0 / 0 | 0 / 0 / 0 | 13.8 / 9.0 / — |

  - **Sure wins are fixed:** 1 in 299, from 19 in 795.
  - **Giveaways: none, but this matchup barely tests them.** k3 had none either, and Lucario's list has no Rocky Helmet and no poison or burn attacks. The Helmet and poison fix has to be judged against a deck that uses them.
  - **New pattern: it passes up some 1-point knockouts, mostly by retreating** (22 of the 28). The typical case is a healthy Mega Blaziken ex facing a 30-HP Bonsly, where it retreats to Heatmor instead of knocking Bonsly out. It scores the retreat clearly higher (0.07–0.37), so it's a choice, not a coin flip.
    - [Inference] Mega Burning discards Fire energy, and Bonsly's attack cuts the Defending Pokémon's damage by 30. Saving the Mega's energy may be the reason.
    - It won 12 of those 28 games. That's under its overall rate, but these positions aren't a random sample (Fable).
    - Whether it's smart or a bad habit is Dustin's call; he knows the deck. Examples: seeds 60000138 and 70000388 (turn 4) and 70000264 (turn 6).

- **Defensive test, previewed on the pilot's ckpt_250k** (`audit_knockouts_v2.py --vs weezing,blaziken`, 400 fresh games per deck, with k3 piloting Blaziken on the same seeds and seats; the uncorrected v2 build, so a preview of the report line, not the result):

  | Per 1,000 player-turns | Bot | k3, same deck and games | Run 1 bot (mirror) |
  |---|---:|---:|---:|
  | Pokémon left to die at checkup (vs Weezing: poison and burn) | 0.5 (1 case) | 0 | 9.0 |
  | Attacks that hand over sure points (vs Limitless Blaziken: Rocky Helmet) | 5.1 (13 cases, 0 fatal) | 1.7 (4) | 13.8 (21 fatal) |

  - **Poison/burn at checkup:** fixed in this preview. One case in 2,078 turns.
  - **Rocky Helmet:** three times k3's rate, down from run 1's four times, and none handed over the game.
    - All 13 were Rocky Helmet, and v2 priced every one correctly ("they gain 1" or "they gain 3"). The bot knew. So the encoding reached the problem; what's left is judgment.
    - 5 were even trades (1 point for 1, or 3 for 3).
    - 8 were a 10–20 HP attacker hitting into the Helmet for nothing. In 6 of those, v2 said the Pokémon would be knocked out next turn anyway if it stayed. But a retreat was available in 7 of the 8, and 2 weren't doomed at all.
  - **Win rate on these 400 paired games:** vs Weezing, bot 33.8% vs k3 44.2%, which is weaker than the transfer table's 46% vs 48% on 200 other seeds. vs Limitless Blaziken, bot 51.7% vs k3 49.8%.
  - Details: `results/ko_audit/v2_pilot_v2_blaziken_lucario_ckpt_250k_vs_weezing_blaziken.json`.

- **Transfer** (`matchup_test_v2.py`, 200 games per row, ±7 points): the bot pilots Blaziken against each Limitless study deck, which k3 pilots. It trained only against Lucario.

  | Opponent (k3 pilots it) | k3 piloting Blaziken | Untrained | Bot, ckpt_50k | Bot, ckpt_150k | Bot, ckpt_250k |
  |---|---:|---:|---:|---:|---:|
  | Lucario (trained on) | 45% | 0% | 49% | 56% | 51% |
  | Altaria | 45% | 0% | 26% | 38% | 33% |
  | Suicune | 48% | 0% | 50% | 49% | 48% |
  | Sceptile | 66% | 0% | | | 57% |
  | Vespiquen | 76% | 0% | | | 63% |
  | Blaziken (Limitless list) | 56% | 0% | | | 50% |
  | Hydreigon | 64% | 0% | | | 55% |
  | Weezing | 48% | 0% | | | 46% |

  - Run 1's bot was at 1–3% in every matchup it hadn't trained on.
  - This one is **at or near k3's level on decks it never saw:** 73–100% of the way from untrained to k3; on average 50% vs k3's 58% over the seven.
  - It beats k3 only in the matchup it trained on. It's a specialist, as intended. [Inference] What carries over looks like the deck-independent part: what a move does and what the opponent can hit back for. Card identities don't carry over.
  - The Lucario row here (51%, different seeds) is lower than the confirmation's 57%. Both are within the ±7-point noise of 200–400 games.
  - Full results: `results/matchup_test_pilot_v2_blaziken_lucario_ckpt_50k.json`, `…_ckpt_150k.json`, `…_ckpt_250k.json`.

**Fixes after Astra's review** (add-on 0.5.0, encoding v2.1; `train_v2.py`)

| Astra's finding | Fix | Now checked by |
|---|---|---|
| 1. Resume could skip the draw gate when it shares a game count with a checkpoint | Every event at one game count is handled together and saved in one commit, draw gate first | Smoke run with the gate and a checkpoint both at 4,000 games, killed exactly there: on resume both ran ("draw gate + checkpoint at 4,000 games") |
| 2. Bench moves reused stale "after" numbers (Bench attach, evolving Lucario) | The shortcut is gone: after every move, the attack and threat numbers are recomputed from the resulting position | Check 6 below, plus Astra's two cases |
| 3. The reuse key missed Korrina, the Stadium and other turn effects | No partial key. A repeated position is only reused when its full game-state hash matches (turn effects, Stadium and flags included) | Check 6 below, plus Astra's two cases |
| 4. One draw window could count twice toward switching shaping off | The draw check runs at most once per game count | `train_v2_checks.py` runs the real function twice at 250k: counted once |
| 5. (minor) Two decks with the same file name could hide an edit from the resume check | Inputs are recorded by role ("deck (mine)", "deck (opponent)", …) | `train_v2_checks.py` |

- **Also added:**
  - Each move's numbers now use their own fixed-seed random stream, so a row depends only on the position and that move, never on the order the moves were listed in.
  - When the opponent chooses mid-turn (Sabrina), v2.1 looks past their choice instead of treating the turn as over. That's where the first version of check 6 found 3 mismatches.
- **Versioning (Astra):**
  - The corrected encoding is called "v2.1", and 0.5.0 refuses "v2" with a message pointing to the 0.4.0 wheel.
  - Run settings record the encoding, and the audit and transfer scripts use whichever one the run was trained with. The pilot's checkpoints still need 0.4.0.
- **Check set rerun on 0.5.0** (`v2_checks.py` → `results/v2_checks.txt`, 3 min):
  1. v1 is unchanged: hash 18e818dfef01e2ca1caa.
  2. Hidden-card probe: 4,666 of 4,666 identical; control 1,628 of 1,628.
  3. Points and wins vs the true game: 6,698 of 6,698.
  4. Threat calibration: unchanged.
  5. **New — damage dealt and damage taken vs the true game:** 5,349 of 5,349 moves with one outcome agree, and 3 of 3 chance-dependent ones fall inside the seeds' range.
  6. **New — "after" numbers vs a fresh look at the resulting position:**
     - Remaining attack and next-turn threat: 1,846 of 1,846 identical.
     - The End turn row against the position's own "if I end my turn now" threat: 2,862 of 2,862.
     - Moves where k3 made a choice in between: 19 of 25. v2.1 assumes their worst-for-us choice and k3 sometimes picks differently, so these can't all match.
     - **Positive control:** the same check on the old 0.4.0 add-on finds 132 mismatches in 1,870 moves (Attach 110, Place 18, Play 4). So this check would have caught Astra's bugs, and it's now a permanent regression test.
  7. **New — Astra's four reproductions, replayed:**

     | Case | v2 (0.4.0) predicted | v2.1 predicts | After the move |
     |---|---:|---:|---:|
     | Bench Energy | 10 | 0 | 0 |
     | Korrina | 40 | 70 | 70 |
     | Arena of Antiquity | 10 | 30 | 30 |
     | Lucario evolution | 10 | 30 | 30 |

- **Smoke runs of the fixed build:**
  - Draw gate and checkpoint sharing a boundary, killed exactly there and resumed: both handled.
  - Shaping switched off at the second distinct low check.
  - The hour budget stopped a run.
  - The runner-up within the gap got its own confirmation on the bar's seeds.
  - The audit and transfer scripts ran on the result with 0 replay problems.

**After the confirmation (Fable, for later):** if the laptop run confirms the transfer, the more useful next run may be the same design trained on a mix of matchups rather than another one-deck specialist. The k3 screen would then be the list of matchups to mix, not a list of decks to pick from.

**Before launch** (done): Astra confirmed the fixes on Sept 19 before the run started: her four reproductions, the trainer checks and the grouped saves (LOG). Dustin started `HOURS=6 bash run_training_v2.sh` at 09:04 CDT with 8 workers.

**Run 2 results** (`runs/blaziken-lucario-v21-01`, encoding v2.1, add-on 0.5.0) [measured]
- **Run:** 1,000,000 games in 3.4 h of training at 80–91 games/sec, 09:04–12:33 CDT, including the end reports. No errors or restarts.
  - Draw gate passed at 250k (0.6% turn-limit draws). Tiebreak shaping switched off at 250k, after two separate low checks.
  - It stopped by the leveled-off rule at 1M: the last three checkpoints were 63%, 60% and 64% (within 5 points), each 51–55% against the one before.

  | Checkpoint | vs k3, 500 games (seat 0 / seat 1) | vs random | vs previous |
  |---|---:|---:|---:|
  | 100k | 50% (53 / 48) | 98% | 98% |
  | 250k | 53% (54 / 52) | 99% | 65% |
  | 500k | 63% (60 / 65) | 99% | 55% |
  | 750k | 60% (61 / 60) | 98% | 55% |
  | 1M | 64% (63 / 66) | 99% | 51% |

- **The verdict: 1,000 paired games, the same seeds and seats as the bar.** k3 piloting Blaziken: **47.6%** (seat 0 46.4%, seat 1 48.8%). The pass line was 52.6%, with neither seat below 41.4% / 43.8%.
  - **ckpt_1000k (best): 62.3%** (seat 0 60.6%, seat 1 64.0%) → **PASS**.
    - Game by game: the bot won 270 games k3 lost, and k3 won 123 the bot lost. Exact p ≈ 1e-13.
    - 2 draws; no game hit the turn limit.
  - ckpt_500k (runner-up, within 7 points): 56.6% (53.8% / 59.4%) → also a pass. 274 vs 184, p ≈ 3e-5.
  - Bot games ran 9.95 turns on average against 9.30 for k3 on the same seeds.
- **Knockout audit in the training matchup** (1,500 bot games vs k3 and the 1,000 bar games, replayed exactly, 0 replay problems):

  | Per player-turn | Bot (ckpt_1000k) | k3 piloting Blaziken | Run 1 bot (mirror) |
  |---|---:|---:|---:|
  | Sure game-winning move on offer / not taken | 795 / **0** | 407 / 0 | 795 / 19 |
  | Sure knockout on offer / not taken | 1,401 / 38 (3%) | 1,048 / 9 (1%) | 1,992 / 44 (2%) |
  | Points handed over, per 1,000 turns | 0 | 0 | 13.8 attack + 9.0 end turn |

  - **Sure wins: fixed** (0 of 795 missed).
  - It still passes up some 1-point knockouts, mostly to retreat. That's 3% of knockout chances, down from the pilot's 5%.
  - Lucario has no Rocky Helmet and no poison or burn, so this matchup can't test giveaways.
- **The defensive test** (Fable), 400 fresh games each against two decks it never trained on. k3 piloted Blaziken on the same seeds and seats for comparison.

  | Per 1,000 player-turns | Bot | k3, same deck and seeds | Pilot preview (v2, ckpt_250k) | Run 1 bot (mirror) |
  |---|---:|---:|---:|---:|
  | vs Weezing: turn ended with the Active then knocked out at checkup (poison/burn) | 5.6 (12 cases) | 0 | 0.5 | 9.0 |
  | vs Limitless Blaziken: attacks into Rocky Helmet that hand over points | 4.0 (10 cases, 0 fatal) | 1.7 | 5.1 | 13.8 (21 fatal) |
  | vs Limitless Blaziken: checkup knockouts (burn) | 4.0 (10 cases) | 0 | 0.4 | — |

  - **Rocky Helmet:** better than run 1 and slightly better than the pilot, but still about 2.4× k3. No Helmet giveaway lost the game.
  - **Poison and burn at the checkup: not fixed.** This checkpoint shows 12 + 10 cases against the pilot preview's 1 + 1. It's a different checkpoint and a different build, so the cause isn't known. I looked at all 22 cases:
    - v2.1 priced every one correctly ("they gain 1", or 3 for a Mega). The bot knew and ended the turn anyway; the score gap to the safe option was small (0.001–0.13).
    - **This audit line is loose** (as for run 1). It counts a case as avoidable if any other move avoided the points *on the spot*, and moves that don't end the turn (attaching energy, playing Professor's Research) always do.
    - **Stricter count:** a retreat was on offer at some point in that turn in only **8 of the 22** (3 vs Weezing, 5 vs Blaziken). Retreating to the Bench clears poison and burn. That's about **1.7 clearly avoidable cases per 1,000 turns, against k3's 0.**
    - Of the other 14, 7 were a poisoned (usually also burned) 10–20 HP Heatmor against Weezing's Boiler Smog. The rest were burned Torchic or Castform against Blaziken, or similar.
    - In all 14, no retreat was ever on offer that turn: no energy for the retreat cost, or no Bench to retreat to. They look unavoidable once the turn started, unless attaching the turn's energy to the Active would have paid the retreat. That's not checked. [inference]
    - Details: `results/ko_audit/v2_blaziken-lucario-v21-01_ckpt_1000k_giveaway_details.json`.
  - **Win rates in these paired games:** vs Weezing, bot 35.2% vs k3 44.2%. vs Limitless Blaziken, bot 50.0% vs k3 49.8%.
- **Transfer test** (400 games per row, ±5 points, the bot piloting Blaziken; seeds differ from the bar's):

  | Opponent (k3 pilots it) | k3 piloting Blaziken | Untrained | Bot, ckpt_1000k | Pilot bot (v2, ckpt_250k, 200 games) |
  |---|---:|---:|---:|---:|
  | Lucario (trained on) | 43% | 0% | **58%** | 51% |
  | Altaria | 43% | 0% | 40% | 33% |
  | Suicune | 48% | 0% | **52%** | 48% |

  - Against decks it never saw, it's at k3's level (Suicune), close to it (Altaria, 3 points under), or clearly under it (Weezing, 9 points under, in the defensive test).
  - Weezing and Altaria are the weak spots. [inference] Both lean on effects the look-ahead only partly sees: status conditions, and plays from hand and Bench.

**What run 2 shows, plainly:**
- **The design works.** A bot trained for 3.4 hours on the laptop pilots Dustin's Blaziken against Lucario about 15 points better than k3 does, on the same games. It never misses a sure win.
- **It carries over partly:** k3's level or close against three of four unseen decks tested here. Run 1's bot was at 1–3%.
- **Defence against poison and burn is not solved.** The bot sees that its Pokémon will die at the checkup and sometimes lets it happen when a retreat was available. That's the clear gap to k3, and the first thing to look at before trusting it against Weezing-type decks.
- **Not shown:** whether the bot's lines are what a human should play on the ladder. That's Dustin's read of transcripts, not a number here.

## Run 3 — a general pilot for a five-deck pool (signed off by Fable; built; Astra's review done and fixed; ran Sept 19 — see "Run 3 result")
**Where it stands:** Fable signed off the design below. It's built and passed the cloud practice test. Astra reviewed it and found three problems in the bookkeeping, not in the design; all three are fixed and re-tested (see "Astra's review" below). Next: Dustin starts it in WSL with one line (at the end of this section).

**The idea (Fable):** the same encoding (v2.1) and training loop as run 2, trained on a mixture of matchups from a small pool instead of one pairing.
- The network pilots both sides, as now.
- It's judged per pairing against k3's own result in that pairing, on paired seeds.
- Two decks are held out of training to measure how it does off the pool.
- Dustin: no time budget on his laptop. So the leveled-off rule does the stopping, and a hard cap only guards against a broken run. The run should go a day or two untouched and produce every report at the end.

**Pre-checks first (Fable's three, plus her optional headroom test; `results/run3_prechecks/`)** [measured; A–C on run 2's final network]
- **A. Poison and burn in run 2's training:**
  - Replayed the 996 recorded self-play games exactly. The Blaziken side's Active was poisoned or burned in **0 of 24,379** decisions, because Lucario's list has no status attacks.
  - The Lucario side was burned in 899 decisions (by Mega Burning) and never poisoned.
  - So the network never trained a poisoned or burned Blaziken position, and never saw poison at all.
- **B. Retreat vs end turn in the 8 checkup deaths where a retreat was on offer:**
  - The inputs were right every time: the End turn row said "opponent gains 1", and the retreat row said 0 with no knockout threat.
  - The network rated every one of these positions as lost (−0.6 to −1.4; below −1 is outside anything it trained on), and it lost all 8 games.
  - It scored ending the turn above retreating: 4 near-ties (gap under 0.06), 4 clear preferences (0.10–0.25).
- **C. The same network piloting Lucario** against k3 piloting Blaziken, on the bar's 1,000 seeds:
  - **52.5% vs k3's 52.2%** as Lucario (198 vs 195 game by game, p = 0.92). No gain.
  - As Blaziken it was +14.7 points. **Run 2's gain was one-sided**, even though the network trained both sides equally.
- **What these mean for the design** [inference]:
  - The poison/burn gap is most likely **missing experience, not missing information**. The encoding already tells the bot; it never lived those positions as Blaziken. A pool with Weezing (poison and burn) and Altaria (sleep and Bad Dreams) supplies exactly that. **No encoding change for run 3**, as Fable proposed.
  - **Part of the gap may be the objective, and a pool won't fix that part.** Under a pure win/loss target, a point handed over in a game that's already lost costs nothing. So "near k3's zero" is the right bar only in positions the bot still thinks it can win. The audit below reports the two apart.
  - **Gains can be one-sided,** so every pairing is measured in both directions (bot on each side). One number per pairing could hide a side that didn't improve.
- **D. Fable's optional headroom test** [measured; 1,000 games each on run 2's bar seeds, `results/run3_prechecks/k2_headroom.json`]: a weaker search (k2) pilots one deck against k3, compared with k3 piloting that deck.
  - **Piloting Blaziken:** k2 45.7% vs k3 47.6% (−1.9 points, within noise).
  - **Piloting Lucario:** k2 42.5% vs k3 52.2% (−9.7 points).
  - **Reading** [inference]: stronger play pays off much more on the Lucario side, so Lucario isn't short of room above k3. The more likely story: the network beat k3 where judgment beats deeper search (Blaziken, where an extra step of search barely helps), and only matched k3 where deeper search pays (Lucario). Run 3 measures both sides of every pairing, so it will show whether that pattern holds.

**The pool and the pairings**
- **Pool:** Dustin's Mega Blaziken (06), Mega Lucario ex, Team Rocket's Weezing ex / Hoopa ex (poison and burn), Mega Altaria ex / Espeon (sleep, Darkrai's Bad Dreams), Suicune ex. The last four are the Limitless study lists.
- **Pairings:** the 10 cross pairings, with no mirrors; the network pilots both decks. That's **20 directed matchups** (bot on deck A, k3 on deck B).
- **Card list:** the union of the five decks. Held-out cards read as "other card"; the v2.1 numbers don't depend on the card list.
- **Which pairing each training game plays:**
  - **Half the games:** Blaziken against one of the other four, split by Limitless share: Lucario 8.6%, Altaria 5.1%, Suicune 4.8%, Weezing 4.2%. That's about 38 / 23 / 21 / 18% of those games.
  - **The other half:** the six non-Blaziken pairings, evenly (about 8% of all games each).
  - Seats are drawn at random each game.
- **Kept from run 2:**
  - self-play plus 20% games against earlier checkpoints (with the same pairing draw)
  - 10% → 5% random moves
  - the 0.97-per-turn discount
  - the draw gate at 250,000 games with tiebreak shaping
  - network size, learning rate, buffer and the "2 uses per move" target

**Evaluation (signed off)**
- **The bars, measured first:** k3 vs k3 in all 10 pairings, **1,000 games each** on the confirmation seeds. Each bar game serves both directions: deck A's result and deck B's result.
- **Checkpoints every 500,000 games** (Fable). Each one plays:
  - **1,000 games per directed matchup against k3** (20,000 games) on a fixed evaluation seed range. It never overlaps the bar and confirmation seeds, so picking the best checkpoint never touches the games that confirm it.
  - 2,000 games against the previous checkpoint across all pairings (decks swap every two games; 50% = no change)
  - 500 games against random moves across all pairings
  - About 10 minutes per checkpoint on the laptop [estimate].
- **The score each checkpoint gets** is the average, over the 20 directed matchups, of (bot's win rate − that matchup's k3 bar): the **average margin**. The STATUS shows it for every checkpoint, plus a grid of the 20 margins for the latest one.
- **Leveled off** (Fable's rule on the average margin): 3 checkpoints in a row within **3 points** of each other, each at or under 55% against its previous checkpoint. The earliest it can stop is 1.5M games.
- **Floors** (insurance; shouldn't fire):
  - at 1M: average margin at least −10 points and at least 90% against random
  - at 2M: average margin at least −5
- **Hard cap:** 20M games, a safety net for a broken run. There's no time limit. Pause and resume with the same command; a resume with changed settings is refused.
- **Confirmation (automatic at the end):** the best checkpoint by average margin, plus the runner-up if it's within 2 points, plays all 20 directed matchups on the bars' own seeds, **1,000 games each**, paired game by game with the bar.

**What run 3 is judged on — fixed before it starts (signed off by Fable)**
On the confirmation's 1,000 paired games per matchup:
1. **Holds run 2's Lucario result:** bot piloting Blaziken vs k3 piloting Lucario at least **+10 points** over the bar. Run 2 was +14.7.
2. **Lifts Weezing:** bot piloting Blaziken vs k3 piloting Weezing at **k3's own result or better** (margin ≥ 0).
3. **Lifts Altaria:** the same against Altaria.
4. **Nothing broken elsewhere:** no directed matchup, on either side, more than **5 points below** k3.
- **PASS = all four.**
- **Checkup deaths are a report line, not a pass rule** (Fable). The audit counts them per matchup three ways: all, strict (a retreat was offered that turn), and strict and still winnable. **"Still winnable"** means the network's own score for the move it chose was above **−0.5**. On its scale (+1 win, −1 loss) that's about a 1-in-4 chance or better by its own estimate (a bit lower early in a game, because the per-turn discount pulls scores toward zero).
- **Reported, not judged:** all 20 margins, the checkpoint history, the knockout audit and the held-out tests below.

**Reports produced automatically at the end** (no one needs to ask; about 1–1.5 h)
- Confirmation results per directed matchup, each with its bar and the game-by-game count ("games won only by the network / only by k3", with p).
- **Knockout audit** on the confirmation games, per directed matchup, next to k3 piloting the same deck on the same seeds:
  - missed sure wins and missed sure knockouts
  - Rocky Helmet and other attack giveaways
  - checkup deaths, three ways (above)
- **Held-out transfer, both sides** (Fable). Two decks never trained on, 1,000 paired games per row:
  - (a) the bot pilots each pool deck against k3 piloting the held-out deck
  - (b) the bot pilots the held-out deck against k3 piloting each pool deck
  - Each row is paired with k3 vs k3 on the same seeds. That's 2 × 5 × 2 = 20 rows.
  - **Held-out decks:** Dustin's 13 Alolan Ninetales/Raticate and 09 Mega Manectric/Heliolisk. Both were even under k3 against the pool's Limitless decks, and both are decks Dustin brings, so (b) also says how well the bot pilots his own lists.
- Everything lands in `runs/pool5-v21-01/REPORT.txt`; STATUS.txt points to it.

**Time** [estimate]: the cloud practice test ran at about the same speed per worker as run 2 on the laptop, so about 80 games/sec with 8 workers. That's about 1¾ h of training per 500,000 games, plus about 10 minutes per checkpoint and 10 minutes for the bars.
- Earliest possible stop (1.5M games): about 6 h.
- If it keeps improving to 3–4M games: about 12–16 h.
- End reports: about 1–1.5 h more.
- The 20M cap would be about 3 days; a healthy run shouldn't get near it.

**What was built** (all in this folder; the engine and the add-on are unchanged, the same 0.5.0 wheel as run 2)
- `train_v3.py`, from `train_v2.py`: the deck pool and pairing draw, the bars, per-matchup checkpoint evaluation, the average-margin plateau, the automatic confirmation and the four pass conditions. Old resume files are now deleted once a newer save is on disk (one is kept).
- `audit_v3.py`: the knockout audit per directed matchup, with the three-way checkup count.
- `transfer_v3.py`: the two-sided held-out test.
- `report_v3.py`: writes REPORT.txt, with a "Report problems" line at the top if a step is missing, out of date or incomplete.
- `run_training_v3.sh`: one command for everything. Running it again resumes training, or finishes any report step that was interrupted; finished steps whose inputs haven't changed are skipped. REPORT.txt is written even if the audit or held-out step stops.

**Cloud practice test (tiny settings: 12,000-game cap, 4 games per matchup)** [measured]
- **Crash at the 3,000-game boundary** that the draw gate and a checkpoint share, then resume: it picked up from the last save and handled both events once.
- **Crash at 4,500 games** (after the 3,000 save), then resume: it picked up at 3,000.
- **The end path:** leveled off at 9,000 games → confirmed the best checkpoint and the runner-up → FINISHED (tiny settings can't pass) → audit, held-out test and REPORT.txt all ran. Running the chain again skipped every finished step.
- **Pass logic on made-up margins:** Lucario at +10.0 passes and +9.9 fails; any matchup at −5.0 passes and −5.1 fails; Altaria at −0.1 fails.
- **Resume-file cleanup:** one file left after each save.
- **Rerun after Astra's fixes (Sept 19):** all of the above passed again, and the one-line launcher itself ran start to finish with `--smoke` (a cloud copy with cloud paths). Rerunning it after a held-out deck was changed still wrote REPORT.txt, with a "Report problems" line.

**Astra's review (Sept 19; `results/astra-review/V3_REVIEW.md`) and the fixes** [measured]
- **Passed her focused checks:** the pass test (+10.0 passes, +9.9 fails; −5.0 passes, −5.1 fails, in all 20 directions), evaluation seeds kept apart from each other and from training, the bar/confirmation pairing, the saves at shared boundaries, the resume-file cleanup, the pairing weights and random seats, and the −0.5 "still winnable" split.
- **Found three problems, all fixed:**
  1. **Training seeds could repeat in a very long run.** Workers had seed blocks 10 million apart, so a worker that played more than 10 million games would reach the next worker's seeds. Now each game's seed comes from its own game number, which only one worker can ever claim. Each resume gets a fresh block of 100 million, and the run refuses a game cap that doesn't fit.
     - Checked: a practice run with a crash and resume recorded all 9,000 games. There were 9,000 different seeds, numbered 0–2,999 before the crash and 3,000–8,999 after, with no gaps.
  2. **A game that didn't replay exactly still counted in the audit, and the audit was then reused as finished.** Now such games are left out of the numbers. The audit is marked INCOMPLETE, REPORT.txt says so at the top, and it's redone on the next run instead of reused.
     - Checked by corrupting one recorded game: marked INCOMPLETE, redone on the rerun, complete once the record was restored, then skipped.
  3. **A finished report step was reused even if its inputs had changed.** Now each audit and held-out result stores what it was made from: the checkpoint, the recorded games, all seven deck files, the settings, the code and the add-on. It's reused only if all of that still matches. Otherwise it's redone, and the old file is kept beside it as evidence.
     - The two held-out decks are now part of the run's recorded inputs, like the pool decks. A report step refuses to run if any deck file differs from the one the run recorded, and REPORT.txt shows that step as out of date.
     - Checked by changing a held-out deck (refused; the report flagged it; skipped again once restored) and by changing the held-out script (redone, old result kept).
- The trainer still does nothing when rerun on a finished run, without comparing inputs. That's fine now, because each report step checks its own inputs.
- Check outputs: `results/v3_fixes_check.txt`.

**To start it:** in WSL Ubuntu, laptop plugged in, sleep off:
`bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v3.sh"`
Progress in plain words: `runs/pool5-v21-01/STATUS.txt`. After an interruption, run the same line again.

## Run 3 result — FAILED: stopped at its 1M floor, and its continuation to 2M leveled off (laptop, Sept 19–20)
**Started** by Dustin at 14:56 CDT; **stopped** at 19:23 by the 1M floor: the average margin was **−11.4** against the −10 it needed. The end reports don't run after a stop. Files: `runs/pool5-v21-01/STATUS.txt`. [measured]

| checkpoint | average margin | vs its previous checkpoint | vs random |
|---|---:|---:|---:|
| ckpt_500k | −11.2 | 95% | 99% |
| ckpt_1000k | −11.4 | **50%** | 97% |

Margins at 1M, in points against k3 piloting the same deck (row = deck the network pilots; 1,000 games each, so about ±3):

| | Blaziken | Lucario | Weezing | Altaria | Suicune |
|---|---:|---:|---:|---:|---:|
| **Blaziken** | — | +1 | +2 | −8 | +8 |
| **Lucario** | −18 | — | +4 | −6 | +19 |
| **Weezing** | −17 | −15 | — | −28 | −16 |
| **Altaria** | −15 | −12 | −8 | — | −2 |
| **Suicune** | −22 | −24 | −36 | −33 | — |

- **No net progress from 500k to 1M.** Head to head, the 1M network beat the 500k one exactly 50% of the time. Matchups moved 5–9 points both ways and cancelled out.
- **Fable:** the floor was calibrated for the wrong run (a single matchup, not an average over 20 with three lagging decks). The flat spot is real, and the 50% head to head matters more than the 1.4-point miss.

**Fable's cheap checks (Sept 19; nothing trained)** [measured; scripts and output in `results/run3_checks/`]
1. **Card list: not a bug.**
   - In 36,456 decisions across all 10 pairings, no pool card ever landed in an "other card" slot, in any part of the input.
   - Control: with a held-out deck in one seat, "other card" was used 16,000–18,000 times.
2. **Training games per pairing** (the draw matched the weights; sampled 1 in 1,000 recorded games):
   - Blaziken vs Lucario got **18.9%** of the games, about **189,000** by 1M. That's not half the run. The other Blaziken pairings got 9–11% each; each non-Blaziken pairing got 8.3%.
   - For comparison: the cloud pilot matched k3 within 25,000–50,000 games of this pairing and passed at 250,000. Run 2 on the laptop trained 1M.
   - Game-sides each deck was piloted by the network (self-play pilots both sides): Blaziken about 464,000, Lucario 403,000, Altaria 347,000, Suicune 316,000, Weezing 270,000.
3. **Running out of Pokémon: it's failing to bench, not benching and losing them.**
   - Suicune lost 219 of its 4,000 checkpoint games with the opponent under 3 points. In 164 of them it never had a Pokémon on its bench at all. At its last End turn the bench was empty in 206 of 218, and in 123 of those it had a Basic in hand it could have placed.
   - Two logs are in `results/run3_checks/`. In one, it ended three turns in a row holding a placeable Chien-Pao ex (and an unplayed Poké Ball), and lost its only Pokémon.
   - **Every deck has this habit.** At the end of a turn where a Basic could be benched, the network still has it in hand 34–50% of the time (Blaziken 50%, Lucario 39%, Weezing 44%, Altaria 37%, Suicune 34%). k3: 3–11%.
   - **Run 2's specialist has it too.** Piloting Blaziken against k3's Lucario on the same 150 seeds, it held a benchable Basic at the end of 37% of such turns, against run 3's 50%, while winning 65% of those games. So separate networks reduce the habit but don't remove it.
   - **The threat numbers said "safe."** In those last turns, the End-turn row's "opponent can win next turn" number was 0 in 62–77% of cases (the "can KO" number in 58–75%), and marked fully known in about 90%. The KO came from lines the one-attack lookahead doesn't cover: evolving, switching in a benched attacker, playing a Supporter first.
   - **Reading** [inference]: benching has no immediate consequence in the move numbers, and the threat numbers confidently say the Active is safe when the danger is a multi-step line. So the network rarely has a reason to bench. Blaziken, the most-trained deck, has the habit too, so this isn't only a matter of training volume. It costs Suicune, Weezing and Altaria more because more of their losses happen this way.

**Continuation result (Sept 20): a plateau** [measured; `runs/pool5-v21-01-cont/REPORT.txt`]
- Started by Dustin at 22:07 from the 1M save, with floors off and a 2M cap. It leveled off at 2M and ran all its end reports.

| checkpoint | average margin | vs its previous checkpoint | Blaziken vs Lucario |
|---|---:|---:|---:|
| 500k | −11.2 | 95% | +4 |
| 1M | −11.4 | 50% | +1 |
| 1.5M | −12.6 | 50% | +5 |
| 2M | −12.4 | 51% | +3 |

- **Plateau:** four checkpoints within about a point of each other, and three head-to-heads at 50%.
- **Not budget (Fable's test):** Blaziken vs Lucario stayed at +1 to +5 after about 380,000 games of that pairing, past the 250,000 at which the cloud pilot passed.
- **Per piloted deck** (average over its 4 opponents, 500k → 2M): Blaziken −0.9 → +0.7, Lucario +1.3 → +3.6, Weezing −20.5 → −20.8, Altaria −9.4 → −9.7, Suicune −26.4 → −35.5.
- **Confirmations** (1,000 paired games per matchup on the bars' seeds):
  - **ckpt_500k:** −12.1 on average. Blaziken vs Lucario −0.8, vs Weezing −6.2, vs Altaria −7.7; lowest matchup −30.5.
  - **ckpt_1000k:** −10.9. Blaziken vs Lucario +0.7, vs Weezing −2.0, vs Altaria −5.5; lowest −32.3.
  - Neither meets any of the four conditions.
- **Audit (new):** the shared network misses a sure knockout on 5–15% of the turns one is offered in most matchups. k3 misses 0–1%, and run 2's specialist 3%. It rarely misses a sure win.
- **Held-out test (ckpt_500k):** facing Ninetales or Manectric, 5–33 points under k3; piloting them, 5–30 under.
- **Fable's reading** [inference]: a single shared network that is worse at everything, not one that is fine on Blaziken and bad on three decks. The weak decks are where "worse at everything" costs most. Decided: run 4 is one network per deck, plus the benching numbers.

**The two checks Fable asked for before run 4 (Sept 20)** [measured; scripts and output in `results/run3_checks/`]
1. **Headroom: how much does deeper search pay with each deck?** k2 (a weaker search) piloted each deck against k3, on run 3's bar seeds, 1,000 games per directed matchup, paired with k3 piloting the same deck.

| k2 pilots | vs Blaziken | vs Lucario | vs Weezing | vs Altaria | vs Suicune | average |
|---|---:|---:|---:|---:|---:|---:|
| **Blaziken** | — | −3.0 | −4.4 | −7.6 | −5.5 | **−5.1** |
| **Lucario** | −7.4 | — | −8.0 | −5.2 | −7.0 | **−6.9** |
| **Weezing** | −9.7 | −10.1 | — | −9.3 | −16.6 | **−11.4** |
| **Altaria** | −3.8 | −1.2 | −6.3 | — | −2.3 | **−3.4** |
| **Suicune** | −8.3 | −7.1 | −21.5 | −9.7 | — | **−11.6** |

   - **Reading** [inference]: where k2 is close to k3, search depth barely pays, so a one-move scorer can beat k3 there; where k2 is far below, depth pays and matching k3 may be the ceiling. Run 2 fits: Blaziken vs Lucario has a small gap (−3.0) and the specialist was +15; the Lucario side has a bigger gap (−7.4) and the specialist only matched k3.
   - The two decks that reward depth most, Weezing and Suicune, are the two the shared network is worst with (−21 and −36). The line isn't clean, though: Lucario's gap is −6.9 and the network is fine with it, Altaria's is the smallest and the network is −10 there.
2. **What goes wrong in Suicune's ordinary losses** (ckpt_1000k's confirmation games, 1,000 seeds, against k3 piloting Suicune on the same seeds):
   - Of 1,000 games: the network won 310, lost 638 with the opponent reaching 3 points, lost 52 by running out of Pokémon. On 299 of those normal losses, k3 won the same seed.
   - **In those 299 games the network barely played:** 1.2 attacks per game against k3's 3.7, 0.7 points scored against 3.5, 1.1 evolutions against 2.2, 2.7 energy attachments against 3.9. In 144 of the 299 it never attacked at all.
   - **The habit, across all 1,000 games** — on turns where the move was on offer, how often it was made (network vs k3): attack **71% vs 97%**, attach energy **64% vs 89%**, use an ability **55% vs 87%**, Rare Candy 68% vs 89%, Professor's Research 46% vs 87%, place Suicune ex 54% vs 97%, place Frigibax 63% vs 86%, Giant Cape 21% vs 93%, Inflatable Boat 13% vs 64%.
   - So benching is one face of a wider habit: **it doesn't play out its turn.**
3. **Is that the shared network or the design?** (extra check) Run 2's specialist, run 3's shared network and k3 all piloting Blaziken against k3's Lucario, on the same 300 seeds:

| | run 2 specialist | run 3 shared net | k3 |
|---|---:|---:|---:|
| won | 66% | 49% | 51% |
| attacked when an attack was on offer | 86% | 68% | 99% |
| ended the turn with an attack on offer | 13% | 31% | 1% |
| benched a Basic when it could | 62% | 54% | 97% |

   - **Both have the habit; the shared network has it twice as badly.** That supports Fable's "worse at everything" reading, and says per-deck networks should recover part of it but not all.
   - **Why it ends the turn** (the same games, looking at its own scores): when it skips an attack it scores ending the turn clearly higher, not as a tie (median gap +0.09 for the specialist, +0.13 for the shared network); only 30–46% of those positions are ones it thinks are already lost; and the attacks it skips would have scored a point in 3–5% of cases but do damage in 55–65%. So it isn't only indifference in decided games — it prefers doing nothing with its turn. No fix for that is in run 4's scope beyond per-deck networks and the benching numbers; the audit will measure whether it improves.

**Why it ends its turn: Fable's two hypotheses, both tested from the recorded games (Sept 20)** [measured; `results/run3_checks/passivity_cause*.py`, `ko_threat_artifact.py`]
- **Hypothesis 1, a bug: "attack then pass" and "end turn" priced differently.** Not supported. In 86–96% of the turns it ends with an attack on offer, that attack knocks nothing out, and there the two options' threat numbers are identical in 86–92% of cases. Where they differ, the attack's threat is *lower*, never higher.
- **Hypothesis 2, the post-knockout promotion priced against the opponent's best bench Pokémon.** The lookahead does work that way (it resolves a forced promotion in the opponent's favour), but it doesn't produce the effect. Across every decision where a sure knockout was on offer (147 and 166 decisions for the specialist and the shared network):

| | knockout attack | end turn |
|---|---:|---:|
| opponent can knock me out next turn (specialist) | 0.06 | 0.32 |
| opponent can knock me out next turn (shared net) | 0.02 | 0.28 |
| opponent wins next turn (shared net) | 0.02 | 0.28 |

  The knockout option looks **safer**, not more dangerous, in 70–75% of cases equal and the rest lower. The promoted Pokémon usually can't attack the turn it comes up, so the worst-case promotion costs little. On those decisions the network prefers the knockout: the specialist passes in 4%, the shared network in 14% — which is the sure-knockout miss rate the audit measures.
- **What the numbers do point at** [inference]: the attacks it skips are small ones. With Blaziken, the skipped attacks come from Castform, Torchic and Heatmor, median 20 damage and a point in 10% of cases; the attacks it makes come from Mega Blaziken ex, median 30 damage and a point in 32%. It prefers ending the turn by 0.05–0.13 in its own units, and the run's own later checkpoints disagree with that preference in 36–40% of the same positions.
  - So the difference is worth a percent or two of win probability, and its value estimates can't resolve that. It isn't a feature bug and it isn't the promotion rule.
  - That also fits the sizes: the specialist, with one deck to learn, misses 3–4% of sure knockouts and skips 13% of small attacks; the shared network, with five, misses 5–15% and skips 31%.
  - **Consequence for run 4:** per-deck networks should recover the specialist's level, and the audit already measures it. Nothing in run 4 addresses the part the specialist still has. If that matters after run 4, the next things to try are a target that distinguishes small gains (damage or points as shaping), bootstrapped targets instead of pure game outcomes, or using the network as the evaluator inside a one-ply search at play time — all bigger changes than v2.2.
  - **In plain terms (Fable):** a 20-damage attack that doesn't change who wins the game produces no training signal at all, because the only thing the network is ever told is who won. So it is genuinely indifferent, and indifference plus noise comes out as passing. k3 attacks because its search sees the damage; this network doesn't care about damage that never reaches a result. That is a resolution limit, not a mistake in what it is shown.
  - **So v2.2 gets the benching numbers only**, and no threat-pricing change: the pricing is behaving correctly where it was suspected.
  - **If the residue matters after run 4** — and for a bot whose job is to rank decks it may not — the cheap options come first: a shaped target, or a bootstrapped one. A bootstrapped target is the one that fits this problem, because it lets damage that changes the position show up in the value even when it doesn't change the result, which win-or-loss cannot do. Using the network as an evaluator inside a one-ply search is the expensive third. **A run 5 conversation, with run 4's numbers in hand.**

## Run 4 design — one network per piloted deck (Fable, Sept 20; built and practice-tested in the cloud Sept 20; with Astra for review)
**Decided by run 3's own rule:** the continuation showed a plateau and showed that Blaziken vs Lucario wasn't short of games, so run 4 is **one network per piloted deck**, plus the two benching numbers. **Signed off by Fable on Sept 20, subject to the passivity checks above** (done: neither hypothesis held, so v2.2 carries the benching numbers only). Built Sept 20 — see "Built" at the end of this section.

**Why** [inference from runs 2 and 3]:
- Facing a deck carried over cheaply for run 2's specialist; run 3's shared network is 5–33 points under k3 even at that.
- The shared network is worse at everything it does, not bad at three decks: it misses sure knockouts on 5–15% of the turns they're offered (k3 0–1%, run 2's specialist 3%), and it leaves its turn unplayed far more often than the specialist (below).
- Separate networks remove the one thing run 3 added over run 2: shared weights across five decks.

**The shape**
- **One network per pool deck.** Each pilots only its own deck; the card list stays the union of the pool.
- **Training games:** the same pairing draw as run 3, but each seat is piloted by that deck's own network, so every game trains two networks, each only on its own side's decisions. That makes run 4 run 3 with a single thing changed.
  - Same games per hour and the same total trainer load (the same recorded decisions, each used twice).
  - Five replay buffers instead of one. Each holds about a fifth of run 3's, so the memory is the same and each still covers the same stretch of recent games.
  - Alternative shapes (rejected): training each network against k3 (about twice the cost per game, and it learns one opponent's habits) or against frozen copies (opponents never improve).
- **20% of games against past versions,** as now: one seat is a past checkpoint of that deck's own network.
- **Pairing weights:** even across the 10 pairings (10% each), so every network gets the same amount of practice and the per-deck comparison is clean. Run 3's Blaziken weighting no longer buys Blaziken anything that costs the others, since the weights aren't shared any more. [Dustin's call if he wants his deck to get more.]
- **Unchanged:** engine, DMC training, the per-turn discount, the draw gate, network size, learning rate.

**Encoding v2.2 — the benching numbers** (small change; v2.1 stays byte-identical, new add-on version, Astra reviews)
1. **"How many Pokémon I'd have in play after this move."**
2. **"If my Active were knocked out right after this move, would I lose?"** — true when nothing is left on the bench, or when that knockout would give the opponent their third point. Both are exact and read only from what the bot is allowed to see.
3. **The "certain" flag on the threat numbers goes away.** It only ever meant "the opponent's current Active's attacks could be simulated", and the network learned to read it as "safe"; the lines that actually kill it (evolving, switching in a benched attacker, a Supporter first) were never in it. An honest flag would say "not certain" almost every turn, so it carries no information and is dropped.
4. **No change to the threat pricing.** Fable's two candidate causes for the passivity were tested and neither holds (see just above), so the post-knockout pricing stays as it is.
5. **Optional, measure first:** pricing the opponent's visible bench switch-ins (retreat or switch, then attack). Honest, since those Pokémon are visible, but it costs engine simulations per decision. Measure the speed cost before deciding.

**What run 4 is judged on** (per network, on 1,000 paired games per matchup)
- **Blaziken vs Lucario: at least +10** over the bar, as before.
- **Where deeper search barely pays, at or above k3 (margin ≥ 0).** From the headroom test below, those matchups are: Blaziken vs Weezing, Altaria vs Blaziken, Altaria vs Lucario, Altaria vs Suicune.
- **Everywhere else, no more than 5 points under k3**, on every directed matchup.
- **PASS = all of the above.**
- **Report lines, not pass rules:** the knockout audit (including the sure-KO rate that says whether per-deck networks recovered the specialist's level), the benching skip rate, the "turn played out" rates below, and the held-out test (facing two decks never trained on; piloting them is no longer meaningful, since each network has one deck).

**Floors, from run 3's actual curve, per network** (insurance against a broken network, not a judgement)
- Run 3's shared network, average margin over each deck's four opponents, at 1M and 2M games: Blaziken +0.7 / +0.7, Lucario −0.4 / +3.6, Weezing −19.1 / −20.8, Altaria −9.6 / −9.7, Suicune −28.8 / −35.5.
- **At 1M games:** each network at least 10 points below run 3's number for its deck at 1M, and at least 90% against random moves.
- **At 2M games:** each network at least 5 points below run 3's number for its deck at 2M.
- These are deliberately loose. A pool average is what fired wrongly in run 3.

**Stopping, per network**
- **Leveled off:** three checkpoints in a row whose average margin (over that deck's four opponents) is within 3 points, and where the newest beats the one before it on no more than 55% of the games they decide differently (the checkpoint games use fixed seeds, so this is a paired comparison; no mirror match needed).
- The run ends when every network has leveled off, or at the cap.
- **Confirmation:** each network's best checkpoint by its own average margin, plus its runner-up within 2 points, replays every matchup on the bars' seeds.

**Budget** [estimate]
- Each network only learns from the side it pilots: with even weights, a deck's network is in 40% of games, and each of its four matchups gets 10% of all games.
- Run 2's pilot matched k3 in 25,000–50,000 games of a pairing and passed at 250,000. That needs about 2.5M games in total here.
- At run 3's 70 games a second that's about 10 hours of training, plus roughly 10 minutes per checkpoint of evaluation (unchanged), and about 1.5 h of end reports.
- **Cap: 6M games** (about a day), with no time limit, as before.

**Decided (Fable, Sept 20)**
- **Pairing weights: even.** With per-deck networks each network only learns from its own games, so a Blaziken bias buys nothing the others lose.
- **The headroom rule applies per matchup, not per deck** — that's the grain the measurement has. Altaria's expectation is "reach k3", not beat it: a deck where depth barely pays and every method is still 10 points under k3 is one nobody plays well yet.
- **Bench switch-in pricing waits** on a speed measurement.
- **A one-deck pilot first, on the laptop** (faster than the cloud): the Blaziken network alone against the pool with v2.2, to about 250,000 games, roughly an hour. It checks that the new numbers don't break what run 2 had before twenty hours go into five networks.

**Order of work**
1. The two passivity checks — done (above); both hypotheses ruled out, so v2.2 carries the benching numbers only.
2. Build v2.2 (add-on 0.6.0; v2.1 byte-identical, the two new numbers, the "certain" flag dropped) and the per-deck trainer — done, Sept 20 (below).
3. Astra reviews v2.2. — next
4. The one-deck pilot on the laptop.
5. Run 4.

### Built — Sept 20 (practice-tested in the cloud; with Astra for review)
**Encoding v2.2, add-on 0.6.0.** `RawEnv(cards, "v2.2")`. Per move 193 numbers → 194: the freed "certain" slot now holds "how many Pokémon I'd have in play after this move" (0–1, i.e. count/4), and one new slot holds "if my Active were knocked out right after this move, would I lose". Asleep/poisoned shift by one. `"v1"` and `"v2.1"` still work and are unchanged; `"v2"` (0.4.0's name) is refused, as in 0.5.0.

**Checks on the new numbers** (`v2_2_checks.py`, ~2 min, writes `results/v2_2_checks.txt`; 47-card list, 20 random games per part — all passed):
1. Sizes: observation 865 unchanged, per-move 193 → 194.
2. Layout: the first 13 numbers match v2.1 exactly in 9,882/9,882 move rows, and asleep/poisoned match shifted by one in all of them.
3. The two new numbers checked against the real game — the move is actually played on a copy of the position and the answer compared: the in-play count 8,034 moves checked, 0 wrong; "losing the Active loses the game" 6,810 moves checked, 0 wrong. Skipped rows are counted and named in the file (moves the engine refuses, moves that end the game, moves that open a follow-up choice, moves that change the Active — for those the forecast and a plain step legitimately stop at different points).
4. The freed slot holds the in-play count and nothing else (values seen: 0, .25, .5, .75, 1).

**v1 and v2.1 are byte-identical to 0.5.0** [measured]: the same 1,762 decisions encoded under the old add-on and the new one hash the same. v1 `316df62a…`, v2.1 `25330650…` (evidence: `results/v2_2_checks/`, the dumps and the script that made them).

**The per-deck trainer** (`train_v4.py`, from `train_v3.py`): five networks, one per pool deck, each seat piloted by its own deck's network, five replay buffers, per-network floors, per-network levelling off, per-network confirmation, and a verdict that judges every matchup by the rules on this page. Checkpoints are saved per deck (`ckpt_500k_blaziken.npz`). The audit, held-out test and report (`audit_v4.py`, `transfer_v4.py`, `report_v4.py`) all work per network, and the audit prints the two benching/attacking rates beside run 3's numbers. Launcher: `run_training_v4.sh`.

**Practice run in the cloud** [measured]: a full small run — trained, killed mid-run, resumed from its last save, finished with every network levelled off, then the confirmations, the audit (10 checkpoint audits, 0 replay problems), the held-out test and REPORT.txt. Re-running any finished step correctly skips it; changing one network's weights behind the report's back makes only that network's audit redo itself, and leaves the other four alone. Small-practice scores mean nothing about strength.

**Speed** [measured, cloud]: on two cores the per-deck trainer ran about a third slower than run 3's single network (15–16 vs 22 games/s) with the encoding itself proven not to blame (579 vs 577 decisions/s); five sets of weights being copied to the workers is the cost. Lazy refreshing (only the two decks in play, only the network that trained) is in. The pilot on the laptop is what measures the real number, on eight cores.

**The one-deck pilot** (next after Astra's review), in WSL, about an hour:
`RUN=runs/pilot-v22-blaziken bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v4.sh" --override "$(cat pilot_v4_settings.json)"`
As built it trains the Blaziken network against Lucario only, to 300,000 games, floors off — the same pairing as run 2's pilot, which is the thing it is meant to be compared against (run 2 matched k3 by 25,000-50,000 games of that pairing and passed at 250,000). **Open for Fable:** the design page says "against the pool", which would instead mean all five networks training together and stopping early to look at Blaziken; that gives Blaziken only about 25,000 games of each matchup in the same hour, and no clean comparison with run 2. Changing it is one line of the settings file.

## Re-running the tests
- Encoding v2 checks (add-on 0.4.0, ~2 min): `python "Boss Folder/rl-feasibility-2026-09-18/v2_checks.py"` from the project root, in an environment with `wheels/run2/pdl_rl_env-0.4.0-…whl` installed. It writes `results/v2_checks.txt`.
- Speed, in WSL (~4 min): `bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_wsl_speed.sh"`. It installs the add-on in its own Python environment, then writes `results/wsl_speed.log` and `results/step2_<machine>.json`.
- The others, from the project root with that environment's Python: `step1_random_check.py`, `step1b_k3_replay_check.py`, `step3_learning.py`, `step3_gap_check.py`.
- If the add-on won't install, build it: `cd "Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env" && maturin build --release -o ../wheels`.


## Astra's training-code review — September 18, 2026

**Ready for the approved laptop run after corrections.** This review covers the training program and its records, not playing strength or a new engine-rules certification. The learning settings, opponents, evaluation counts, thresholds and 5M-game budget remain as approved.

Corrections made before launch:
- **Interrupted saves:** weights are immutable per save and referenced by the atomically committed state, so an interrupted checkpoint cannot pair newer weights with an older game count. Resume restores the committed opponent pool, separates interrupted logs/checkpoints, reserves a fresh seed range before workers start, and checks input/settings identity.
- **Evaluation pauses:** every worker sends a numbered acknowledgment through the same queue as its completed games. Evaluation waits for all acknowledgments, accounting for all earlier game messages. Shared game reservations keep checkpoints and the final budget exact.
- **Worker failure:** dead training workers stop the run with a resumable error. Evaluation workers now exit when the trainer is killed; a real SIGKILL test caught the orphan-process case that the built-in simulated crash did not exercise. Evaluations also have a generous timeout (at least 20 minutes) for lost tasks.
- **Move reuse after resume:** an empty buffer starts with zero training credit; old deficits cannot be repaid by overusing new rows. The displayed reuse rate is an average, not a promise that every individual row was sampled.
- **Design/reporting details:** exact score ties only; every turn-limit game counts toward the cap-draw rate; per-seat win/loss/draw counts for each evaluation opponent; both the best checkpoint and a close runner-up get confirmation even if the first passes. Duplicate trainers are refused. The launcher preserves failure exit codes and fixes each process to one math-library thread.

**Verification: 22 targeted checks passed**, including repeated crash/resume with a changed worker count; failure between weight and state writes; checkpoint/log recovery after a real SIGKILL during evaluation; worker death and cleanup; exact game budgets; training-credit isolation; draw/floor/budget/pass stops; both confirmation candidates; and duplicate-run/settings guards. All **56 recorded evaluation games** in the final small confirmation test replayed exactly from their saved moves. An independent focused review of the pause, credit, recovery and process-lifetime changes found no remaining issue after the timeout was increased. Test scores are not strength evidence.

The repository-requested older `run_records_selftest.py` also ran: it has 15 failed assertions/subtests because its temporary fixture omits `current_engine.py`, plus one intentionally skipped real-engine test. That fixture and its separate runner are unchanged and are not imported by `train.py`; this is an outstanding unrelated test failure.

Original/reviewed source, hashes, small-test logs and assertions are preserved in `results/training-review-20260918.zip`. Temporary test checkpoints were kept separate from the real run. The real run writes `runs/brew03a-01/STATUS.txt`; checkpoint 0 is evaluated before any training games.

**Laptop launch verified:** September 18, 14:04 CDT; eight workers, approved settings, power connected, AC sleep and hibernation already disabled. Baseline evaluation completed (400 k3 games, 200 random games), and all eight training workers plus the trainer are active. The background run continues independently of this task. STATUS initially shows the 0-game baseline until the 100,000-game checkpoint; that initial 0.0 reuse value is not a throughput measurement.
