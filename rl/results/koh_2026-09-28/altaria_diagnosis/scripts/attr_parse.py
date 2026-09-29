import json, glob, collections, math, sys
W = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria"
pref = sys.argv[1] if len(sys.argv) > 1 else "attr_p"
names = ["blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
rows = []
bad_lines = 0
for fn in sorted(glob.glob(W + f"/synth/{pref}[0-9].jsonl")):
    for ln in open(fn):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except Exception:
            bad_lines += 1
seen = set()
dd = []
for r in rows:
    if (r["p"], r["seed"]) in seen:
        continue
    seen.add((r["p"], r["seed"]))
    dd.append(r)
print("bad lines", bad_lines, "dupes", len(rows) - len(dd))
rows = dd
print("rows", len(rows), collections.Counter(r["p"] for r in rows))


def sign_p(w, b):
    n = w + b
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(w, b) + 1)) / 2 ** n)


def rep(label, g, tot=3500):
    w = sum(r["delta"] < 0 for r in g); b = sum(r["delta"] > 0 for r in g)
    print(f"  {label:58} n={len(g):4d} worse {w:3d} better {b:3d} net pts/{tot} {100*sum(r['delta'] for r in g)/tot:+.2f} sign p {sign_p(w,b):.3f}")


rep_ok = [r for r in rows if r["picks"].get("kog") == r["kog_act"] and r["picks"].get("koh") == r["koh_act"]]
print("reproduced both picks:", len(rep_ok), "of", len(rows))
bad = [r for r in rows if r not in rep_ok]


def X(r, v):
    return r["picks"].get(v) == r["koh_act"]


def cls(r):
    kpf, kpha, kphb = X(r, "kpf"), X(r, "kpha"), X(r, "kphb")
    if kpf and kpha and kphb:
        return "R alone already gives koh's move (A, B not needed)"
    if kpf and not kpha:
        return "R gives it, A takes it back, (B/A+B restore)" if not kphb else "R+B gives it, A takes it back"
    if not kpf and kphb:
        return "needs B (R alone keeps kog's move)"
    if not kpf and kpha and not kphb:
        return "needs A (R alone keeps kog's move)"
    if not kpf and not kpha and not kphb:
        return "needs A+B together (each alone keeps kog's move)"
    return "other pattern " + str((kpf, kpha, kphb))


for scope, sel in (("ALL cells", rep_ok),) + tuple((names[p], [r for r in rep_ok if r["p"] == p]) for p in range(7)):
    if not sel:
        continue
    print(f"== {scope}: {len(sel)} reproduced first-divergence rows")
    c = collections.defaultdict(list)
    for r in sel:
        c[cls(r)].append(r)
    for k, g in sorted(c.items(), key=lambda kv: -len(kv[1])):
        rep(k, g)
    rep("(all reproduced rows)", sel)
print("== not reproduced:", len(bad))
rep("(not reproduced rows)", bad)
# by category: which class
print("== by (category, class), ALL cells, n>=15")
cc = collections.defaultdict(list)
for r in rep_ok:
    cc[(r["cat"], cls(r))].append(r)
for k, g in sorted(cc.items(), key=lambda kv: -len(kv[1])):
    if len(g) >= 15:
        rep(f"{k[0][:26]} | {k[1][:40]}", g)
