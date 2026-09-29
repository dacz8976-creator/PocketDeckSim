import json, glob, collections, math, sys
W = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria"
names = ["blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
st = {(int(r["p"]), str(r["seed"])): r for r in json.load(open(W + "/rows/rows_all.json.stories.json"))}
rows = {}
for fn in sorted(glob.glob(W + "/synth/attr_p[0-9].jsonl")):
    for ln in open(fn):
        ln = ln.strip()
        if not ln:
            continue
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
    print(f"  {label:50} n={len(g):4d} worse {w:3d} better {b:3d} sign p {sign_p(w, b):.3f}")


ok = [r for r in rows.values() if r["picks"].get("kog") == r["kog_act"] and r["picks"].get("koh") == r["koh_act"]]
print("reproduced", len(ok), "of", len(rows))
for scope, sel in (("Lucario", [r for r in ok if r["p"] == 2]), ("other six cells", [r for r in ok if r["p"] != 2])):
    print("==", scope)
    for name, f in (("kog attacks, koh not, that turn", lambda s: s["kog_attack"] and not s["koh_attack"]), ("neither/else", lambda s: not (s["kog_attack"] and not s["koh_attack"]))):
        g = [r for r in sel if f(st[(r["p"], str(r["seed"]))])]
        rep(name, g)
        c = collections.defaultdict(list)
        for r in g:
            c[cls(r)].append(r)
        for k, v in sorted(c.items(), key=lambda kv: -len(kv[1])):
            rep("     " + k, v)
