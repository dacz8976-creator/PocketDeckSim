#!/usr/bin/env python3
"""analyze_kg.py: reads the logger's games (engine/examples/kg_log.rs, one JSON line per game) and prints ky3 item 7's measures for deck 01
(Kingambit), per arm; with two files, the paired comparison per deal (mean difference +/- 1.96 sd/sqrt(n), seats separately).

  analyze_kg.py ARM.jsonl                 the arm's measures
  analyze_kg.py BASE.jsonl SWITCH.jsonl   both arms, then SWITCH - BASE per deal (deals matched by seed and seat)
  analyze_kg.py --selftest                the made-up games below (deck 01 in seat 1, a denied knock-out, an Ilima return, a gust)

Every count is indexed by the record's own `deck_seat`, never by seat 0. The measures (KINGAMBIT_ITEM7.md section 3):
  PL1  Pawniard reached play and was never knocked out before the first Bisharp/Kingambit evolution
  PL2  the first Overlord's Blade came at own-knock-out count >= 2 and knocked out (also: count at the first Blade; Blade by own turn 6/8;
       the count at own turns 6 and 8)
  secondary: Dark Energy on Pawniard before it evolved, fodder share of own knock-outs before the first Blade (fodder = any Pokemon that is
  not Pawniard/Bisharp/Kingambit), Glimmora denials, plan passes P2-P5, win rate, switches by a play-out pilot.
  guards G2 (opponent's points at the first Blade; share of deals with 2+ opponent points before any Blade), G4, G5, G6.
Limits (stated, not hidden): boards are seen at decisions with more than one legal move; "a Glimmora had its turn" (P2) counts attack
tenures (a new tenure starts at each Promote or Retreat by the deck seat and at each own Glimmora knock-out), so a Glimmora that retreats
and returns counts twice; P3 does not separate forced from chosen, it names the cause (opening, gust, other)."""
import json
import math
import sys

BLADE = "Attack:Overlord's Blade"
LINE = ("Pawniard", "Bisharp", "Kingambit")
GUSTS = ("Play:Sabrina", "Play:Cyrus")


def pts(name):
    return 3 if name.startswith("Mega ") or " Mega " in name or name.startswith("M ") else (2 if name.endswith(" ex") else 1)


def evolve_idx(ds, seat):
    """Index (in ds) of the deck seat's first evolution of Pawniard: an Evolve into Bisharp or Kingambit, or a Rare Candy played with a Pawniard
    in play and a Kingambit or Bisharp in hand (the engine's Candy evolution is a follow-up frame that is not a decision of its own)."""
    for i, d in enumerate(ds):
        if d["actor"] != seat:
            continue
        if d["chosen"].startswith(("Evolve:Bisharp", "Evolve:Kingambit")):
            return i
        if d["chosen"] == "Play:Rare Candy" and any(s and s["n"] == "Pawniard" for s in d["boards"][seat]) and \
                any(h in ("Kingambit", "Bisharp") for h in d["hands"][seat]):
            return i
    return None


