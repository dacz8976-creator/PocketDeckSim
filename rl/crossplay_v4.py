"""Run 4 analysis step, after training: frozen checkpoints against frozen checkpoints (Astra's design; Fable
asked for it, Sept 21; revised after Astra's review, V4_CROSSPLAY_REVIEW_20260921.md).

What it is for. Several matchups swing 8-15 points between checkpoints against k3, which is fixed and plays the
same seeds at every checkpoint, so the network's own play is changing. Chasing (adapting to opponents that are
themselves changing), drift (a constant learning rate with exploration never settles) and trade-offs between
one network's four matchups all fit that. THIS STEP DESCRIBES; IT DOES NOT DECIDE BETWEEN THEM. Astra showed
that two players whose styles change on a fixed schedule, never reacting to each other, produce the same
checkpoint-age pattern that chasing would. Separating the explanations needs an intervention (for example,
training one side against a frozen opponent), which is a run-5 question.

What it measures, for a pairing X vs Y chosen because it swung (so: this run's trajectory, not self-play in
general):
  - from the saved k3 evaluations, no new games: how X's changes against Y moved alongside its changes against
    its other opponents, checkpoint to checkpoint;
  - every saved X checkpoint against every saved Y checkpoint, both frozen, choosing moves exactly as evaluation
    does (best-scored move, ties broken by the game's seed), on the SAME seeds in every cell, X in seat 0 on even
    seeds and seat 1 on odd ones. Score = wins + half the draws, from X's side; wins, draws and losses are kept;
  - the checkpoint-age pattern D: after fitting each checkpoint's overall strength additively on the log-odds,
    the mean remaining effect where X is 1-2 checkpoints newer than Y, minus where Y is 1-2 checkpoints newer.
    The 1-2 window is fixed in advance. It is checkpoint-age proximity, not a record of which opponents each
    network actually met (training used continuously changing networks and a 20% mix of past versions);
  - against the oldest opponents: X's last checkpoint against Y's three oldest checkpoints, compared with the
    average of all X's earlier checkpoints against them (fixed in advance; not a best-of, which exaggerates);
  - X's overall strength against Y's networks, set beside its k3 margin in that matchup.
Every interval is a 90% interval from resampling seeds, within each seat, identically in every cell. It covers
evaluation noise for these fixed checkpoints only - not run-to-run variation, and not confidence in any cause.
When only noise is present it excludes zero about 1 time in 10, by construction.

It reads a finished run only, and only under that run's own runtime: it refuses while a trainer holds the run's
lock, before the run has ended, with fewer than 4 scored checkpoints, or if the engine add-on, trainer, model,
observation wrapper, decks, Python or numpy differ from what the run recorded (a different-engine experiment must
be a separate, explicit step). Every game's outcome is saved with its seed and seat, so every number can be
recomputed from the file without replaying. A saved result is reused only if all of its inputs are unchanged;
results are written whole or not at all, and a damaged file is set aside and redone.

    python crossplay_v4.py --run runs/pool5-v22-perdeck-01          # the two approved pairings, 400 games a cell
    python crossplay_v4.py --run runs/<run> --pair blaziken,lucario --games 400 --workers 8
"""
import argparse
import fcntl
import hashlib
import json
import math
import multiprocessing as mp
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_v4 as T  # noqa: E402

SEED_BASE = 97_000_000        # no Run 4 step uses 97M-98M (k3 80M, random 81M, confirm 90M, transfer 95M, train 3e9+)
SEED_BLOCK = 1_000_000        # so at most this many games per cell
DEFAULT_PAIRS = [("blaziken", "lucario"), ("suicune", "blaziken")]   # approved by Fable and Astra, Sept 21
NEAR = (1, 2)                 # checkpoint-age window, fixed before any results were seen
OLDEST = 3                    # the "oldest opponents" comparison uses Y's three oldest checkpoints
MIN_CHECKPOINTS = 4
BOOT_REPS = 1000
VALUE = {"W": 1.0, "D": 0.5, "L": 0.0}
_W = {}


