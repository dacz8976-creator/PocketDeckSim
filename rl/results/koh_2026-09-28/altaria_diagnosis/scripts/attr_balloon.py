import json, glob, collections, math
W = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria"
rows = {}
for fn in sorted(glob.glob(W + "/synth/attr_p[0-9].jsonl")):
    for ln in open(fn):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        rows[(r["p"], str(r["seed"]))] = r


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


def sign_p(w, b):
    n = w + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(w, b) + 1)) / 2 ** n)


def rep(label, g):
    w = sum(r["delta"] < 0 for r in g); b = sum(r["delta"] > 0 for r in g)
    print(f"  {label:60} n={len(g):4d} worse {w:3d} better {b:3d} net pts/3500 {100*sum(r['delta'] for r in g)/3500:+.2f} sign p {sign_p(w,b):.3f}")


ok = [r for r in rows.values() if r["picks"].get("kog") == r["kog_act"] and r["picks"].get("koh") == r["koh_act"]]
bal = lambda r: "Small Balloon" in r["koh_act"]
balk = lambda r: "Small Balloon" in r["kog_act"]
for k in ("R alone", "needs B", "needs A", "mixed"):
    g = [r for r in ok if cls(r) == k]
    rep(f"{k}: all", g)
    rep(f"{k}: koh plays Small Balloon first, kog does not", [r for r in g if bal(r)])
    rep(f"{k}: kog plays Small Balloon first, koh does not", [r for r in g if balk(r)])
# every Altaria row (not only reproduced) with Small Balloon in koh_act
allr = list(rows.values())
rep("ALL sampled rows: koh_act Small Balloon", [r for r in allr if bal(r)])
rep("ALL sampled rows: kog_act Small Balloon", [r for r in allr if balk(r)])
# what does koh's balloon row look like in the B classes: which kphb/kpf picks
print("B rows with balloon by opponent:", collections.Counter(r["p"] for r in ok if cls(r) == "needs B" and bal(r)))
