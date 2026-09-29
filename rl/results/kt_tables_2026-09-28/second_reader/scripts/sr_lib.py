"""Second reader's own code for the kt-on-kog registration (written from the registration text; read_kt.py not opened).
Pure stdlib. Everything reads game files only; nothing is written in the repo."""
import csv, itertools, json, math, os, random, sys

REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
R = REPO + "/rl/results"
K = R + "/kt_tables_2026-09-28"
SCR = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kt2/second-reader"
B = "ec7e1a8"

NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
PANEL_ORDER = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
TABLE28 = list(itertools.combinations(NAMES, 2))
NEW17 = [(d, o) for d in ("rayquaza", "altaria_greninja") for o in PANEL_ORDER] + [("rayquaza", "altaria_greninja")]
CELLS45 = TABLE28 + NEW17
DECKS10 = NAMES + ["rayquaza", "altaria_greninja"]
QUARANTINE = {("altaria", "sceptile")}


def rd(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load(paths, keyfn):
    """{cellkey: {i: record}}"""
    out = {}
    for p in paths:
        for r in rd(p):
            k = keyfn(r)
            c = out.setdefault(k, {})
            if r["i"] in c:
                raise SystemExit(f"duplicate deal {k} {r['i']} in {p}")
            c[r["i"]] = r
    return out


def ab(r):
    return (r["a"], r["b"])


def pairing(r):
    return r["pairing"]


def score(r):
    return float(r["first_deck_score"])


def table_paths(tag_or_paths):
    return tag_or_paths


# ----- Limitless (development half, 45 cells) -----
def limitless45():
    cells = {}
    v2 = json.load(open(R + "/scoreboard_v2_2026-09-25/limitless_v2_dev.json", encoding="utf-8"))["cells"]
    for k, v in v2.items():
        a, b = k.split("|")
        cells[(a, b)] = tuple(v)
    with open(R + "/gauntlet_runs_2026-09-26/gauntlet_cells.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for a, b in NEW17:
        m = [r for r in rows if r["dataset"] == "development" and r["a"] == a and r["b"] == b]
        assert len(m) == 1, (a, b, len(m))
        cells[(a, b)] = (int(m[0]["W"]), int(m[0]["L"]), int(m[0]["T"]))
    assert set(cells) == set(CELLS45), set(cells) ^ set(CELLS45)
    return cells


def lim_rate(cells, k):
    w, l, t = cells[k]
    n = w + l + t
    return (w + 0.5 * t) / n, n


# ----- statistics -----
def mean_var_of_mean(d):
    n = len(d)
    m = sum(d) / n
    v = sum((x - m) ** 2 for x in d) / (n - 1) / n if n > 1 else 0.0
    return m, v


def pool(parts):
    """Stratified pool over cells: (mean of the cell means, 95% half-width, total deals)."""
    mv = [mean_var_of_mean(d) for d in parts]
    kk = len(mv)
    m = sum(x for x, _ in mv) / kk
    hw = 1.96 * math.sqrt(sum(v for _, v in mv)) / kk
    return m, hw, sum(len(d) for d in parts)


def paired_change(base, other, sign=1):
    """List of 100*sign*(other score - base score) over the common deals, deal by deal, seeds checked."""
    common = sorted(set(base) & set(other))
    assert len(common) == len(base) == len(other), (len(common), len(base), len(other))
    out = []
    for i in common:
        assert base[i]["seed"] == other[i]["seed"], (i, base[i]["seed"], other[i]["seed"])
        out.append(sign * 100.0 * (score(other[i]) - score(base[i])))
    return out


def cell_means(games, keys):
    return {k: sum(score(r) for r in games[k].values()) / len(games[k]) for k in keys}


def tau(S, nS, L, nL, keys):
    acc = 0.0
    for k in keys:
        acc += (S[k] - L[k]) ** 2 - L[k] * (1 - L[k]) / nL[k] - S[k] * (1 - S[k]) / nS[k]
    return 100 * math.sqrt(max(0.0, acc / len(keys)))


def deck_avgs(sc, keys):
    tot = {}
    for a, b in keys:
        tot.setdefault(a, []).append(sc[(a, b)])
        tot.setdefault(b, []).append(1 - sc[(a, b)])
    return {d: sum(v) / len(v) for d, v in tot.items()}


def pct(sorted_vals, q):
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals))))]
