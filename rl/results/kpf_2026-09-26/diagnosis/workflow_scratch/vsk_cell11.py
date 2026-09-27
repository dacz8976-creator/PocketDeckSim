import json, re, sys
from collections import Counter
from vsk_stats import test

F = json.load(open("vsk_feat.json"))
ONE = {"Shuckle ex", "Combee"}
MAIN = {"Vespiquen ex", "Teal Mask Ogerpon ex"}


def short(a):
    if a.startswith("Attack("):
        return "ATK:" + re.search(r'title: "([^"]+)"', a).group(1)
    m = re.search(r"trainer_card: (?:\S+ \S+ )?([^}]+?) }", a)
    if a.startswith("Play") and m:
        return "PLAY:" + m.group(1)
    m = re.search(r"attachments: \[\(1, Grass, (\d)\)\]", a)
    if m:
        return "ATT" + m.group(1)
    m = re.match(r"Place\(Pokemon\(\S+ \S+ (.*?)\), (\d)\)", a)
    if m:
        return "PLACE:" + m.group(1) + "@" + m.group(2)
    m = re.match(r"Evolve \{ evolution: Pokemon\(\S+ \S+ (.*?)\), in_play_idx: (\d)", a)
    if m:
        return "EVO:" + m.group(1) + "@" + m.group(2)
    if a.startswith("AttachTool"):
        m = re.search(r"in_play_idx: (\d)", a)
        return "TOOL@" + m.group(1)
    if a.startswith("Retreat"):
        return a
    for k in ("EndTurn", "UseStadium", "DrawCard", "ApplyDamage", "ResolveAttackRetaliation", "DiscardOwnBenchedThenDamage", "Promote", "Activate"):
        if a.startswith(k):
            return k
    return a[:30]


def cls(g):
    a = g["attach"]
    if not a:
        return "none"
    h = g.get("holder_end", a["name"])
    return f"{a.get('where_end')}-" + ("1c" if h in ONE else "GG" if h in MAIN else h)


want = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("active-1c", "active-1c")
rows = [r for r in F if (cls(r["kp3"]), cls(r["kpf"])) == want]
sub = Counter()
for r in rows:
    k, f = r["kp3"], r["kpf"]
    drop = {"DrawCard", "ApplyDamage", "ResolveAttackRetaliation", "EndTurn"}
    ks = [short(a) for a in k["rest"] if short(a) not in drop]
    fs = [short(a) for a in f["rest"] if short(a) not in drop]
    tags = []
    if k["attack"] != f["attack"]:
        tags.append(f"atk {k['attack']}->{f['attack']}")
    if k.get("attacker") != f.get("attacker"):
        tags.append(f"attacker {k.get('attacker')}->{f.get('attacker')}")
    if k["end_active"] != f["end_active"]:
        tags.append(f"endActive {k['end_active']}->{f['end_active']}")
    if k["sabrina"] != f["sabrina"]:
        tags.append(f"sabrina {k['sabrina']}->{f['sabrina']}")
    if Counter(ks) == Counter(fs):
        tags.append("same-multiset")
    tag = "; ".join(tags) if tags else "other"
    sub[(tag, r["kind"])] += 1
    print(f"{r['kind']:6s} {r['seed']} t{r['turn']} Z={k['zone']} | kp3: {' '.join(ks)}\n{'':26s}kpf: {' '.join(fs)}\n{'':26s}[{tag}] board: {k['div_board']} || opp: {k['div_opp']}")
print()
tags = sorted({t for t, _ in sub}, key=lambda t: -(sub[(t, 'worse')] + sub[(t, 'better')]))
for t in tags:
    print(f"{sub[(t, 'worse')]:3d}/{sub[(t, 'better')]:3d}  {t}")
