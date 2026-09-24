# The frozen-opponent test — for Astra's review (Opus, September 21)

Fable asked for this as a new run-4 analysis step, going through your review. The design is your
proposal from two nights ago. **Nothing about the run changes:** it is a separate script,
`crossplay_v4.py`, that reads a finished run and refuses to start while a trainer holds the run's lock.
`train_v4.py`, `report_v4.py` and the launcher are untouched. The launcher is also the file bash is
executing right now, so editing it mid-run could break the run. Whether this runs right after run 4's
reports or later is your call; Fable is fine either way.

## The question

Several matchups swing 8–15 points between checkpoints against k3 (`swings_to_3.5M.txt`). k3 is fixed
and plays the same 1,000 seeds per matchup at every checkpoint, so **those measurements already hold the
opponent still.** The swings are the network's own play changing. The quietest matchups move 1.6–2.5
points between checkpoints, about what noise gives; the loud ones move 6–9. Three explanations fit:

- **(A) Chasing.** Each network trains against the other networks as they change, and adapts to their
  current habits rather than improving in general.
- **(B) Drift.** A constant learning rate plus random exploration never lets a network settle, whatever its
  opponents do. Fable calls this the simplest explanation.
- **(C) Trade-off.** One network plays four matchups, so an update that helps one can hurt another.

## The test

For a pairing X vs Y, every saved X checkpoint plays every saved Y checkpoint. Both are frozen, and both
choose moves exactly as the evaluation does (best-scored move, ties broken by the seed). Every cell uses
the **same seeds**, with X in seat 0 on even seeds and seat 1 on odd ones. Cell (i, j) is X checkpoint i's
win rate against Y checkpoint j; draws count as half. `ckpt_0` is left out, since it's untrained.

**What separates the three:**

- **(A)**: X's checkpoint i was trained against the Y networks alive just before it. So beyond general
  strength, the newer side of a pair should beat the opponents it just trained against. I fit each
  checkpoint's overall strength additively on the log-odds and take the residuals.
  **D = mean residual where X is 1–2 checkpoints newer than Y, minus where Y is 1–2 checkpoints newer.**
  Chasing predicts D > 0. The output also reports a forgetting check: the latest X against the oldest Y
  checkpoints, compared with X's best against them before.
- **(B)**: predicts D near 0. It also predicts that each X checkpoint's overall strength against Y's
  networks (its row effect) tracks its k3 margin in that matchup — reported as a correlation.
- **(C)**: needs no games. It asks whether changes in X's k3 margin against Y correlate negatively with
  changes against X's other three opponents, using the saved checkpoint evaluations.

The three aren't mutually exclusive, and the output reports numbers, not verdicts. With 12 checkpoints,
the (B) and (C) correlations are weak evidence, and the output says so. D is the part with statistical
power.

## Choices for you (and Fable) to confirm

1. **Pairings: Blaziken–Lucario and Suicune–Blaziken.** Blaziken–Lucario is the matchup Fable named, and
   the only one that swings hard from **both** sides (6.6 and 6.5 points of average change). Suicune–
   Blaziken is the largest swinger overall (8.6) and was your original proposal. The next candidates are
   Suicune–Altaria (7.8) and Blaziken–Altaria (6.2); `--pair` takes any.
2. **400 games per cell**, matched seeds from a new block at 97,000,000 (k3 uses 80M, random 81M, confirm
   90M, transfer 95M, training 3 billion+). At 12 × 12 checkpoints that's 57,600 games per pairing, or
   115,200 for both: about 30 minutes on the laptop, or about 2 hours in the cloud from staged checkpoints.
3. **"Just trained against" means 1–2 checkpoints apart**, i.e. within 1M games.
4. **Output:** `results/crossplay_v4_<run>_<X>-<Y>.json` and the run folder's `CROSSPLAY.txt`, not REPORT.txt.
   `report_v4.py` is a live, approved file; if you want REPORT.txt to point at this, that's a small change
   to make after run 4's reports are written.

## What's been checked

- **The statistic, on synthetic matrices with a known answer** (`test_analysis.*`), 12 × 12 at 400 games a
  cell, with a shared per-seed luck term as matched seeds give:
  - drift only: D −0.012, interval covers 0;
  - steady improvement on both sides: D +0.011, covers 0;
  - chasing at +0.25 log-odds: D +0.429 against a true +0.423;
  - chasing at +0.10 log-odds (about 2.5 win-rate points): D +0.141 against a true +0.169.
  All four intervals cover the truth. Under pure drift, 40 repeats excluded zero 4 times — the 10% the
  interval is built for.
  - One mistake of mine, disclosed: my test first compared against the effect *before* averaging over the
    luck of the deal, and reported two misses. The statistic was right; the reference was wrong.
- **Real games, on the finished practice run** (`practice.*`, `CROSSPLAY_practice.txt`): 20 × 20
  checkpoints, both default pairings, 4 games a cell. 11 of 11 checks pass: both matrices complete; an
  identical re-run is skipped; `--redo` reproduces the matrix exactly and keeps the old result as
  superseded; it refuses while the lock is held, refuses a deck paired with itself, and refuses a RUNNING
  run; and the run's `state.json` is unchanged.
  - One bug found and fixed along the way: `--redo` first overwrote the old result instead of keeping it,
    as the audit step does.
  - The practice numbers themselves mean nothing: 4 games a cell, on networks minutes old.

## Limits, stated up front

- It measures network against network, not against k3. The link to the k3 swings runs through (B)'s
  correlation, which is weak at 12 points.
- D detects mutual local adaptation. It can't say which side is chasing harder.
- A positive D supports chasing; it doesn't rule out drift also being present.
