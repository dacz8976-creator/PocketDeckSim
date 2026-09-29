"""Clause (c), clause (d), Suicune's reported side, and coverage (Dustin's rule) for one code. usage: sr_step3.py CODE"""
import sys
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kt2/second-reader")
from sr_lib import *

code = sys.argv[1]
lim = limitless45()
KOG = [R + "/kog_composition_2026-09-27/table_kog3.jsonl", R + "/kog_composition_2026-09-27/new17_kog3.jsonl"]
O_g = load(KOG, ab)
N_g = load([f"{K}/{B}_{code}_table.jsonl", f"{K}/{B}_{code}_new17.jsonl"], ab)
MF = load([f"{K}/{B}_mixed_table_{code}_first.jsonl", f"{K}/{B}_mixed_new17_{code}_first.jsonl"], ab)
MS = load([f"{K}/{B}_mixed_table_{code}_second.jsonl", f"{K}/{B}_mixed_new17_{code}_second.jsonl"], ab)
fpc = {k: sum(N_g[k][i]["moves"] != O_g[k][i]["moves"] for i in O_g[k]) for k in CELLS45}
own = {}
for k in CELLS45:
    for i in O_g[k]:
        assert MF[k][i]["seed"] == O_g[k][i]["seed"] == MS[k][i]["seed"]
    own[k] = {k[0]: paired_change(O_g[k], MF[k], +1), k[1]: paired_change(O_g[k], MS[k], -1)}

print(f"##### {code}")
# ---- clause (c)
nz = [k for k in CELLS45 if fpc[k] > 0]
print(f"\n--- clause (c): own side per meta deck, pooled over the {len(nz)} cells where {code}'s footprint is non-zero (mixed rows, both directions)")
flag_c = []
for d in DECKS10:
    dk = [k for k in nz if d in k]
    if not dk:
        print(f"   {d:>17}: no non-zero cell")
        continue
    m, h, n = pool([own[k][d] for k in dk])
    w = m < -h
    if w:
        flag_c.append(d)
    print(f"   {d:>17}: own side {m:+6.2f} ± {h:4.2f} over {len(dk)} cells ({n:,} deals){'   WORSE BEYOND NOISE' if w else ''}{'   (better beyond noise)' if m > h else ''}")
print("   decks worse beyond noise:", flag_c or "none")
print("   per cell-side (deck in cell): mean ± 95% half-width; flagged if worse beyond noise")
cell_flag = []
for k in nz:
    for d in k:
        m, h, n = pool([own[k][d]])
        w = m < -h
        if w:
            cell_flag.append((k, d, m, h))
        print(f"     {k[0]:>17} v {k[1]:<17} {d:>17}: {m:+6.2f} ± {h:4.2f}{'  <-- worse' if w else ''}{'  (better)' if m > h else ''}")
print("   cell-sides worse beyond noise:", [(f'{k[0]} v {k[1]}', d, round(m, 2), round(h, 2)) for k, d, m, h in cell_flag] or "none")

# ---- Suicune reported
sc = [k for k in CELLS45 if "suicune" in k]
print(f"\n--- Suicune's own side on its {len(sc)} rows, {code} v kog3 (mixed rows)")
m, h, n = pool([own[k]["suicune"] for k in sc])
print(f"   pooled: {m:+.2f} ± {h:.2f} over {len(sc)} cells ({n:,} deals)")
for k in sc:
    m1, h1, _ = pool([own[k]["suicune"]])
    print(f"     {k[0]} v {k[1]}: footprint {fpc[k]}, suicune own side {m1:+.2f} ± {h1:.2f}")
O = cell_means(O_g, CELLS45)
Nn = cell_means(N_g, CELLS45)
print("   Suicune's real cells (first-named deck's score; Limitless dev), sim kog3 -> sim", code)
tot_b = tot_a = 0.0
for k in sc:
    Lr, nl = lim_rate(lim, k)
    mis_b, mis_a = 100 * (O[k] - Lr), 100 * (Nn[k] - Lr)
    tot_b += abs(mis_b); tot_a += abs(mis_a)
    print(f"     {k[0]:>17} v {k[1]:<10} Limitless {100*Lr:5.1f} (n {nl:3d})  kog3 {100*O[k]:5.1f} ({mis_b:+5.1f})  {code} {100*Nn[k]:5.1f} ({mis_a:+5.1f})")
