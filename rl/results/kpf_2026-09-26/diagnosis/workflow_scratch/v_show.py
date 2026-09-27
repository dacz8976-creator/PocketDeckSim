import json, sys
from collections import Counter
rows = json.load(open("v_cls.json"))
seq = {r["seed"]: r for r in json.load(open("v_rows.json"))}
flt = sys.argv[1]
sub = [r for r in rows if eval(flt, {}, {"r": r})]
print(Counter((r["cls"][:1], r["kind"]) for r in sub))
for r in sub:
    s = seq[r["seed"]]
    print(f"--- {r['kind']} {r['seed']} t{r['turn']} v {r['opp']} [{r['cls'][:1]}]")
    print(f"   own: {r['own']}")
    print(f"   opp: {r['oppb']}")
    print(f"   kp3: {' ; '.join(s['seq_b'])}")
    print(f"   kpf: {' ; '.join(s['seq_f'])}")
    print(f"   end kp3: {s['b_end']}")
    print(f"   end kpf: {s['f_end']}")
