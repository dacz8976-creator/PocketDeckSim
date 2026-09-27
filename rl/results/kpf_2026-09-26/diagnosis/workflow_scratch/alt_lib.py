"""Altaria analysis helpers (scratch, read-only over the diagnosis files)."""
import json, os, re
from collections import defaultdict

HERE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis"
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")
MON = re.compile(r"\s*(.+?) (\d+)hp((?: [A-Z]{3})*) E\[([A-Za-z]*)\]")


def parse_side(s):
    head, active, bench = (s.split(" | ") + ["", ""])[:3]
    m = re.match(r"Z(\S+)/(\S+) D(\d+) H(\d+) P(\d+)", head)
    zc, zn, d, h, p = m.groups()
    def mon(x):
        mm = MON.match(x)
        if not mm:
            return None
        return {"name": mm.group(1).strip(), "hp": int(mm.group(2)), "st": mm.group(3).strip(), "e": mm.group(4)}
    a = mon(active) if active.strip() not in ("-", "") else None
    b = [mon(x) for x in re.findall(r"[^,]+?hp(?: [A-Z]{3})* E\[[A-Za-z]*\]", bench)]
    return {"zc": zc, "zn": zn, "D": int(d), "H": int(h), "P": int(p), "active": a, "bench": [x for x in b if x]}


def load_dump(name, seeds):
    """seed -> list of games (each a list of line dicts), split at tick resets."""
    g = defaultdict(list)
    last = {}
    for line in open(os.path.join(HERE, name), encoding="utf-8"):
        if not line.startswith("DUMP2"):
            continue
        sp = line.split(" ", 3)
        seed = int(sp[1])
        if seed not in seeds:
            continue
        m = LINE.match(line.rstrip("\n"))
        if not m:
            continue
        seed, tick, turn, tomove, actor, act, s0, s1 = m.groups()
        seed, tick = int(seed), int(tick)
        if seed not in last or tick <= last[seed]:
            g[seed].append([])
        last[seed] = tick
        g[seed][-1].append({"tick": tick, "turn": int(turn), "tomove": int(tomove), "actor": int(actor), "act": act,
                            "raw": [s0, s1]})
    return g


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
        m = re.search(r"trainer_card: \w+(?:-\w+)? \w+ ([^}]+?) }", act) or re.search(r"trainer_card: ([^}]+?) }", act)
        return "PLAY " + (m.group(1).strip() if m else "?")
    return "OTHER " + act.split("(")[0].split(" ")[0]


class Slots:
    """Tracks in_play slot occupancy (names) for both seats through a game."""
    def __init__(self):
        self.s = [[None] * 4, [None] * 4]

    def sync(self, seat, side):
        sl = self.s[seat]
        a = side["active"]["name"] if side["active"] else None
        if sl[0] != a:
            sl[0] = a
        names = [m["name"] for m in side["bench"]]
        tracked = [(i, sl[i]) for i in range(1, 4) if sl[i] is not None]
        if [n for _, n in tracked] == names:
            return True
        # try removing KO'd ones (subsequence match)
        j = 0
        keep = []
        for i, n in tracked:
            if j < len(names) and names[j] == n:
                keep.append(i)
                j += 1
        if j == len(names):
            for i, n in tracked:
                if i not in keep:
                    sl[i] = None
            return True
        # resync compactly
        for i in range(1, 4):
            sl[i] = names[i - 1] if i - 1 < len(names) else None
        return False

    def apply(self, actor, act):
        m = re.match(r"Place\(Pokemon\(\S+ \S+ (.+?)\), (\d+)\)", act)
        if m:
            self.s[actor][int(m.group(2))] = m.group(1)
            return
        m = re.match(r"Evolve \{ evolution: Pokemon\(\S+ \S+ (.+?)\), in_play_idx: (\d+)", act)
        if m:
            self.s[actor][int(m.group(2))] = m.group(1)
            return
        m = re.match(r"Retreat\((\d+)\)", act)
        if m:
            i = int(m.group(1)); sl = self.s[actor]; sl[0], sl[i] = sl[i], sl[0]
            return
        m = re.match(r"(?:Promote|Activate) \{ player: (\d), in_play_idx: (\d+)", act)
        if m:
            p, i = int(m.group(1)), int(m.group(2)); sl = self.s[p]; sl[0], sl[i] = sl[i], sl[0]


def annotate(game):
    """Adds parsed sides and slot names (before each action) to each line."""
    sl = Slots()
    for ln in game:
        ln["side"] = [parse_side(ln["raw"][0]), parse_side(ln["raw"][1])]
        for seat in (0, 1):
            sl.sync(seat, ln["side"][seat])
        ln["slots"] = [list(sl.s[0]), list(sl.s[1])]
        sl.apply(ln["actor"], ln["act"])
    return game


def describe(ln, seat):
    """Human-readable detail of an action by seat."""
    act = ln["act"]
    c = cat(act)
    sl = ln["slots"][ln["actor"]]
    if c.startswith("ATTACH"):
        m = re.search(r"\((\d+), (\w+), (\d+)\)", act)
        tgt = sl[int(m.group(3))] if m else "?"
        z = "zone" if "is_turn_energy: true" in act else "other"
        return f"{c}({tgt},{z})"
    if c == "RETREAT":
        i = int(re.match(r"Retreat\((\d+)\)", act).group(1))
        return f"RETREAT({sl[0]}->{sl[i]})"
    if c == "PROMOTE":
        m = re.search(r"in_play_idx: (\d+)", act)
        return f"PROMOTE({ln['slots'][int(re.search(r'player: (\d)', act).group(1))][int(m.group(1))]})"
    if c == "EVOLVE":
        m = re.search(r"Pokemon\(\S+ \S+ (.+?)\), in_play_idx: (\d+)", act)
        return f"EVOLVE({m.group(1)}@{'A' if m.group(2) == '0' else 'B'})"
    if c == "PLACE":
        m = re.match(r"Place\(Pokemon\(\S+ \S+ (.+?)\), (\d+)\)", act)
        return f"PLACE({m.group(1)})" if m else c
    if c == "TOOL":
        m = re.search(r"in_play_idx: (\d+), tool_card: Trainer\(\S+ \S+ (.+?)\)", act)
        return f"TOOL({m.group(2)}->{sl[int(m.group(1))]})" if m else c
    if c.startswith("OTHER Activate"):
        m = re.search(r"player: (\d), in_play_idx: (\d+)", act)
        return f"ACTIVATE(p{m.group(1)}:{ln['slots'][int(m.group(1))][int(m.group(2))]})"
    return c


def load_all(deck="altaria"):
    recs = [json.loads(l) for l in open(os.path.join(HERE, "divergences.jsonl"), encoding="utf-8")]
    recs = [r for r in recs if r["deck"] == deck]
    seeds = {r["seed"] for r in recs}
    base = load_dump("dump_base.txt", seeds)
    kpf = load_dump("dump_kpf.txt", seeds)
    return recs, base, kpf
