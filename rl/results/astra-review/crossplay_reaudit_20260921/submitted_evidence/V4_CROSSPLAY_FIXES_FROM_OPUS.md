# Frozen-checkpoint test — your four corrections and the notes (Opus, September 21)

Reply to `V4_CROSSPLAY_REVIEW_20260921.md`. `crossplay_v4.py` is rewritten rather than patched; the version
you reviewed (`add097af…`) is kept as `results/crossplay_v4_design/crossplay_v4.as_reviewed.py`. No real run-4
games have been played. The trainer, launcher and engine are untouched, and run 4 carries on unchanged.

## 1. Interpretation — accepted, and the whole framing changed

Your counterexample is right, and I reproduced it with the script's own analysis: two styles moving on a fixed
cycle, never reacting to each other, give D +1.41 log-odds with an interval far from zero
(`test_analysis2.out`, case 1). So the step now **describes and does not decide**.

- The docstring and the output both say, first, that this is a description of this run's trajectory in a
  pairing chosen because it swung, and that it does not identify a cause. They name the intervention that
  would (training one side against a frozen opponent) as a run-5 question.
- **D is called the checkpoint-age pattern.** The output says: chasing would make it positive, but so do
  styles that change independently in a matchup that isn't simply stronger-beats-weaker; and near zero
  doesn't rule out adaptation on a different time scale.
- The 1–2 window is fixed in advance and described as checkpoint-age proximity, not a record of which
  opponents a network met.
- The strength-vs-k3 correlation says general improvement produces it as well as drift. The change
  correlations say they describe movement, not mechanism.
- Every interval is stated as covering evaluation noise for these fixed checkpoints only: not run-to-run
  variation, and not confidence in a cause. No verdict across pairings.
- **The sensitivity claim is withdrawn.** One small-effect case wasn't a power study, and I haven't run one;
  nothing in the script or this note claims a detectable effect size.

## 2. Runtime identity and cache — fixed

The script now **refuses** unless every entry in the run's `identity.json` matches the current bytes:
engine add-on binary, trainer, model, observation wrapper, all pool and held-out decks, Python and numpy. A
different engine is a separate experiment, as you said. The cache key holds that full runtime identity, plus
the settings file's hash, the script's own hash, every checkpoint's hash, the saved checkpoint evaluations,
the game count, the seed base and both fixed windows.

Tested one input at a time on the practice run (`practice2.log`):
- add-on binary, `model.py`, `pdl_env.py`, `train_v4.py` or a deck file changed: **refused**, with the
  saved result untouched;
- `crossplay_v4.py`, the run's `settings.json`, a checkpoint file or the game count changed: **redone**, with
  the previous result kept;
- everything restored: reused.

The add-on test changed the real installed binary by one byte, then restored it and checked the bytes.

## 3. Individual games saved — fixed

Each result file now holds `outcomes[i][j][k]`: W, D or L from X's side, for every cell and every seed. The
file also states which seed game k used and which seat X sat in. Every statistic is computed from those
outcomes by one function, `analyse()`, and the practice run checks that re-running it on the saved file
reproduces the saved statistics exactly, for both pairings. Wins, draws and losses are counted separately.
The headline is labelled **"score = wins + half the draws"**, with a note that the k3 reports count wins
only. Your same-averages point is reproduced as case 4.

## 4. Interrupted and damaged output — fixed

- A result is written to a temporary file, flushed to disk, then swapped in whole, so a partial file never
  sits at the real path.
- The previous result is copied aside only **after** the new one is complete, so a failure during the games
  leaves the old file exactly as it was.
- A file that isn't valid JSON is renamed aside as `.damaged-…` and the pairing is redone; `--redo` no
  longer reads it first.
- A leftover temporary file from a killed write is cleared.

Tested: the process killed mid-games (SIGKILL) leaves the saved result byte-identical, and the retry
completes. A truncated file on a plain retry, and an unparseable one with `--redo`, are both set aside and
redone, with the damaged copies kept. A stale temporary file is ignored and removed.

## Your further notes — all taken

- **The best-of forgetting comparison is gone.** It's replaced by one fixed in advance: X's last checkpoint
  against Y's three oldest, minus the mean of *all* X's earlier checkpoints against them. With every
  checkpoint equally strong it averages +0.28 points over 100 trials, against +3.94 for the best-of. Its
  interval excluded zero 4 times in 100, so if anything it's conservative (case 3).
- **Validation before any worker starts:** the game count must be even, positive and inside the seed block;
  there must be at least 4 scored checkpoints; and the run must be finished. All three are tested, as are a
  held lock, a RUNNING run and a deck paired with itself.
- **The bootstrap resamples within each seat** (even and odd seeds separately), with the same draw in every
  cell, so the fixed 200/200 seat design holds. Under additive drift, D's interval excluded zero 12 times in
  100. I report that as consistent with the nominal 10% (the binomial range is roughly 5–15), not as a
  validation of it (case 2).
- **Selected pairings:** the output's first line says so.
- **Evidence bound to source:** `practice2.log` and `test_analysis2.out` each start with the sha256 of the
  script they tested, and both were run on the final file.
- **Fable's two presentation changes are in:** the change correlations from the saved evaluations come first,
  and the 1-in-10 rate is stated in the output.

## Results

- Practice run on real games (`practice2.*`): **42 of 42 explicit checks pass**, and the run's `state.json`
  is byte-for-byte unchanged. Checkpoints run 1k–20k, both approved pairings, 2–6 games a cell. The practice
  numbers mean nothing; the run exercises the mechanics only.
- Synthetic analysis checks: `test_analysis2.*`, five cases as above.
- Two mistakes of mine during testing, both in the test driver, not the script: it first omitted `--run`,
  and it first expected the 2-game baseline not to replace the 4-game result. Both are corrected; the log
  above is the clean run.

## When it runs

After run 4's reports, on the laptop, under the run's own pinned runtime; the script refuses anything
else. The command is at the top of the script. The real game time is untested for this script on the
laptop; your "estimate, not a guarantee" stands.
