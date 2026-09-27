import json
from math import comb
rows = {r["seed"]: r for r in json.load(open("v_rows.json"))}
cls = {r["seed"]: r for r in json.load(open("v_cls.json"))}
GG = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def p2(k, n):
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


def show(name, fn):
    w = [s for s, r in rows.items() if r["kind"] == "worse" and fn(r, cls[s])]
    b = [s for s, r in rows.items() if r["kind"] == "better" and fn(r, cls[s])]
    n = len(w) + len(b)
    print(f"{name:80} {len(w):3} / {len(b):3}  p={p2(len(w), n) if n else 1:.3f}   e.g. worse {w[:4]} better {b[:3]}")


nozone = lambda r: r["own"].startswith("ZNone")
show("pure reorder (same kpf-side action multiset rest of turn, same end board)", lambda r, c: r["same_multiset"] and r["same_end"])
show("same end board, different actions (e.g. extra trainer)", lambda r, c: r["same_end"] and not r["same_multiset"])
show("A1E->A1E and pure reorder", lambda r, c: r["same_multiset"] and r["same_end"] and c["b"]["zone"] == "A" and c["f"]["zone"] == "A" and c["b"]["zone_name"] not in GG and c["f"]["zone_name"] not in GG)
show("A1E->A1E and NOT pure reorder", lambda r, c: not (r["same_multiset"] and r["same_end"]) and c["b"]["zone"] == "A" and c["f"]["zone"] == "A" and c["b"]["zone_name"] not in GG and c["f"]["zone_name"] not in GG)
show("no Zone Energy this turn (first player's t1 / zone used): kpf ends with Shuckle Active, kp3 not", lambda r, c: nozone(r) and r["f_end_active"] == "Shuckle ex" and r["b_end_active"] != "Shuckle ex")
show("no Zone Energy this turn: kp3 ends with Shuckle Active, kpf not", lambda r, c: nozone(r) and r["b_end_active"] == "Shuckle ex" and r["f_end_active"] != "Shuckle ex")
show("Zone Energy turn: kp3 moves Combee out for Shuckle ex and attacks; kpf keeps Combee Active", lambda r, c: not nozone(r) and r["b_end_active"] == "Shuckle ex" and r["f_end_active"] == "Combee")
show("Zone Energy turn: kpf ends with Combee Active, kp3 with Shuckle/GG", lambda r, c: not nozone(r) and r["f_end_active"] == "Combee" and r["b_end_active"] != "Combee")
show("kp3 attacks with Shuckle ex; kpf ends with an unready GG attacker Active (no attack)", lambda r, c: c["b"]["attacker"] == "Shuckle ex" and not c["f"]["attack"] and c["f"]["end_active"] in GG and not c["f"]["end_ready"])
show("kp3 attacks with Shuckle ex; kpf powers a benched GG attacker instead (no attack)", lambda r, c: c["b"]["attacker"] == "Shuckle ex" and not c["f"]["attack"] and c["f"]["zone"] == "B" and c["f"]["zone_name"] in GG)
show("kp3 attacks (any); kpf does not", lambda r, c: c["b"]["attack"] and not c["f"]["attack"])
show("kp3 attacks with a GG attacker; kpf does not", lambda r, c: c["b"]["attacker"] in GG and not c["f"]["attack"])
show("kpf retreats Shuckle ex out (Shuckle Active at start, not at end), kp3 keeps it", lambda r, c: "| Shuckle ex" in r["own"][:60] and r["b_end_active"] == "Shuckle ex" and r["f_end_active"] != "Shuckle ex")
show("kpf ends with an unready GG attacker Active and no attack; kp3 does not", lambda r, c: c["f"]["end_active"] in GG and not c["f"]["end_ready"] and not c["f"]["attack"] and not (c["b"]["end_active"] in GG and not c["b"]["end_ready"] and not c["b"]["attack"]))
show("kp3 ends with an unready GG attacker Active and no attack; kpf does not", lambda r, c: c["b"]["end_active"] in GG and not c["b"]["end_ready"] and not c["b"]["attack"] and not (c["f"]["end_active"] in GG and not c["f"]["end_ready"] and not c["f"]["attack"]))
show("kp3 took more points this turn", lambda r, c: c["b"]["P"] > c["f"]["P"])
show("Sabrina: kp3 plays it, kpf doesn't", lambda r, c: "Sabrina" in r["b_plays"] and "Sabrina" not in r["f_plays"])
show("X Speed: kpf plays it, kp3 doesn't", lambda r, c: "P-A 002 X Speed" in r["f_plays"] and "P-A 002 X Speed" not in r["b_plays"])
show("X Speed: kp3 plays it, kpf doesn't", lambda r, c: "P-A 002 X Speed" in r["b_plays"] and "P-A 002 X Speed" not in r["f_plays"])
show("Leaf Cape on the Active: kp3 yes kpf no", lambda r, c: any(t.endswith("@0") for t in r["b_tools"]) and not any(t.endswith("@0") for t in r["f_tools"]))
show("Leaf Cape on the Active: kpf yes kp3 no", lambda r, c: any(t.endswith("@0") for t in r["f_tools"]) and not any(t.endswith("@0") for t in r["b_tools"]))