# ---------- the games ----------

def _init(S):
    T.set_decks(S)
    _W["env"] = T.make_env()
    _W["dim"] = T.env_dims()
    _W["nets"] = T.NetCache(4)   # a chunk needs two networks; weights only


def _net(path):
    return _W["nets"].get(path, lambda: T.load_scorer(path, _W["dim"]))


def play_cell(args):
    """Games for one cell: (i, j, x_path, y_path, x_deck, y_deck, [(k, seed)]) -> (i, j, [(k, 'W'|'D'|'L')])."""
    i, j, xp, yp, xd, yd, seeds = args
    env, nx, ny = _W["env"], _net(xp), _net(yp)
    res = []
    for k, seed in seeds:
        rng = np.random.default_rng(seed)
        x_seat = k % 2
        d = (xd, yd) if x_seat == 0 else (yd, xd)
        nets = (nx, ny) if x_seat == 0 else (ny, nx)
        env.reset(T.deck_path(d[0]), T.deck_path(d[1]), seed, bots=None)
        while not env.done:
            p = env.current_player
            obs, feats = env.observe(p), env.action_features()
            env.step(T.pick(nets[p].score_actions(obs, feats), rng))
        w, _, _ = env.result()
        res.append((k, "D" if w == -1 else ("W" if w == x_seat else "L")))
    return i, j, res


