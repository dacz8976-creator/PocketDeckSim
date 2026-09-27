"""Skeptic (lucario): independent loader. Splits each seed's trace into runs at tick resets, assigns the lucario run by
config order (first < second inside one pairing), finds the first divergence, and derives per-game turn facts."""
import json, os, re, pickle, math
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")
POK = re.compile(r"^(.+?) (\d+)hp(.*?) E\[([A-Za-z]*)\]$")
RIOLU_LINE = {"Riolu", "Mega Lucario ex", "Lucario"}
WALLS = {"Bonsly", "Hitmonlee"}


def parse_pok(s):
    s = s.strip()
    if not s or s == "-":
        return None
    m = POK.match(s)
    if not m:
        return {"name": s, "hp": None, "st": "", "e": ""}
    return {"name": m.group(1), "hp": int(m.group(2)), "st": m.group(3).strip(), "e": m.group(4)}


def parse_board(s):
    parts = s.split(" | ")
    m = re.match(r"Z(\S+)/(\S+) D(\d+) H(\d+) P(\d+)", parts[0])
    act = parse_pok(parts[1]) if len(parts) > 1 else None
    bench = [parse_pok(x) for x in parts[2].split(", ")] if len(parts) > 2 and parts[2].strip() else []
    bench = [b for b in bench if b]
    return {"zone": m.group(1), "next": m.group(2), "disc": int(m.group(3)), "hand": int(m.group(4)),
            "pts": int(m.group(5)), "active": act, "bench": bench}


def load_runs(name, want):
    runs = defaultdict(list)
    last = {}
    for line in open(os.path.join(D, name), encoding="utf-8"):
        if not line.startswith("DUMP2 "):
            continue
        seed = int(line.split(" ", 2)[1])
        if seed not in want:
            continue
        m = LINE.match(line.rstrip("\n"))
        if not m:
            raise SystemExit("unparsed: " + line[:200])
        _, tick, turn, tomove, actor, act, s0, s1 = m.groups()
        tick = int(tick)
        if seed not in last or tick <= last[seed]:
            runs[seed].append([])
        last[seed] = tick
        runs[seed][-1].append({"tick": tick, "turn": int(turn), "tomove": int(tomove), "actor": int(actor),
                               "act": act, "s": [s0, s1]})
    return runs


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
        m = re.search(r"trainer_card: [\w-]+ \d+ ([^}]+?) }", act) or re.search(r"trainer_card: ([^}]+?) }", act)
        return "PLAY " + (m.group(1).strip() if m else "?")
    return "OTHER " + act.split("(")[0].split(" ")[0]


def turn_owner(run, t):
    for x in run:
        if x["turn"] == t and x["act"].startswith("DrawCard"):
            return x["actor"]
    c = Counter(x["actor"] for x in run if x["turn"] == t and x["act"].startswith("EndTurn"))
    return c.most_common(1)[0][0] if c else None


def turn_facts(run, k, seat, T):
    """Facts about seat's own turn T in `run`, from index k on (lines before k are shared by both games)."""
    idx = [n for n in range(len(run)) if run[n]["turn"] == T]
    after = [n for n in idx if n >= k]
    acts = [run[n] for n in after if run[n]["actor"] == seat]
    # end-of-turn own board: board at the last EndTurn line of T by seat (state before EndTurn); fallback next line
    ends = [n for n in idx if run[n]["actor"] == seat and run[n]["act"].startswith("EndTurn")]
    if ends:
        endb = parse_board(run[ends[-1]]["s"][seat])
        end_n = ends[-1]
    else:
        nxt = [n for n in range(len(run)) if run[n]["turn"] > T]
        end_n = nxt[0] if nxt else len(run) - 1
        endb = parse_board(run[end_n]["s"][seat])
    # zone attach in T (whole turn), with slot tracking through retreats
    zone = None
    for n in idx:
        x = run[n]
        if x["actor"] != seat:
            continue
        if x["act"].startswith("Attach {") and "is_turn_energy: true" in x["act"]:
            m = re.search(r"\((\d+), (\w+), (\d+)\)", x["act"])
            slot = int(m.group(3))
            b0 = parse_board(x["s"][seat])
            b1 = parse_board(run[n + 1]["s"][seat]) if n + 1 < len(run) else b0
            target = None
            if slot == 0:
                target = b0["active"]["name"] if b0["active"] else None
            else:  # bench Pokemon whose energy grew
                for p0, p1 in zip(b0["bench"], b1["bench"]):
                    if p0["name"] == p1["name"] and len(p1["e"]) > len(p0["e"]):
                        target = p1["name"]
                if target is None and len(b0["bench"]) == 1:
                    target = b0["bench"][0]["name"]
            zone = {"n": n, "slot": slot, "pos": slot, "target": target, "before_k": n < k}
        elif zone is not None and x["act"].startswith("Retreat("):
            j = int(re.search(r"Retreat\((\d+)\)", x["act"]).group(1))
            if zone["pos"] == 0:
                zone["pos"] = j
                zone["retreated_from_active"] = True
            elif zone["pos"] == j:
                zone["pos"] = 0
    retreats = []
    for n in after:
        x = run[n]
        if x["actor"] == seat and x["act"].startswith("Retreat("):
            b0 = parse_board(x["s"][seat])
            b1 = parse_board(run[n + 1]["s"][seat]) if n + 1 < len(run) else b0
            retreats.append({"n": n, "from": b0["active"]["name"] if b0["active"] else None,
                             "to": b1["active"]["name"] if b1["active"] else None,
                             "from_e": b0["active"]["e"] if b0["active"] else "",
                             "from_e_after": next((p["e"] for p in b1["bench"] if b0["active"] and p["name"] == b0["active"]["name"]), None)})
    attacks = [cat(x["act"]) for x in acts if x["act"].startswith("Attack(")]
    plays = [cat(x["act"]) for x in acts if x["act"].startswith("Play {")]
    return {"acts": [cat(x["act"]) for x in acts], "raw": [x["act"][:90] for x in acts], "end": endb, "end_n": end_n,
            "zone": zone, "retreats": retreats, "attacks": attacks, "plays": plays}


