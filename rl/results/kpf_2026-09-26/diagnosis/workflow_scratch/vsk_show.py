import json, pickle, re, sys
T = pickle.load(open("/tmp/vsk_traces.pkl", "rb"))
F = {r["seed"]: r for r in json.load(open("vsk_feat.json"))}


def short(a):
    a = re.sub(r"Attack\(Attack \{ energy_required: \[[^\]]*\], title: \"([^\"]+)\".*", r"ATTACK \1", a)
    a = re.sub(r"is_turn_energy: true", "turn", a)
    return a[:90]


for s in map(int, sys.argv[1:]):
    r = F[s]
    t = r["turn"]
    print(f"##### {s} {r['kind']} change {r['change']} pairing {r['pairing']} {r['a']} v {r['b']} seat {r['seat']} div turn {t}")
    for key in ("base", "kpf"):
        tr = T[key][s][r["trace"]]
        print(f"  --- {key}")
        lines = [L for L in tr if t <= L["turn"] <= t + 1]
        for L in lines[:40]:
            if L["turn"] == t + 1 and L["act"].startswith("DrawCard"):
                print(f"    t{L['turn']} END-OF-TURN own: {L['s'][r['seat']]}\n{'':20s}opp: {L['s'][1 - r['seat']]}")
                break
            who = "V" if L["actor"] == r["seat"] else "o"
            print(f"    t{L['turn']} {who} {short(L['act']):90s} || {L['s'][r['seat']]}")
        # points at end
        print(f"    final: {tr[-1]['s'][r['seat']][:40]} vs {tr[-1]['s'][1 - r['seat']][:40]} last turn {tr[-1]['turn']}")
