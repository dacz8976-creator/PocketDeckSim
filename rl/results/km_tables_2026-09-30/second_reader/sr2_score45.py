"""Item 2: score45 (--rules v2) on the 45 cells, --old kta3 (the references) --new km3, with MY mixed-row composites
(sr1_cells.py). score45.py / score.py are the registered instrument and run unchanged; the one addition is a tap on
score.pct that records the unrounded percentiles it returns (the page is not altered), so the near-zero rule (step 4:
a ΔMSE bound within 5% of the interval's width of 0; the τ̂ 90% lower bound within 0.10 of -1.0) is read at more digits.
My own point arithmetic (τ, ΔMSE, the rule-v2 veto sizes, a delta-method sd) is printed beside, as a cross-check.
Writes OUT/sr2_score45_page[_repsN].txt (score45's own page) and OUT/sr2_score45[_repsN].txt."""
import sys, io, os, runpy, csv, json, math, contextlib
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30/second_reader")
from sr_lib import *

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
lines = []
p = lines.append
OLD = [KT + "/ec7e1a8_kta3_table.jsonl", KT + "/ec7e1a8_kta3_new17.jsonl"]
NEW = [B + "km3_table.jsonl", B + "km3_new17.jsonl"]

# ---------- my own point arithmetic (independent of score.py)
v2 = json.load(open(R + "/scoreboard_v2_2026-09-25/limitless_v2_dev.json", encoding="utf-8"))["cells"]
LIM = {tuple(k.split("|")): tuple(v) for k, v in v2.items()}
with open(R + "/gauntlet_runs_2026-09-26/gauntlet_cells.csv", encoding="utf-8", newline="") as f:
    rows = [r for r in csv.DictReader(f) if r["dataset"] == "development"]
for a, b in NEW17:
    m = [r for r in rows if r["a"] == a and r["b"] == b]
    assert len(m) == 1
    LIM[(a, b)] = (int(m[0]["W"]), int(m[0]["L"]), int(m[0]["T"]))
assert set(LIM) == set(CELLS45)
L = {k: (LIM[k][0] + 0.5 * LIM[k][2]) / sum(LIM[k]) for k in CELLS45}
nL = {k: sum(LIM[k]) for k in CELLS45}
O = by_key(rd(OLD[0]) + rd(OLD[1]), ab)
N = by_key(rd(NEW[0]) + rd(NEW[1]), ab)
So = {k: sum(sc(r) for r in O[k].values()) / 500 for k in CELLS45}
Sn = {k: sum(sc(r) for r in N[k].values()) / 500 for k in CELLS45}


def tau(S, keys):
    acc = sum((S[k] - L[k]) ** 2 - L[k] * (1 - L[k]) / nL[k] - S[k] * (1 - S[k]) / 500 for k in keys)
    return 100 * math.sqrt(max(0.0, acc / len(keys)))


def deck_avg(S, keys):
    t = {}
    for a, b in keys:
        t.setdefault(a, []).append(S[(a, b)])
        t.setdefault(b, []).append(1 - S[(a, b)])
    return {d: sum(v) / len(v) for d, v in t.items()}


QUAR = {("altaria", "sceptile")}
for label, keys in (("45 cells", CELLS45), ("44-cell decision set", [k for k in CELLS45 if k not in QUAR])):
    d_point = sum((Sn[k] - L[k]) ** 2 - (So[k] - L[k]) ** 2 for k in keys) / len(keys) * 1e4
    to, tn = tau(So, keys), tau(Sn, keys)
    grow = {k: 100 * (abs(Sn[k] - L[k]) - abs(So[k] - L[k])) for k in keys}
    do, dn, dl = deck_avg(So, keys), deck_avg(Sn, keys), deck_avg(L, keys)
    dg = {d: 100 * (abs(dn[d] - dl[d]) - abs(do[d] - dl[d])) for d in dl}
    var = 0.0
    for k in keys:
        a_, b_ = 2 * (Sn[k] - L[k]), -2 * (So[k] - L[k])
        z = [a_ * sc(N[k][i]) + b_ * sc(O[k][i]) for i in range(500)]
        var += mv(z)[1] + (2 * (So[k] - Sn[k])) ** 2 * L[k] * (1 - L[k]) / nL[k]
    sd = math.sqrt(var) / len(keys) * 1e4
    p(f"[mine] {label}: dMSE (km3 - kta3) {d_point:+.4f} points^2 (delta-method sd {sd:.3f}: {d_point - 1.96 * sd:+.2f} to {d_point + 1.96 * sd:+.2f});"
      f" real error kta3 {to:.4f} km3 {tn:.4f}; margin (kta3 - km3) {to - tn:+.4f}")
    p(f"[mine]   cell misses growing > 6: {[(k, round(g, 2)) for k, g in grow.items() if g > 6] or 'none'} (largest {max(grow.values()):+.2f} at {max(grow, key=grow.get)});"
      f" deck gaps growing > 2: {[(d, round(g, 2)) for d, g in dg.items() if g > 2] or 'none'} (largest {max(dg.values()):+.2f} at {max(dg, key=dg.get)})")
    if label == "45 cells":
        for d in DECKS10:
            p(f"[mine]     deck {d:>17}: kta3 {100 * do[d]:6.2f} -> km3 {100 * dn[d]:6.2f}; Limitless {100 * dl[d]:6.2f}; change in gap {dg[d]:+.3f}")

