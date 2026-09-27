import os, re, pickle, math
HERE = os.path.dirname(os.path.abspath(__file__))
games = pickle.load(open(os.path.join(HERE, "luc_games.pkl"), "rb"))

MON = re.compile(r"^(.*?) (\d+)hp(?: (\w+))? E\[(.*?)\]")


def parse_mon(s):
    s = s.strip()
    if not s or s == "-":
        return None
    m = MON.match(s)
    if not m:
        return {"name": s, "hp": 0, "status": None, "e": ""}
    return {"name": m.group(1), "hp": int(m.group(2)), "status": m.group(3), "e": m.group(4)}


def parse_board(b):
    parts = b.split(" | ")
    head = parts[0]
    active = parse_mon(parts[1]) if len(parts) > 1 else None
    bench = []
    if len(parts) > 2 and parts[2].strip():
        # split on ", " followed by a capital letter name
        for x in re.split(r", (?=[A-Z])", parts[2]):
            pm = parse_mon(x)
            if pm:
                bench.append(pm)
    hm = re.match(r"Z(\S+)/(\S+) D(\d+) H(\d+) P(\d+)", head)
    return {"zcur": hm.group(1), "znext": hm.group(2), "D": int(hm.group(3)), "H": int(hm.group(4)),
            "P": int(hm.group(5)), "active": active, "bench": bench}


def ecount(mon):
    if not mon:
        return 0
    return len([c for c in mon["e"].split(",") if c.strip()]) if "," in mon["e"] else len(mon["e"].strip())


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


def kpf_seat(meta):
    first_seat = 0 if meta["i"] % 2 == 0 else 1
    return first_seat if meta["deck"] == meta["a"] else 1 - first_seat


def first_div(x, y):
    return next((n for n in range(min(len(x), len(y))) if x[n]["act"] != y[n]["act"]), None)


def turn_story(moves, k, seat, turn):
    """kpf-seat moves from index k to the end of `turn` (own turn). Returns dict."""
    out = {"acts": [], "attach": None, "attack": None, "retreat": None, "evolve": [], "place": [], "end_active": None,
           "promote": None}
    n = k
    while n < len(moves) and moves[n]["turn"] == turn:
        mv = moves[n]
        if mv["actor"] == seat:
            c = cat(mv["act"])
            out["acts"].append(c)
            b = parse_board(mv["s"][seat])
            nb = parse_board(moves[n + 1]["s"][seat]) if n + 1 < len(moves) else None
            if c.startswith("ATTACH"):
                m = re.search(r"\((\d+), (\w+), (\d+)\)", mv["act"])
                slot = int(m.group(3))
                is_zone = "is_turn_energy: true" in mv["act"]
                # name of target: Active if 0; bench: the bench mon whose energy grew
                name = b["active"]["name"] if slot == 0 and b["active"] else None
                if slot != 0 and nb:
                    for i2, bm in enumerate(nb["bench"]):
                        old = b["bench"][i2] if i2 < len(b["bench"]) else None
                        if old and old["name"] == bm["name"] and len(bm["e"]) > len(old["e"]):
                            name = bm["name"]
                if is_zone and out["attach"] is None:
                    out["attach"] = ("A" if slot == 0 else "B", name)
            elif c.startswith("ATTACK"):
                out["attack"] = (c[7:], b["active"]["name"] if b["active"] else None)
            elif c == "RETREAT":
                to = nb["active"]["name"] if nb and nb["active"] else "?"
                out["retreat"] = (b["active"]["name"] if b["active"] else None, to)
            elif c == "EVOLVE":
                m = re.search(r"Evolve\((?:Pokemon\()?\w+ \d+ ([^,\)]+)", mv["act"])
                out["evolve"].append(m.group(1) if m else mv["act"][:40])
            elif c == "PLACE":
                m = re.search(r"Pokemon\(\w+ \d+ ([^\)]+)\)", mv["act"])
                out["place"].append(m.group(1) if m else "?")
            elif c == "PROMOTE":
                out["promote"] = mv["act"]
        n += 1
    # active at end of turn: board of the first move of next turn
    if n < len(moves):
        b = parse_board(moves[n]["s"][seat])
        out["end_active"] = (b["active"]["name"], b["active"]["e"], b["active"]["hp"]) if b["active"] else None
        out["end_bench"] = [(m["name"], m["e"]) for m in b["bench"]]
    else:
        out["end_active"] = None
        out["end_bench"] = []
    out["end_n"] = n
    return out


def game_result(moves, seat):
    last = moves[-1]
    b0 = parse_board(last["s"][seat])
    b1 = parse_board(last["s"][1 - seat])
    return b0["P"], b1["P"]


def two_prop(a, n1, b, n2):
    p1, p2 = a / n1, b / n2
    p = (a + b) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else 1
    return p1, p2, (p1 - p2) / se
