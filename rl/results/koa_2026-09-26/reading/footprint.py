"""koa's reading, steps 0 and 1 only (REGISTRATION.md section 7: the footprint is read first and fixes the route before
(b) to (e) or any dMSE is read). Usage: python3 footprint.py > footprint.txt"""
import json, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RES, "table_readings_2026-09-24"))
import score as S  # noqa: E402
PAIRS = S.D.PAIRS[:28]
load = lambda f: {(g["pairing"], g["i"]): g for g in map(json.loads, open(f, encoding="utf-8"))}
kp3 = load(os.path.join(RES, "kpf_2026-09-26", "reading", "table_kp3.jsonl"))
koa = load(os.path.join(HERE, "table_koa3.jsonl"))
cloud = load(os.path.join(RES, "koa_2026-09-26", "identity_koa3_40.jsonl"))
f0 = [f for f in ("moves", "winner_seat", "points", "seed") if all(f in g for g in cloud.values())]
same0 = sum(all(koa[k][f] == cloud[k][f] for f in f0) for k in cloud)
print(f"0. koa3 at the official build (main-83e17ae) v the cloud's koa3 at 9af40c8: {same0} of {len(cloud)} games equal on {f0}")
assert len(kp3) == len(koa) == 14000
diff = [k for k in kp3 if koa[k]["moves"] != kp3[k]["moves"]]
res = [k for k in diff if (koa[k]["winner_seat"], koa[k]["points"]) != (kp3[k]["winner_seat"], kp3[k]["points"])]
fp = 100 * len(diff) / 14000
by = Counter(k[0] for k in diff)
print(f"1. FOOTPRINT: {len(diff)} of 14,000 paired table games differ from kp3's moves = {fp:.2f}% (registered prediction 6.0%); "
      f"results differ in {len(res)}")
print(f"   ROUTE (fixed now, before anything else is read): {'RESERVE route, clauses (a)-(e)' if fp < 15 else 'ORDINARY adoption rule'}")
print("   by pairing: " + "; ".join(f"{PAIRS[p][0]} v {PAIRS[p][1]} {n}" for p, n in sorted(by.items())))
print(f"   pairings without Altaria that differ: {sorted(p for p in by if 'altaria' not in PAIRS[p])}")