def measures(g):
    seat, opp = g["deck_seat"], 1 - g["deck_seat"]
    ds, kos = g["decisions"], g["kos"]
    m = {"seed": g["seed"], "seat": seat, "first": g.get("first"), "win": 1.0 if g["winner"] == seat else 0.0}
    mine = [d for d in ds if d["actor"] == seat]
    boards = [d["boards"][seat] for d in mine]
    placed = any(d["chosen"].startswith("Place:Pawniard") for d in mine) or any(s and s["n"] == "Pawniard" for b in boards for s in b)
    ev = evolve_idx(ds, seat)
    ev_turn = ds[ev]["turn"] if ev is not None else None
    pk = [k for k in kos if k["victim_seat"] == seat and k["victim"] == "Pawniard"]
    pk_before = [k for k in pk if ev_turn is None or k["turn"] < ev_turn]
    m["PL1"] = float(placed and not pk_before)
    # first Blade
    blades = [d for d in mine if d["chosen"] == BLADE]
    b = blades[0] if blades else None
    m["blade"] = float(b is not None)
    if b is not None:
        count = b["own_kos"][seat]
        hit = any(k["turn"] == b["turn"] and k["victim_seat"] == opp for k in kos)
        m["blade_count"], m["blade_ko"], m["blade_turn"] = float(count), float(hit), float(b["own_turn"])
        m["PL2"] = float(count >= 2 and hit)
        m["blade_by6"], m["blade_by8"] = float(b["own_turn"] <= 6), float(b["own_turn"] <= 8)
        m["opp_pts_at_blade"] = float(b["points"][opp])
        pre = [k for k in kos if k["victim_seat"] == seat and k["turn"] < b["turn"]]
        pre_opp_pts = max([d["points"][opp] for d in ds if d["turn"] <= b["turn"]] or [0])
    else:
        m["PL2"] = 0.0
        pre = [k for k in kos if k["victim_seat"] == seat]
        pre_opp_pts = g["points"][opp]
    m["opp2_before_blade"] = float(pre_opp_pts >= 2)
    m["fodder_share"] = (sum(1 for k in pre if k["victim"] not in LINE) / len(pre)) if pre else None
    m["denials"] = float(sum(1 for k in kos if k["victim_seat"] == seat and k["denied"]))
    for n in (6, 8):
        cs = [d["own_kos"][seat] for d in mine if d["own_turn"] == n]
        m[f"count_t{n}"] = float(cs[-1]) if cs else None
    # Dark Energy on Pawniard before it evolved (deals where it evolved)
    if ev is not None:
        m["dark_before_evolve"] = float(any(s and s["n"] == "Pawniard" and "Darkness" in s["e"] for d in ds[:ev] if d["actor"] == seat for s in d["boards"][seat]))
    else:
        m["dark_before_evolve"] = None
    # plan: P2 tenures, P3, P4, P5
    own_glim = [k for k in kos if k["victim_seat"] == seat and k["victim"] == "Glimmora"]
    # a Glimmora knock-out ends its tenure: recount with the knock-outs in turn order
    events = sorted([(d["turn"], 0, d) for d in mine if d["chosen"] == "Attack:Venomous Hit" or d["chosen"].startswith(("Promote", "Retreat"))] +
                    [(k["turn"], 1, k) for k in own_glim], key=lambda e: (e[0], e[1]))
    cur, tenures = 0, set()
    for _, kind, e in events:
        if kind == 1 or (kind == 0 and e["chosen"].startswith(("Promote", "Retreat"))):
            cur += 1
        else:
            tenures.add(cur)
    m["P2"] = float(len(tenures) >= 2)
    causes = []
    for i, d in enumerate(ds):
        if d["actor"] != seat:
            continue
        a = d["boards"][seat][0]
        if a and a["n"] in ("Alolan Muk", "Pawniard"):
            prev_opp = next((x for x in reversed(ds[:i]) if x["actor"] == opp), None)
            causes.append("opening" if d["turn"] <= 2 else ("gust" if prev_opp and prev_opp["chosen"].startswith(GUSTS) else "other"))
    m["P3_broken"] = float(bool(causes))
    m["P3_cause"] = causes[0] if causes else None
    wm = None
    for i, d in enumerate(ds):
        if d["actor"] != seat:
            continue
        top = max([s for s in d["boards"][opp] if s], key=lambda s: s["hp"], default=None)
        if top is None:
            continue
        if 60 + 40 * d["own_kos"][seat] >= top["hp"]:
            wm = (i, d, top)
            break
    m["P4_hp"] = m["P4_win"] = m["P4_ready"] = m["P5"] = None
    if wm:
        i, d, top = wm
        still = 3 - d["points"][seat]  # points still needed, from the log's own score
        def ready(x):
            for s in x["boards"][seat]:
                if s and s["n"] == "Kingambit" and s["e"].count("Darkness") >= 2:
                    return True
            able = "Kingambit" in x["hands"][seat] and "Rare Candy" in x["hands"][seat] and any(s and s["n"] == "Pawniard" and s["e"].count("Darkness") >= 1 for s in x["boards"][seat])
            return able
        m["P4_hp"] = 1.0
        m["P4_win"] = float(pts(top["n"]) >= still)
        r = ready(d)
        m["P4_ready"] = float(r)
        m["P5"] = float(r and d["points"][opp] < 3)
    # guards
    g4 = 0.0
    g4n = 0.0
    prev_king = False
    for i, d in enumerate(ds):
        if d["actor"] != seat:
            continue
        a = d["boards"][seat][0]
        king = bool(a and a["n"] == "Kingambit")
        if king and not prev_king and d["own_kos"][seat] <= 1:
            g4n += 1
            nxt_blade = next((x["turn"] for x in mine if x["turn"] >= d["turn"] and x["chosen"] == BLADE), 10 ** 9)
            if any(k["victim_seat"] == seat and k["victim"] == "Kingambit" and d["turn"] <= k["turn"] <= d["turn"] + 2 and k["turn"] < nxt_blade for k in kos):
                g4 += 1
        prev_king = king
    m["G4_promos"], m["G4"] = g4n, float(g4 > 0)
    turns = {d["own_turn"] for d in mine if any(s and s["n"] == "Kingambit" and s["e"].count("Darkness") >= 2 for s in d["boards"][seat][1:])}
    m["G5"] = float(len(turns) >= 2 and g["winner"] != seat)
    m["G6"] = float(any(k["slot"] != 0 for k in pk))
    m["switches"] = float(sum(1 for d in mine if d.get("switch") and d["switch"]["changed"]))
    m["playout_decisions"] = float(sum(1 for d in mine if d.get("switch")))
    return m


