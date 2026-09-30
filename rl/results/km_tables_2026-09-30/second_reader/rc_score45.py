"""Reconciler (Sept 30): score45.py (the registered instrument, unchanged) at --reps 4000 on the first reader's own
score45 inputs, with taps on score.pct (unrounded bootstrap percentiles) and score.pass_parts (unrounded real error per
bot per block), to settle the second reader's one DISAGREE (item 2b: detectable size as real error). Writes the page to
the scratch folder given as argv[1] and compares it with the committed score45_km3_vs_kta3.txt."""
import sys, io, runpy, math, contextlib

REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
R = REPO + "/rl/results"
KT = R + "/kt_tables_2026-09-28/ec7e1a8_"
KM = R + "/km_tables_2026-09-30/"
SCR = sys.argv[1]
SCORE45 = R + "/kpf_2026-09-26/reading/score45.py"
sys.path.insert(0, R + "/table_readings_2026-09-24")
import score as S

CAP, TAU = [], []
_pct, _pp = S.pct, S.pass_parts


def tap_pct(vals, q):
    x = _pct(vals, q)
    CAP.append((q, x))
    return x


def tap_pp(Sx, nS, keys):
    r = _pp(Sx, nS, keys)
    TAU.append((len(keys), r[0]))
    return r


S.pct, S.pass_parts = tap_pct, tap_pp
sys.argv = [SCORE45, "--rules", "v2",
            "--old-games", KT + "kta3_table.jsonl", KT + "kta3_new17.jsonl",
            "--new-games", KM + "1f6319e_km3_table.jsonl", KM + "1f6319e_km3_new17.jsonl",
            "--old", "kta3", "--new", "km3",
            "--mixed", KM + "score45_inputs/1f6319e_km3_mixed_first_composite.jsonl",
            KM + "score45_inputs/1f6319e_km3_mixed_second_composite.jsonl",
            "--reps", "4000"]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(SCORE45, run_name="__main__")
page = buf.getvalue()
open(SCR + "/rc_page_reps4000.txt", "w", encoding="utf-8").write(page)

out = []
p = out.append
p(f"pct calls: {len(CAP)}; pass_parts calls (cells, real error): {[(n, round(t, 6)) for n, t in TAU]}")
names = ["dMSE lo", "dMSE hi", "dMSE_e lo", "dMSE_e hi", "tau lo", "tau hi", "tau_e lo", "tau_e hi"]
for bi, label in enumerate(("45 cells", "44-cell set")):
    blk = CAP[8 * bi: 8 * bi + 8]
    p(f"[reps 4000] {label}: " + "; ".join(f"{n} {x:+.4f}" for n, (_, x) in zip(names, blk)))
    lo, hi = blk[0][1], blk[1][1]
    w = hi - lo
    lab = "BELOW" if hi < 0 else ("ABOVE" if lo > 0 else "SPANS")
    sd = w / 3.92
    p(f"   label {lab}; width {w:.4f}; 5% of width {0.05 * w:.4f}; hi near 0: {abs(hi) <= 0.05 * w}; lo near 0: "
      f"{abs(lo) <= 0.05 * w}; tau lo within 0.10 of -1: {abs(blk[4][1] + 1) <= 0.10}; sd {sd:.4f} MDE50 {1.96 * sd:.4f} "
      f"MDE80 {2.8 * sd:.4f}")
    ts = [t for n, t in TAU if n == (45 if bi == 0 else 44)]
    if ts:
        k = ts[0]
        p(f"   kta3 real error unrounded {k:.4f}; km3 {ts[1]:.4f}")
        for base in (k, 13.80):
            p(f"   from {base:.4f}: MDE50 -> {math.sqrt(base ** 2 - 1.96 * sd):.4f}; MDE80 -> {math.sqrt(base ** 2 - 2.8 * sd):.4f}")
disk = open(KM + "score45_km3_vs_kta3.txt", encoding="utf-8").read().splitlines()
mine = page.splitlines()
diff = [(a, b) for a, b in zip(disk, mine) if a != b]
p(f"committed page lines {len(disk)}, mine {len(mine)}; differing lines {len(diff)}:")
for a, b in diff:
    p("   committed: " + a[:200])
    p("   mine:      " + b[:200])
open(KM + "second_reader/rc_score45.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
