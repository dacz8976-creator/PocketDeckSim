"""Reconciler: score45 (the registered instrument, unchanged) at --reps 20000 on the fresh 45 cells, with taps on
score.pct (unrounded bootstrap percentiles) and score.pass_parts (unrounded real error per bot per block).
Mixed rows: the second reader's composites (shown equal to the first reader's on every kept field).
Writes only into this scratch folder. Also: the B2e both-sides split held-out (pairings 0-47) vs Dustin's (48-95)."""
import sys, io, os, runpy, json, math, contextlib

REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
R = REPO + "/rl/results"
T = R + "/kta_tables_2026-09-29/ec7e1a8_fresh_"
SCR = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kta2"
OUT = SCR + "/reconciler"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 20000

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
            "--old-games", T + "kog3_table.jsonl", T + "kog3_new17.jsonl",
            "--new-games", T + "kta3_table.jsonl", T + "kta3_new17.jsonl",
            "--old", "kog3", "--new", "kta3",
            "--mixed", SCR + "/second-reader/sr_mixed_first.jsonl", SCR + "/second-reader/sr_mixed_second.jsonl",
            "--reps", str(REPS)]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(SCORE45, run_name="__main__")
page = buf.getvalue()
open(OUT + f"/rc_page_reps{REPS}.txt", "w", encoding="utf-8").write(page)

out = []
p = out.append
p(f"pct calls: {len(CAP)}; pass_parts calls: {TAU}")
names = ["dMSE lo", "dMSE hi", "dMSE_e lo", "dMSE_e hi", "tau lo", "tau hi", "tau_e lo", "tau_e hi"]
for bi, label in enumerate(("45 cells", "44-cell set")):
    blk = CAP[8 * bi: 8 * bi + 8]
    p(f"[reps {REPS}] {label}: " + "; ".join(f"{n} {x:+.4f}" for n, (_, x) in zip(names, blk)))
    lo, hi = blk[0][1], blk[1][1]
    w = hi - lo
    lab = "BELOW" if hi < 0 else ("ABOVE" if lo > 0 else "SPANS")
    sd = w / 3.92
    p(f"   label {lab}; width {w:.4f}; 5% width {0.05*w:.4f}; hi near: {abs(hi) <= 0.05*w}; lo near: {abs(lo) <= 0.05*w}; "
      f"tau lo near -1: {abs(blk[4][1] + 1) <= 0.10}; sd {sd:.4f} MDE50 {1.96*sd:.4f} MDE80 {2.8*sd:.4f}")
    t_old = [t for n, t in TAU if n == (45 if bi == 0 else 44)]
    if t_old:
        k = t_old[0]
        p(f"   kog3 real error unrounded {k:.4f}; kta3 {t_old[1]:.4f}")
        for base in (k, 13.60):
            p(f"   from {base:.3f}: MDE50 -> {math.sqrt(base**2 - 1.96*sd):.3f}; MDE80 -> {math.sqrt(base**2 - 2.8*sd):.3f}")
# the 4000-rep bounds as the second reader tapped them (sr2_score45.txt) for the conversion at 4000
for lo, hi in ((-8.9830, 0.0655),):
    sd = (hi - lo) / 3.92
    k = [t for n, t in TAU if n == 45][0]
    p(f"[reps 4000, second reader's tapped bounds] sd {sd:.4f}; from {k:.3f}: {math.sqrt(k**2-1.96*sd):.3f}, {math.sqrt(k**2-2.8*sd):.3f};"
      f" from 13.600: {math.sqrt(13.6**2-1.96*sd):.3f}, {math.sqrt(13.6**2-2.8*sd):.3f}")

# compare with the on-disk 20000 page (read only)
disk = open(R + "/kta_tables_2026-09-29/score45_kta3_vs_kog3.txt", encoding="utf-8").read().splitlines()
mine = page.splitlines()
diff = [(a, b) for a, b in zip(disk, mine) if a != b]
p(f"on-disk page lines {len(disk)}, mine {len(mine)}; differing lines {len(diff)}:")
for a, b in diff:
    p("   disk: " + a[:220])
    p("   mine: " + b[:220])


# B2e split (N4)
def rd(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


o = {(r["pairing"], r["i"]): r for r in rd(T + "b2e_kog3.jsonl")}
n = {(r["pairing"], r["i"]): r for r in rd(T + "b2e_kta3.jsonl")}
assert set(o) == set(n)
dif = [k for k in o if o[k]["moves"] != n[k]["moves"]]
p(f"B2e both-sides differing: {len(dif)}; held-out (0-47) {sum(1 for k in dif if k[0] < 48)}; Dustin's (48-95) {sum(1 for k in dif if k[0] >= 48)};"
  f" pairings {sorted({k[0] for k in dif})}")
open(OUT + f"/rc_score45_reps{REPS}.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
