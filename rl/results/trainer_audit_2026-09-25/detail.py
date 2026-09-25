"""Detail for the Tools with the most waste: where they were attached, on what, and how often the holder was ever
eligible; and for every deck, the share of its games with at least one wasted Tool."""
import collections
import json
import sys

G = [json.loads(l) for l in open(sys.argv[1])]
FOCUS = {"Protective Poncho", "Small Balloon", "Heavy Helmet", "Elegant Cape", "Metal Core Barrier", "Steel Apron",
         "Deceptive Needle", "Rocky Helmet", "Poison Barb"}
by = collections.defaultdict(collections.Counter)
holders = collections.defaultdict(collections.Counter)
games_wasted = collections.Counter()
games_with_tool = collections.Counter()
for g in G:
    wasted_here = False
    for e in g["tool_episodes"]:
        if e["tool"] not in FOCUS:
            continue
        k = (g["deck"], e["tool"])
        by[k]["n"] += 1
        by[k]["at_" + e["pos_at_attach"]] += 1
        useless = (not e["ever_eligible"]) or (e["windows"] > 0 and e["worked"] == 0)
        by[k]["useless"] += useless
        by[k]["useless_at_" + e["pos_at_attach"]] += useless
        if useless:
            holders[k][e["holder"] + " (" + e["pos_at_attach"] + ")"] += 1
            wasted_here = True
        games_with_tool[g["deck"]] += 0
    if any(e["tool"] in FOCUS for e in g["tool_episodes"]):
        games_with_tool[g["deck"]] += 1
    games_wasted[g["deck"]] += wasted_here
print("useless = holder never met the Tool's condition, or the Tool had chances to act and never could")
for k, c in sorted(by.items(), key=lambda kv: -kv[1]["useless"] / kv[1]["n"]):
    if c["n"] < 20:
        continue
    print(f"{k[0]:48s} {k[1]:19s} n={c['n']:4d} attached Active {c['at_Active']:4d} Bench {c['at_Bench']:4d} | "
          f"useless {c['useless']:4d} ({100 * c['useless'] / c['n']:4.1f}%; Active {c['useless_at_Active']}, Bench "
          f"{c['useless_at_Bench']}) | {', '.join(f'{h} x{n}' for h, n in holders[k].most_common(4))}")
print("\ngames (of 240) with at least one useless Tool:")
for d, n in games_wasted.most_common():
    if n:
        print(f"  {d:48s} {n:4d}")
