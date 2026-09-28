"""koh's footprint, read first and committed alone (kph's registration, ../../kph_2026-09-27/REGISTRATION.md, section 5,
step 1; koh = kph's R' on the composed pilot kog, section 2). The share of paired games on the 45 cells whose moves
differ from the base's (kog3: the laptop's composition runs, ../../kog_composition_2026-09-27/table_kog3.jsonl and
new17_kog3.jsonl). Under 15% the reserve route (a)-(e) applies; otherwise the ordinary adoption rule. The route is
fixed on this number. koh's files are the cloud's (branch claude/pensive-ptolemy-spwc0b, rl/results/koh_2026-09-28/
reading/), read from git into a scratch copy. Reads moves only; no result, score or error is read.
Usage: python3 footprint.py <scratch dir holding table_koh3.jsonl and new17_koh3.jsonl>"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KOG = os.path.join(HERE, "..", "..", "kog_composition_2026-09-27")
S = sys.argv[1]
load = lambda p: {(g["a"], g["b"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}
base = {**load(os.path.join(KOG, "table_kog3.jsonl")), **load(os.path.join(KOG, "new17_kog3.jsonl"))}
new = {**load(os.path.join(S, "table_koh3.jsonl")), **load(os.path.join(S, "new17_koh3.jsonl"))}
assert base.keys() == new.keys(), (len(base), len(new))
assert all(base[k]["seed"] == new[k]["seed"] for k in base), "different deals"
assert {(g["bot_a"], g["bot_b"]) for g in new.values()} == {("koh3", "koh3")}, "koh's files are not koh3 on both sides"
diff = [k for k in base if base[k]["moves"] != new[k]["moves"]]
fp = 100 * len(diff) / len(base)
print(f"FOOTPRINT: {len(diff)} of {len(base)} paired games on the 45 cells differ from kog3's moves = {fp:.2f}%")
print(f"ROUTE (fixed on this number, before anything else is read): "
      f"{'RESERVE route, clauses (a)-(e)' if fp < 15 else 'ORDINARY adoption rule (15% or more)'}")
by = collections.Counter((a, b) for a, b, _ in diff)
print("by cell (games differing of 500): " + ", ".join(f"{a} v {b} {n}" for (a, b), n in sorted(by.items())))
