"""Extra checks by the second reader: (i) one-sided mixed rows vs the both-sides footprint, (ii) exact sign tests for clause (d),
(iii) ktb3/ktc3 real errors, (iv) the other route's numbers for both codes (robustness note only; the route was fixed by the footprint)."""
import sys
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kt2/second-reader")
from sr_lib import *
from math import comb

lim = limitless45()
KOG = [R + "/kog_composition_2026-09-27/table_kog3.jsonl", R + "/kog_composition_2026-09-27/new17_kog3.jsonl"]
O_g = load(KOG, ab)
L = {k: lim_rate(lim, k)[0] for k in CELLS45}
nL = {k: lim_rate(lim, k)[1] for k in CELLS45}
O = cell_means(O_g, CELLS45)
nS = {k: 500 for k in CELLS45}
print("kog3 real error (45 cells): %.3f" % tau(O, nS, L, nL, CELLS45))

# (i) integrity of the mixed rows against the both-sides footprint
for code in ("kta3", "kt3"):
    N_g = load([f"{K}/{B}_{code}_table.jsonl", f"{K}/{B}_{code}_new17.jsonl"], ab)
    MF = load([f"{K}/{B}_mixed_table_{code}_first.jsonl", f"{K}/{B}_mixed_new17_{code}_first.jsonl"], ab)
    MS = load([f"{K}/{B}_mixed_table_{code}_second.jsonl", f"{K}/{B}_mixed_new17_{code}_second.jsonl"], ab)
    zero_bad = 0
    union_ne = 0
    tot_both = tot_union = tot_f = tot_s = 0
    for k in CELLS45:
        both = {i for i in O_g[k] if N_g[k][i]["moves"] != O_g[k][i]["moves"]}
        f = {i for i in O_g[k] if MF[k][i]["moves"] != O_g[k][i]["moves"]}
        s = {i for i in O_g[k] if MS[k][i]["moves"] != O_g[k][i]["moves"]}
        if not both and (f or s):
            zero_bad += 1
        if (f | s) != both:
            union_ne += 1
        tot_both += len(both); tot_union += len(f | s); tot_f += len(f); tot_s += len(s)
    print(f"{code}: both-sides footprint {tot_both}; games where first-only or second-only differ {tot_union}; first-only {tot_f}, second-only {tot_s}; "
          f"cells with zero footprint but a differing mixed game: {zero_bad}; cells where (first|second) != both-sides set: {union_ne}")

# (ii) exact sign tests for clause (d)
def two_sided(k, n):
    pk = [comb(n, j) / 2 ** n for j in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] * (1 + 1e-12)))
for code in ("kta3", "kt3"):
    Db = load([f"{K}/{B}_d_kog3.jsonl"], pairing)
    Dn = load([f"{K}/{B}_d_{code}.jsonl"], pairing)
    bet = wor = 0
    for p in Db:
        for i in Db[p]:
            d = score(Dn[p][i]) - score(Db[p][i])
            bet += d > 0
            wor += d < 0
    print(f"(d) {code}: better {bet}, worse {wor}, exact two-sided sign test p = {two_sided(min(bet, wor), bet + wor):.3g}")

# (iii) ktb3, ktc3 real errors (no mixed rows needed)
for code in ("ktb3", "ktc3", "kt3", "kta3"):
    N_g = load([f"{K}/{B}_{code}_table.jsonl", f"{K}/{B}_{code}_new17.jsonl"], ab)
    N = cell_means(N_g, CELLS45)
    print(f"{code}: real error {tau(N, nS, L, nL, CELLS45):.3f}; margin (kog3 - {code}) {tau(O, nS, L, nL, CELLS45) - tau(N, nS, L, nL, CELLS45):+.3f}")

# (iv) the other route for each code, own arithmetic: kt3 under the reserve-route clauses (b),(c),(d) is in out_step3_kt3 / out_step2_kt3;
#      kta3 under the ordinary rule is in out_step2_kta3 (dMSE and its interval).
print("done")
