#!/usr/bin/env python3
"""Second pass: the counters legality_scan prints (Hyper Ray, Chase Order) for kp3 and kpr3 side by side."""
import re
from pathlib import Path

B = Path(r"C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\75cb92d0-6f2d-44b8-a636-513a8f7ee71a\scratchpad\reviews\branch")


def parse(txt):
    hr, co = {}, {}
    cur = None
    for line in open(B / txt, encoding="utf-8"):
        m = re.match(r"\s*(\w+) v (\w+)\s+first deck\s+([\d.]+)%", line)
        if m:
            cur = (m.group(1), m.group(2))
        m = re.search(r"KO-able used (\d+) passed (\d+) \| not KO-able used (\d+) passed (\d+)", line)
        if m and cur:
            hr[cur] = tuple(int(x) for x in m.groups())
        m = re.search(r"Chase Order choices: discarded (\d+) of (\d+) \(Combee (\d+), Shuckle ex (\d+), Teal Mask Ogerpon ex (\d+)\)", line)
        if m and cur:
            co[cur] = tuple(int(x) for x in m.groups())
    return hr, co


for label, f in (("k3", "identity_k3_500.txt"), ("kp3", "identity_kp3_500.txt"), ("kpr3", "kpr3_500.txt")):
    hr, co = parse(f)
    print(f"--- {label}: Hyper Ray turns per Hydreigon cell (KO-able used/passed | non-KO used/passed), total turns offered")
    tot = [0, 0, 0, 0]
    for c, v in hr.items():
        tot = [a + b for a, b in zip(tot, v)]
        print(f"  {c[0]} v {c[1]:10} KO {v[0]}/{v[1]}  nonKO {v[2]}/{v[3]}  offered {sum(v)}")
    print(f"  all: KO {tot[0]}/{tot[1]} ({100*tot[1]/(tot[0]+tot[1]):.1f}% passed)  nonKO {tot[2]}/{tot[3]} ({100*tot[2]/(tot[2]+tot[3]):.0f}% used)  offered {sum(tot)}")
    print(f"--- {label}: Chase Order (Vespiquen) per cell: discarded/choices, Combee, Shuckle ex, Ogerpon ex shares of discards")
    T = [0] * 5
    for c, v in co.items():
        T = [a + b for a, b in zip(T, v)]
        d, n, cb, sh, og = v
        print(f"  {c[0]:9} v {c[1]:9} discarded {d}/{n} ({100*d/n:.0f}%)  Combee {100*cb/d:.0f}%  Shuckle {100*sh/d:.0f}%  Ogerpon {100*og/d:.0f}%")
    d, n, cb, sh, og = T
    print(f"  all: discarded {d}/{n} ({100*d/n:.1f}%)  Combee {cb} ({100*cb/d:.1f}%)  Shuckle {sh} ({100*sh/d:.1f}%)  Ogerpon {og} ({100*og/d:.1f}%)")
    print()
