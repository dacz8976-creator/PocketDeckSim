"""kta's second reader: shared helpers (written from REGISTRATION.md and the raw game files; read_kta.py not opened).
Pure stdlib. Reads game files only; the only files written are this folder's outputs and the scratch composites."""
import csv, hashlib, itertools, json, math, os

REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
R = REPO + "/rl/results"
T = R + "/kta_tables_2026-09-29"
KT = R + "/kt_tables_2026-09-28"
OUT = T + "/second_reader"
SCR = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kta2/second-reader"
F = T + "/ec7e1a8_fresh_"

NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
PANEL_ORDER = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
TABLE28 = list(itertools.combinations(NAMES, 2))
NEW17 = [(d, o) for d in ("rayquaza", "altaria_greninja") for o in PANEL_ORDER] + [("rayquaza", "altaria_greninja")]
CELLS45 = TABLE28 + NEW17
DECKS10 = NAMES + ["rayquaza", "altaria_greninja"]

# Section 2: the lists that carry a switch-1 card. On the 45 cells: Suicune's (Frigibax, Stiffen) and the scoreboard
# Rayquaza list's (Gouging Fire). So a cell is reachable iff it contains suicune or rayquaza.
REACH_DECKS = {"suicune", "rayquaza"}

# The comparison fields of Dustin's coverage condition (top block item 3): the complete move fingerprint, both decks
# (names and deck files), the seed, the seats. Winners are never used.
COV_FIELDS = ("moves", "a", "b", "a_file", "b_file", "seed", "first_seat")


def rd(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def by_key(recs, keyfn):
    """{cellkey: {i: record}}; refuses duplicates."""
    out = {}
    for r in recs:
        c = out.setdefault(keyfn(r), {})
        if r["i"] in c:
            raise SystemExit(f"duplicate deal {keyfn(r)} {r['i']}")
        c[r["i"]] = r
    return out


def ab(r):
    return (r["a"], r["b"])


def pairing(r):
    return r["pairing"]


def sc(r):
    return float(r["first_deck_score"])


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


# ----- statistics -----
def mv(d):
    """mean and variance of the mean (n - 1 denominator)."""
    n = len(d)
    m = sum(d) / n
    v = sum((x - m) ** 2 for x in d) / (n - 1) / n if n > 1 else 0.0
    return m, v


def pool(parts):
    """Stratified pool over rows/cells: mean of row means, 95% half-width 1.96*sqrt(sum var)/k, deals."""
    s = [mv(d) for d in parts]
    k = len(s)
    return sum(m for m, _ in s) / k, 1.96 * math.sqrt(sum(v for _, v in s)) / k, sum(len(d) for d in parts)


def paired(base, other, sign=1):
    """Per-deal change in points (100 x score), other minus base, over every deal; deals and seeds must match."""
    assert set(base) == set(other), (len(base), len(other))
    out = []
    for i in sorted(base):
        assert base[i]["seed"] == other[i]["seed"], (i, base[i]["seed"], other[i]["seed"])
        out.append(sign * 100.0 * (sc(other[i]) - sc(base[i])))
    return out


def fmt_pm(m, h, nd=2):
    return f"{m:+.{nd}f} +/- {h:.{nd}f}"
