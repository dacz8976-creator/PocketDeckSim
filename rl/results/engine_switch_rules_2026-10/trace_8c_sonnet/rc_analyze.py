#!/usr/bin/env python3
import collections, csv, sys
path = sys.argv[1] if len(sys.argv) > 1 else "/home/dacz8976/c8c/out/revert_check.tsv"
rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
print("games", len(rows))
print("process_ok:", collections.Counter(r["process_ok"] for r in rows))
print("replay_ok (old choice != R choice at k):", collections.Counter(r["replay_ok"] for r in rows))
for r in rows:
    r["b"] = "B" if (r["coin_on_board"] == "yes" or int(r["gate_R"]) > 0) else "A-only"
print("B-in-play vs A-only:", collections.Counter(r["b"] for r in rows))
print("by verdict x group:", sorted(collections.Counter((r["verdict"], r["b"]) for r in rows).items()))
for g in ("B", "A-only"):
    sub = [r for r in rows if r["b"] == g]
    print(f"\n== {g}: {len(sub)} games; reproduced {sum(r['reproduced'] == 'yes' for r in sub)}; scores of every candidate equal old's {sum(r['scores_old_eq_revert'] == 'yes' for r in sub)}; "
          f"gate printed in R's search {sum(int(r['gate_R']) > 0 for r in sub)}; gate in old {sum(int(r['gate_old']) > 0 for r in sub)}")
    bad = [r for r in sub if r["reproduced"] != "yes" or r["scores_old_eq_revert"] != "yes"]
    print(f"   not reproduced (choice) {sum(r['reproduced'] != 'yes' for r in sub)}; candidate scores differ {sum(r['scores_old_eq_revert'] != 'yes' for r in sub)}; either {len(bad)}")
    if g == "B":
        for r in bad[:80]:
            print("   FAIL", r["step"], r["bot"], "p" + r["pairing"], "i" + r["i"], "k" + r["k"], "| old:", r["old_choice"][:60], "| R:", r["R_choice"][:60], "| revert:", r["revert_choice"][:60],
                  "| verdict:", r["verdict"][:22], "| coin_on_board", r["coin_on_board"], "gate_R", r["gate_R"], "| scores_eq", r["scores_old_eq_revert"])
print("\nfailures by (bot, pairing) among B:", sorted(collections.Counter((r["bot"], int(r["pairing"])) for r in rows if r["b"] == "B" and (r["reproduced"] != "yes" or r["scores_old_eq_revert"] != "yes")).items()))