print(f"   mean |miss| over the 9: kog3 {tot_b/len(sc):.2f} -> {code} {tot_a/len(sc):.2f}")
rq = [k for k in CELLS45 if "rayquaza" in k]
tb = ta = 0.0
for k in rq:
    Lr, nl = lim_rate(lim, k)
    tb += abs(100 * (O[k] - Lr)); ta += abs(100 * (Nn[k] - Lr))
print(f"   the scoreboard's Rayquaza cells (9): mean |miss| kog3 {tb/9:.2f} -> {code} {ta/9:.2f}  (reported only; a different list from the census list)")

# ---- clause (d)
D_base = load([f"{K}/{B}_d_kog3.jsonl"], pairing)
D_new = load([f"{K}/{B}_d_{code}.jsonl"], pairing)
print(f"\n--- clause (d): the census Rayquaza list's own side, {code} v kog3, paired by deal, 8 rows")
parts = []
better = worse = 0
for p in sorted(D_base):
    assert set(D_base[p]) == set(D_new[p])
    for i in D_base[p]:
        r0, r1 = D_base[p][i], D_new[p][i]
        assert r0["seed"] == r1["seed"] and r0["a"] == r1["a"] == "c-rayquaza"
        assert (r0["bot_a"], r0["bot_b"]) == ("kog3", "kog3") and (r1["bot_a"], r1["bot_b"]) == (code, "kog3")
    ch = paired_change(D_base[p], D_new[p], +1)
    nd = sum(D_base[p][i]["moves"] != D_new[p][i]["moves"] for i in D_base[p])
    b_ = sum(1 for x in ch if x > 0); w_ = sum(1 for x in ch if x < 0)
    better += b_; worse += w_
    parts.append(ch)
    m1, h1, _ = pool([ch])
    print(f"     row {p} (v {D_base[p][0]['b']}): moves differ in {nd}; own side {m1:+.2f} ± {h1:.2f} (better {b_}, worse {w_})")
m, h, n = pool(parts)
print(f"   POOLED over 8 rows: own-side gain {m:+.3f} ± {h:.3f} ({n:,} games); gain beyond paired noise: {'YES' if m > h else 'no'}; interval {m-h:+.3f} to {m+h:+.3f}")
# exact sign test on the discordant deals (a second, distribution-free look)
nd_ = better + worse
def binom_two_sided(k, n):
    from math import comb
    pk = [comb(n, j) / 2 ** n for j in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] * (1 + 1e-12)))
print(f"   discordant games (score differs): better {better}, worse {worse}; exact two-sided sign-test p = {binom_two_sided(better, nd_):.4f}")
# the full-game footprint on the d rows
print(f"   (d) rows {code}: moves differ in {sum(D_base[p][i]['moves'] != D_new[p][i]['moves'] for p in D_base for i in D_base[p])} of {sum(len(v) for v in D_base.values())}")

# ---- coverage
print(f"\n--- coverage, Dustin's rule: own side in the mixed rows; harm = the pooled 95% interval wholly below zero")
def chk(m, h):
    return "HARM (wholly below zero)" if m + h < 0 else ("gain beyond noise" if m - h > 0 else "no harm")

# B2e
b_base = load([SCR + "/data/b2e_kog3.jsonl"], pairing)
b_mix = load([f"{K}/{B}_mixed_b2e_{code}_first.jsonl"], pairing)
b_full = load([f"{K}/{B}_b2e_{code}.jsonl"], pairing)
groups = {}
for p in sorted(b_base):
    assert set(b_base[p]) == set(b_mix[p])
    for i in b_base[p]:
        assert b_base[p][i]["seed"] == b_mix[p][i]["seed"]
        assert (b_mix[p][i]["bot_a"], b_mix[p][i]["bot_b"]) == (code, "kog3")
    nm = b_base[p][0]["a"]
    groups.setdefault(nm, []).append((p, paired_change(b_base[p], b_mix[p], +1)))
print("   B2e (own side = the B2e deck, first-named, with the code on it only):")
harm_cov = []
for nm, lst in groups.items():
    ps = [p for p, _ in lst]
    held = all(p < 48 for p in ps)
    m, h, n = pool([c for _, c in lst])
    tag = chk(m, h)
    if held and tag.startswith("HARM"):
        harm_cov.append(f"B2e {nm}")
    print(f"     {'HELD-OUT' if held else 'Dustin  '} {nm:>26} (pairings {ps[0]}-{ps[-1]}): {m:+6.2f} ± {h:4.2f}  {tag}")
    if tag.startswith("HARM") or (held and m < 0 and abs(m) > 0.7 * h):
        for p, c in lst:
            m1, h1, _ = pool([c])
            print(f"          pairing {p} v {b_base[p][0]['b']}: {m1:+.2f} ± {h1:.2f}")
