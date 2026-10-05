# Does km3's continuation hide good first moves? (the cloud, Oct 5)

Set by the Fable coordinator via Dustin, Oct 5: "does km3's continuation of the play-outs hide good first moves?"
- **The positions and plans** are the laptop's (`../kx3_examples_2026-10-04/CONTINUATION_POSITIONS.md`).
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **The code.**
  - The plan continuation is a diagnostic option beside the play-out pilot: `engine/src/players/playout_plan.rs`, and
    `continuation_study` in `playout_player.rs`.
  - Its tests are `engine/tests/playout_continuation_test.rs`; the runner is `engine/examples/playout_continuation.rs`.
- **What it doesn't touch.**
  - kx3's own decisions, km3, `mod.rs` and the rest of `engine/` are unchanged.
  - No table game was played.

## In short

- **Mostly no.** With the intended plan played out instead of km3, the plan's first move overtakes kx3's move at only 2
  of the 8 positions.
  - **Position 6 is a real case.** km3's own later Elegant Cape on the Active Ninetales ex makes "bench the Vulpix" lose
    all 128 play-outs. Without it, the move edges past kx3's Binding Snow: +0.020 [+0.003, +0.036]. That is real, but
    small, in a nearly lost game (0.13 v 0.11).
  - **Position 1 only counts by the rule.** The Water on the Vulpix leads only inside the plan, +0.055 [+0.005, +0.105].
    The plan's whole line is weaker than km3's own continuation from either first move (0.70 and 0.64 v 0.77 and 0.78).
    So there is no better line for kx3 to find there.
- **Elsewhere the plan isn't better in these worlds.**
  - At positions 2 and 4 the two first moves are the same game in another order. They score the same in every round,
    either way.
  - At position 3 the game is won either way.
  - At position 5 the plan's first move is clearly worse, either way: −0.24.
  - At position 7, kx3's Misty leads under km3's continuation (+0.297). Under the plan's continuation it falls below
    Cyrus. The plan's turn 20 ("keep the lock with Binding Snow") loses every play-out where km3 instead switches to a
    Mega for Turbo Shark.
  - At position 8, the control, the plan's first move leads under both continuations (+0.062 under km3's). So km3's
    continuation doesn't hide it. kx3's 16 play-outs simply can't see a lead that small.
    - At 128 play-outs kx3 itself prefers End Turn there (+0.102 over Copycat). That turn has no Copycat either.
- **A pattern in what the scripted plan does against km3's own continuation from the same first move.**
  - Where it **kept** an Active or an attack that km3 would switch away from, it lost: positions 1, 2 and 7.
  - Where it won (+0.19, +0.13 and +0.08), the main difference in the traces is a Trainer km3 plays later and the plan
    doesn't: Copycat at positions 4 and 8, Elegant Cape at 6.
    - At 4 the gain is the same after either first move, so it changes no choice.
    - At 8 it comes on top of a lead km3's continuation already shows.
- **Item 4 is not triggered.** The plan's continuation doesn't win on most positions, so no change to the play-out policy
  is proposed. The evidence argues against a "stick to the opening intention for K turns" rule: sticking cost value at
  3 of the 8 positions. If anything it points at km3's Trainer play late in the play-outs. That would be a separate,
  bounded check, and it isn't run here.
- **The plans were run twice.**
  - Run 1 scripted "keep the Active" without a condition. At position 2's turn 14, that stopped km3 from starting the lock
    in the 85 rounds where the plan's turn 12 couldn't evolve the Vulpix.
  - Run 2 keeps a named Pokémon Active only while it is the Active. It changed position 2 alone: the plan went from −0.31
    to −0.05 against km3's continuation. The other seven positions reproduced run 1 round for round.
  - Both runs are kept here; run 2 is the result.

## The question

kx3 plays each candidate move out to the end of the game with km3 on both sides. km3 plays every later turn of every
play-out, so a first move whose value lies in a plan several turns long (build a Benched attacker, keep a sacrificial
Active, promote the armed one) is only worth what km3 makes of it. The examples suggested km3 sometimes spoils such a
move later, so kx3 never sees it. This experiment tests that directly: the same first move, continued by km3 and by the
intended plan.

## What was run

