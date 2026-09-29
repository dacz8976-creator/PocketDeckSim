import json, glob, collections, math
W = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria"
recs = json.load(open(W + "/rows/rows_all.json"))
fam = {(int(r["p"]), str(r["seed"])) for r in recs if r.get("cat") == "Zone attach target differs" and r.get("detail", "") == "kog Mega Altaria ex@B vs koh Darkrai@A"}
rows = {}
for fn in sorted(glob.glob(W + "/synth/attr_p[0-9].jsonl")):
    for ln in open(fn):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        rows[(r["p"], str(r["seed"]))] = r


def sign_p(w, b):
    n = w + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(w, b) + 1)) / 2 ** n)


def X(r, v):
    return r["picks"].get(v) == r["koh_act"]


def cls(r):
    kpf, kpha, kphb = X(r, "kpf"), X(r, "kpha"), X(r, "kphb")
    if kpf and kpha and kphb:
        return "R alone"
    if not kpf and kphb:
        return "needs B"
    if not kpf and kpha and not kphb:
        return "needs A"
    return "mixed"


def rep(label, g):
    w = sum(r["delta"] < 0 for r in g); b = sum(r["delta"] > 0 for r in g)
    print(f"  {label:50} n={len(g):4d} worse {w:3d} better {b:3d} net pts/3500 {100*sum(r['delta'] for r in g)/3500:+.2f} sign p {sign_p(w, b):.3f}")


ok = [r for r in rows.values() if r["picks"].get("kog") == r["kog_act"] and r["picks"].get("koh") == r["koh_act"]]
inf = [r for r in ok if (r["p"], str(r["seed"])) in fam]
print("family rows reproduced", len(inf), "of", len(fam))
for k in ("R alone", "needs B", "needs A", "mixed"):
    rep("family, " + k, [r for r in inf if cls(r) == k])
outf = [r for r in ok if (r["p"], str(r["seed"])) not in fam]
print("outside the family:")
for k in ("R alone", "needs B", "needs A", "mixed"):
    rep("outside family, " + k, [r for r in outf if cls(r) == k])
rep("outside family, all reproduced", outf)
# Lucario cell: R alone rows by category
print("Lucario R-alone rows by category")
luc = [r for r in ok if r["p"] == 2 and cls(r) == "R alone"]
c = collections.defaultdict(list)
for r in luc:
    c[r["cat"]].append(r)
for k, v in sorted(c.items(), key=lambda kv: -len(kv[1])):
    rep(k, v)
print("Lucario R-alone rows by divergence turn")
c = collections.defaultdict(list)
for r in luc:
    c[min(int(r["turn"]), 6)].append(r)
for k, v in sorted(c.items()):
    rep(f"turn {k}", v)
# other six cells R alone
print("other six cells R alone", end=" ")
o6 = [r for r in ok if r["p"] != 2 and cls(r) == "R alone"]
rep("", o6)
