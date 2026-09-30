"""Step 2: score45 (--rules v2, --reps 4000) on the fresh 45 cells with MY composites (sr1_cells.py), plus my own
arithmetic beside it. score45.py / score.py are the registered instrument and run unchanged; the only addition is a
tap on score.pct that records the unrounded percentiles it returns (its output is not altered), so the near-zero rule
(5.4) can be read at more digits than the page prints.
Writes OUT/sr2_score45_page.txt (score45's own page) and OUT/sr2_score45.txt (mine)."""
import sys, io, os, runpy, csv, json, math, contextlib
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kta_tables_2026-09-29/second_reader")
from sr_lib import *

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
lines = []
p = lines.append

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
O = by_key(rd(F + "kog3_table.jsonl") + rd(F + "kog3_new17.jsonl"), ab)
N = by_key(rd(F + "kta3_table.jsonl") + rd(F + "kta3_new17.jsonl"), ab)
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
    # delta-method sd of the dMSE (simulator deals + Limitless binomial), a cross-check on the bootstrap width
    var = 0.0
    for k in keys:
        a_, b_ = 2 * (Sn[k] - L[k]), -2 * (So[k] - L[k])
        z = [a_ * sc(N[k][i]) + b_ * sc(O[k][i]) for i in range(500)]
        var += mv(z)[1] + (2 * (So[k] - Sn[k])) ** 2 * L[k] * (1 - L[k]) / nL[k]
    sd = math.sqrt(var) / len(keys) * 1e4
    p(f"[mine] {label}: dMSE (kta3 - kog3) {d_point:+.3f} points^2 (delta-method sd {sd:.2f}: {d_point - 1.96*sd:+.1f} to {d_point + 1.96*sd:+.1f});"
      f" real error kog3 {to:.3f} kta3 {tn:.3f}; margin (kog3 - kta3) {to - tn:+.3f}")
    p(f"[mine]   cell misses growing > 6: {[(k, round(g, 2)) for k, g in grow.items() if g > 6] or 'none'} (largest {max(grow.values()):+.2f});"
      f" deck gaps growing > 2: {[(d, round(g, 2)) for d, g in dg.items() if g > 2] or 'none'} (largest {max(dg.values()):+.2f})")
    if label == "45 cells":
        for d in DECKS10:
            p(f"[mine]     deck {d:>17}: kog3 {100*do[d]:5.1f} -> kta3 {100*dn[d]:5.1f}; Limitless {100*dl[d]:5.1f}; change in gap {dg[d]:+.2f}")

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
args = ["--rules", "v2",
        "--old-games", F + "kog3_table.jsonl", F + "kog3_new17.jsonl",
        "--new-games", F + "kta3_table.jsonl", F + "kta3_new17.jsonl",
        "--old", "kog3", "--new", "kta3",
        "--mixed", SCR + "/sr_mixed_first.jsonl", SCR + "/sr_mixed_second.jsonl",
        "--reps", str(REPS)]
sys.argv = [SCORE45] + args
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(SCORE45, run_name="__main__")
page = buf.getvalue()
suffix = "" if REPS == 4000 else f"_reps{REPS}"
open(OUT + f"/sr2_score45_page{suffix}.txt", "w", encoding="utf-8").write(page)

# score.py's order per block: dm .025, dm .975, dm_e .025, dm_e .975, dt .05, dt .95, dt_e .05, dt_e .95
names = ["dMSE lo (2.5%)", "dMSE hi (97.5%)", "dMSE by event lo", "dMSE by event hi",
         "tau margin lo (5%)", "tau margin hi (95%)", "tau by event lo", "tau by event hi"]
assert len(CAP) == 16, len(CAP)
for bi, label in enumerate(("45 cells (all)", "44-cell decision set")):
    blk = CAP[8 * bi: 8 * bi + 8]
    p(f"[score45 unrounded, --reps {REPS}] {label}: " + "; ".join(f"{n} {x:+.4f}" for n, (_, x) in zip(names, blk)))
    lo, hi = blk[0][1], blk[1][1]
    w = hi - lo
    near_hi = abs(hi) <= 0.05 * w
    near_lo = abs(lo) <= 0.05 * w
    label3 = "wholly BELOW zero (outcome 1)" if hi < 0 else ("wholly ABOVE zero (outcome 2)" if lo > 0 else "SPANS zero (outcome 3, the fallback)")
    p(f"   label at these reps: {label3}; width {w:.3f}, 5% of width {0.05*w:.3f}; upper edge within 5% of 0: {near_hi}; lower edge within: {near_lo};"
      f" tau lower bound within 0.10 of -1.0: {abs(blk[4][1] + 1.0) <= 0.10}")
p("")
p("score45's page (" + OUT + f"/sr2_score45_page{suffix}.txt), key lines:")
for ln in page.splitlines():
    if any(s in ln for s in ("== ", "dMSE", "real error", "veto", "ADOPTION", "Mixed rows:")):
        p("   " + ln)
open(OUT + f"/sr2_score45{suffix}.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
