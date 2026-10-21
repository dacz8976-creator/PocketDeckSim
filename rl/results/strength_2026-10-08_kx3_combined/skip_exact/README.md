# skip_exact: the identity replay behind SKIP_ATTACK_EXACT.md (the cloud, Oct 12)

Asked by Fable (direct route, Oct 12): the exact attack-skipping measure of the combined run, built as an identity replay of the
recorded games, not a re-run. The results and how to read them are in `../SKIP_ATTACK_EXACT.md`. This folder holds how it was made.

## How it works

`skip_replay.rs` is an example program. It is built in a copy of the source of the program that played the games; nothing in the
engine or the players changes. For each recorded game it does the following:
- **Rebuild:** the game is set up as the strength harness set it up, with the same seed, the same seats and km3 by its code.
- **Play:** the opponent's km3 plays itself. The deck side plays the moves its log records, each found among the legal moves by the
  harness's own move label. A label that fits more than one legal move is tried each way until the rest of the log and the ending
  agree.
- **Check:** at every deck-side decision, the turn, the number of legal moves, the points, the Active and the Bench count must be
  the logged ones. At the end, the points, turns, winner, plies and the opponent's number of decisions must be the recorded ones.
- **Output:** one line per deck-side decision, with the legal moves, whether any was an attack, the move taken and whether it was an
  attack.

`skip_exact.py` reads those lines and makes the comparison. It stops unless every game of every bot replayed exactly.

## Oct 12: km3's proposal, the boards, the laptop's review

**Not the pre-registered measure on its own.** The turn-level count (a legal attack and none made) is not what the pre-registration
asked for. It asked for turns where km3 proposed an attack and none followed. That count now exists, from the column below: candidate
8, frozen kx3 8 (the development run's scan also found 8; the turn-level count is 73), km3 0.

**km3's proposal** (`--km3`; `--km3-all` in km3's own games).
- At each of the bot's decisions with a legal attack, km3 is asked for its move. The answer is written as `km3_move` and
  `km3_attacked` on the decision line, and summed per turn in `skip_turns.tsv`.
- **How the decision seed is reproduced:**
  - The engine gives each decision its own search seed, from the seat and that seat's decision number
    (`GameRandomness::decision` in `play_tick`, game.rs at 172cbe9c and d513e37b). That seed is separate from the shuffles and coin
    flips.
  - The replay asks the bot's side exactly the decisions it was asked in play, in the same order. So the seed `play_tick` hands to
    the scripted side is the one the bot got there.
  - km3 is given a copy of it, with the same observation and the same legal moves.
  - km3 keeps no memory between decisions (its player holds only its settings), so its answer is the move it would have made there
    in play.
- **Proof:** in km3's own games, km3 is asked at every decision, and its answer equals the move it played at all 15,355.

**Ambiguous labels, resolved by the pilot.**
- Where a logged label fits more than one legal move, the replay now asks the pilot that played, by the code in the record, built
  as the harness builds it. It is asked with the same observation and seed. kx3 keeps no memory between decisions either (its
  `Core` holds its deck, the candidate lists and settings).
- All ambiguous labels were resolved this way (`ambiguous_resolved_by_pilot` in `check_*.jsonl`; `ambiguous_unresolved` is 0
  everywhere). `skip_exact.py` refuses a game matched only by trial.
- Before this, the replay tried options until one fit the log: 130, 134 and 131 games, with retries in 68, 71 and 75. In km3's
  games that gave 18 decisions in 10 games where km3's answer differed from its recorded move, which is how the problem showed up.
- The 217 skip turns are unchanged, row for row.

**The identity check now also compares** each logged decision's points (`p`), Active (`act`) and Bench count (`b`), and each game's
plies and the opponent's number of decisions (`moves_opp.n`).

