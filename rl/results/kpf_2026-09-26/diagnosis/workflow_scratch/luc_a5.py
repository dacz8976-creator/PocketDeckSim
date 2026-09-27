import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import two_prop, parse_board

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
W = [r for r in rows if r["kind"] == "worse"]
B = [r for r in rows if r["kind"] == "better"]
MAIN = ("Riolu", "Mega Lucario ex", "Lucario")
WALL = ("Bonsly", "Hitmonlee")


def show(title, f):
    a, b = sum(1 for r in W if f(r)), sum(1 for r in B if f(r))
    p1, p2, z = two_prop(a, len(W), b, len(B))
    print(f"{title:95} worse {a:3}/140  better {b:3}/140  z={z:+.2f}")


def endA(st):
    return st["end_active"][0] if st["end_active"] else None


def cls(n):
    if n in MAIN:
        return "main"
    if n in WALL:
        return "wall"
    return "other"


show("kpf end-of-turn Active is main line, kp3's is a wall", lambda r: cls(endA(r["ks"])) == "main" and cls(endA(r["bs"])) == "wall")
show("kpf end-of-turn Active is a wall, kp3's is main line", lambda r: cls(endA(r["ks"])) == "wall" and cls(endA(r["bs"])) == "main")
show("kpf retreats a wall into main line this turn", lambda r: r["ks"]["retreat"] and cls(r["ks"]["retreat"][0]) == "wall" and cls(r["ks"]["retreat"][1]) == "main")
show("kp3 retreats a wall into main line this turn", lambda r: r["bs"]["retreat"] and cls(r["bs"]["retreat"][0]) == "wall" and cls(r["bs"]["retreat"][1]) == "main")
show("kpf retreats main line into a wall this turn", lambda r: r["ks"]["retreat"] and cls(r["ks"]["retreat"][0]) == "main" and cls(r["ks"]["retreat"][1]) == "wall")
show("kp3 retreats main line into a wall this turn", lambda r: r["bs"]["retreat"] and cls(r["bs"]["retreat"][0]) == "main" and cls(r["bs"]["retreat"][1]) == "wall")
show("kp3 Teary Attack this turn, kpf no Teary Attack", lambda r: (r["bs"]["attack"] or [""])[0] == "Teary Attack" and (r["ks"]["attack"] or [""])[0] != "Teary Attack")
show("kpf Teary Attack this turn, kp3 not", lambda r: (r["ks"]["attack"] or [""])[0] == "Teary Attack" and (r["bs"]["attack"] or [""])[0] != "Teary Attack")
show("kp3 attacks, kpf does not attack", lambda r: r["bs"]["attack"] and not r["ks"]["attack"])
show("kp3 Stretch Kick, kpf not", lambda r: (r["bs"]["attack"] or [""])[0] == "Stretch Kick" and (r["ks"]["attack"] or [""])[0] != "Stretch Kick")
show("kpf zone->Active main line; kp3 zone->Bench main line", lambda r: r["ks"]["attach"] and r["bs"]["attach"] and r["ks"]["attach"][0] == "A" and cls(r["ks"]["attach"][1]) == "main" and r["bs"]["attach"][0] == "B" and cls(r["bs"]["attach"][1]) == "main")
show("kpf zone->Active (any); kp3 zone->Bench (any)", lambda r: r["ks"]["attach"] and r["bs"]["attach"] and r["ks"]["attach"][0] == "A" and r["bs"]["attach"][0] == "B")
show("kpf zone->Bench; kp3 zone->Active", lambda r: r["ks"]["attach"] and r["bs"]["attach"] and r["ks"]["attach"][0] == "B" and r["bs"]["attach"][0] == "A")
show("kpf zone->Bench main; kp3 zone->Active wall (Hitmonlee)", lambda r: r["ks"]["attach"] and r["bs"]["attach"] and r["ks"]["attach"][0] == "B" and cls(r["ks"]["attach"][1]) == "main" and r["bs"]["attach"][0] == "A" and cls(r["bs"]["attach"][1]) == "wall")
show("Bonsly is Active at divergence", lambda r: (parse_board(r["own"])["active"] or {}).get("name") == "Bonsly")
show("Bonsly Active at div AND kpf end Active main while kp3 end Active Bonsly", lambda r: (parse_board(r["own"])["active"] or {}).get("name") == "Bonsly" and cls(endA(r["ks"])) == "main" and endA(r["bs"]) == "Bonsly")
show("Hitmonlee Active at divergence", lambda r: (parse_board(r["own"])["active"] or {}).get("name") == "Hitmonlee")
show("Riolu Active at divergence", lambda r: (parse_board(r["own"])["active"] or {}).get("name") == "Riolu")
show("kpf end Active is Mega Lucario ex, kp3's not", lambda r: endA(r["ks"]) == "Mega Lucario ex" and endA(r["bs"]) != "Mega Lucario ex")
show("kp3 end Active is Mega Lucario ex, kpf's not", lambda r: endA(r["bs"]) == "Mega Lucario ex" and endA(r["ks"]) != "Mega Lucario ex")
show("kpf end Active main line (any)", lambda r: cls(endA(r["ks"])) == "main")
show("kp3 end Active main line (any)", lambda r: cls(endA(r["bs"])) == "main")

# the "exposure" direction score: +1 kpf more exposed main line, -1 kpf less, 0 same
def expo(r):
    a, b = cls(endA(r["ks"])), cls(endA(r["bs"]))
    if a == "main" and b != "main":
        return "+ kpf main in front, kp3 not"
    if b == "main" and a != "main":
        return "- kp3 main in front, kpf not"
    return "0 same class"
c1, c2 = Counter(expo(r) for r in W), Counter(expo(r) for r in B)
print(c1, c2)
