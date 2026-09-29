"""Step 1: the four footprints (moves differing from kog3 on the 45 cells) and the routes; plus baseline identity checks."""
import sys
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kt2/second-reader")
from sr_lib import *

KOG = [R + "/kog_composition_2026-09-27/table_kog3.jsonl", R + "/kog_composition_2026-09-27/new17_kog3.jsonl"]
base = load(KOG, ab)
assert set(base) == set(CELLS45)
print("kog3 baseline: cells", len(base), "games", sum(len(c) for c in base.values()))

# Limitless cross-checks
lim = limitless45()
tot_n = sum(sum(v) for v in lim.values())
print("Limitless dev cells: 45; matches total", tot_n)
ev = json.load(open(R + "/scoreboard_v3_2026-09-27/limitless_45_dev_events.json", encoding="utf-8"))["events"]
bad = 0
for k in CELLS45:
    s = [0, 0, 0]
    for e in ev:
        v = e["cells"].get(f"{k[0]}|{k[1]}")
        if v:
            for j in range(3):
                s[j] += v[j]
    if tuple(s) != tuple(lim[k]):
        bad += 1
print("cells whose event sums differ from my Limitless cells:", bad)
fz = list(csv.DictReader(open(R + "/scoreboard_v3_2026-09-27/frozen_cells.csv", encoding="utf-8", newline="")))
mx = 0.0
for r in fz:
    k = (r["a"], r["b"])
    L, n = lim_rate(lim, k)
    mx = max(mx, abs(100 * L - float(r["limitless_dev"])))
    assert n == int(r["n_dev"]), (k, n, r["n_dev"])
print("frozen_cells.csv: rows", len(fz), " max |my Limitless dev % - csv| =", round(mx, 3))

codes = ["kt3", "kta3", "ktb3", "ktc3"]
fp = {}
for c in codes:
    g = load([f"{K}/{B}_{c}_table.jsonl", f"{K}/{B}_{c}_new17.jsonl"], ab)
    assert set(g) == set(CELLS45)
    diff_moves = {}
    diff_dec = {}
    diff_res = {}
    for k in CELLS45:
        assert set(g[k]) == set(base[k])
        dm = dd = dr = 0
        for i in base[k]:
            assert g[k][i]["seed"] == base[k][i]["seed"]
            dm += g[k][i]["moves"] != base[k][i]["moves"]
            dd += g[k][i]["decisions"] != base[k][i]["decisions"]
            dr += score(g[k][i]) != score(base[k][i])
        diff_moves[k], diff_dec[k], diff_res[k] = dm, dd, dr
    fp[c] = diff_moves
    N = sum(len(base[k]) for k in CELLS45)
    tm, td, tr = sum(diff_moves.values()), sum(diff_dec.values()), sum(diff_res.values())
    nz = [k for k in CELLS45 if diff_moves[k] > 0]
    print(f"\n{c}: moves differ in {tm} of {N} = {100*tm/N:.2f}%  | decisions differ {td} = {100*td/N:.2f}% | first-deck score differs {tr} = {100*tr/N:.2f}%")
    t28 = sum(diff_moves[k] for k in TABLE28)
    n17 = sum(diff_moves[k] for k in NEW17)
    print(f"   table 28 cells: {t28} of 14000 = {100*t28/14000:.2f}%; new 17 cells: {n17} of 8500 = {100*n17/8500:.2f}%")
    print(f"   route: {'reserve route (under 15%)' if 100*tm/N < 15 else 'ordinary adoption rule (15% or more)'}; non-zero cells: {len(nz)} of 45")
    if c in ("kta3", "ktc3"):
        for k in nz:
            print(f"     {k[0]} v {k[1]}: {diff_moves[k]} moves-differ, {diff_dec[k]} decisions-differ, {diff_res[k]} result-differs")
    else:
        # cells with the biggest and smallest footprint
        srt = sorted(CELLS45, key=lambda k: diff_moves[k])
        print("   lowest cells:", [(f"{k[0]}v{k[1]}", diff_moves[k]) for k in srt[:6]])
        print("   highest cells:", [(f"{k[0]}v{k[1]}", diff_moves[k]) for k in srt[-4:]])
        print("   zero cells:", [f"{k[0]}v{k[1]}" for k in CELLS45 if diff_moves[k] == 0])

# identity of kog3 at the kt build against the baselines
print("\n--- kog3 at the kt build (ec7e1a8) vs the baselines")
def ident(idpath, basepaths, keyfn, label, ilim=None):
    g = load([idpath], keyfn)
    b = load(basepaths, keyfn)
    n = same = 0
    missing = 0
    for k, c in g.items():
        for i, r in c.items():
            if ilim is not None and i >= ilim:
                continue
            if k not in b or i not in b[k]:
                missing += 1
                continue
            n += 1
            same += (r["moves"] == b[k][i]["moves"] and r["seed"] == b[k][i]["seed"] and score(r) == score(b[k][i]))
    print(f"   {label}: {same} of {n} identical (moves, seed, score); {missing} missing in baseline")
ident(f"{K}/{B}_id_kog3_500.jsonl", [KOG[0]], ab, "table")
ident(f"{K}/{B}_id_kog3_new17.jsonl", [KOG[1]], ab, "new17")
ident(f"{K}/{B}_id_kog3_b2e40.jsonl", [SCR + "/data/b2e_kog3.jsonl"], pairing, "b2e i<40")
ident(f"{K}/{B}_id_kog3_scz40.jsonl", [R + "/koh_2026-09-28/laptop_runs/scizor_kog3.jsonl"], pairing, "scizor i<40")
for nm, f in (("v-lucario_2", "var_v-lucario_2_kog3"), ("v-suicune_2", "var_v-suicune_2_kog3"), ("v-weezing_2", "var_v-weezing_2_kog3"), ("l-charizardy", "var_l-charizardy_kog3")):
    pth = {"v-lucario_2": "v-lucario_240", "v-suicune_2": "v-suicune_240", "v-weezing_2": "v-weezing_240", "l-charizardy": "l-charizardy40"}[nm]
    ident(f"{K}/{B}_id_kog3_var_{pth}.jsonl", [R + f"/koh_2026-09-28/laptop_runs/{f}.jsonl"], pairing, f"second list {nm}")
