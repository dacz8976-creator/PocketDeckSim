import json, os, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
old = {}
for l in open(os.path.join(os.path.dirname(HERE), "divergences.jsonl"), encoding="utf-8"):
    r = json.loads(l)
    if r["deck"] == "lucario":
        old[r["seed"]] = r

rows = []
for s, g in games.items():
    meta = g["meta"]
    seat = kpf_seat(meta)
    x, y = g["base"], g["kpf"]
    k = first_div(x, y)
    if k is None:
        print("no div", s)
        continue
    d = x[k]
    T = d["turn"]
    row = {"seed": s, "kind": meta["kind"], "change": meta["change"], "pairing": f'{meta["a"]}-{meta["b"]}',
           "opp": meta["b"] if meta["a"] == "lucario" else meta["a"], "seat": seat, "k": k, "turn": T,
           "actor": d["actor"], "is_kpf": d["actor"] == seat, "kp3_cat": cat(x[k]["act"]), "kpf_cat": cat(y[k]["act"]),
           "kp3_act": x[k]["act"][:120], "kpf_act": y[k]["act"][:120], "own": d["s"][seat], "oppb": d["s"][1 - seat],
           "old_turn": old[s]["turn"], "old_kpfcat": old[s]["kpf_cat"], "occ": g["occ"], "nk": g["nk"]}
    if d["actor"] == seat:
        row["bs"] = turn_story(x, k, seat, T)
        row["ks"] = turn_story(y, k, seat, T)
    row["res_b"] = game_result(x, seat)
    row["res_k"] = game_result(y, seat)
    rows.append(row)

json.dump(rows, open(os.path.join(HERE, "luc_rows.json"), "w"), indent=0)
fixed = [r for r in rows if r["occ"] == 1]
print("records whose divergences.jsonl entry came from the other deck's run:", len(fixed))
for r in fixed:
    print("  ", r["seed"], r["kind"], "old turn/cat", r["old_turn"], r["old_kpfcat"], "-> new", r["turn"], r["kpf_cat"], r["is_kpf"])
print("actor is kpf:", Counter((r["kind"], r["is_kpf"]) for r in rows))
for r in rows:
    if not r["is_kpf"]:
        print("  opp-first divergence", r["seed"], r["kind"], r["turn"], r["kp3_cat"], "|", r["kpf_cat"])
