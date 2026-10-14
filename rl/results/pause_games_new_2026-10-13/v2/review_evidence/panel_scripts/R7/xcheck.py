import json, collections, re
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2"
pos = json.load(open(V2 + "/positions_all.json"))
GAMES = {"261013_015659000": "20261013_015659000_iOS", "261013_020824000": "20261013_020824000_iOS"}


def nm(s):
    return str(s).replace("’", "'").strip()


def inst(side):
    out = []
    a = side.get("active")
    if a and a.get("name"):
        out.append(a)
    b = [p for p in side.get("bench_in_position_order") or [] if p and p.get("name")]
    b.sort(key=lambda p: p.get("bench_position") or 99)
    return out + b


def en(p):
    c = collections.Counter()
    for t, n in ((p.get("attached_energy") or {}).get("by_type") or {}).items():
        c[t] += n
    return dict(c)


for g, d in GAMES.items():
    L = json.load(open(QA + "/" + d + "/TURN_LEDGER.json"))
    rows = {t["turn_number"]: t for t in L["turns"]}
    for p in pos:
        if not p["id"].startswith("KW-" + g):
            continue
        tn = p["turn_count"]
        r = rows[tn]
        b = r["board_at_start"]
        issues = []
        # points
        if [b["owner"]["points"], b["opponent"]["points"]] != p["points"]:
            issues.append("points %s v %s" % (p["points"], [b["owner"]["points"], b["opponent"]["points"]]))
        # hand
        lh = [nm(c["name"]) for c in r["hand_at_start"]["cards_left_to_right"]]
        ph = [" ".join(x.split(" ")[:-2]) for x in p["me"]["hand"]]
        if sorted(lh) != sorted(ph):
            issues.append("hand %s v %s" % (ph, lh))
        # opp hand
        oh = r["opponent_hand_at_owner_turn_start"].get("count")
        if oh != p["opp"]["hand_count"]:
            issues.append("opp hand %s v %s" % (p["opp"]["hand_count"], oh))
        for side, key in (("me", "owner"), ("opp", "opponent")):
            li = inst(b[key])
            pb = p[side]["board"]
            if len(li) != len(pb):
                issues.append("%s board len %d v %d" % (side, len(pb), len(li)))
            for x, y in zip(pb, li):
                xn = " ".join(x["card"].split(" ")[:-2])
                if xn != nm(y["name"]):
                    issues.append("%s name %s v %s" % (side, xn, y["name"]))
                if x["hp"] != y["hp_now"]:
                    issues.append("%s %s hp %s v %s" % (side, xn, x["hp"], y["hp_now"]))
                pe = dict(collections.Counter(x.get("energy", [])))
                if pe != en(y):
                    issues.append("%s %s energy %s v %s" % (side, xn, pe, en(y)))
                pt = [" ".join(t.split(" ")[:-2]) for t in x.get("tools", [])]
                lt = [] if str(y.get("tool")).lower() in ("none", "null") else [nm(y.get("tool"))]
                if pt != lt:
                    issues.append("%s %s tool %s v %s" % (side, xn, pt, lt))
                pc = x.get("conditions", [])
                lc = y.get("special_conditions") or []
                if sorted(pc) != sorted(lc):
                    issues.append("%s %s cond %s v %s" % (side, xn, pc, lc))
        st = b.get("stadium")
        pst = p["stadium"]["card"] if p["stadium"] else None
        if (st in (None, "none") and pst) or (st not in (None, "none") and (not pst or not pst.startswith(st))):
            issues.append("stadium %s v %s" % (pst, st))
        ez = b["owner"]["energy_zone"]
        if ez["this_turn"]["type"] != p["me"]["energy_now"] and not (p["me"]["energy_now"] is None and tn == 1):
            issues.append("energy_now %s v %s" % (p["me"]["energy_now"], ez["this_turn"]))
        print(p["id"], "OK" if not issues else issues)