NUM = ["PL1", "PL2", "blade", "blade_count", "blade_by6", "blade_by8", "count_t6", "count_t8", "dark_before_evolve", "fodder_share", "denials",
       "P2", "P3_broken", "P4_hp", "P4_win", "P4_ready", "P5", "opp_pts_at_blade", "opp2_before_blade", "G4", "G5", "G6", "win", "switches"]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs), len(xs)) if xs else (None, 0)


def report(ms, name):
    out = [f"== {name}: {len(ms)} deals"]
    for seat in (None, 0, 1):
        sub = [m for m in ms if seat is None or m["seat"] == seat]
        if not sub:
            continue
        out.append(f" seat {'both' if seat is None else seat}: n={len(sub)}")
        for k in NUM:
            mu, n = mean([m.get(k) for m in sub])
            out.append(f"   {k:<20} {'-' if mu is None else f'{mu:.3f}'}  (n={n})")
        out.append(f"   {'P3 causes':<20} " + str({c: sum(1 for m in sub if m.get('P3_cause') == c) for c in ('opening', 'gust', 'other')}))
    return "\n".join(out)


def paired(a, b):
    ka = {(m["seed"], m["seat"]): m for m in a}
    kb = {(m["seed"], m["seat"]): m for m in b}
    keys = sorted(set(ka) & set(kb))
    out = [f"== paired (second - first): {len(keys)} common deals; first-mover mismatches: {sum(1 for k in keys if ka[k].get('first') != kb[k].get('first'))}"]
    for seat in (0, 1):
        ks = [k for k in keys if k[1] == seat]
        if not ks:
            continue
        out.append(f" seat {seat}: n={len(ks)}")
        for name in NUM:
            d = [kb[k][name] - ka[k][name] for k in ks if kb[k].get(name) is not None and ka[k].get(name) is not None]
            if len(d) < 2:
                continue
            mu = sum(d) / len(d)
            sd = math.sqrt(sum((x - mu) ** 2 for x in d) / (len(d) - 1))
            h = 1.96 * sd / math.sqrt(len(d))
            out.append(f"   {name:<20} {mu:+.3f} +/- {h:.3f}  (n={len(d)})")
    return "\n".join(out)


