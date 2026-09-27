import json, pickle, re
from collections import Counter
from vsk_lib import parse_board
T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
div = json.load(open("vsk_div.json"))
c = Counter()
shown = 0
for r in div:
    for key in ("base", "kpf"):
        tr = T[key][r["seed"]][r["trace"]]
        for n, L in enumerate(tr):
            if L["actor"] != r["seat"]:
                continue
            b = parse_board(L["s"][r["seat"]])
            m = re.match(r"Place\(Pokemon\(.*?\), (\d)\)", L["act"])
            if m and m.group(1) != "0":
                idx = int(m.group(1))
                c[("place", idx == len(b["bench"]) + 1)] += 1
                if idx != len(b["bench"]) + 1 and shown < 4:
                    shown += 1
                    print("PLACE", L["act"], "|", L["s"][r["seat"]], "->", tr[n + 1]["s"][r["seat"]])
            m = re.match(r"Retreat\((\d)\)", L["act"])
            if m:
                idx = int(m.group(1))
                c[("retreat_in_range", idx <= len(b["bench"]))] += 1
            m = re.search(r"attachments: \[\(1, Grass, (\d)\)\], is_turn_energy: true", L["act"])
            if m:
                idx = int(m.group(1))
                c[("attach_in_range", idx <= len(b["bench"]))] += 1
            # zone at turn start
        # zone field at first line of each own turn
        seen = set()
        for L in tr:
            if L["tomove"] == r["seat"] and L["turn"] not in seen and L["turn"] > 0:
                seen.add(L["turn"])
                b = parse_board(L["s"][r["seat"]])
                c[("zone_at_turn_start", L["act"][:8], b["zc"])] += 1
print(c)
