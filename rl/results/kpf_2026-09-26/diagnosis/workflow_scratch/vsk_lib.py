"""Skeptic's own loader (vespiquen check). Splits each seed's dump lines into separate traces where the tick restarts,
and picks the trace that belongs to each selected record by the run order in run_dumps.sh (groups sorted by
(pairing, config))."""
import json, os, re
from collections import defaultdict

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")


def load_traces(name):
    g = defaultdict(list)  # seed -> list of traces
    last = {}
    for line in open(os.path.join(D, name), encoding="utf-8"):
        m = LINE.match(line.rstrip("\n"))
        if not m:
            continue
        seed, tick, turn, tomove, actor, act, s0, s1 = m.groups()
        seed, tick = int(seed), int(tick)
        if seed not in last or tick <= last[seed]:
            g[seed].append([])
        last[seed] = tick
        g[seed][-1].append({"tick": tick, "turn": int(turn), "tomove": int(tomove), "actor": int(actor), "act": act,
                            "s": [s0, s1]})
    return g


def selection():
    return json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))


def trace_index(sel):
    """record -> index of its trace among the seed's traces (order of (pairing, config) groups in run_dumps.sh)."""
    groups = defaultdict(set)
    for x in sel:
        groups[x["seed"]].add((x["pairing"], x["config"]))
    return lambda x: sorted(groups[x["seed"]]).index((x["pairing"], x["config"]))


def seat_of(rec):
    first_seat = 0 if rec["i"] % 2 == 0 else 1
    return first_seat if rec["deck"] == rec["a"] else 1 - first_seat


POKE = re.compile(r"^(.*?) (\d+)hp(.*?) E\[([A-Za-z]*)\]")


def parse_board(s):
    """'Z<cur>/<next> D.. H.. P.. | Active | Bench' -> dict"""
    parts = s.split(" | ")
    head = parts[0]
    m = re.match(r"Z(\S+)/(\S+) D(\d+) H(\d+) P(\d+)", head)
    zc, zn, disc, hand, pts = m.groups()
    def poke(t):
        t = t.strip()
        if not t or t == "-":
            return None
        mm = POKE.match(t)
        if not mm:
            return {"name": t, "hp": None, "status": "", "E": ""}
        return {"name": mm.group(1), "hp": int(mm.group(2)), "status": mm.group(3).strip(), "E": mm.group(4)}
    active = poke(parts[1]) if len(parts) > 1 else None
    bench = []
    if len(parts) > 2 and parts[2].strip():
        # split on '], ' boundaries
        for t in re.split(r"(?<=\]), ", parts[2].strip()):
            p = poke(t)
            if p:
                bench.append(p)
    return {"zc": zc, "zn": zn, "disc": int(disc), "hand": int(hand), "pts": int(pts), "active": active, "bench": bench}
