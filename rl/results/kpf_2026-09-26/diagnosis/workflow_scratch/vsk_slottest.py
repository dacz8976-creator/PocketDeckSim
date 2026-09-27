import json, pickle, re
from collections import Counter
from vsk_slots import simulate
from vsk_lib import parse_board
T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
div = json.load(open("vsk_div.json"))
c = Counter()
chk = Counter()
for r in div:
    for key in ("base", "kpf"):
        tr = T[key][r["seed"]][r["trace"]]
        sl, bad = simulate(tr, r["seat"])
        c[bad > 0] += 1
        # check attach index consistency: the slot targeted gains a G on the next line
        for n, L in enumerate(tr):
            m = re.search(r"attachments: \[\(1, Grass, (\d)\)\], is_turn_energy: true", L["act"])
            if m and L["actor"] == r["seat"] and n + 1 < len(tr):
                k = int(m.group(1))
                tgt = sl[n][k]
                b0 = parse_board(L["s"][r["seat"]]); b1 = parse_board(tr[n + 1]["s"][r["seat"]])
                occ0 = [s for s in sl[n] if s]
                pos = occ0.index(tgt) if tgt in occ0 else None
                ps0 = ([b0["active"]] + b0["bench"]) if b0["active"] else b0["bench"]
                ps1 = ([b1["active"]] + b1["bench"]) if b1["active"] else b1["bench"]
                ok = pos is not None and len(ps0) == len(ps1) and len(ps1[pos]["E"]) == len(ps0[pos]["E"]) + 1
                chk[ok] += 1
print("traces with unsynced lines:", c)
print("attach target check:", chk)
