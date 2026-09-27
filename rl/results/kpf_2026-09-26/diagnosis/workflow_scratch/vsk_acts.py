import json, pickle, re
from collections import Counter
T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
div = json.load(open("vsk_div.json"))
c = Counter()
ex = {}
for r in div:
    for key in ("base", "kpf"):
        tr = T[key][r["seed"]][r["trace"]]
        for L in tr:
            if L["actor"] != r["seat"]:
                continue
            a = L["act"]
            k = re.sub(r"\d+", "#", a)[:90]
            c[k] += 1
            ex.setdefault(k, a)
for k, n in c.most_common(80):
    print(n, "|", ex[k][:160])
