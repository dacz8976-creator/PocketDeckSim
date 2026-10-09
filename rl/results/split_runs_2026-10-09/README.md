Decision this informs: whether a registered strength run can be played by several cloud workers, each playing its own slice into its own
folder, with the merged result standing for one straight run. Asked by the Fable coordinator (direct route, Oct 9): "Build the missing piece
so several cloud workers can each play a slice into their own output folder and we can prove the result equals one straight run". Built by
the Opus cloud on `claude/pensive-ptolemy-spwc0b`; no table game, km3 untouched, not the combined run.

# Split runs: the collector, its proof and a worker's recipe (the cloud, Oct 9)

## In plain words

- **The harness already splits a run.** `strength run --only-deck NAME` plays only that deck's games of a registration, with the
  registration's own seeds (`rl/strength/src/main.rs`, the job list).
- **The new piece is `rl/strength/split_collect.py`.** It reads the workers' folders and the registration's manifest, and:
  - checks that every game the manifest expects appears exactly once, with the inputs the manifest gives it (deck, opponent, deal, seat,
    arm, seed, each side's pilot);
  - checks that each worker played this manifest (by sha256), with the registration's program (by sha256), on its engine tree, and only its
    own decks;
  - flags anything else: a missing game, a duplicate, a game with other inputs or from outside the registration, an errored game, an
    unreadable line;
  - writes one merged `games.jsonl` in the harness's job-list order, each line exactly as its worker wrote it, and a `MERGE_RECORD.md`
    (which worker played what, with which build, and every gap). It exits 0 only when the merge is complete and clean.
- **A worker's build hashes have to be written down by the worker.** Game records don't carry them, so each worker stamps its folder first
  (`split_collect.py stamp`, a `worker.json`).
- **A rebuilt program.** A Sonnet or Haiku cloud that builds the harness itself will usually get another sha256 than the laptop's build
  (`build.sh`: "the same bytes need the same machine setup"). The stamp replays the manifest's 12-game self-check, as `slow_report.py`
  does for a rebuild. A rebuild counts only when every self-check digest line equals the manifest's; the merge record says so, as a note.
- **The proof: passed.** 12 games played straight, then again as two workers (8 games and 4 games, each in its own folder). The merge is
  complete and clean, and all 12 games are the same as the straight run's, game for game. Only the timing fields and the line order
  differ. With worker 2 left out, the merge is flagged INCOMPLETE and names the 4 missing games.

## The proof (`run_proof.sh`, output in `proof_output.txt`)

- The registration: t-altaria, t-suicune and t-hydreigon against t-blaziken, 1 deal, both seats, the arms ref and X, km3 against km3
  (12 games). Seeds 20,910,000,000 + (deck index x 1,000) x 10,000, in Claude Code's diagnostic block. The program is the harness built by
  `rl/strength/build.sh` on the official engine (8626a358, engine tree 38af8b0), program sha256 `9d45a158...`. Its 12-game self-check
  digest `81b572198c04d5d1` is written into the manifest.
- The straight run played all 12 games. Worker 1 played t-altaria and t-suicune (8), worker 2 played t-hydreigon (4). Nothing errored,
  and each folder was stamped before it was played.
- `merge` of the two workers: COMPLETE, 12 of 12, 0 problems. `compare` against the straight run: EQUAL, every game with the same seed,
  winner, turns, moves and log.
- **One fix along the way.** The first run of the proof said DIFFERENT. Two games (t-suicune v t-blaziken, seat 1, ref and X) were in
  swapped lines. A straight run with 2 threads writes each game when it finishes, while the merge writes them in job-list order. So
  `compare` now pairs games by key, not by line; a key missing or repeated on either side still counts as a difference. Two tests cover
  it (`tests_before_compare_by_key.log`: 1 failing before; `tests_after_compare_by_key.log`: 31 of 31).
- The straight folder merged alone is also COMPLETE (12 of 12). Worker 1 merged alone is INCOMPLETE: 8 of 12, with the 4 t-hydreigon
  games named as missing (`proof/MERGE_RECORD_w1_only.md`).

## A worker's recipe (for a Sonnet or Haiku cloud)

You are worker NAME of the registration in `REG/` (its `manifest.json` is on main), and your slice is the decks DECKS. Reserve nothing:
the registration already holds every seed, so don't touch START_HERE's seed table or the manifest. Build the harness on the engine the
manifest names, `rl/strength/build.sh <engine ref> $HOME/strength_build/strength`, into your own scratch folder. Then stamp your output
folder, `python3 rl/strength/split_collect.py stamp --manifest REG/manifest.json --program $HOME/strength_build/strength --worker NAME
--out REG/workers/NAME --only-deck DECK ...` (it replays the 12 self-check games; if its digest line differs from the manifest's
`selfcheck`, stop and report it). Play your slice, `$HOME/strength_build/strength run --manifest REG/manifest.json --out REG/workers/NAME
--only-deck DECK ...` (the same command again resumes after a stop; it skips finished games). Commit only your folder (`worker.json`,
`games.jsonl`, `run_log.jsonl`, `errors.jsonl` if there is one) on your own branch and push it. Last, append one line to your status file:
worker NAME, slice DECKS, games played of games expected, the program sha256, the commit. The laptop merges with `split_collect.py merge`
and reviews before anything goes to main.

## Files

- `../../strength/split_collect.py`: the collector (`stamp`, `merge`, `compare`; read its docstring).
- `../../strength/test_split_collect.py`: its 31 tests. `tests_before_collector.log` (before the collector existed),
  `tests_before_rebuilt.log` (the 4 tests for a rebuilt program and the engine tree, 3 failing before), `tests_after_collector.log`
  (29 of 29), `tests_before_compare_by_key.log` and `tests_after_compare_by_key.log` (the fix above; 31 of 31).
- `run_proof.sh`, `proof_output.txt`: the proof.
- `registration/`: the proof's registration (`manifest.json`, `manifest.sha256`).
- `proof/`: the merged and the straight `games.jsonl`, the merge records (both workers; worker 1 alone) and the three stamps.
