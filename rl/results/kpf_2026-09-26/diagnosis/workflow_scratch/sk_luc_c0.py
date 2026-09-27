"""Skeptic: compare the original divergences.jsonl lucario rows with the independent re-split records."""
import json, os
from collections import Counter
from sk_luc_lib import load_cached, D
out, notes = load_cached()
orig = {}
for line in open(os.path.join(D, "divergences.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    if r["deck"] == "lucario":
        orig[(r["seed"], r["kind"])] = r
diff = Counter()
for r in out:
    o = orig[(r["seed"], r["kind"])]
    same = (o["kp3_act"] == r["kp3_act"] and o["kpf_act"] == r["kpf_act"] and o["turn"] == r["turn"])
    if not same:
        diff[(r["kind"], r["occ"], o["actor_is_kpf"])] += 1
print("original lucario rows not kpf-side:", sum(not o["actor_is_kpf"] for o in orig.values()))
print("rows that change under re-split (kind, lucario run index, orig actor_is_kpf):", dict(diff))
# all decks: how many seeds appear in 2 entries
sel = json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))
c = Counter(g["seed"] for g in sel)
dup = [s for s, n in c.items() if n > 1]
print("seeds selected twice (all decks):", len(dup))
dd = Counter()
for g in sel:
    if c[g["seed"]] > 1:
        dd[g["deck"]] += 1
print("entries on shared seeds by deck:", dict(dd))
print("div not in own turn (promote etc.):", Counter((r["kind"], r["kpf_cat"]) for r in out if not r["div_in_own_turn"]))