- **The positions.** The laptop's eight in `rl/results/kx3_examples_2026-10-04/CONTINUATION_POSITIONS.md` (main 2c689e83).
  - All are draft A against the computer deck (Mega Blastoise ex / Wailord ex), exact lists, Soothing Shore in play.
  - Each state is the position runner's own build at seed 1: `pg_pos.rs` from `pause_games_decisions_2026-10-02/harness`,
    with `pg_pos_dump.patch` (it writes the built state and stops). All eight built with no problems.
  - The runner's copies of both lists match `decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt` (3f39092b…) and
    `decks/computer/blastoise-wailord-deluxe.txt` (168a42d0…) byte for byte.
- **Two first moves per position.**
  - The plan's first move.
  - A rival: kx3's own move in the laptop's trace at seed 1 (`playout_pilot_positions_2026-10-04/runs_kx3_trace`).
  - Position 7 is the other way round, as the laptop set it. The plan is kx3's line (Misty), and the rival is the move of
    Auto and km3 (Cyrus).
- **Two continuations of each.**
  - *km3's:* the play-out exactly as kx3 plays it.
  - *The plan's:* for the pilot's next K own turns the plan is played, then km3. The opponent is km3 throughout.
- **The same worlds.** Round j of every first move and both continuations starts from the same sampled world and game
  seed, the ones kx3's `evaluate` would use at the same decision. A test proves the study's km3 numbers are kx3's own.
- **What the opponent's hidden cards come from.** LAB: the computer deck's exact list, which is in the wide pool. The
  laptop's REALISTIC run used the same list in effect: it was the one consistent list ("1 of 1 consistent") in every
  round.