def play_all(run_dir, S, x, y, names, n, workers):
    seeds = [(k, SEED_BASE + k) for k in range(n)]
    per = max(1, n // 2)
    jobs = [(i, j, str(T.ckpt_path(run_dir, xi, x)), str(T.ckpt_path(run_dir, yj, y)), x, y, seeds[s:s + per])
            for i, xi in enumerate(names) for j, yj in enumerate(names) for s in range(0, n, per)]
    cells = [[[None] * n for _ in names] for _ in names]
    with mp.get_context("spawn").Pool(workers, initializer=_init, initargs=(S,)) as pool:
        for i, j, res in pool.imap_unordered(play_cell, jobs, chunksize=1):
            for k, o in res:
                cells[i][j][k] = o
    if any(o is None for row in cells for cell in row for o in cell):
        raise RuntimeError("some games did not come back; nothing was saved")
    return [["".join(cell) for cell in row] for row in cells]


# ---------- the analysis: everything below is computed from the saved outcomes ----------

def tensor(outcomes):
    """Saved outcome strings -> array [X checkpoint, Y checkpoint, seed index] of scores (W 1, D 0.5, L 0)."""
    return np.array([[[VALUE[c] for c in cell] for cell in row] for row in outcomes])


def logit(p, n):
    p = min(max(p, 0.5 / n), 1 - 0.5 / n)
    return math.log(p / (1 - p))


def additive_fit(W, n):
    """Log-odds(cell) = mu + row_i - col_j, rows and columns summing to zero (row = X's strength, col = Y's)."""
    L = np.vectorize(lambda p: logit(p, n))(W)
    mu = L.mean()
    row = L.mean(axis=1) - mu
    col = -(L.mean(axis=0) - mu)
    return L, mu + row[:, None] - col[None, :], row, col


def age_pattern(W, n):
    """D, in log-odds: mean residual where X is NEAR checkpoints newer, minus where Y is NEAR checkpoints newer."""
    L, fit, _, _ = additive_fit(W, n)
    R, k = L - fit, len(W)
    x_newer = [R[i, j] for i in range(k) for j in range(k) if i - j in NEAR]
    y_newer = [R[i, j] for i in range(k) for j in range(k) if j - i in NEAR]
    return float(np.mean(x_newer) - np.mean(y_newer)), len(x_newer)


def oldest_opponents(G):
    """X's last checkpoint against Y's OLDEST checkpoints, minus the mean of all X's earlier checkpoints against
    them (score points). Fixed in advance; no selection."""
    k = G.shape[0]
    cols = list(range(min(OLDEST, k - 1)))
    return float(100 * (G[k - 1, cols].mean() - G[:k - 1][:, cols].mean())), cols


def resample(G, rng):
    """One bootstrap draw of seeds, within each seat (even / odd seed index), the same draw in every cell."""
    n = G.shape[2]
    even, odd = np.arange(0, n, 2), np.arange(1, n, 2)
    idx = np.concatenate([rng.choice(even, size=len(even)), rng.choice(odd, size=len(odd))])
    return G[:, :, idx]


def interval(G, stat, reps=BOOT_REPS, seed=0):
    rng = np.random.default_rng(seed)
    vals = [stat(resample(G, rng)) for _ in range(reps)]
    return float(np.percentile(vals, 5)), float(np.percentile(vals, 95))


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def k3_margins(st, deck, names):
    cps = {c["name"]: c for c in st["checkpoints"] if c.get("decks")}
    return {t: [cps[nm]["decks"][deck]["margins"][t] for nm in names] for t in cps[names[0]]["decks"][deck]["margins"]}


def change_correlations(st, x, y, names):
    """From the saved k3 evaluations: correlation of X's checkpoint-to-checkpoint changes against Y with its
    changes against each other opponent."""
    m = k3_margins(st, x, names)
    dk = np.diff(m[f"{x}>{y}"])
    return {t.split(">")[1]: corr(dk, np.diff(v)) for t, v in m.items() if t != f"{x}>{y}"}


def analyse(result, st):
    """All statistics, from a result's saved outcomes and the run's saved evaluations."""
    x, y = result["inputs"]["pair"]
    names = result["axes"]["checkpoints"]
    G = tensor(result["outcomes"])
    n = G.shape[2]
    W = G.mean(axis=2)
    D, cells = age_pattern(W, n)
    D_lo, D_hi = interval(G, lambda g: age_pattern(g.mean(axis=2), n)[0])
    old, cols = oldest_opponents(G)
    old_lo, old_hi = interval(G, lambda g: oldest_opponents(g)[0])
    _, _, row, _ = additive_fit(W, n)
    k3 = k3_margins(st, x, names)[f"{x}>{y}"]
    p = float(W.mean())
    return {"D": D, "D_points": 100 * D * p * (1 - p), "D_interval": [D_lo, D_hi], "cells_each_side": cells,
            "oldest_opponents_points": old, "oldest_opponents_interval": [old_lo, old_hi], "oldest_columns": cols,
            "strength_vs_k3_r": corr(row, k3), "k3_margins": [100 * v for v in k3],
            "change_correlations": change_correlations(st, x, y, names)}


def summarise(result, stats):
    x, y = result["inputs"]["pair"]
    names = result["axes"]["checkpoints"]
    n, k = result["axes"]["games_per_cell"], len(names)
    G = tensor(result["outcomes"])
    W = G.mean(axis=2)
    wins = sum(o.count("W") for row in result["outcomes"] for o in row)
    draws = sum(o.count("D") for row in result["outcomes"] for o in row)
    short = [nm.replace("ckpt_", "").replace("000k", "M").replace("500k", ".5M") for nm in names]
    short = ["0" + s if s.startswith(".") else s for s in short]
    cc = stats["change_correlations"]
    lines = [f"Frozen checkpoints, {x} against {y} (run 4, {result['inputs']['run']}): a description of this run's "
             f"trajectory in a pairing chosen because it swung. It does not identify a cause.",
             "",
             f"1. From the saved k3 evaluations (no new games): over {k - 1} checkpoint-to-checkpoint changes, how {x}'s "
             f"change against {y} moved with its change against each other opponent (correlation): "
             + ", ".join(f"{t} {v:+.2f}" for t, v in cc.items())
             + ". Negative = moved in opposite directions, positive = together. With this few changes each is weak, "
             "and none shows a mechanism.",
             "",
             f"2. Every {x} checkpoint against every {y} checkpoint: {n:,} games per cell on the same seeds, "
             f"{n // 2} from each seat, {k * k * n:,} games ({wins:,} {x} wins, {draws:,} draws). "
             f"{x}'s score = wins + half the draws (the k3 reports count wins only):",
             "        " + "".join(f"{s:>7}" for s in short)]
    for i in range(k):
        lines.append(f"  {short[i]:>6}" + "".join(f"{100 * W[i, j]:>7.1f}" for j in range(k)))
    lo, hi = stats["D_interval"]
    olo, ohi = stats["oldest_opponents_interval"]
    lines += ["",
              f"3. Checkpoint-age pattern: D = {stats['D']:+.3f} log-odds (about {stats['D_points']:+.1f} score points), "
              f"90% interval {lo:+.3f} to {hi:+.3f} ({stats['cells_each_side']} cells each side). How much better each side "
              f"scores against opponent checkpoints 1-2 older than itself than against ones 1-2 newer, beyond each "
              f"checkpoint's overall strength. Chasing would make this positive, but so do styles that change "
              f"independently in a matchup that isn't simply stronger-beats-weaker; near zero doesn't rule out "
              f"adaptation on a different time scale.",
              f"4. Against the oldest opponents: {x}'s last checkpoint against {y}'s {len(stats['oldest_columns'])} oldest "
              f"checkpoints scores {stats['oldest_opponents_points']:+.1f} points compared with the average of all its "
              f"earlier checkpoints against them (90% interval {olo:+.1f} to {ohi:+.1f}).",
              f"5. {x}'s overall strength against {y}'s networks beside its k3 margin in that matchup, checkpoint by "
              f"checkpoint: correlation {stats['strength_vs_k3_r']:+.2f} over {k} checkpoints (k3 margins "
              + ", ".join(f"{v:+.0f}" for v in stats["k3_margins"]) + "). General improvement produces this as well as "
              "drift; it is not specific to either.",
              "",
              "Intervals come from resampling seeds within each seat, identically in every cell. They cover evaluation "
              "noise for these fixed checkpoints only - not run-to-run variation, and not confidence in a cause - and "
              "exclude zero about 1 time in 10 when only noise is present."]
    return "\n".join(lines)


# ---------- the step ----------

def write_whole(path, text):
    """Write to a temporary file in the same folder, flush it to disk, then replace: never a partial file."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def runtime_mismatch(run_dir, S):
    """Roles whose current bytes differ from what the run recorded (engine add-on, trainer, model, wrapper,
    decks, held-out decks, Python, numpy)."""
    T.set_decks(S)
    now = T.input_identity()
    saved = json.loads((run_dir / "identity.json").read_text())
    bad = sorted(k for k in set(now["sha256"]) | set(saved["sha256"]) if now["sha256"].get(k) != saved["sha256"].get(k))
    bad += [k for k in ("python", "numpy") if now[k] != saved[k]]
    return bad, now


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--pair", action="append", default=[], help="X,Y (repeatable); default: the two approved pairings")
    ap.add_argument("--games", type=int, default=400, help="games per cell, even (default 400)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    if a.games <= 0 or a.games % 2 or a.games > SEED_BLOCK:
        sys.exit(f"REFUSED: --games must be even, positive and at most {SEED_BLOCK:,} (the reserved seed block)")
    run_dir = Path(a.run) if Path(a.run).is_absolute() else HERE / a.run
    settings_bytes = (run_dir / "settings.json").read_bytes()
    S = json.loads(settings_bytes)
    pairs = [tuple(p.split(",")) for p in a.pair] or DEFAULT_PAIRS
    for x, y in pairs:
        if x not in S["pool"] or y not in S["pool"] or x == y:
            sys.exit(f"REFUSED: {x},{y} is not a pairing of two different pool decks")
    with (run_dir / "run.lock").open("a") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)   # held throughout: no trainer can start meanwhile
        except BlockingIOError:
            sys.exit("REFUSED: a trainer holds this run's lock; this step runs after training")
        st = json.loads((run_dir / "state.json").read_text())
        if st["status"] not in ("PASSED", "FINISHED", "STOPPED"):
            sys.exit(f"REFUSED: the run is {st['status']}; this step runs on a finished run")
        names = [c["name"] for c in st["checkpoints"] if c.get("decks")]
        if len(names) < MIN_CHECKPOINTS:
            sys.exit(f"REFUSED: {len(names)} scored checkpoints; this step needs at least {MIN_CHECKPOINTS}")
        bad, runtime = runtime_mismatch(run_dir, S)
        if bad:
            sys.exit(f"REFUSED: these don't match what this run recorded: {', '.join(bad)}. This step asks what the run's "
                     f"own networks did in the run's own simulator; a different engine is a separate experiment.")
        texts = []
        for x, y in pairs:
            inputs = {"step": "crossplay", "run": run_dir.name, "pair": [x, y], "checkpoints": names,
                      "games_per_cell": a.games, "seed_base": SEED_BASE, "near": list(NEAR), "oldest": OLDEST,
                      "runtime identity": runtime,
                      "settings sha256": hashlib.sha256(settings_bytes).hexdigest(),
                      "crossplay_v4.py sha256": T.sha_file(HERE / "crossplay_v4.py"),
                      "checkpoint sha256": {f"{d} {nm}": T.sha_file(T.ckpt_path(run_dir, nm, d))
                                            for d in (x, y) for nm in names},
                      "state checkpoints sha256": hashlib.sha256(
                          json.dumps(st["checkpoints"], sort_keys=True).encode()).hexdigest()}
            out = HERE / f"results/crossplay_v4_{run_dir.name}_{x}-{y}.json"
            stamp = f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
            for stale in out.parent.glob(f".{out.name}.*.tmp"):   # left by a run killed mid-write; never read
                stale.unlink(missing_ok=True)
            old = None
            if out.exists():
                try:
                    old = json.loads(out.read_text())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    bad_copy = out.with_name(f"{out.stem}.damaged-{stamp}.json")
                    out.replace(bad_copy)
                    print(f"{out.name} was damaged (not valid JSON); set aside as {bad_copy.name} and redone")
            if old is not None and old.get("inputs") == inputs and old.get("complete") and not a.redo:
                print(f"{out.name} exists with the same inputs; skipped (--redo to rerun)")
                texts.append(old["summary"])
                continue
            t0 = time.time()
            outcomes = play_all(run_dir, S, x, y, names, a.games, a.workers)
            result = {"inputs": inputs,
                      "axes": {"rows": f"{x} checkpoint", "columns": f"{y} checkpoint", "checkpoints": names,
                               "games_per_cell": a.games,
                               "seed": f"game k of every cell uses seed {SEED_BASE} + k",
                               "seat": f"{x} sits in seat 0 when k is even, seat 1 when k is odd",
                               "outcome": f"outcomes[i][j][k] = W, D or L from {x}'s side in cell (row i, column j), game k"},
                      "outcomes": outcomes}
            result["stats"] = analyse(result, st)
            result["summary"] = summarise(result, result["stats"]) + f"\n({time.time() - t0:,.0f} s, {a.workers} workers)"
            result["complete"] = True
            if old is not None:   # keep the previous result; the canonical file stays valid until the replace
                kept = out.with_name(f"{out.stem}.superseded-{stamp}.json")
                shutil.copy2(out, kept)
                why = "--redo" if a.redo and old.get("inputs") == inputs else "its inputs changed"
                print(f"{out.name}: redone ({why}); the previous result is kept as {kept.name}")
            out.parent.mkdir(exist_ok=True)
            write_whole(out, json.dumps(result))
            print(result["summary"] + "\n")
            texts.append(result["summary"])
        write_whole(run_dir / "CROSSPLAY.txt", "\n\n".join(texts) + "\n")


if __name__ == "__main__":
    main()
