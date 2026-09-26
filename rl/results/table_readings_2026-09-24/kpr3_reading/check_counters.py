"""Second reader: behaviour counters in kpr3_paired_reading.md, section 5 (own code).
hyper_ray = [KO-able used, KO-able passed, not KO-able used, not KO-able passed] (order checked against the scan's
printed lines in kpr3_500.txt and kp3_500_*.txt). chase_order = {offered, discarded, names}. 95% ranges are
game-clustered (ratio estimator over all games of the condition, games without the counter counted as 0/0)."""
import math, os, re
import numpy as np
from check_common import PAIRS, KP3, KPR3, MIX1, MIX2, RES, SP, load, score

kp3 = load(KP3, ("kp3", "kp3"))
kpr3 = load(KPR3, ("kpr3", "kpr3"))
m1 = load(MIX1, ("kpr3", "kp3"))
m2 = load(MIX2, ("kp3", "kpr3"))
cov = load([os.path.join(RES, "chase_order_2026-09-25", "kp3_vespiquen.jsonl")], ("kp3", "kp3"))

# Which fields exist at all.
fields = set()
for t in (kp3, kpr3, m1, m2, cov):
    for c in t.values():
        for r in c.values():
            fields |= set(r)
print("fields seen in any per-game file:", sorted(fields))
print("kp3 table games with chase_order:", sum("chase_order" in r for c in kp3.values() for r in c.values()))

# The kp3 Chase Order replay is the kp3 table's games.
same = tot = 0
for k, c in cov.items():
    for i, r in c.items():
        tot += 1
        b = kp3[k][i]
        same += all(r[f] == b[f] for f in ("seed", "first_seat", "moves", "winner_seat", "points", "turns", "first_deck_score"))
print(f"chase_order_2026-09-25/kp3_vespiquen.jsonl: {same:,} of {tot:,} identical to kp3's table games; "
      f"cells {sorted(cov) == sorted(k for k in PAIRS if 'vespiquen' in k)}")


def parse_scan(paths):
    hr, co = {}, {}
    cur = None
    for p in paths:
        for line in open(p, encoding="utf-8"):
            m = re.match(r"\s*(\w+) v (\w+)\s+first deck", line)
            if m:
                cur = (m.group(1), m.group(2))
                continue
            m = re.search(r"Hyper Ray turns: KO-able used (\d+) passed (\d+) \| not KO-able used (\d+) passed (\d+)", line)
            if m and cur:
                hr[cur] = [int(x) for x in m.groups()]
            m = re.search(r"Chase Order choices: discarded (\d+) of (\d+)", line)
            if m and cur:
                co[cur] = [int(x) for x in m.groups()]
    return hr, co


hyd = [k for k in PAIRS if "hydreigon" in k]
ves = [k for k in PAIRS if "vespiquen" in k]
conds = {
    "kp3 table": {k: kp3[k] for k in PAIRS},
    "kpr3 table": {k: kpr3[k] for k in PAIRS},
    "kpr3 on Hydreigon only": {k: (m1 if k[0] == "hydreigon" else m2)[k] for k in hyd},
    "kpr3 on Hyd's opponent only": {k: (m2 if k[0] == "hydreigon" else m1)[k] for k in hyd},
    "kpr3 on Vespiquen only": {k: (m1 if k[0] == "vespiquen" else m2)[k] for k in ves},
    "kpr3 on Ves's opponent only": {k: (m2 if k[0] == "vespiquen" else m1)[k] for k in ves},
    "kp3 Chase Order replay": {k: cov[k] for k in ves},
}


def hr_sum(games):
    return np.array([r.get("hyper_ray", [0, 0, 0, 0]) for r in games.values()])


