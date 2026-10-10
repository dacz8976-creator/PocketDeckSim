"""Summarizes the open test: python3 summarize.py (run in this folder). Prints summary.txt's text."""
import collections, csv
d = list(csv.DictReader(open("open_test_default.tsv"), delimiter="\t"))
w = list(csv.DictReader(open("open_test_walk.tsv"), delimiter="\t"))
g = lambda r: int(r["gate_R"]) > 0
print(f"games: {len(d)} (default run), {len(w)} (walk run); gate_R > 0 in {sum(map(g, d))}; probe errors {sum(bool(r['error']) for r in d + w)}")
print("1. PLAN's test as written, free = true exactly where gate_R > 0:",
      dict(collections.Counter((('gate_R>0' if g(r) else 'gate_R=0') + ', free=' + r['free']) for r in d)))
print("2. the default probe, a pure queued frame at any ply (PURE_PLIES not empty) against gate_R > 0:",
      dict(collections.Counter((('gate_R>0' if g(r) else 'gate_R=0') + ', pure=' + str(bool(r['pure_plies']))) for r in d)))
print("3. the walk run, R's gate frame found (GATE_PLIES not empty) against gate_R > 0:",
      dict(collections.Counter((('gate_R>0' if g(r) else 'gate_R=0') + ', gate=' + str(bool(r['gate_plies']))) for r in w)))
key = lambda r: (r["step"], r["bot"], r["pairing"], r["i"])
dd = {key(r): r for r in d}
print("walk run's queued and free equal to the default run's:", sum(dd[key(r)]["queued"] == r["queued"] and dd[key(r)]["free"] == r["free"] for r in w), "of", len(w))
print("walk run, first gate ply:", sorted(collections.Counter(min(map(int, r["gate_plies"].split(","))) for r in w if r["gate_plies"]).items()))
print("walk run, retried at 600,000 nodes:", [key(r) for r in w if r["node_limit"] == "600000"])
print("walk run, stopped at the node limit (having found something):", [(key(r), r["gate_R"], r["gate_plies"] or "-") for r in w if r["stopped"] == "True"])