- **R = 128 rounds per position.** Seeds: position i (0–7, in `plans.json`'s order) uses decision randomness
  24,200,001,000 + i. That is inside the play-out pilot's registered block.
- **kx3's own trace line at each position.** Same seed, same 128 rounds, LAB (`run/kx3.jsonl`). It shows every legal
  move's km3-continuation score. For the two moves studied, those scores equal the study's km3 column: the summarizer
  checks this.

## The plan continuation

The code is `engine/src/players/playout_plan.rs`. A plan gives each of its K own turns:

- **Steps, in order, written by intent.** A step names Pokémon, never action indices, because draws and coins differ
  between worlds. The kinds are:
  - the turn's Energy to a named Pokémon;
  - an extra Energy from an effect (Turbo Shark's) to one;
  - evolve; bench; play a Trainer;
  - a target (Misty's, a Tool's);
  - retreat to a named Pokémon;
  - attack.
- **How steps are played.**
  - At each of the pilot's decisions, the first pending step that is legal is played.
  - A step that isn't legal yet stays pending, because a draw may bring its card.
  - When no step is legal, km3 decides that move. It chooses among the moves the turn's rules leave:
    - `avoid`: Trainers by name;
    - `keep_active_if`: no retreat while a Pokémon it names is the Active;
    - if the rules leave no move, every move is allowed.
  - The plan's attack is played when km3 would end the turn.
  - So km3 fills in what the plan doesn't name (a draw, a heal, a Bench), and the plan decides what it does name.
- **Turn 0's steps start with the plan's first move.**
  - In the plan's first-move run, the first move is that step.
  - In the rival's run, that step stays pending and is played if it becomes legal that turn. That is, "kx3's move, then
    the plan".
- **Skips.** A step still pending when its turn ends is counted as *skipped*: km3 decided in its place. A step whose turn
  the game never reached is counted as *unreached*. Both are reported per step.
- **Promotion.** Within the K turns, when the Active falls, the first Pokémon in play named in the plan's `promote` list
  is promoted.
- **K = 0 gives km3 exactly.** With K = 0 the pilot's side is km3 itself, final state for final state. That is tested;
  see "Checks".

**How the plans were transcribed** (`plans.json`). The laptop's steps were scripted as written, with these readings:

- "The Vulpix" in an extra-Energy step also means its Alolan Ninetales ex. km3, filling in, sometimes evolves the
  Vulpix before the plan's turn, and the Energy should still follow it.
- Copycat is avoided in position 4's turn 12 ("evolve that Vulpix into the Alolan Ninetales ex kept in hand": Copycat
  would shuffle it away). It is also avoided in position 8's turn 2: the recorded line is the Water, then Sharp Fang.
- `keep_active_if` names the Pokémon on each turn the plan keeps it in front:
  - the Mega Sharpedo ex: position 1's turns 6 to 10, position 2's turn 10, position 3's turn 8;
  - Lapras: position 5's turn 14;
  - the Alolan Ninetales ex: position 6's turn 16, position 2's turn 14, position 7's turn 20.
- Every plan promotes Alolan Ninetales ex first, then Mega Sharpedo ex.
- Every name and attack in the plans is checked against draft A's list before anything runs.

## Results (run 2: `run/study.jsonl`, `run/summary.txt`)

Scores are the pilot's (win 1, tie ½, loss 0). Each mean is over 128 rounds; brackets are 95% intervals of the paired
differences.
- *Lead* is the plan's first move minus the rival, in the same worlds.
- *Change* is the lead under the plan's continuation minus the lead under km3's.

| # | Position | K | The plan's first move: km3 / plan | The rival: km3 / plan | Lead, km3's continuation | Lead, the plan's | Change | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | B-214254-t06 | 4 | the turn's Water to the Benched Vulpix: 0.766 / 0.695 | Turbo Shark (kx3, km3): 0.781 / 0.641 | −0.016 [−0.059, +0.028] | +0.055 [+0.005, +0.105] | +0.070 [+0.008, +0.133] | hidden, by the rule; but see below |
| 2 | B-214254-t10 | 3 | Lucky Ice Pop: 0.730 / 0.680 | Irida (kx3, km3): 0.730 / 0.680 | 0 (every round) | 0 (every round) | 0 | no difference |
| 3 | B-205731-t08 | 2 | evolve the Benched Vulpix: 1.000 / 1.000 | retreat into the Vulpix (kx3, km3): 0.992 / 0.992 | +0.008 [−0.007, +0.023] | +0.008 [−0.007, +0.023] | 0 | no difference (won) |
| 4 | B-205731-t10 | 2 | bench the Vulpix: 0.539 / 0.727 | retreat into the Ninetales ex (kx3, km3): 0.539 / 0.727 | 0 (every round) | 0 (every round) | 0 | no difference |
| 5 | B-210952-t14 | 2 | bench Carvanha (km3's): 0.031 / 0.031 | retreat into the Ninetales ex (kx3): 0.266 / 0.273 | −0.234 [−0.286, −0.182] | −0.242 [−0.295, −0.189] | −0.008 [−0.019, +0.003] | worse |
| 6 | B-210952-t16 | 2 | bench the Vulpix (km3's): 0.000 / 0.133 | Binding Snow (kx3): 0.113 / 0.113 | −0.113 [−0.150, −0.077] | +0.020 [+0.003, +0.036] | +0.133 [+0.094, +0.171] | hidden |
| 7 | B-210952-t18 | 2 | Misty (kx3's): 0.430 / 0.000 | Cyrus (Auto, km3): 0.133 / 0.133 | +0.297 [+0.245, +0.348] | −0.133 [−0.171, −0.094] | −0.430 [−0.502, −0.358] | worse |
| 7′ | the same, K = 1 | 1 | Misty: 0.430 / 0.262 | Cyrus: 0.133 / 0.133 | +0.297 [+0.245, +0.348] | +0.129 [+0.071, +0.187] | −0.168 [−0.226, −0.110] | ahead either way |
| 8 | B-205731-t02 | 1 | the turn's Water to the Active Carvanha: 0.789 / 0.867 | Copycat (kx3, km3): 0.727 / 0.727 | +0.062 [+0.015, +0.110] | +0.141 [+0.044, +0.237] | +0.078 [−0.008, +0.164] | ahead either way |

**The verdict rule.** It was fixed in the runner before the runs (`verdict()` in `playout_continuation.rs`):
- *hidden*: under the plan's continuation the lead's interval is above 0, and under km3's the lead is 0 or less;
- *lifted*: the change's interval is above 0;
- *worse*: the lead under the plan is below 0 beyond noise;
- *ahead either way*: the plan's first move leads beyond noise without the change being beyond noise;
- else *no difference*.

**The plan against km3's continuation from the same first move** (plan minus km3; the plan's first move, then the rival):

| # | The plan's first move | The rival |
|---|---|---|
| 1 | −0.070 [−0.158, +0.017] | −0.141 [−0.224, −0.057] |
| 2 | −0.051 [−0.095, −0.006] | −0.051 [−0.095, −0.006] |
| 3 | 0 | 0 |
| 4 | +0.188 [+0.113, +0.262] | +0.188 [+0.113, +0.262] |
| 5 | 0 | +0.008 [−0.003, +0.019] |
| 6 | +0.133 [+0.094, +0.171] | 0 |
| 7 | −0.430 [−0.502, −0.358] | 0 |
| 7′ (K = 1) | −0.168 [−0.226, −0.110] | 0 |
| 8 | +0.078 [−0.008, +0.164] | 0 |

**How often the scripted steps could be played.** This is out of 128 per step; the full table is in `run/summary.txt`.
- Steps that need a card the deck has to supply were often skipped, and km3 decided in their place:
  - position 1's turn-8 evolution of Carvanha: 18 played;
  - its turn-12 evolution of the Vulpix: 31 played (km3 had often evolved it already, which the plan allows);
  - position 2's turn-12 evolution: 44 played;
  - position 3's turn-10 second Vulpix: 34 played;
  - position 5's turn-16 Vulpix: 78 played.
- Every other step of the plans' own turn 0 was played in all 128 rounds, after the plan's first move. After the rival,
  the steps the rival made impossible were skipped (e.g. position 7's Misty after Cyrus: 128 skipped).
- No round failed, and no plan attack ever replaced a different turn-ending move of km3's. Where km3 ended the turn, it
  was with the plan's attack, or the plan's attack wasn't legal.

## Per position, with the trace lines

The trace lines are round 0's pilot moves within the K turns, under each continuation (`round_0_*_trace` in
`run/study.jsonl`; all of them in `run/summary.txt`). km3's line comes from a plan of K empty turns, which plays exactly
as km3 does: its final state equals km3's play-out's at every position, and a test checks this.

1. **B-214254-t06** (the Water first, then Turbo Shark three turns, then the lock).
   - Under km3, the two first moves are equal (−0.016).
   - Under the plan, the Water leads (+0.055). The plan keeps the Caped Mega Turbo Sharking on turns 8 and 10 and switches
     on turn 12 to the Pokémon the Water went to.
   - But km3's own line is better from either first move. It retreats into the Vulpix on turn 8 and locks with Binding
     Snow from then on.
     - Plan: `t8 plan: attack Turbo Shark | t10 plan: attack Turbo Shark | t12 plan: retreat into the Benched Alolan
       Ninetales ex | t12 plan: attack Binding Snow`.
     - km3: `t8 km3: retreat into the Benched Alolan Vulpix | ... | t8 km3: evolve the Active Alolan Vulpix into Alolan
       Ninetales ex | t8 km3: attack Binding Snow | t10 ... attack Binding Snow`.
   - **Not a hidden good move.** The first move matters only inside a plan that is worse than km3's own play.
2. **B-214254-t10** (Lucky Ice Pop or Irida first).
   - The two orders end in the same game in effect. Their scores are equal in every round under both continuations.
   - The plan's turn 12 (draw first, evolve, retreat, lock) is slightly below km3's own continuation: −0.051.
   - kx3 "changed nothing at any of its 14 decisions here", and there was nothing to change.
3. **B-205731-t08** (keep the Mega in front and evolve on the Bench, or retreat now). Won either way, 1.000 v 0.992. km3's
   own continuation after the evolution retreats at once anyway: `t8 km3: retreat into the Benched Alolan Ninetales ex`.
4. **B-205731-t10** (bench the Vulpix first, or retreat first).
   - The same game in another order. Under the plan the two end in the same final state in all 128 rounds.
   - The plan's continuation is +0.188 above km3's after **both** first moves. The plan avoids Copycat; km3 plays it on
     turn 12 (`t12 km3: play Copycat | t12 km3: bench Lapras`).
   - This lowers kx3's estimate of both moves alike, so it hides no first move.
5. **B-210952-t14** (bench Carvanha and Surf, or retreat).
   - The plan's first move (km3's move) is clearly worse under both continuations. kx3's retreat is right.
   - The plan's continuation is km3's own here: the same final state in all 128 rounds after Carvanha.
6. **B-210952-t16** (bench the Vulpix, no Elegant Cape; or Binding Snow at once). The hiding case, as the laptop found.
   - km3's continuation plays `t16 km3: play Elegant Cape | t16 km3: Elegant Cape on the Active Alolan Ninetales ex`, and
     the Vulpix move then loses all 128 play-outs.
   - The plan withholds the Cape on turn 16 and scores 0.133, against Binding Snow's 0.113 (+0.020 [+0.003, +0.036]).
   - A real flip, worth about 2 games in 100 in a lost position.
7. **B-210952-t18** (Misty, kx3's denial line; or Cyrus).
   - Misty leads under km3's continuation, +0.297. Turn 18 of km3's continuation is the plan's own line in round 0, move
     for move.
   - The plan's turn 20 (keep the lock: `t20 plan: attack Binding Snow`) then loses every play-out. km3 instead plays
     `t20 km3: retreat into the Benched Mega Sharpedo ex | t20 km3: attack Turbo Shark` and wins 43%.
   - With the plan for turn 18 only (7′, the same worlds), Misty still leads Cyrus, +0.129. But the scripted turn 18 is
     itself below km3's (0.262 v 0.430). It ends as km3's does in 73 of 128 rounds; in the other 55, km3's own choices
     did better.
   - kx3's Misty is right. The plan's continuation of it is worse than km3's.
8. **B-205731-t02** (the control: the Water and Sharp Fang, or Copycat).
   - The Water leads under both continuations, so km3's continuation doesn't hide it.
   - After the Water, km3's continuation plays Copycat anyway (`t2 km3: play Copycat | t2 km3: bench Alolan Vulpix | ...`).
     The two first moves end in the same final state in 95 of 128 rounds; the lead comes from the other 33.
   - At kx3's 16 play-outs a lead of +0.06 is inside the noise: one standard error was 0.06 to 0.11 in the laptop's
     three seeds.
   - kx3 played the Water in 1 seed of 3, and there it was km3's own move. Its play-outs never switched to it.

## Run 1, and why it was rerun

Run 1 (`plans_run1.json`, `run1/`) was the first transcription. It wrote "keep the Active" as `keep_active: true`: km3,
filling in, could not retreat at all that turn.
- **The problem.** At position 2's turn 14 ("Binding Snow each turn"), 85 of 128 rounds had no Ninetales ex. The plan's
  turn 12 couldn't evolve the Vulpix. The rule then stopped km3 retreating into the Vulpix to evolve it and lock, which is
  what the plan means. That made the plan look 0.31 worse than km3's continuation.
- **The fix, made before looking at any other change.** Every keep rule now names the Pokémon it keeps
  (`keep_active_if`), and binds only while that Pokémon is the Active.
  - The rule is applied to all nine keep rules, not only position 2's.
  - A test checks the rule (`the_keep_rules_forbid_a_retreat_only_while_they_hold`).
- **Run 2's result.**
  - Position 2 is now −0.051.
  - The other seven positions are identical to run 1 round for round (all 256 play-outs each). So their keep rules
    never mattered, and the runs are deterministic.
  - Run 1's verdicts are the same as run 2's.

## Item 4: a change to the play-out policy? Not proposed

Fable's condition was "if the plan continuation wins on most positions". It flips the lead at 2 of 8, and at one of
those (position 1) only inside a line weaker than km3's own. So nothing is proposed.

For the record, what the eight positions say about the candidates named:
- **"Stick to the opening intention for K turns", or a sticky attachment target.** The evidence is against it.
  - The plan's continuation was below km3's own after the plan's first move at positions 1 (−0.070), 2 (−0.051) and 7
    (−0.430; −0.168 with K = 1).
  - Each time it held on to something km3 would change: the attacking Mega, the draw-first order, the lock.
  - It was above km3's at 4, 6 and 8, where the plan's difference was withholding a Trainer, not sticking to a target.
  - kx3's own 128-play-out line at position 8 agrees. Its best move is End Turn (0.891), a turn without Copycat. The plan's
    Water and Sharp Fang without Copycat scored 0.867. km3's Water-then-Copycat line scored 0.789, and Copycat first
    0.727.
- **What the evidence points at instead,** as an observation, not a proposal. km3's Trainer play late in the play-outs
  (Copycat, Elegant Cape) cost 0.08 to 0.19 at three positions.
  - That lowers kx3's estimates, but changed the order of the two moves only at position 6.
  - Whether it is general would take its own bounded check: km3 with those Trainers withheld in the play-outs, on the
    same worlds. It isn't run here.
- **Whatever the continuation, small leads are below kx3's threshold.** kx3 switches at 16 play-outs only on a lead over
  2 standard errors, about 0.12 to 0.3 at these positions. Position 8's +0.06 needed the 128 here.

## kx3's own decision at each position (`run/kx3.jsonl`)

kx3 here is `kx3_r128_c12_z2_lab_t0_poolwide`: kx3 at 128 play-outs, LAB, run on the study's decision randomness.
- **Its scores match the study.** At all 8 positions it scores the two studied moves exactly as the study's km3
  continuation does (the summarizer's check: "same, same"), so the study is kx3's own measurement.
- **Its choices**, with its lead over km3's move (the full candidate lists are in `run/summary.txt`):

| # | kx3 at 128 play-outs | At 16 (the laptop's seed 1) |
|---|---|---|
| 1 | Turbo Shark (km3's); the Water on the Vulpix −0.016 (SE 0.022) | the same |
| 2 | Irida (km3's); Misty +0.035 (SE 0.040), within the noise | the same |
| 3 | the retreat (km3's); everything ~1.0 | the same |
| 4 | **the turn's Water on the Active Mega, +0.125 (3.1 SE)**; the plan's bench-the-Vulpix 0.539 = km3's retreat | the retreat |
| 5 | the retreat into the Ninetales ex, +0.234 (8.8 SE) | the same |
| 6 | Binding Snow, +0.113 (6.1 SE); the plan's bench-the-Vulpix 0.000 | the same |
| 7 | Misty, +0.297 (11.3 SE) | the same |
| 8 | **End Turn, +0.102 (2.3 SE)**; the Water 0.789, Copycat 0.727 | Copycat |

The two choices that change with more play-outs are moves neither kx3 at 16 play-outs nor the plan picked. At position 8
this is the same signal as the plan's continuation: the value is in not playing Copycat on turn 2.

## Checks

On `7c3d62f6`, the last change to `engine/`. The files are in `checks/`.

- **The tests, written first.** `engine/tests/playout_continuation_test.rs` (`tests_before.log` shows them failing
  before the option existed, e48fe5ee). There are 6:
  1. **K = 0 is km3 exactly.** With K = 0, with a full plan or an empty one (and with an empty plan at any K), every
     play-out ends in the same final state, turn and score as km3's.
     - Round 0's km3 log (a plan of K empty turns) is km3's play-out too.
     - The two first moves don't always reach the same game, so the pairing is real.
  2. **The study's km3 continuation is kx3's.** At the same decision randomness, the two moves' km3 means equal their
     scores in kx3's `evaluate` report.
  3. **Steps are played, and skips are counted.**
     - At t06 with K = 4, the plan's turn-0 steps are played in every round after its first move.
     - After Turbo Shark (the rival), the Water step is skipped in every round.
     - Played + skipped + unreached = rounds, for every step.
     - The plan changes some games.
  4. **The study is deterministic.**
  5. **A misspelt plan is refused** (an unknown field, step or key).
  6. **The keep rules hold only as written** (`keep_active`, `keep_active_if`, `avoid`).
- **km3 and the official engine are unchanged.**
  - `deckgym` built from 7c3d62f6 and the official program `rl/engine-2026-10-02/deckgym` agree on all 240 per-game
    results of step 10's command, field for field (digest 9dde28db2de6c9bc).
  - Both equal the pinned record `engine_switch_rules_2026-10/5a18d31_10_cli_km3.txt` on every line but the wall time.
- **kx3's decisions are unchanged** (`play_out`, `sample_round` and `round_base` were factored out of its code).
  - The strength harness built from 7c3d62f6 prints the pinned km3 self-check, `digest=81b572198c04d5d1`.
  - It also prints the pilot's LAB self-check of every round before, `kx3_r2_c3_lab` `digest=3a2eb43bd9053639`, twice.
- **The full suite:** `cargo test --release --features test-utils` gives 2,053 passed, 0 failed. That is 2,047 before,
  plus the 6 tests here.
- **`mod.rs` is unchanged** (still its 12 added lines, Windows line endings). The new module is declared from
  `playout_player.rs`.

## Time

On this machine's 4 threads:
- the study, 128 rounds × 2 first moves × 2 continuations: 46 to 136 s a position, 12½ minutes for the eight;
- kx3's lines at 128 play-outs: 82 to 333 s a position, 27 minutes;
- the checks: 20 minutes.

## Files

- `plans.json`: the eight plans as run (run 2). Also `plans_run1.json` (run 1's) and `plans_variant_t18_k1.json`
  (position 7, K = 1).
- `states/`: the eight built states (seed 1), from `pg_pos_dump.patch` applied to the position runner.
- `run/`: run 2.
  - `study.jsonl`: one line per position, with every round's score, final-state digest and turn, both ways.
  - `variant_t18_k1.jsonl`, `kx3.jsonl` and `summary.txt`, plus the runs' stdout.
- `run1/`: run 1's `study.jsonl` and `summary.txt`.
- `summarize.py`: the table, tallies, trace lines and kx3 check (`python3 .../summarize.py [run | run1]`).
- `checks/`: the km3 replay, the self-checks and `suite.log`. `tests_before.log` is the tests failing first.
- To rerun a position, from the repository root, with the example built:
  `playout_continuation --plans <this folder>/plans.json --states <this folder>/states --deck decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt --opponent decks/computer/blastoise-wailord-deluxe.txt --rounds 128 --only <id> [--kx3]`.
