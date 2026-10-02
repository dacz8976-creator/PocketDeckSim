#!/usr/bin/env python3
import csv
O = "/home/dacz8976/c8c/out/"
v = {(r["step"], r["bot"], r["pairing"], r["i"]): r for r in csv.DictReader(open(O + "verdicts.tsv", encoding="utf-8"), delimiter="\t")}
rc = list(csv.DictReader(open(O + "revert_check.tsv", encoding="utf-8"), delimiter="\t"))
a = [r for r in rc if not (r["coin_on_board"] == "yes" or int(r["gate_R"]) > 0)]
print(len(a), "A-only games (no coin-Ability Pokemon on the board at k, no gate in R's search):")
for r in a:
    x = v[(r["step"], r["bot"], r["pairing"], r["i"])]
    print(f"  {r['step']} {r['bot']} p{r['pairing']} i{r['i']} k{r['k']}: {x['verdict'][:32]} | coin_probe {x['coin_probe']} | vs_probe {x['vs_probe']} | counters {x['reach_counters_that_explain'][:90]}")
    print(f"      old {r['old_choice'][:70]} | R {r['R_choice'][:70]} | revert {r['revert_choice'][:70]}")
nb = [r for r in rc if (r["coin_on_board"] == "yes" or int(r["gate_R"]) > 0)]
print("\nB games: gate in R's search", sum(int(r["gate_R"]) > 0 for r in nb), "of", len(nb), "; coin Ability on the board", sum(r["coin_on_board"] == "yes" for r in nb))
print("B games with gate_R == 0 and coin on board:", sum(int(r["gate_R"]) == 0 and r["coin_on_board"] == "yes" for r in nb))
import collections
print("B games by step:", collections.Counter(r["step"] for r in nb), "; by bot:", collections.Counter(r["bot"] for r in nb))
