import csv, json
from collections import Counter
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
load = lambda f: {(g["pairing"], g["i"]): g for g in map(json.loads, open(f, encoding="utf-8"))}
import itertools
NAMES = ['altaria', 'blaziken', 'hydreigon', 'lucario', 'sceptile', 'suicune', 'vespiquen', 'weezing']
PAIRS = list(itertools.combinations(NAMES, 2))
old_t = load(R + "/rl/results/engine_identity_2026-09-25/kp3_500.jsonl")
new_t = load(R + "/rl/results/kpf_2026-09-26/reading/table_kp3.jsonl")
ch = [k for k in new_t if old_t[k]["moves"] != new_t[k]["moves"]]
print("table kp3 7fc6ccb vs repaired: changed", len(ch), "of", len(new_t))
print("  by pairing:", {f"{PAIRS[p][0][:4]}-{PAIRS[p][1][:4]}": n for p, n in sorted(Counter(k[0] for k in ch).items())})
# Altaria cells before (7fc6ccb) vs after (repaired)
for p in range(7):
    s0 = 100 * sum(old_t[(p, i)]["first_deck_score"] for i in range(500)) / 500
    s1 = 100 * sum(new_t[(p, i)]["first_deck_score"] for i in range(500)) / 500
    print(f"  {PAIRS[p]}: 7fc6ccb {s0:.1f} -> repaired {s1:.1f}")
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(R + "/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"), delimiter="\t")}
old_b = load(R + "/rl/results/b2e_rows_2026-09-26/b2e_kp3_arch.jsonl")
new_b = load(R + "/rl/results/kpf_2026-09-26/reading/b2e_kp3.jsonl")
chb = [k for k in old_b if old_b[k]["moves"] != new_b[k]["moves"]]
print("B2e kp3 0-47 changed by engine switch:", len(chb))
c = Counter((tsv[k[0]]["held_key"], tsv[k[0]]["opponent"]) for k in chb)
byh = Counter(tsv[k[0]]["held_key"] for k in chb)
print("  by held deck:", dict(byh))
print("  by cell:", dict(c))
# held-out panel averages old vs new kp3
for h in sorted(byh):
    ps = [p for p in range(48) if tsv[p]["held_key"] == h]
    a = sum(old_b[(p, i)]["first_deck_score"] for p in ps for i in range(500)) / (500 * len(ps)) * 100
    b = sum(new_b[(p, i)]["first_deck_score"] for p in ps for i in range(500)) / (500 * len(ps)) * 100
    print(f"  {h}: kp3 7fc6ccb {a:.1f} -> repaired {b:.1f}")
# old B2e dustin rows exist?
import os
print("dustin kp3 rows (old):", os.path.exists(R + "/rl/results/b2e_rows_2026-09-26/b2e_kp3_dustin.jsonl"))
print("kpf b2e_kp3 has 48-95:", sum(1 for k in new_b if k[0] >= 48))
print("dustin pairings 48-95 held keys:", sorted({tsv[p]["held_key"] + "|" + tsv[p]["held_file"] for p in range(48, 96)})[:12])