# ---------- the instrument, unchanged, with a tap on pct
SCORE45 = R + "/kpf_2026-09-26/reading/score45.py"
sys.path.insert(0, R + "/table_readings_2026-09-24")
import score as S  # the module score45 imports (cached, so score45 gets this same object)
_orig = S.pct
CAP = []


def _tap(vals, q):
    x = _orig(vals, q)
    CAP.append((q, x))
    return x


S.pct = _tap
TAU = []
_pp = S.pass_parts


def _tap_pp(Sx, nS, keys):
    r = _pp(Sx, nS, keys)
    TAU.append((len(keys), r[0]))
    return r


S.pass_parts = _tap_pp
args = ["--rules", "v2", "--old-games", *OLD, "--new-games", *NEW, "--old", "kta3", "--new", "km3",
        "--mixed", SCR + "/sr_mixed_first.jsonl", SCR + "/sr_mixed_second.jsonl", "--reps", str(REPS)]
sys.argv = [SCORE45] + args
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(SCORE45, run_name="__main__")
page = buf.getvalue()
suffix = "" if REPS == 4000 else f"_reps{REPS}"
open(OUT + f"/sr2_score45_page{suffix}.txt", "w", encoding="utf-8").write(page)

names = ["dMSE lo (2.5%)", "dMSE hi (97.5%)", "dMSE by event lo", "dMSE by event hi",
         "tau margin lo (5%)", "tau margin hi (95%)", "tau by event lo", "tau by event hi"]
p(f"[tap] score.pct calls recorded: {len(CAP)} (q values {[q for q, _ in CAP]})")
assert len(CAP) == 16, len(CAP)
for bi, label in enumerate(("45 cells (all)", "44-cell decision set")):
    blk = CAP[8 * bi: 8 * bi + 8]
    p(f"[score45 unrounded, --reps {REPS}] {label}: " + "; ".join(f"{n} {x:+.5f}" for n, (_, x) in zip(names, blk)))
    lo, hi = blk[0][1], blk[1][1]
    w = hi - lo
    lab = "wholly BELOW zero (outcome 1)" if hi < 0 else ("wholly ABOVE zero (outcome 2)" if lo > 0 else "SPANS zero (outcome 3, the fallback)")
    p(f"   label: {lab}; width {w:.4f}; 5% of width {0.05 * w:.4f}; upper edge within 5% of 0: {abs(hi) <= 0.05 * w} (|hi| = {abs(hi):.4f});"
      f" lower edge within: {abs(lo) <= 0.05 * w} (|lo| = {abs(lo):.4f}); tau lower bound {blk[4][1]:+.5f}, within 0.10 of -1.0: {abs(blk[4][1] + 1.0) <= 0.10}"
      f" (distance {blk[4][1] + 1.0:+.4f}); sd from the interval {w / 3.92:.4f}, MDE50 {1.96 * w / 3.92:.3f}, MDE80 {2.80 * w / 3.92:.3f}")
    t = [x for n_, x in TAU if n_ == (45 if bi == 0 else 44)]
    if len(t) >= 2:
        sdv = w / 3.92
        p(f"   [tap] score.py's real error unrounded: kta3 {t[0]:.5f}, km3 {t[1]:.5f}; detectable size as real error (sqrt(kta3^2 - delta)):"
          f" MDE50 {t[0]:.2f} -> {math.sqrt(t[0] ** 2 - 1.96 * sdv):.3f}, MDE80 {t[0]:.2f} -> {math.sqrt(t[0] ** 2 - 2.80 * sdv):.3f}"
          f" (from the rounded 13.80: {math.sqrt(13.80 ** 2 - 1.96 * sdv):.3f} and {math.sqrt(13.80 ** 2 - 2.80 * sdv):.3f})")
p(f"[tap] score.pass_parts calls (keys, real error): {[(n_, round(x, 5)) for n_, x in TAU]}")
# my page against the first reader's saved page, line by line
disk = open(K + "/score45_km3_vs_kta3.txt", encoding="utf-8").read().splitlines()
mine_pg = page.splitlines()
dl = [(a, b) for a, b in zip(disk, mine_pg) if a != b]
theirs_reps = json.load(open(K + "/score45_km3_vs_kta3.txt.reps", encoding="utf-8"))["reps"]
p(f"first reader's page score45_km3_vs_kta3.txt (--reps {theirs_reps}): {len(disk)} lines, mine {len(mine_pg)}; differing lines {len(dl)}:")
for a, b in dl:
    p("   theirs: " + a[:200])
    p("   mine:   " + b[:200])
p("")
p("score45's page (" + OUT + f"/sr2_score45_page{suffix}.txt), key lines:")
for ln in page.splitlines():
    if any(s in ln for s in ("== ", "dMSE", "real error", "veto", "VETO", "ADOPTION", "Mixed rows:", "margin")):
        p("   " + ln)
write(f"sr2_score45{suffix}.txt", lines)
