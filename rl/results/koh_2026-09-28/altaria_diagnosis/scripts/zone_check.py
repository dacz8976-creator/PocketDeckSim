import json, collections, math, sys
W = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria"
recs = json.load(open(W + "/rows/rows_all.json"))
print("records", len(recs))
# overall per pairing paired diff (koh - kog on Altaria side; score in points = 100*delta)
byp = collections.defaultdict(list)
for r in recs:
    byp[r["p"]].append(r)
tot = []
for p, g in sorted(byp.items()):
    d = [100 * r["delta"] for r in g]
    n = len(d); m = sum(d) / n
    sd = (sum((x - m) ** 2 for x in d) / (n - 1)) ** 0.5
    w = sum(x < 0 for x in d); b = sum(x > 0 for x in d)
    print(f"pairing {p} n={n} mean {m:+.2f} +/- {1.96*sd/math.sqrt(n):.2f} worse {w} better {b}")
    tot += d
n = len(tot); m = sum(tot) / n; sd = (sum((x - m) ** 2 for x in tot) / (n - 1)) ** 0.5
print(f"pooled n={n} mean {m:+.2f} +/- {1.96*sd/math.sqrt(n):.2f} worse {sum(x<0 for x in tot)} better {sum(x>0 for x in tot)}")
# clean zone family
sel = [r for r in recs if r.get("cat") == "Zone attach target differs" and r.get("detail","") == "kog Mega Altaria ex@B vs koh Darkrai@A"]
w = sum(r["delta"] < 0 for r in sel); b = sum(r["delta"] > 0 for r in sel)
print("clean zone family n", len(sel), "worse", w, "better", b, "mean pts", 100 * sum(r["delta"] for r in sel) / len(sel))
nn = w + b
p = min(1, 2 * sum(math.comb(nn, i) for i in range(min(w, b) + 1)) / 2 ** nn)
print("sign p", p)
print("by pairing", {q: (sum(1 for r in sel if r['p'] == q and r['delta'] < 0), sum(1 for r in sel if r['p'] == q and r['delta'] > 0)) for q in sorted(byp)})
# how many distinct categories/details exist (multiplicity)
cats = collections.Counter((r.get("cat"), r.get("detail","")) for r in recs if r.get("state_equal_at_div") in (True, "True"))
print("distinct (cat,detail):", len(cats))
cc = collections.Counter(r.get("cat") for r in recs)
print(cc)
# per-category worse/better for Zone-related categories
for c in cc:
    if c is None: continue
    g = [r for r in recs if r.get("cat") == c]
    print(f"  {c:40} n={len(g)} worse {sum(r['delta']<0 for r in g)} better {sum(r['delta']>0 for r in g)} net pts {100*sum(r['delta'] for r in g)/3500:+.2f}")
# the reverse-direction family
rev = [r for r in recs if r.get("cat") == "Zone attach target differs" and "vs koh Mega Altaria ex@B" in r.get("detail","")]
print("reverse family (koh feeds bench Mega):", len(rev), sum(r["delta"] < 0 for r in rev), sum(r["delta"] > 0 for r in rev))
# list details of zone cat
zc = collections.Counter(r.get("detail","") for r in recs if r.get("cat") == "Zone attach target differs")
for k, v in zc.most_common(12):
    g = [r for r in recs if r.get("cat") == "Zone attach target differs" and r.get("detail","") == k]
    print(f"   {k:55} n={v} worse {sum(r['delta']<0 for r in g)} better {sum(r['delta']>0 for r in g)}")



