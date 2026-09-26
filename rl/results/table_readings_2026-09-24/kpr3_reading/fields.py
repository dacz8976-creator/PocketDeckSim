#!/usr/bin/env python3
"""Which fields the per-game files carry (kp3 table, kpr3 table, the two mixed rows), with an example of each
counter field. Read-only; prints to stdout."""
import json, sys, collections

for path in sys.argv[1:]:
    keys = collections.Counter()
    ex = {}
    n = 0
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        n += 1
        for k, v in r.items():
            keys[k] += 1
            if k not in ex and isinstance(v, (list, dict)) and k not in ("points",):
                ex[k] = (r["a"], r["b"], r["i"], v)
    print(path)
    print(f"  {n} games; fields: " + ", ".join(f"{k} ({c})" for k, c in sorted(keys.items())))
    for k, v in ex.items():
        print(f"  example {k}: {v}")
