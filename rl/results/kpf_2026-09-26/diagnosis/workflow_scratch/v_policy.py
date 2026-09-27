"""Vespiquen, whole-game policy counts for the vespiquen seat: kp3 game (base) vs kpf game on the same deal.
Per own turn with Zone Energy: attacked? ended with a ready Active but no attack (skipped while able)? where did the Zone
Energy end (Active / Bench, main attacker or not)? retreats, X Speed. KOs taken: own Active knocked out while unready."""
import json, re
from collections import Counter, defaultdict
from v_lib import game_pairs, parse_side, cat

COST = {"Vespiquen ex": 2, "Teal Mask Ogerpon ex": 2, "Shuckle ex": 1, "Combee": 1}
GG = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def game_stats(tr, seat):
    st = Counter()
    turns = defaultdict(list)
    for n, t in enumerate(tr):
        turns[t["turn"]].append(n)
    for T, idx in sorted(turns.items()):
        if T == 0:
            continue
        first = tr[idx[0]]
        if first["tomove"] != seat:
            # opponent's turn: did our Active get knocked out? (a Promote by us during their turn)
            for n in idx:
                t = tr[n]
                if t["actor"] == seat and cat(t["act"]) == "PROMOTE":
                    # find the Active before it went missing
                    m = n - 1
                    while m >= 0 and parse_side(tr[m]["s"][seat])["active"] is None:
                        m -= 1
                    a = parse_side(tr[m]["s"][seat])["active"] if m >= 0 else None
                    if a:
                        st["ko_taken"] += 1
                        st["ko_taken_pts"] += 2 if a["name"].endswith(" ex") else 1
                        unready = len(a["e"]) < COST.get(a["name"], 9)
                        if a["name"] in GG:
                            st["ko_taken_GG"] += 1
                            if unready:
                                st["ko_taken_GG_unready"] += 1
                        if a["name"] == "Shuckle ex":
                            st["ko_taken_shuckle"] += 1
                        if a["name"] == "Combee":
                            st["ko_taken_combee"] += 1
            continue
        side0 = parse_side(first["s"][seat])
        has_zone = side0["cur"] != "None"
        st["turns"] += 1
        attacked, zone_slot, zone_name, xs, ret = False, None, None, 0, 0
        for n in idx:
            t = tr[n]
            if t["actor"] != seat:
                continue
            a, c = t["act"], cat(t["act"])
            side = parse_side(t["s"][seat])
            if c.startswith("ATTACK"):
                attacked = True
                st["atk_" + (side["active"]["name"] if side["active"] else "?")] += 1
            elif c.startswith("ATTACH") and "is_turn_energy: true" in a:
                zone_slot = int(re.search(r"\(\d+, \w+, (\d+)\)", a).group(1))
                if zone_slot == 0:
                    zone_name = side["active"]["name"]
                else:
                    nxt = parse_side(tr[n + 1]["s"][seat])
                    zone_name = next((m["name"] for i, m in enumerate(nxt["bench"])
                                      if i < len(side["bench"]) and len(m["e"]) > len(side["bench"][i]["e"])), "?")
            elif c == "RETREAT":
                ret += 1
                kk = int(re.search(r"Retreat\((\d+)\)", a).group(1))
                if zone_slot is not None:
                    zone_slot = kk if zone_slot == 0 else (0 if zone_slot == kk else zone_slot)
            elif c == "PLAY P-A 002 X Speed":
                xs += 1
        end = parse_side(tr[idx[-1]]["s"][seat])
        ea = end["active"]
        if has_zone:
            st["zturns"] += 1
            st["attack"] += attacked
            if ea and not attacked and len(ea["e"]) >= COST.get(ea["name"], 9) and not ({"SLP", "PAR"} & set(ea["status"])):
                st["skip_ready"] += 1
            if zone_slot is None:
                st["zone_none"] += 1
            else:
                where = "A" if zone_slot == 0 else "B"
                kind = "GG" if zone_name in GG else "1E"
                st[f"zone_{where}_{kind}"] += 1
            if ea and ea["name"] in GG and len(ea["e"]) < 2 and not attacked:
                st["end_GG_unready_active"] += 1
            if ea and ea["name"] == "Shuckle ex":
                st["end_shuckle_active"] += 1
        st["retreat"] += ret
        st["xspeed"] += xs
    st["P"] = parse_side(tr[-1]["s"][seat])["P"]
    return st


agg = {k: {"base": Counter(), "kpf": Counter(), "n": 0} for k in ("worse", "better")}
for g, bt, ft, seat, nb, nf in game_pairs():
    a = agg[g["kind"]]
    a["base"].update(game_stats(bt, seat))
    a["kpf"].update(game_stats(ft, seat))
    a["n"] += 1

keys = ["turns", "zturns", "attack", "skip_ready", "zone_A_1E", "zone_A_GG", "zone_B_1E", "zone_B_GG", "zone_none",
        "end_GG_unready_active", "end_shuckle_active", "retreat", "xspeed", "atk_Shuckle ex", "atk_Combee",
        "atk_Vespiquen ex", "atk_Teal Mask Ogerpon ex", "ko_taken", "ko_taken_pts", "ko_taken_GG", "ko_taken_GG_unready",
        "ko_taken_shuckle", "ko_taken_combee", "P"]
print(f"{'':26} {'worse: kp3':>11} {'kpf':>6} {'diff':>6} | {'better: kp3':>11} {'kpf':>6} {'diff':>6} | {'all: kp3':>9} {'kpf':>6} {'ratio':>6}")
for k in keys:
    w, b = agg["worse"], agg["better"]
    wb, wk, bb, bk = w["base"][k], w["kpf"][k], b["base"][k], b["kpf"][k]
    tb, tk = wb + bb, wk + bk
    print(f"{k:26} {wb:11} {wk:6} {wk-wb:+6} | {bb:11} {bk:6} {bk-bb:+6} | {tb:9} {tk:6} {tk/tb if tb else 0:6.2f}")
print("per zone-turn rates (all 280 games): ")
for k in ("attack", "skip_ready", "zone_A_1E", "zone_A_GG", "zone_B_1E", "zone_B_GG", "zone_none", "end_GG_unready_active", "end_shuckle_active"):
    tb = agg["worse"]["base"][k] + agg["better"]["base"][k]
    tk = agg["worse"]["kpf"][k] + agg["better"]["kpf"][k]
    zb = agg["worse"]["base"]["zturns"] + agg["better"]["base"]["zturns"]
    zk = agg["worse"]["kpf"]["zturns"] + agg["better"]["kpf"]["zturns"]
    print(f"  {k:24} kp3 {tb/zb:.3f}  kpf {tk/zk:.3f}")
