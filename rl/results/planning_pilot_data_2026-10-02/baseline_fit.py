"""The planning pilot's data (Oct 2): the baseline fit, a sanity check only (no pilot change, no claim).
A plain logistic regression of the mover's win on the features of each decision row:
- the battle rows only (setup = 0); ties left out;
- every feature column except km_value (km's terms added up, so a sum of the others), setup and opening_term (constant in
  the battle rows);
- standardised with the training rows' mean and standard deviation; a column constant in training is dropped;
- a small ridge (lambda = 1 on the standardised coefficients, not on the intercept), fitted by Newton's method.
The held-out games (README, fixed before any game): every game with i % 5 == 4, all of its rows. The rows of one game are
not independent, so no standard errors are given; the sign question is read across the five folds (i % 5 == k held out).
Reported:
- test log loss and accuracy for the base rate, km's own value alone (one feature), and all features;
- the features carrying the most weight (standardised coefficients);
- the fitted sign of my_bench_attacker_energy (the Energy on the likely benched attacker) in the full model, in each fold, and
  in a small model (km's terms and the Bench Energy features only).
Usage: python3 baseline_fit.py <rows.tsv.gz> [more rows files...]   (writes baseline_fit.txt here)"""
import csv, gzip, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
META = ["pairing", "i", "seed", "tick", "seat", "deck", "opp_deck", "n_offered", "chosen_kind", "own_turn"]
LABELS = ["result", "final_points_mine", "final_points_opp", "final_turn", "game_ticks"]
LEFT_OUT = {"km_value", "setup", "opening_term"}
RIDGE = 1.0
KEY = "my_bench_attacker_energy"

header, data, game_i, labels, kmv = None, [], [], [], []
for path in sys.argv[1:]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        h = next(reader)
        if header is None:
            header = h
            idx = {name: k for k, name in enumerate(header)}
            feats = [name for name in header if name not in META and name not in LABELS and name not in LEFT_OUT]
            cols = [idx[name] for name in feats]
        assert h == header, f"{path}: a different header"
        for r in reader:
            if r[idx["setup"]] != "0" or r[idx["result"]] == "0.5":
                continue
            data.append([float(r[k]) for k in cols])
            labels.append(float(r[idx["result"]]))
            game_i.append(int(r[idx["i"]]))
            kmv.append(float(r[idx["km_value"]]))
X_all = np.array(data, dtype=np.float64)
y_all = np.array(labels)
fold = np.array(game_i) % 5
kmv = np.array(kmv)
del data


def fit(X, y):
    """Ridge logistic regression by Newton's method; X has the intercept in column 0 (not penalised)."""
    w = np.zeros(X.shape[1])
    pen = np.full(X.shape[1], RIDGE)
    pen[0] = 0.0
    for _ in range(50):
        p = 1.0 / (1.0 + np.exp(-(X @ w)))
        g = X.T @ (y - p) - pen * w
        H = (X * (p * (1 - p))[:, None]).T @ X + np.diag(pen)
        step = np.linalg.solve(H, g)
        w += step
        if np.max(np.abs(step)) < 1e-8:
            break
    return w


def design(X, mean, sd):
    return np.hstack([np.ones((X.shape[0], 1)), (X - mean) / sd])


def logloss(y, p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def run(names, test_fold):
    k = [feats.index(n) for n in names]
    train, test = fold != test_fold, fold == test_fold
    Xtr, Xte = X_all[train][:, k], X_all[test][:, k]
    mean, sd = Xtr.mean(axis=0), Xtr.std(axis=0)
    keep = sd > 0
    names = [n for n, kept in zip(names, keep) if kept]
    Xtr, Xte, mean, sd = Xtr[:, keep], Xte[:, keep], mean[keep], sd[keep]
    w = fit(design(Xtr, mean, sd), y_all[train])
    p = 1.0 / (1.0 + np.exp(-(design(Xte, mean, sd) @ w)))
    return names, w, p, y_all[test], y_all[train].mean()


out = []
say = out.append
say(f"rows: {len(y_all)} battle rows without ties ({int((fold == 4).sum())} held out: games with i % 5 == 4); "
    f"features: {len(feats)}; wins {y_all.mean():.1%} of rows")
names, w, p, yte, base = run(feats, 4)
# km's own value alone (the rows' km_value column), as one standardised feature.
train, test = fold != 4, fold == 4
m, s = kmv[train].mean(), kmv[train].std()
wkm = fit(np.column_stack([np.ones(train.sum()), (kmv[train] - m) / s]), y_all[train])
pkm = 1.0 / (1.0 + np.exp(-(np.column_stack([np.ones(test.sum()), (kmv[test] - m) / s]) @ wkm)))
say("held-out games: log loss / accuracy")
say(f"  base rate ({base:.3f}):       {logloss(yte, np.full(len(yte), base)):.4f} / {max(base, 1 - base):.3f}")
say(f"  km's value alone:        {logloss(yte, pkm):.4f} / {np.mean((pkm > 0.5) == (yte == 1)):.3f}")
say(f"  all {len(names)} features:     {logloss(yte, p):.4f} / {np.mean((p > 0.5) == (yte == 1)):.3f}")

order = np.argsort(-np.abs(w[1:]))
say("\nthe weightiest features (standardised coefficient; + favours the mover's win):")
for j in order[:30]:
    say(f"  {names[j]:40} {w[1 + j]:+.3f}")
rank = {names[j]: r + 1 for r, j in enumerate(order)}

say(f"\n{KEY}: coefficient {w[1 + names.index(KEY)]:+.4f} (rank {rank[KEY]} of {len(names)} by size) in the full model")
for other in ["my_bench_energy_total", "my_bench_attacker_missing", "opp_bench_attacker_energy", "opp_bench_energy_total"]:
    if other in names:
        say(f"  {other}: {w[1 + names.index(other)]:+.4f} (rank {rank[other]})")
signs = []
for k in range(5):
    n_k, w_k, p_k, y_k, _ = run(feats, k)
    signs.append(w_k[1 + n_k.index(KEY)])
say(f"  by fold (held out i % 5 == 0..4): " + ", ".join(f"{v:+.4f}" for v in signs))
small = [n for n in feats if n in {f"{s}_{t}" for s in ("my", "opp") for t in (
    "points", "pokemon_value", "hand_size", "deck_size", "active_retreat_cost", "online_pokemon_count",
    "energy_distance_to_online", "active_online_score", "active_safety", "active_has_tool", "is_winner",
    "turns_until_opponent_wins", "discard_size", "fuel_credit", "bench_attacker_energy", "bench_energy_total")}]
n_s, w_s, p_s, y_s, _ = run(small, 4)
say(f"  in a small model (km's terms and the two Bench Energy features, {len(n_s)} columns): {KEY} {w_s[1 + n_s.index(KEY)]:+.4f}, "
    f"my_bench_energy_total {w_s[1 + n_s.index('my_bench_energy_total')]:+.4f}; held-out log loss {logloss(y_s, p_s):.4f}")
(HERE / "baseline_fit.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
