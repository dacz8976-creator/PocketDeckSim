import json, os, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import two_prop, parse_board

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
W = [r for r in rows if r["kind"] == "worse"]
B = [r for r in rows if r["kind"] == "better"]


def grp(c):
    if c.startswith("ATTACK"):
        return "ATTACK"
    if c in ("RETREAT", "ATTACH->ACTIVE", "ATTACH->BENCH", "EVOLVE", "PLACE", "END", "PROMOTE", "TOOL"):
        return c
    if c.startswith("PLAY"):
        if any(t in c for t in ("Professor", "Copycat", "Poké Ball")):
            return "PLAY draw/search"
        if "X Speed" in c:
            return "PLAY X Speed"
        return "PLAY other"
    return "OTHER"


def table(title, f):
    cw, cb = Counter(f(r) for r in W), Counter(f(r) for r in B)
    print(f"\n== {title}   (worse n={len(W)}, better n={len(B)})")
    for key in sorted(set(cw) | set(cb), key=lambda k: -(cw[k] + cb[k])):
        a, b = cw[key], cb[key]
        p1, p2, z = two_prop(a, len(W), b, len(B))
        print(f"  {str(key):45} worse {a:3}  better {b:3}   z={z:+.2f}")


table("kpf choice at divergence (grouped)", lambda r: grp(r["kpf_cat"]))
table("kp3 choice at divergence (grouped)", lambda r: grp(r["kp3_cat"]))
table("kpf chose RETREAT", lambda r: r["kpf_cat"] == "RETREAT")
table("kp3 chose RETREAT", lambda r: r["kp3_cat"] == "RETREAT")


# turn-level
def tl(r, key):
    return r.get(key)


def fmt_att(a):
    return a[0] if a else "none"


def retreat_pair(st):
    return st["retreat"] if st["retreat"] else None


table("turn: retreat done (kp3, kpf)", lambda r: (bool(r["bs"]["retreat"]), bool(r["ks"]["retreat"])))
table("turn: attacked (kp3, kpf)", lambda r: (bool(r["bs"]["attack"]), bool(r["ks"]["attack"])))
table("turn: zone attach target (kp3 -> kpf)", lambda r: (fmt_att(r["bs"]["attach"]), fmt_att(r["ks"]["attach"])))
table("turn: zone attach same side?", lambda r: fmt_att(r["bs"]["attach"]) == fmt_att(r["ks"]["attach"]))
table("kpf retreat from->to", lambda r: r["ks"]["retreat"] and tuple(r["ks"]["retreat"]))
table("kp3 retreat from->to", lambda r: r["bs"]["retreat"] and tuple(r["bs"]["retreat"]))


def short(n):
    return n.replace("Mega Lucario ex", "MLex") if n else n


table("end-of-turn Active (kp3 -> kpf)", lambda r: (short(r["bs"]["end_active"][0]) if r["bs"]["end_active"] else None,
                                                    short(r["ks"]["end_active"][0]) if r["ks"]["end_active"] else None))
table("end-of-turn Active differs", lambda r: (r["bs"]["end_active"] or [None])[0] != (r["ks"]["end_active"] or [None])[0])
table("turn of divergence", lambda r: min(r["turn"], 6))
table("Active at divergence", lambda r: short(parse_board(r["own"])["active"]["name"]) if parse_board(r["own"])["active"] else None)
table("opponent", lambda r: r["opp"])
