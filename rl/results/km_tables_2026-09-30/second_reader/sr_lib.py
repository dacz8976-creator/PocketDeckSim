"""km's second reader: shared helpers.
Written from the registration (REGISTRATION_DRAFT.md: top block, Amendment 1, Amendment 2, section 5, section 6),
RUN5's frame, km_config.json and the raw game files. read_km.py, footprint_km.py and km_check.py are not opened or
imported. Pure standard library. Reads game files only; writes only this folder's outputs and scratch composites."""
import csv, hashlib, itertools, json, math, os

REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
R = REPO + "/rl/results"
K = R + "/km_tables_2026-09-30"           # km's games (B = 1f6319e)
KT = R + "/kt_tables_2026-09-28"          # kta3's references (ec7e1a8)
OUT = K + "/second_reader"
SCR = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_km2r/second-reader"
B = K + "/1f6319e_"
CONFIG = R + "/trainer_pricing_2026-09-28/km_run/km_config.json"

NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
PANEL_ORDER = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
TABLE28 = list(itertools.combinations(NAMES, 2))                       # table pairing p = TABLE28[p]
NEW17 = [(d, o) for d in ("rayquaza", "altaria_greninja") for o in PANEL_ORDER] + [("rayquaza", "altaria_greninja")]
NEW_PAIRING = {k: 8 + j for j, k in enumerate(NEW17)}                  # new_decks.tsv pairings 8-24
CELLS45 = TABLE28 + NEW17
DECKS10 = NAMES + ["rayquaza", "altaria_greninja"]
TABLE_BASE, NEW_BASE, B2E_BASE, D_BASE = 72_000_000, 21_108_000_000, 21_106_000_000, 22_900_000_000

# The 17 named cells (step 3): the cells holding the panel Altaria or Lucario list.
NAMED17 = [k for k in CELLS45 if "altaria" in k or "lucario" in k]
# M1 (Arena, Lucario's side): table 2, 8, 13, 18, 19, 20, 21; new_decks 8, 16.  M2 (Training Area, Altaria's side):
# table 0, 1, 3, 4; new_decks 9 (registration step 3; Amendment 2).
M1_CELLS = [("table", p) for p in (2, 8, 13, 18, 19, 20, 21)] + [("new", p) for p in (8, 16)]
M2_CELLS = [("table", p) for p in (0, 1, 3, 4)] + [("new", 9)]
# (d)'s nine rows: 0-6 the table's Lucario cells in increasing pairing, 7 Rayquaza v Lucario, 8 Alt/Gren v Lucario.
D_ROWS = [("table", p) for p in (2, 8, 13, 18, 19, 20, 21)] + [("new", 8), ("new", 16)]

# Dustin's coverage condition (block item 7): complete move fingerprint, both decks, seed, seats. Winners never used.
COV_FIELDS = ("moves", "a", "b", "a_file", "b_file", "seed", "first_seat")


def cell_of(src, p):
    return TABLE28[p] if src == "table" else NEW17[p - 8]


def rd(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def by_key(recs, keyfn, ikey="i"):
    """{cellkey: {i: record}}; refuses duplicates."""
    out = {}
    for r in recs:
        c = out.setdefault(keyfn(r), {})
        if r[ikey] in c:
            raise SystemExit(f"duplicate deal {keyfn(r)} {r[ikey]}")
        c[r[ikey]] = r
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


def mv(d):
    """mean and variance of the mean (n - 1 denominator), as read_koh.py's paired() takes them."""
    n = len(d)
    m = sum(d) / n
    v = sum((x - m) ** 2 for x in d) / (n - 1) / n if n > 1 else 0.0
    return m, v


def pool(parts):
    """Equal-weight pool over rows/cells: mean of row means, 95% half-width 1.96*sqrt(sum var)/k, deals."""
    s = [mv(d) for d in parts]
    k = len(s)
    return sum(m for m, _ in s) / k, 1.96 * math.sqrt(sum(v for _, v in s)) / k, sum(len(d) for d in parts)


def paired(base, other, sign=1):
    """Per-deal change in points (100 x score), other minus base; deals and seeds must match."""
    assert set(base) == set(other), (len(base), len(other))
    out = []
    for i in sorted(base):
        assert base[i]["seed"] == other[i]["seed"], (i, base[i]["seed"], other[i]["seed"])
        out.append(sign * 100.0 * (sc(other[i]) - sc(base[i])))
    return out


def write(name, lines):
    open(OUT + "/" + name, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
