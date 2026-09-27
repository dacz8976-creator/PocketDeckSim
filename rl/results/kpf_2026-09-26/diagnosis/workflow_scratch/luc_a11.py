import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import two_prop, parse_board
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
MAIN = ("Riolu", "Mega Lucario ex", "Lucario")
endA = lambda st: st["end_active"][0] if st["end_active"] else None
same_line = lambda a, b: a == b or (a in MAIN and b in MAIN and a == "Riolu")  # Riolu attached then evolved


def on_end_active(st):
    if not st["attach"] or st["attach"][0] != "A":
        return False
    return same_line(st["attach"][1], endA(st))


for kind in ("worse", "better"):
    R = [r for r in rows if r["kind"] == kind and parse_board(r["own"])["zcur"] != "None"]
    c = Counter((on_end_active(r["bs"]), on_end_active(r["ks"])) for r in R)
    print(kind, len(R), "(kp3 zone on its end Active, kpf zone on its end Active):", dict(c))