allheld = [c for nm, lst in groups.items() for p, c in lst if p < 48]
m, h, n = pool(allheld)
print(f"     all 48 held-out rows pooled: {m:+.2f} ± {h:.2f}  ({chk(m, h)})")

# Scizor
s_base = load([R + "/koh_2026-09-28/laptop_runs/scizor_kog3.jsonl"], pairing)
s_f = load([f"{K}/{B}_mixed_scizor_{code}_first.jsonl"], pairing)
s_s = load([f"{K}/{B}_mixed_scizor_{code}_second.jsonl"], pairing)
for p in s_base:
    for i in s_base[p]:
        assert s_base[p][i]["seed"] == s_f[p][i]["seed"] == s_s[p][i]["seed"]
        assert (s_f[p][i]["bot_a"], s_f[p][i]["bot_b"]) == (code, "kog3") and (s_s[p][i]["bot_a"], s_s[p][i]["bot_b"]) == ("kog3", code)
sc_own = [paired_change(s_base[p], s_f[p], +1) for p in sorted(s_base)]
sc_opp = [paired_change(s_base[p], s_s[p], -1) for p in sorted(s_base)]
m, h, n = pool(sc_own)
print(f"   Scizor own side (8 rows): {m:+.2f} ± {h:.2f}  {chk(m, h)}   [older test: fall > 2 and wholly below zero: {'YES' if (m < -2 and m + h < 0) else 'no'}]")
for p, c in zip(sorted(s_base), sc_own):
    m1, h1, _ = pool([c])
    print(f"          row {p} (v {s_base[p][0]['b']}): {m1:+.2f} ± {h1:.2f}")
if m + h < 0:
    harm_cov.append("Scizor")
m2, h2, _ = pool(sc_opp)
print(f"   Scizor's panel decks' side (code on the panel deck only; reported only): {m2:+.2f} ± {h2:.2f}")

# second lists
for nm, base_f, mixa, mixb in (
    ("v-lucario_2", "var_v-lucario_2_kog3", "var_v-lucario_2_%s_mixed_a", "var_v-lucario_2_%s_mixed_b"),
    ("v-suicune_2", "var_v-suicune_2_kog3", "var_v-suicune_2_%s_mixed_a", "var_v-suicune_2_%s_mixed_b"),
    ("v-weezing_2", "var_v-weezing_2_kog3", "var_v-weezing_2_%s_mixed_a", "var_v-weezing_2_%s_mixed_b"),
    ("l-charizardy", "var_l-charizardy_kog3", "var_l-charizardy_%s_mixed_a", "var_l-charizardy_%s_mixed_b"),
):
    vb = load([R + f"/koh_2026-09-28/laptop_runs/{base_f}.jsonl"], pairing)
    ma = mb = {}
    pa, pb = f"{K}/{B}_{mixa % code}.jsonl", f"{K}/{B}_{mixb % code}.jsonl"
    if os.path.exists(pa):
        ma = load([pa], pairing)
    if os.path.exists(pb):
        mb = load([pb], pairing)
    parts, rows = [], []
    for p in sorted(vb):
        first_is_list = vb[p][0]["a"] == nm
        assert first_is_list or vb[p][0]["b"] == nm
        if first_is_list:
            mm, sg = ma[p], +1
            assert all((r["bot_a"], r["bot_b"]) == (code, "kog3") for r in mm.values())
        else:
            mm, sg = mb[p], -1
            assert all((r["bot_a"], r["bot_b"]) == ("kog3", code) for r in mm.values())
        c = paired_change(vb[p], mm, sg)
        parts.append(c)
        m1, h1, _ = pool([c])
        rows.append((p, vb[p][0]["b"] if first_is_list else vb[p][0]["a"], "first" if first_is_list else "second", m1, h1))
    m, h, n = pool(parts)
    tag = chk(m, h)
    if tag.startswith("HARM"):
        harm_cov.append(f"second list {nm}")
    print(f"   second list {nm:>13} own side ({len(parts)} rows, {n:,} deals): {m:+6.2f} ± {h:4.2f}  {tag}")
    for p, opp, seat, m1, h1 in rows:
        print(f"          row {p} v {opp} (list {seat}-named): {m1:+.2f} ± {h1:.2f}")
print("\n   COVERAGE harm found (Dustin's rule):", harm_cov or "none")