def next_own_turn_start(run, seat, T):
    """own board at the first line of seat's next own turn (T+2), or None."""
    for x in run:
        if x["turn"] == T + 2:
            return parse_board(x["s"][seat]), x
    return None, None


def build():
    sel = json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))
    luc = [g for g in sel if g["deck"] == "lucario"]
    want = {g["seed"] for g in luc}
    by_seed = defaultdict(list)
    for g in sel:
        by_seed[g["seed"]].append(g)
    base, kpf = load_runs("dump_base.txt", want), load_runs("dump_kpf.txt", want)
    out, notes = [], Counter()
    for g in luc:
        s = g["seed"]
        entries = sorted(by_seed[s], key=lambda e: (str(e["pairing"]), e["config"]))
        occ = [e["deck"] for e in entries].index("lucario")
        nb, nk = len(base[s]), len(kpf[s])
        notes[f"runs base={nb} kpf={nk} entries={len(entries)}"] += 1
        if nb > 1 and base[s][0] != base[s][1]:
            # compare actions only
            same = [x["act"] for x in base[s][0]] == [x["act"] for x in base[s][1]]
            notes[f"base runs differ (acts same={same})"] += 1
        B, K = base[s][min(occ, nb - 1)], kpf[s][occ]
        k = next((n for n in range(min(len(B), len(K))) if B[n]["act"] != K[n]["act"]), None)
        kb = next((n for n in range(min(len(B), len(K))) if B[n]["s"] != K[n]["s"] or B[n]["act"] != K[n]["act"]), None)
        first_seat = 0 if g["i"] % 2 == 0 else 1
        seat = first_seat if g["deck"] == g["a"] else 1 - first_seat
        opp = g["b"] if g["deck"] == g["a"] else g["a"]
        if k is None:
            notes["no divergence"] += 1
            continue
        if kb != k:
            notes["board diverged before act"] += 1
        d = B[k]
        t = d["turn"]
        own = turn_owner(B, t)
        T = t if own == seat else t + 1
        rec = {**g, "opp": opp, "seat": seat, "k": k, "turn": t, "T": T, "actor": d["actor"],
               "actor_is_kpf": d["actor"] == seat, "div_in_own_turn": own == seat,
               "kp3_act": B[k]["act"], "kpf_act": K[k]["act"], "kp3_cat": cat(B[k]["act"]), "kpf_cat": cat(K[k]["act"]),
               "div_board": parse_board(d["s"][seat]), "div_opp": parse_board(d["s"][1 - seat]),
               "kp3": turn_facts(B, k, seat, T), "kpf": turn_facts(K, k, seat, T),
               "occ": occ, "multi": len(entries) > 1}
        nb2, nl = next_own_turn_start(K, seat, T)
        rec["kpf_next_start"] = nb2
        nb3, _ = next_own_turn_start(B, seat, T)
        rec["kp3_next_start"] = nb3
        out.append(rec)
    return out, notes


def z2(a, n1, b, n2):
    p1, p2 = a / n1, b / n2
    p = (a + b) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else float("nan")
    z = (p1 - p2) / se if se else float("nan")
    pv = math.erfc(abs(z) / math.sqrt(2)) if se else float("nan")
    return z, pv


def binom_split(a, b):
    """two-sided exact sign test: a worse vs b better among a+b pattern games, null 50/50."""
    n = a + b
    k = min(a, b)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load_cached():
    p = os.path.join(HERE, "sk_luc_games.pkl")
    if os.path.exists(p):
        return pickle.load(open(p, "rb"))
    out, notes = build()
    pickle.dump((out, notes), open(p, "wb"))
    return out, notes


if __name__ == "__main__":
    out, notes = build()
    pickle.dump((out, notes), open(os.path.join(HERE, "sk_luc_games.pkl"), "wb"))
    print(len(out), "records")
    for k, v in notes.items():
        print(" ", k, v)
    print("actor is kpf:", sum(r["actor_is_kpf"] for r in out), "div in own turn:", sum(r["div_in_own_turn"] for r in out))
    print("multi-entry seeds:", sum(r["multi"] for r in out), "lucario second:", sum(r["occ"] == 1 for r in out))
