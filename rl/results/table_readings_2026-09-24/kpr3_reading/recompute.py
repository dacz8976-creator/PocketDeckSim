#!/usr/bin/env python3
"""Independent recompute of the decision line (laptop, Sept 26): scoreboard v2 development cells, decision set of 27
(Altaria v Sceptile quarantined) and all 28; kp3 (current) against kpr3 (new), paired by deal. Written from the rule's
definitions, not from score.py's code, with numpy and a different random stream, as a check on score.py's output:
  MSE = mean over cells of (S - L)^2; real error tau = 100 sqrt(max(0, mean[(S-L)^2 - L(1-L)/nL - S(1-S)/nS]));
  dMSE = MSE(kpr3) - MSE(kp3), 95% interval; tau margin = tau(kp3) - tau(kpr3), 90% interval;
  bootstrap: deals resampled within each cell for both bots at once; Limitless redrawn Binomial(nL, L), or by event
  (the 58 development events resampled with replacement, a draw with an empty cell drawn again).
Also the same on the Sept 23 cells (deep_table.py) for the descriptive line. Read-only; prints to stdout.
Usage: recompute.py <kpr3_500.jsonl copied from the cloud branch>
"""
import json, sys
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "deep_search_table"))
import deep_table as DT  # noqa: E402

REPS = 4000
rng = np.random.default_rng(20260926)


def load(*paths):
    out = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out.setdefault((r["a"], r["b"]), {})[r["i"]] = r["first_deck_score"]
    return out


kp3 = load(R / "public_pricing_2026-09-25/kp3_500_worst5.jsonl", R / "public_pricing_2026-09-25/kp3_500_rest.jsonl")
kpr = load(Path(sys.argv[1]))
k3 = load(R / "per_game_table_2026-09-25/k3_500.jsonl")
v2 = {tuple(k.split("|")): v for k, v in json.load(open(R / "scoreboard_v2_2026-09-25/limitless_v2_dev.json"))["cells"].items()}
ev = json.load(open(R / "scoreboard_v2_2026-09-25/limitless_v2_dev_events.json"))["events"]
s23 = {k: tuple(v) for k, v in DT.LIMITLESS.items()}


def tau(S, nS, L, nL):
    x = (S - L) ** 2 - L * (1 - L) / nL - S * (1 - S) / nS
    return 100 * np.sqrt(np.maximum(0.0, x.mean(axis=-1)))


def run(label, cells, lim, events=None):
    keys = [k for k in DT.PAIRS if k in cells]
    O = np.array([[kp3[k][i] for i in range(500)] for k in keys])
    N = np.array([[kpr[k][i] for i in range(500)] for k in keys])
    K = np.array([[k3[k][i] for i in range(500)] for k in keys])
    W = np.array([lim[k] for k in keys], dtype=float)
    nL = W.sum(1)
    L = (W[:, 0] + 0.5 * W[:, 2]) / nL
    So, Sn, Sk = O.mean(1), N.mean(1), K.mean(1)
    mse = lambda S: 1e4 * ((S - L) ** 2).mean()  # noqa: E731
    print(f"== {label}: {len(keys)} cells")
    print(f"  MSE: k3 {mse(Sk):.1f}, kp3 {mse(So):.1f}, kpr3 {mse(Sn):.1f} | real error: k3 {tau(Sk, 500, L, nL):.2f}, "
          f"kp3 {tau(So, 500, L, nL):.2f}, kpr3 {tau(Sn, 500, L, nL):.2f}")
    dpt = mse(Sn) - mse(So)
    tpt = tau(So, 500, L, nL) - tau(Sn, 500, L, nL)
    dm, dt, dme, dte = [], [], [], []
    if events:
        E = np.array([[e["cells"].get("|".join(k), [0, 0, 0]) for k in keys] for e in events], dtype=float)  # (ev, cells, 3)
        assert np.allclose(E.sum(0), W), "events do not sum to the cells"
    for start in range(0, REPS, 250):
        m = min(250, REPS - start)
        idx = rng.integers(0, 500, size=(m, len(keys), 500))
        Os = np.take_along_axis(np.broadcast_to(O, idx.shape), idx, 2).mean(2)
        Ns = np.take_along_axis(np.broadcast_to(N, idx.shape), idx, 2).mean(2)
        Ls = rng.binomial(nL.astype(int), L, size=(m, len(keys))) / nL
        dm.append(1e4 * (((Ns - Ls) ** 2) - ((Os - Ls) ** 2)).mean(1))
        dt.append(tau(Os, 500, Ls, nL) - tau(Ns, 500, Ls, nL))
        if events:
            got = 0
            LE, nE = np.empty((m, len(keys))), np.empty((m, len(keys)))
            while got < m:
                c = rng.multinomial(len(events), np.full(len(events), 1 / len(events)))
                C = np.tensordot(c, E, 1)
                n = C.sum(1)
                if (n == 0).any():
                    continue
                LE[got], nE[got] = (C[:, 0] + 0.5 * C[:, 2]) / n, n
                got += 1
            dme.append(1e4 * (((Ns - LE) ** 2) - ((Os - LE) ** 2)).mean(1))
            dte.append(tau(Os, 500, LE, nE) - tau(Ns, 500, LE, nE))
    dm, dt = np.concatenate(dm), np.concatenate(dt)
    print(f"  dMSE kpr3 - kp3 {dpt:+.1f}, 95% {np.quantile(dm, .025):+.1f} to {np.quantile(dm, .975):+.1f} (binomial)", end="")
    if events:
        dme, dte = np.concatenate(dme), np.concatenate(dte)
        print(f"; {np.quantile(dme, .025):+.1f} to {np.quantile(dme, .975):+.1f} (by event)")
    else:
        print()
    print(f"  tau margin kp3 - kpr3 {tpt:+.2f}, 90% {np.quantile(dt, .05):+.2f} to {np.quantile(dt, .95):+.2f} (binomial)", end="")
    print(f"; {np.quantile(dte, .05):+.2f} to {np.quantile(dte, .95):+.2f} (by event)" if events else "")


Q = {("altaria", "sceptile")}
run("scoreboard v2, decision set", {k: 1 for k in v2 if k not in Q}, v2, ev)
run("scoreboard v2, all cells", {k: 1 for k in v2}, v2, ev)
run("Sept 23 cells, decision set", {k: 1 for k in s23 if k not in Q}, s23)
run("Sept 23 cells, all cells", {k: 1 for k in s23}, s23)
