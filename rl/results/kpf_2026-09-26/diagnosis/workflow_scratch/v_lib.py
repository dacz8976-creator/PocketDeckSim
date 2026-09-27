"""Vespiquen analyst helpers: load the dumps with each seed's traces split (a tick of 1 starts a new trace), pick the
right trace for each selected game, parse boards and actions."""
import json, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")
MON = re.compile(r"^(.+?) (\d+)hp((?: PSN| BRN| SLP| PAR)*) E\[(\w*)\]$")
SIDE = re.compile(r"^Z(\w+(?:\(\w+\))?)/(\w+(?:\(\w+\))?) D(\d+) H(\d+) P(\d+) \| (.*?) \| (.*)$")


def load_traces(name, seeds):
    """seed -> list of traces (each a list of tick dicts), split where the tick restarts at 1."""
    out = defaultdict(list)
    for line in open(os.path.join(HERE, name), encoding="utf-8"):
        m = LINE.match(line.rstrip("\n"))
        if not m:
            continue
        seed = int(m.group(1))
        if seed not in seeds:
            continue
        tick = int(m.group(2))
        if tick == 1 or not out[seed]:
            out[seed].append([])
        out[seed][-1].append({"tick": tick, "turn": int(m.group(3)), "tomove": int(m.group(4)),
                              "actor": int(m.group(5)), "act": m.group(6), "s": [m.group(7), m.group(8)]})
    return out


def parse_mon(txt):
    m = MON.match(txt.strip())
    if not m:
        return None
    return {"name": m.group(1), "hp": int(m.group(2)), "status": m.group(3).split(), "e": m.group(4)}


def parse_side(txt):
    m = SIDE.match(txt)
    if not m:
        raise ValueError(txt)
    cur, nxt, d, h, p, act, bench = m.groups()
    return {"cur": cur, "next": nxt, "D": int(d), "H": int(h), "P": int(p),
            "active": None if act.strip() == "-" else parse_mon(act),
            "bench": [parse_mon(b) for b in bench.split(", ") if b.strip()]}


def cat(act):
    if act.startswith("Attack("):
        m = re.search(r'title: "([^"]+)"', act)
        return "ATTACK " + (m.group(1) if m else "?")
    if act.startswith("EndTurn"):
        return "END"
    if act.startswith("Attach {"):
        m = re.search(r"\(\d+, \w+, (\d+)\)", act)
        return "ATTACH->ACTIVE" if m and m.group(1) == "0" else "ATTACH->BENCH"
    for pre, name in (("Evolve", "EVOLVE"), ("Place", "PLACE"), ("Retreat", "RETREAT"), ("UseAbility", "ABILITY"),
                      ("AttachTool", "TOOL"), ("Promote", "PROMOTE")):
        if act.startswith(pre):
            return name
    if act.startswith("Play {"):
        m = re.search(r"trainer_card: \w+ \d+ ([^}]+?) }", act) or re.search(r"trainer_card: ([^}]+?) }", act)
        return "PLAY " + (m.group(1).strip() if m else "?")
    return "OTHER " + act.split("(")[0].split(" ")[0]


def detail(act):
    """A short readable action: category plus its object."""
    c = cat(act)
    if c in ("EVOLVE", "PLACE"):
        m = re.search(r"Pokemon\(\w+(?:-\w+)? \d+ ([^)]+)\)", act)
        idx = re.search(r"(?:in_play_idx: |\), )(\d+)", act)
        return f"{c} {m.group(1) if m else '?'}@{idx.group(1) if idx else '?'}"
    if c == "RETREAT":
        return "RETREAT->" + re.search(r"Retreat\((\d+)\)", act).group(1)
    if c.startswith("ATTACH"):
        m = re.search(r"\(\d+, \w+, (\d+)\)", act)
        return f"ATTACH@{m.group(1)}"
    if c == "TOOL":
        m = re.search(r"in_play_idx: (\d+), tool_card: Trainer\(\w+ \d+ ([^)]+)\)", act)
        return f"TOOL {m.group(2)}@{m.group(1)}" if m else c
    if c == "PROMOTE":
        m = re.search(r"in_play_idx: (\d+)", act)
        return f"PROMOTE@{m.group(1)}"
    return c


def selected():
    return json.load(open(os.path.join(HERE, "selected.json"), encoding="utf-8"))


def game_pairs(deck="vespiquen"):
    """For each selected game of `deck`: (record, base trace, kpf trace, kpf seat). Picks the kpf trace by run order:
    run_dumps.sh ran groups sorted by (pairing, config), so a seed selected for two decks has its 'first' trace first."""
    sel = selected()
    by_seed = defaultdict(list)
    for g in sel:
        by_seed[g["seed"]].append(g)
    mine = [g for g in sel if g["deck"] == deck]
    seeds = {g["seed"] for g in mine}
    base, kpf = load_traces("dump_base.txt", seeds), load_traces("dump_kpf.txt", seeds)
    out = []
    for g in mine:
        order = sorted(by_seed[g["seed"]], key=lambda h: (h["pairing"], h["config"]))
        k = order.index(g)
        b = base[g["seed"]]
        f = kpf[g["seed"]]
        first_seat = 0 if g["i"] % 2 == 0 else 1
        kseat = first_seat if g["deck"] == g["a"] else 1 - first_seat
        out.append((g, b[min(k, len(b) - 1)], f[k], kseat, len(b), len(f)))
    return out


def first_div(x, y):
    return next((n for n in range(min(len(x), len(y))) if x[n]["act"] != y[n]["act"]), None)
