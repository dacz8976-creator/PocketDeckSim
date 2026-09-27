"""Vespiquen: first divergence (traces split correctly) and the kpf side's whole divergence turn under each bot."""
import json, sys
from collections import Counter
from v_lib import game_pairs, first_div, parse_side, cat, detail

COST = {"Vespiquen ex": 2, "Teal Mask Ogerpon ex": 2, "Shuckle ex": 1, "Combee": 1}


def turn_actions(tr, k, seat):
    """All of `seat`'s ticks in the turn of tick k (from the turn's start), until the turn number changes."""
    T = tr[k]["turn"]
    start = k
    while start > 0 and tr[start - 1]["turn"] == T:
        start -= 1
    end = k
    while end + 1 < len(tr) and tr[end + 1]["turn"] == T:
        end += 1
    return start, end


def mons(side):
    out = []
    if side["active"]:
        out.append(("A", side["active"]))
    out += [("B", m) for m in side["bench"]]
    return out


def attach_target(tr, n, seat):
    before, after = parse_side(tr[n]["s"][seat]), parse_side(tr[n + 1]["s"][seat]) if n + 1 < len(tr) else None
    act = tr[n]["act"]
    if ", 0)]" in act:
        return "A:" + (before["active"]["name"] if before["active"] else "?")
    if after is None:
        return "B:?"
    bb, ab = before["bench"], after["bench"]
    for i, m in enumerate(ab):
        if i < len(bb) and len(m["e"]) > len(bb[i]["e"]):
            return "B:" + m["name"]
    return "B:?"


def summarize(tr, s, e, seat):
    zone, attack, retreat, evolve, place, plays, tools, stadium, abil = None, None, [], [], [], [], [], 0, 0
    for n in range(s, e + 1):
        t = tr[n]
        if t["actor"] != seat:
            continue
        c = cat(t["act"])
        if c.startswith("ATTACH") and "is_turn_energy: true" in t["act"]:
            zone = attach_target(tr, n, seat)
        elif c.startswith("ATTACK"):
            attack = c[7:]
        elif c == "RETREAT":
            nxt = parse_side(tr[n + 1]["s"][seat]) if n + 1 < len(tr) else None
            retreat.append((parse_side(t["s"][seat])["active"]["name"], nxt["active"]["name"] if nxt and nxt["active"] else "?"))
        elif c == "EVOLVE":
            evolve.append(detail(t["act"]))
        elif c == "PLACE":
            place.append(detail(t["act"]))
        elif c.startswith("PLAY"):
            plays.append(c[5:])
        elif c == "TOOL":
            tools.append(detail(t["act"]))
        elif c.startswith("OTHER UseStadium"):
            stadium += 1
    endb = parse_side(tr[e]["s"][seat])
    return {"zone": zone, "attack": attack, "retreat": retreat, "evolve": evolve, "place": place, "plays": plays,
            "tools": tools, "stadium": stadium, "end": endb}


def fmt_side(sd):
    def m(x):
        return f"{x['name']} {x['hp']}{''.join(' ' + s for s in x['status'])} [{x['e']}]" if x else "-"
    return f"Z{sd['cur']}/{sd['next']} H{sd['H']} P{sd['P']} | {m(sd['active'])} | " + ", ".join(m(b) for b in sd["bench"])


def main():
    rows = []
    for g, b, f, seat, nb, nf in game_pairs():
        k = first_div(b, f)
        if k is None:
            continue
        d = b[k]
        sb, eb = turn_actions(b, k, seat)
        sf, ef = turn_actions(f, k, seat)
        on_kpf_turn = d["tomove"] == seat
        rb = summarize(b, sb, eb, seat)
        rf = summarize(f, sf, ef, seat)
        seq_b = [detail(b[n]["act"]) for n in range(k, eb + 1) if b[n]["actor"] == seat]
        seq_f = [detail(f[n]["act"]) for n in range(k, ef + 1) if f[n]["actor"] == seat]
        rows.append({"seed": g["seed"], "kind": g["kind"], "pairing": g["pairing"], "opp": g["a"] if g["b"] == "vespiquen" else g["b"],
                     "i": g["i"], "turn": d["turn"], "actor": d["actor"], "seat": seat, "tomove": d["tomove"],
                     "kp3": detail(b[k]["act"]), "kpf": detail(f[k]["act"]),
                     "own": b[k]["s"][seat], "opp_board": b[k]["s"][1 - seat],
                     "b_zone": rb["zone"], "f_zone": rf["zone"], "b_attack": rb["attack"], "f_attack": rf["attack"],
                     "b_retreat": rb["retreat"], "f_retreat": rf["retreat"], "b_evolve": rb["evolve"], "f_evolve": rf["evolve"],
                     "b_place": rb["place"], "f_place": rf["place"], "b_plays": rb["plays"], "f_plays": rf["plays"],
                     "b_tools": rb["tools"], "f_tools": rf["tools"],
                     "b_end": fmt_side(rb["end"]), "f_end": fmt_side(rf["end"]),
                     "b_end_active": rb["end"]["active"]["name"] if rb["end"]["active"] else None,
                     "f_end_active": rf["end"]["active"]["name"] if rf["end"]["active"] else None,
                     "seq_b": seq_b, "seq_f": seq_f,
                     "same_multiset": sorted(seq_b) == sorted(seq_f),
                     "same_end": fmt_side(rb["end"]) == fmt_side(rf["end"]),
                     "change": g["change"], "ntraces": (nb, nf)})
    json.dump(rows, open("v_rows.json", "w"), indent=0)
    print(len(rows), Counter((r["kind"], r["actor"] == r["seat"]) for r in rows))


main()