**Negative controls** (`negative_control.txt`): 2 records per deck and arm, candidate, km3 and frozen kx3 (42 records). Each is
changed one way:
- a wrong seed: 42 caught;
- one logged label swapped for another from the same game: 42 caught;
- a wrong opponent pilot (km2): 39 caught. The record holds only how many decisions the opponent made, not which moves, so a km2
  that plays like km3 in a game can't be seen (3 games).

**The boards** (`skip_boards.jsonl`, `--boards skip_turns.tsv --bot NAME`).
- **What each record holds:** one record for each of the bot's decisions in each skip turn (1,139 for the 217 turns), taken from
  the true game state just before the decision:
  - **ours and theirs:** Active and Bench, each with name, `hp` / `max_hp`, Energy, Tools and Special Conditions;
  - **our side:** `hand` (card names) and `deck_count`;
  - **the turn:** `points` (ours, theirs), `turn`, the `legal` moves, the one `taken` and `km3_move`;
  - **`our_attacks`:** each legal attack's cost, printed damage and forecast against their Active;
  - **`their_active_attacks`:** their Active's attacks, with cost, printed damage and the forecast against our Active.
- **The forecast** is the engine's own.
  - `try_forecast_action` gives the attack's branches with their probabilities; in play, `apply_action` samples one of them.
  - Each branch is applied to a copy of the board. Any choices it queues are resolved with the first one offered: for example, a
    damage target or a discard.
  - The damage is read off the target Active.
- **What a forecast reports:**
  - `expected_damage`: the probability-weighted HP lost, so it is capped at the HP the target has left;
  - `ko_chance`: the chance of a Knock Out;
  - `branches`.
- **For their attacks,** the forecast is made as if they attacked from this board now. It doesn't play out our turn, their draw,
  or whether they will have the Energy (their Active's attached Energy is in the record, beside each attack's cost).
- All 1,736 forecasts were made; the engine refused none.

## Run it

`bash run_skip_exact.sh <scratch folder>`, from anywhere in the repository. It takes about an hour:
- it checks the deck files against both manifests;
- it builds the program twice:
  - on 172cbe9c, the combined run's source, engine tree 69a5a441;
  - on d513e37b, the development run's source, engine tree 31dbd2e6;
- it replays the candidate's 560 games, km3's 560 and the frozen kx3's 560;
- it also replays the development run's km3 games on the frozen build;
- it runs the negative controls and the comparison;
- it replays the games a second time, writing the boards at this run's skip turns.

## Results (Oct 12)

- **The replay check:**
  - all 560 games of each bot replayed exactly (`run_output.txt`);
  - km3's decisions are byte for byte the same on both builds.
- **The negative controls:** see the Oct 12 section above.
  - Earlier, a first-attack-to-EndTurn control on 20 candidate records caught 18. Before that, a single 4-decision game wasn't
    caught, because its change altered nothing recorded.
- **Tests:** `test_skip_exact.py`, 21 tests.
  - First job: `tests_before.log` (failing before `skip_exact.py` existed) and `tests_after.log` (11 of 11).
  - km3's proposal: `tests_before_followup.log` (7 failing) and `tests_after_followup.log` (18 of 18).
  - The laptop's review: `tests_before_review.log` (failing) and `tests_after_review.log` (21 of 21).
  - No engine or harness code changed, so the engine suite isn't affected.

## Files

- `skip_replay.rs`: the replay program.
- `skip_exact.py`, `test_skip_exact.py`: the comparison and its tests.
- `run_skip_exact.sh`, `run_output.txt`, `negative_control.txt`: the run.
- `check_<bot>.jsonl`: each game's replay check.
- `decisions_<bot>.jsonl.gz`: every deck-side decision.
- `exact_summary.txt`: all the rows (overall, per group, per deck; decision and turn level).
- `skip_turns.tsv`: the skip turns, for a hand check.
- `skip_decisions.tsv.gz`: the skip decisions.
- `skip_boards.jsonl`: the boards at every decision of the skip turns.
