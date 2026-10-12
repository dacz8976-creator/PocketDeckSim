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
- **Check:** at every deck-side decision, the turn and the number of legal moves must be the logged ones. At the end, the points,
  turns and winner must be the recorded ones.
- **Output:** one line per deck-side decision, with the legal moves, whether any was an attack, the move taken and whether it was an
  attack.

`skip_exact.py` reads those lines and makes the comparison. It stops unless every game of every bot replayed exactly.

## Run it

`bash run_skip_exact.sh <scratch folder>`, from anywhere in the repository. It takes about 25 minutes:
- it checks the deck files against both manifests;
- it builds the program twice:
  - on 172cbe9c, the combined run's source, engine tree 69a5a441;
  - on d513e37b, the development run's source, engine tree 31dbd2e6;
- it replays the candidate's 560 games, km3's 560 and the frozen kx3's 560;
- it also replays the development run's km3 games on the frozen build;
- it runs the negative control and the comparison.

## Results (Oct 12)

- **The replay check:**
  - all 560 games of each bot replayed exactly (`run_output.txt`);
  - km3's decisions are byte for byte the same on both builds.
- **The negative control** (`negative_control.txt`): 20 candidate records, each with its first logged attack changed to EndTurn.
  - 18 are caught (a later decision's legal moves no longer match the log).
  - 2 are not: there the change left every recorded field the same.
  - The first run used a weaker control: one 4-decision game whose change altered nothing recorded. It was not caught (see
    `run_output.txt`), so the script now uses the 20-record control.
- **Tests:** `test_skip_exact.py`, 11 tests.
  - `tests_before.log`: they fail before `skip_exact.py` existed.
  - `tests_after.log`: 11 of 11 pass.
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
