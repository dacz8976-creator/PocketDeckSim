"""Turn features at the divergence turn for both games of each Vespiquen record -> vsk_feat.json"""
import json, pickle, re
from collections import Counter
from vsk_slots import simulate
from vsk_lib import parse_board

T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
div = json.load(open("vsk_div.json"))
ONE = {"Shuckle ex", "Combee"}
MAIN = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def turn_feat(tr, seat, t, sl):
    idx = [n for n, L in enumerate(tr) if L["turn"] == t]
    own = [n for n in idx if tr[n]["actor"] == seat]
    first = idx[0]
    b0 = parse_board(tr[first]["s"][seat])
    f = {"zone": b0["zc"], "acts": [tr[n]["act"] for n in own], "attack": None, "attach": None, "retreats": 0,
         "xspeed": 0, "sabrina": 0}
    for n in own:
        a = tr[n]["act"]
        if a.startswith("Attack("):
            f["attack"] = re.search(r'title: "([^"]+)"', a).group(1)
            f["attacker"] = sl[n][0]["name"]
            f["attacker_E"] = parse_board(tr[n]["s"][seat])["active"]["E"]
        m = re.search(r"attachments: \[\(1, Grass, (\d)\)\], is_turn_energy: true", a)
        if m:
            k = int(m.group(1))
            s = sl[n][k]
            bb = parse_board(tr[n]["s"][seat])
            occ = [x for x in sl[n] if x]
            ps = ([bb["active"]] if bb["active"] else []) + bb["bench"]
            pos = occ.index(s)
            f["attach"] = {"slot": k, "name": s["name"], "uid": s["uid"], "E_before": len(ps[pos]["E"]), "n": n}
        if a.startswith("Retreat("):
            f["retreats"] += 1
        if "X Speed" in a:
            f["xspeed"] += 1
        if "Sabrina" in a:
            f["sabrina"] += 1
    # end of turn: first line of a later turn
    later = [n for n in range(first, len(tr)) if tr[n]["turn"] > t]
    e = later[0] if later else None
    if e is not None:
        be = parse_board(tr[e]["s"][seat])
        f["end_active"] = be["active"]["name"] if be["active"] else None
        f["end_active_E"] = be["active"]["E"] if be["active"] else ""
        f["end_board"] = tr[e]["s"][seat]
        f["end_opp"] = tr[e]["s"][1 - seat]
        if f["attach"]:
            uid = f["attach"]["uid"]
            where = None
            for k, s in enumerate(sl[e]):
                if s and s["uid"] == uid:
                    where = "active" if k == 0 else "bench"
                    f["holder_end"] = s["name"]
                    occ = [x for x in sl[e] if x]
                    ps = ([be["active"]] if be["active"] else []) + be["bench"]
                    f["holder_end_E"] = ps[occ.index(s)]["E"]
            f["attach"]["where_end"] = where or "gone"
    else:
        f["end_active"] = None
        f["end_board"] = None
    f["end_state_slots"] = [(s["name"]) if s else None for s in (sl[e] if e is not None else [None] * 4)]
    return f


out = []
for r in div:
    g = {}
    for key in ("base", "kpf"):
        tr = T[key][r["seed"]][r["trace"]]
        sl, _ = simulate(tr, r["seat"])
        g[key] = turn_feat(tr, r["seat"], r["turn"], sl)
        # remaining own actions of the turn from the divergence point
        g[key]["rest"] = [L["act"] for L in tr[r["k"]:] if L["turn"] == r["turn"] and L["actor"] == r["seat"]]
        g[key]["div_board"] = tr[r["k"]]["s"][r["seat"]]
        g[key]["div_opp"] = tr[r["k"]]["s"][1 - r["seat"]]
    out.append(dict(r, kp3=g["base"], kpf=g["kpf"]))
json.dump(out, open("vsk_feat.json", "w"))
print(len(out))
