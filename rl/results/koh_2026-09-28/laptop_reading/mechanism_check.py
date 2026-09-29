"""koh's mechanism check (kph registration section 5 step 3, as made exact by amendment 3; diagnostic, not an adoption
test). For each slice row (slices_{altaria,lucario,vespiquen}.json, role 'registered' only): take the tick-split
traces of kp3 v kp3 (../../kpf_2026-09-26/diagnosis/dump_base.txt) and of koh3 on the diagnosed deck
(../laptop_runs/dump_koh.txt), the copy chosen by config as classify.py does. koh reached the row's position when its
first k moves and its board at k equal kp3's; its move at k is then kp3's, kpf's (the row's kpf_act) or another.
Section 6's lines: A fails if koh plays kp3's move in half or fewer of the reached rows in any of Swablu/Eevee, bare
Riolu and Combee, or pooled over them; B fails if koh plays kpf's move in more than half of the reached forward swaps
(all three decks pooled; per deck reported). Worse and better rows both count. Reported beside, gating nothing:
unreached counts, Lucario's end-of-turn Active in turn T, the Lucario hides and the Vespiquen tempo trades.
Usage: python3 mechanism_check.py > mechanism_check.txt"""
import collections, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
DG = os.path.join(HERE, "..", "..", "kpf_2026-09-26", "diagnosis")
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")


def load(path):
    g = collections.defaultdict(list)
    for line in open(path, encoding="utf-8"):
        m = LINE.match(line.rstrip("\n"))
        if m:
            seed, tick, turn, tomove, actor, act, s0, s1 = m.groups()
            if int(tick) == 1 or not g[int(seed)]:
                g[int(seed)].append([])
            g[int(seed)][-1].append({"tick": int(tick), "turn": int(turn), "actor": int(actor), "act": act, "s": [s0, s1]})
    return g


def pick(traces, config):
    if not traces:
        return []
    return traces[1] if len(traces) > 1 and config == "second" else traces[0]


def active_name(side):
    part = side.split(" | ")[1] if " | " in side else ""
    m = re.match(r"(.+?) \d+hp", part)
    return m.group(1) if m else part


import sys  # noqa: E402
# Self-test: python3 mechanism_check.py <kpf's dump_kpf.txt> must find every row reached and kpf's move in every one.
KOH_DUMP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "laptop_runs", "dump_koh.txt")
base, koh = load(os.path.join(DG, "dump_base.txt")), load(KOH_DUMP)
rows = []
for deck in ("altaria", "lucario", "vespiquen"):
    for r in json.load(open(os.path.join(HERE, f"slices_{deck}.json"), encoding="utf-8"))["rows"]:
        if isinstance(r, dict) and r.get("role", "registered") == "registered" and "slice" in r:
            rows.append({**r, "deck": deck})
res = []
for r in rows:
    x, y = pick(base.get(r["seed"], []), r["config"]), pick(koh.get(r["seed"], []), r["config"])
    k = r["k"]
    if not x or not y or k >= len(x) or k >= len(y):
        res.append({**r, "reached": False, "why": "no trace or too short"}); continue
    same_path = all(x[n]["act"] == y[n]["act"] for n in range(k)) and x[k]["s"] == y[k]["s"]
    if not same_path:
        first = next((n for n in range(k) if x[n]["act"] != y[n]["act"]), k)
        res.append({**r, "reached": False, "why": f"split earlier at {first}" if first < k else "same moves, different board"}); continue
    act = y[k]["act"]
    move = "kp3" if act == x[k]["act"] else ("kpf" if act[:120] == r["kpf_act"][:120] else "other")
    out = {**r, "reached": True, "move": move, "koh_act": act}
    if r["deck"] == "lucario" and "lucario_seat" in r:
        seat, T = r["lucario_seat"], r.get("own_turn_T", r["turn"])
        ends = [z for z in y if z["turn"] == T and z["actor"] == seat and z["act"].startswith("EndTurn")]
        if ends:
            name = active_name(ends[-1]["s"][seat])
            out["koh_end_active"] = name
            out["end_like"] = "wall" if name in ("Bonsly", "Hitmonlee") else ("riolu_line" if name in ("Riolu", "Mega Lucario ex", "Lucario") else "other")
    res.append(out)