def load(path):
    return [measures(json.loads(l)) for l in open(path, encoding="utf-8") if l.strip()]


# ---- self-test on made-up games -------------------------------------------------------------------------------------------------------

def sl(n, hp=100, e=(), tools=()):
    return {"n": n, "hp": hp, "e": list(e), "tools": list(tools)}


def dec(turn, own, actor, chosen, boards, hands=([], []), pts_=(0, 0), kos_=(0, 0), legal=None, switch=None):
    return {"turn": turn, "own_turn": own, "actor": actor, "legal": legal or [chosen, "EndTurn"], "chosen": chosen, "switch": switch,
            "boards": boards, "hands": list(hands), "points": list(pts_), "own_kos": list(kos_)}


def ko(turn, seat, victim, slot, cause, gained, kop=1, coin=False, denied=False, count=1):
    return {"victim_seat": seat, "victim": victim, "slot": slot, "ko_points": kop, "coin_ability": coin, "points_gained": gained, "denied": denied,
            "cause": cause, "actor": 1 - seat, "turn": turn, "count_after": count}


def game(seed, decisions, kos_, winner, deck_seat=1, points=(0, 0), first=0):
    return {"seed": seed, "deck_seat": deck_seat, "first": first, "winner": winner, "turns": 20, "points": list(points), "own_kos_final": [0, 0],
            "decisions": decisions, "kos": kos_}


def made_up():
    """Deck 01 sits in seat 1 (the opponent, seat 0, is a 180-HP Mega ex deck). Game A: a denied Glimmora knock-out, an Ilima return that is
    NOT a knock-out, a gust that pulls Pawniard Active, Pawniard evolves, a Blade at count 2 that knocks out. Game B: Pawniard knocked out on the
    Bench before evolving, no Blade, a lost game."""
    opp_b = [sl("Mega Gengar ex", 180), None, None, None]
    K = sl("Kingambit", 160, ["Darkness", "Darkness"])
    a = [
        dec(2, 1, 1, "Place:Regigigas@0", [[None] * 4, [sl("Regigigas", 130), None, None, None]]),
        dec(3, 1, 0, "Play:Sabrina", [opp_b, [sl("Regigigas", 130), sl("Pawniard", 60, ["Darkness"]), None, None]]),
        dec(4, 2, 1, "Attack:Venomous Hit", [opp_b, [sl("Pawniard", 60, ["Darkness"]), sl("Glimmora", 90, ["Darkness"]), None, None]], kos_=(0, 0)),
        dec(5, 3, 1, "Play:Ilima", [opp_b, [sl("Regigigas", 40), sl("Glimmora", 90, ["Darkness"]), None, None]]),
        dec(6, 4, 1, "Attack:Venomous Hit", [opp_b, [sl("Glimmora", 90, ["Darkness"]), sl("Pawniard", 60, ["Darkness", "Darkness"]), None, None]]),
        dec(8, 5, 1, "Promote:0", [opp_b, [None, sl("Glimmora", 90, ["Darkness"]), sl("Pawniard", 60, ["Darkness", "Darkness"]), None]], kos_=(0, 1)),
        dec(8, 5, 1, "Attack:Venomous Hit", [opp_b, [sl("Glimmora", 90, ["Darkness"]), None, sl("Pawniard", 60, ["Darkness", "Darkness"]), None]], kos_=(0, 1)),
        dec(10, 6, 1, "Evolve:Kingambit@2", [opp_b, [sl("Glimmora", 30, ["Darkness"]), None, sl("Pawniard", 60, ["Darkness", "Darkness"]), None]],
            hands=([], ["Kingambit", "Rare Candy"]), kos_=(0, 2)),
        dec(12, 7, 1, BLADE, [[sl("Mega Gengar ex", 140), None, None, None], [K, None, None, None]], pts_=(2, 0), kos_=(0, 2)),
    ]
    ka = [ko(7, 1, "Glimmora", 0, "Attack:Slash", 0, coin=True, denied=True, count=1), ko(9, 1, "Regigigas", 0, "Attack:Slash", 1, count=2),
          ko(12, 0, "Mega Gengar ex", 0, BLADE, 0, kop=3, count=1)]
    A = game(1, a, ka, 1, points=(2, 3))
    b = [
        dec(2, 1, 1, "Place:Regigigas@0", [[None] * 4, [sl("Regigigas", 130), sl("Pawniard", 60), None, None]]),
        dec(4, 2, 1, "Attack:Giga Turbo", [opp_b, [sl("Regigigas", 130), sl("Pawniard", 60, ["Darkness"]), None, None]]),
    ]
    kb = [ko(5, 1, "Pawniard", 1, "Attack:Slash", 1, count=1)]
    B = game(2, b, kb, 0, points=(3, 0))
    return A, B


