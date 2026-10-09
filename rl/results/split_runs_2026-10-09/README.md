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
  - writes one merged `games.jsonl` in the harness's own game order, each line exactly as its worker wrote it, and a `MERGE_RECORD.md`
    (which worker played what, with which build, and every gap). It exits 0 only when the merge is complete and clean.
- **A worker's build hashes have to be written down by the worker.** Game records don't carry them, so each worker stamps its folder first
  (`split_collect.py stamp`, a `worker.json`).
- **A rebuilt program.** A Sonnet or Haiku cloud that builds the harness itself will usually get another sha256 than the laptop's build
  (`build.sh`: "the same bytes need the same machine setup"). The stamp replays the manifest's 12-game self-check, as `slow_report.py`
  does for a rebuild. A rebuild counts only when every self-check digest line equals the manifest's; the merge record says so, as a note.
- **The proof:** PROOF_RESULT

## The proof (`run_proof.sh`, output in `proof_output.txt`)

PROOF_DETAILS

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
- `../../strength/test_split_collect.py`: its 29 tests. `tests_before_collector.log` (before the collector existed),
  `tests_before_rebuilt.log` (the 4 tests for a rebuilt program and the engine tree, 3 failing before), `tests_after_collector.log`
  (29 of 29).
- `run_proof.sh`, `proof_output.txt`: the proof.
- `registration/`: the proof's registration (`manifest.json`, `manifest.sha256`).
- `proof/`: the merged and the straight `games.jsonl`, the merge records (both workers; worker 1 alone) and the three stamps.
