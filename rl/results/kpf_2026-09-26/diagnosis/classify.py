"""kpf veto diagnosis, step 2: each traced game's first divergence between kp3 v kp3 (dump_base.txt) and the mixed row
with kpf3 on the diagnosed deck (dump_kpf.txt). Writes divergences.jsonl (one record per game: the decision's board,
both choices raw and as categories) and prints the category table, worse against better games, per deck.
Categories: ATTACK <name> | END | ATTACH->ACTIVE | ATTACH->BENCH | EVOLVE | PLACE | RETREAT | PLAY <card> | ABILITY |
TOOL | PROMOTE | OTHER. Usage: python3 classify.py > summary.txt"""
import json, os, re
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")


def load(name):
    """{seed: [trace, ...]}: a seed traced more than once (a pairing in two decks' selections, one run per config) gives
    one trace per run, split where the tick counter restarts. run_dumps.sh runs the (pairing, config) groups sorted, so
    for a seed with two traces the first is config "first" and the second is config "second"."""
    g = defaultdict(list)
    for line in open(os.path.join(HERE, name), encoding="utf-8"):
        m = LINE.match(line.rstrip("\n"))
        if m:
            seed, tick, turn, tomove, actor, act, s0, s1 = m.groups()
            rec = {"tick": int(tick), "turn": int(turn), "actor": int(actor), "act": act, "s": [s0, s1]}
            if int(tick) == 1 or not g[int(seed)]:
                g[int(seed)].append([])
            g[int(seed)][-1].append(rec)
    return g


def pick(traces, config):
    if not traces:
        return []
    return traces[1] if len(traces) > 1 and config == "second" else traces[0]


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


sel = json.load(open(os.path.join(HERE, "selected.json"), encoding="utf-8"))
base, kpf = load("dump_base.txt"), load("dump_kpf.txt")
out, table, missing = [], defaultdict(Counter), 0
for g in sel:
    seed = g["seed"]
    x, y = pick(base.get(seed, []), g["config"]), pick(kpf.get(seed, []), g["config"])
    if not x or not y:
        missing += 1
        continue
    k = next((n for n in range(min(len(x), len(y))) if x[n]["act"] != y[n]["act"]), None)
    if k is None:
        missing += 1
        continue
    kpf_seat = None  # the seat kpf plays: the diagnosed deck's seat in this game
    first_seat = 0 if g["i"] % 2 == 0 else 1  # even deal: first-named deck in seat 0
    deck_is_a = g["deck"] == g["a"]
    kpf_seat = first_seat if deck_is_a else 1 - first_seat
    d = x[k]
    rec = {**g, "tick": d["tick"], "turn": d["turn"], "actor": d["actor"], "kpf_seat": kpf_seat,
           "actor_is_kpf": d["actor"] == kpf_seat, "kp3_act": x[k]["act"], "kpf_act": y[k]["act"],
           "kp3_cat": cat(x[k]["act"]), "kpf_cat": cat(y[k]["act"]),
           "own_board": d["s"][kpf_seat], "opp_board": d["s"][1 - kpf_seat],
           "kp3_next": [cat(z["act"]) for z in x[k:k + 4]], "kpf_next": [cat(z["act"]) for z in y[k:k + 4]]}
    out.append(rec)
    table[(g["deck"], g["kind"])][(rec["kp3_cat"], rec["kpf_cat"])] += 1
with open(os.path.join(HERE, "divergences.jsonl"), "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
print(f"{len(out)} games with a first divergence; {missing} without dumps or divergence; "
      f"divergence on a kpf-side decision: {sum(r['actor_is_kpf'] for r in out)} of {len(out)}")
for deck in ("altaria", "lucario", "vespiquen"):
    for kind in ("worse", "better"):
        c = table[(deck, kind)]
        n = sum(c.values())
        print(f"\n== {deck} {kind} ({n} games): kp3 choice -> kpf choice at the first divergence")
        for (a, b), m in c.most_common(12):
            print(f"   {m:3}  {a:28} -> {b}")
