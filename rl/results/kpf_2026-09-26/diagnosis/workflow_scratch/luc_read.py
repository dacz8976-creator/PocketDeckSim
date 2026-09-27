"""Print readable stories: python3 luc_read.py <kind> <filter> <max>
filter: all | retreat | bonsly | hitriolu | seeds=1,2,3"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luc_lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "luc_rows.json")))
kind, filt, mx = sys.argv[1], sys.argv[2], int(sys.argv[3])


def keep(r):
    if kind != "any" and r["kind"] != kind:
        return False
    if filt == "all":
        return True
    if filt.startswith("seeds="):
        return str(r["seed"]) in filt[6:].split(",")
    ks = r["ks"]
    if filt == "retreat":
        return ks["retreat"] is not None
    if filt == "bonsly":
        return ks["retreat"] and ks["retreat"][0] == "Bonsly" and ks["retreat"][1] in ("Riolu", "Mega Lucario ex")
    if filt == "hitriolu":
        return ks["retreat"] and ks["retreat"][0] == "Hitmonlee" and ks["retreat"][1] in ("Riolu", "Mega Lucario ex")
    if filt == "riohit":
        return ks["retreat"] and ks["retreat"][0] == "Riolu" and ks["retreat"][1] == "Hitmonlee"
    if filt == "noretreat":
        return ks["retreat"] is None
    return True


def own_turns(moves, seat, start_n, count):
    """summaries of the next `count` own turns after index start_n: per turn, active at start, actions compressed"""
    out = []
    n = start_n
    cur = None
    buf = []
    while n < len(moves) and len(out) < count:
        mv = moves[n]
        if mv["actor"] == seat and mv["tomove"] == seat:
            if cur != mv["turn"]:
                if buf:
                    out.append(buf)
                cur = mv["turn"]
                b = parse_board(mv["s"][seat])
                o = parse_board(mv["s"][1 - seat])
                a = b["active"]
                oa = o["active"]
                buf = [f"t{cur} P{b['P']}-{o['P']} A:{a['name'] if a else '-'}{a['hp'] if a else ''}[{a['e'] if a else ''}] vs {oa['name'] if oa else '-'}{oa['hp'] if oa else ''}:"]
            c = cat(mv["act"])
            if c not in ("OTHER DrawCard",):
                buf.append(c.replace("PLAY P-A 007 Professor's Research", "PR").replace("PLAY P-A 005 Poké Ball", "Ball"))
        n += 1
    if buf and len(out) < count:
        out.append(buf)
    return [" ".join(x) for x in out]


cnt = 0
for r in rows:
    if not keep(r):
        continue
    cnt += 1
    if cnt > mx:
        break
    g = games[r["seed"]]
    seat = r["seat"]
    print(f"### seed {r['seed']} {r['kind']} chg {r['change']:+} vs {r['opp']} turn {r['turn']}  final kp3 {r['res_b']} kpf {r['res_k']}")
    print(f"  own: {r['own']}")
    print(f"  opp: {r['oppb']}")
    print(f"  kp3: {r['kp3_act'][:90]}")
    print(f"  kpf: {r['kpf_act'][:90]}")
    for lab, st in (("kp3", r["bs"]), ("kpf", r["ks"])):
        print(f"  {lab} turn: {' '.join(a.replace('PLAY P-A 007 Professor', 'PR').replace('PLAY P-A 005 Poké Ball', 'Ball') for a in st['acts'])}")
        print(f"       zone->{st['attach']} retreat {st['retreat']} attack {st['attack']} end A {st['end_active']} bench {st['end_bench']}")
    for lab, mv in (("kp3", g["base"]), ("kpf", g["kpf"])):
        st = r["bs"] if lab == "kp3" else r["ks"]
        for line in own_turns(mv, seat, st["end_n"], 3):
            print(f"    {lab} next: {line}")
    print()