def own_knockouts_of(g):
    return max(k["count_after"] for k in g["kos"] if k["victim_seat"] == g["deck_seat"])


def selftest():
    A, B = made_up()
    ma, mb = measures(A), measures(B)
    assert ma["seat"] == 1 and ma["win"] == 1.0 and mb["win"] == 0.0, "indexed by the deck's seat 1"
    assert ma["PL1"] == 1.0 and mb["PL1"] == 0.0, "Pawniard knocked out on the Bench before evolving fails PL1"
    assert ma["blade"] == 1.0 and ma["blade_count"] == 2.0 and ma["blade_ko"] == 1.0 and ma["PL2"] == 1.0, "Blade at count 2 that knocks out"
    assert mb["PL2"] == 0.0 and mb["blade"] == 0.0
    assert ma["denials"] == 1.0 and mb["denials"] == 0.0, "the denied Glimmora knock-out"
    assert ma["fodder_share"] == 1.0, "both knock-outs before the Blade were fodder"
    assert ma["count_t6"] == 2.0 and ma["count_t8"] is None, "the count at own turn 6; no own turn 8"
    assert ma["blade_by6"] == 0.0 and ma["blade_by8"] == 1.0, "the Blade came on own turn 7"
    assert ma["P3_broken"] == 1.0 and ma["P3_cause"] == "gust", "Pawniard Active after Sabrina is a gust, not a choice"
    assert ma["dark_before_evolve"] == 1.0, "Darkness on Pawniard before Evolve:Kingambit"
    assert ma["P2"] == 1.0, "Glimmora attacked in two tenures (the first one's knock-out and a promote between)"
    assert mb["P2"] == 0.0 and mb["G6"] == 1.0, "Pawniard knocked out on the Bench is G6"
    assert ma["G6"] == 0.0
    C = json.loads(json.dumps(A))
    C["decisions"][7]["chosen"] = "Play:Rare Candy"
    assert evolve_idx(C["decisions"], 1) == 7 and measures(C)["dark_before_evolve"] == 1.0, "a Rare Candy evolution counts"
    # winning moment: count 2 gives a 140 Blade, which reaches the 140 HP Mega Gengar ex only at the last decision (180 HP before)
    assert (ma["P4_hp"], ma["P4_win"], ma["P4_ready"], ma["P5"]) == (1.0, 1.0, 1.0, 1.0)
    assert mb["P4_hp"] is None, "no Pokemon of theirs within reach of a count-1 Blade"
    assert ma["G5"] == 0.0 and ma["G4"] == 0.0 and ma["switches"] == 0.0
    ko_ilima = [k for k in A["kos"] if k["cause"] == "Play:Ilima"]
    assert not ko_ilima and own_knockouts_of(A) == 2, "the Ilima return and the gust are not knock-outs"
    # a sample arm file in the logger's format, paired with itself: every difference is 0
    assert "+0.000" in paired([ma, mb], [ma, mb])
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif len(a) == 1:
        print(report(load(a[0]), a[0]))
    elif len(a) == 2:
        ma, mb = load(a[0]), load(a[1])
        print(report(ma, a[0]))
        print(report(mb, a[1]))
        print(paired(ma, mb))
    else:
        print(__doc__)
        sys.exit(2)