A = ("swablu_eevee", "bare_riolu", "combee")
B = ("forward_swap", "forward_swap_darkrai")


def tally(sel):
    n = len(sel); reach = [z for z in sel if z["reached"]]
    c = collections.Counter(z["move"] for z in reach)
    return n, len(reach), c["kp3"], c["kpf"], c["other"]


print("koh's mechanism check (kph registration section 5 step 3, amendment 3). Rows: worse and better together.")
print(f"{'slice':30} {'rows':>5} {'reached':>8} {'kp3 move':>9} {'kpf move':>9} {'other':>6}  share kp3 | share kpf (of reached)")
lines = {}
for deck in ("altaria", "lucario", "vespiquen"):
    for sl in sorted({z["slice"] for z in res if z["deck"] == deck}):
        n, rc, a, b, o = tally([z for z in res if z["deck"] == deck and z["slice"] == sl])
        lines[(deck, sl)] = (n, rc, a, b, o)
        print(f"{deck + ' ' + sl:30} {n:5} {rc:8} {a:9} {b:9} {o:6}  {a / rc if rc else float('nan'):.2f} | {b / rc if rc else float('nan'):.2f}")
fail = []
print("\nFix A (section 6: fails if kp3's move is played in half or fewer of the reached rows, any A slice or pooled):")
for sl in A:
    n, rc, a, b, o = tally([z for z in res if z["slice"] == sl])
    ok = rc and a / rc > 0.5
    print(f"  {sl:14} kp3's move {a} of {rc} reached ({a / rc if rc else float('nan'):.2f}) -> {'holds' if ok else 'FAILS'}  [{n - rc} of {n} unreached]")
    fail += [] if ok else [f"A: {sl}"]
n, rc, a, b, o = tally([z for z in res if z["slice"] in A])
ok = rc and a / rc > 0.5
print(f"  {'pooled':14} kp3's move {a} of {rc} reached ({a / rc if rc else float('nan'):.2f}) -> {'holds' if ok else 'FAILS'}  [{n - rc} of {n} unreached]")
fail += [] if ok else ["A: pooled"]
print("\nFix B (section 6: fails if kpf's move is played in more than half of the reached forward swaps):")
for deck in ("altaria", "lucario", "vespiquen"):
    n, rc, a, b, o = tally([z for z in res if z["deck"] == deck and z["slice"] in B])
    print(f"  {deck:10} kpf's move {b} of {rc} reached ({b / rc if rc else float('nan'):.2f}); kp3's {a}; other {o}  [{n - rc} unreached]  (reported)")
n, rc, a, b, o = tally([z for z in res if z["slice"] in B])
ok = rc and b / rc <= 0.5
print(f"  {'pooled':10} kpf's move {b} of {rc} reached ({b / rc if rc else float('nan'):.2f}) -> {'holds' if ok else 'FAILS'}  [{n - rc} of {n} unreached]")
fail += [] if ok else ["B: pooled forward swaps"]
print("\nReported beside, gating nothing:")
for sl in ("hides", "tempo_trade"):
    n, rc, a, b, o = tally([z for z in res if z["slice"] == sl])
    print(f"  {sl:12} rows {n}, reached {rc}: kp3's move {a}, kpf's move {b}, other {o}")
luc = [z for z in res if z["deck"] == "lucario" and z["reached"] and "end_like" in z]
for sl in ("bare_riolu", "forward_swap", "hides"):
    c = collections.Counter(z["end_like"] for z in luc if z["slice"] == sl)
    print(f"  Lucario {sl:12} koh's end-of-turn Active in T: wall {c['wall']}, Riolu line {c['riolu_line']}, other {c['other']}")
why = collections.Counter(z["why"].split(" at ")[0] for z in res if not z["reached"])
print(f"  unreached, why: {dict(why)}")
print("\nRESULT:", "no refutation line crossed" if not fail else "REFUTATION LINES CROSSED: " + "; ".join(fail))
json.dump(res, open(os.path.join(HERE, "mechanism_rows.json"), "w", encoding="utf-8"), indent=0)