def ratio_ci(y, x):
    """game-clustered 95% half-width of sum(y)/sum(x)."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    n, r = len(x), y.sum() / x.sum()
    se = math.sqrt(n / (n - 1) * ((y - r * x) ** 2).sum()) / x.sum()
    return r, 1.96 * se


print("== scan text vs per-game sums (Hyper Ray, Chase Order)")
kpr_txt = parse_scan([os.path.join(SP, "kpr3_500.txt")])
kp3_txt = parse_scan([os.path.join(RES, "public_pricing_2026-09-25", f) for f in ("kp3_500_worst5.txt", "kp3_500_rest.txt")])
for name, txt in (("kpr3 table", kpr_txt), ("kp3 table", kp3_txt)):
    ok_h = all(list(hr_sum(conds[name][k]).sum(axis=0)) == txt[0][k] for k in hyd) and set(txt[0]) == set(hyd)
    ok_c = all([sum(r.get("chase_order", {}).get("discarded", 0) for r in conds[name][k].values()),
                sum(r.get("chase_order", {}).get("offered", 0) for r in conds[name][k].values())] == txt[1].get(k)
               for k in ves) if txt[1] else "no Chase Order lines in the scan text"
    print(f"  {name}: Hyper Ray sums match the printed lines on all 7 cells: {ok_h}; Chase Order: {ok_c}")

print("== Hyper Ray per cell: [KO used, KO passed, noKO used, noKO passed]; noKO use; KO-able passed")
pooled = {}
for name in ("kp3 table", "kpr3 table", "kpr3 on Hydreigon only", "kpr3 on Hyd's opponent only"):
    Y1, X1, Y2, X2 = [], [], [], []
    for k in hyd:
        h = hr_sum(conds[name][k])
        s = h.sum(axis=0)
        r1, e1 = ratio_ci(h[:, 2], h[:, 2] + h[:, 3])
        r2, e2 = ratio_ci(h[:, 1], h[:, 0] + h[:, 1])
        print(f"  {name:<28} {k[0]} v {k[1]:<10} {[int(x) for x in s]}  noKO used {s[2]}/{s[2] + s[3]} = {100 * r1:.1f}% +/- "
              f"{100 * e1:.1f} | KO passed {s[1]}/{s[0] + s[1]} = {100 * r2:.1f}% +/- {100 * e2:.1f}")
        Y1 += list(h[:, 2]); X1 += list(h[:, 2] + h[:, 3]); Y2 += list(h[:, 1]); X2 += list(h[:, 0] + h[:, 1])
        pooled.setdefault(name, {})[k] = r1
    r1, e1 = ratio_ci(Y1, X1)
    r2, e2 = ratio_ci(Y2, X2)
    print(f"  {name:<28} ALL: noKO used {int(sum(Y1))}/{int(sum(X1))} = {100 * r1:.1f}% +/- {100 * e1:.1f} | KO passed "
          f"{int(sum(Y2))}/{int(sum(X2))} = {100 * r2:.1f}% +/- {100 * e2:.1f}")

print("== Chase Order per cell: discarded/offered; Combee")
for name in ("kp3 Chase Order replay", "kpr3 table", "kpr3 on Vespiquen only", "kpr3 on Ves's opponent only"):
    Y, X, C = [], [], []
    for k in ves:
        g = [r.get("chase_order", {"offered": 0, "discarded": 0, "names": {}}) for r in conds[name][k].values()]
        y = [c["discarded"] for c in g]; x = [c["offered"] for c in g]; cb = [c["names"].get("Combee", 0) for c in g]
        r, e = ratio_ci(y, x)
        print(f"  {name:<28} {k[0]} v {k[1]:<10} {sum(y)}/{sum(x)} = {100 * r:.1f}% +/- {100 * e:.1f} (Combee {sum(cb)})")
        Y += y; X += x; C += cb
    r, e = ratio_ci(Y, X)
    rc, ec = ratio_ci(C, X)
    print(f"  {name:<28} ALL: choices {sum(X):,}, discarded {sum(Y):,} = {100 * r:.1f}% +/- {100 * e:.1f}; Combee {sum(C)} "
          f"= {100 * rc:.1f}% of choices +/- {100 * ec:.1f}")

# Hydreigon: own-side change against the rise in no-KO Hyper Ray use, per cell.
print("== Hydreigon cell by cell: rise in noKO use (points) vs Hydreigon's score change")
xs_t, ys_t, xs_m, ys_m = [], [], [], []
for k in hyd:
    sg = 1 if k[0] == "hydreigon" else -1
    base = np.array([score(kp3[k][i]) for i in range(500)])
    tab = np.array([score(kpr3[k][i]) for i in range(500)])
    own = np.array([score(conds["kpr3 on Hydreigon only"][k][i]) for i in range(500)])
    dt, dm = sg * 100 * (tab - base).mean(), sg * 100 * (own - base).mean()
    rt = 100 * (pooled["kpr3 table"][k] - pooled["kp3 table"][k])
    rm = 100 * (pooled["kpr3 on Hydreigon only"][k] - pooled["kp3 table"][k])
    print(f"  v {k[1] if sg == 1 else k[0]:<10} table: rise {rt:+.1f}, Hydreigon {dt:+.1f} | own side: rise {rm:+.1f}, "
          f"Hydreigon {dm:+.1f}")
    xs_t.append(rt); ys_t.append(dt); xs_m.append(rm); ys_m.append(dm)
print(f"  r table {np.corrcoef(xs_t, ys_t)[0, 1]:+.3f}; r own side {np.corrcoef(xs_m, ys_m)[0, 1]:+.3f}")
