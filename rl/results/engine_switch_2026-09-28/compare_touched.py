"""The touched-path check's comparison (run_touched.sh). Identical means equal on every field the files carry:
moves (every chosen move, hashed in order), decisions, openings, winner seat, points, seed. Exit 1 on any difference.
Reach: the watch build's per-game counters (instrument_reach.py): damage applications on the board where Metal Core
Barrier cut damage, and where a turn effect (Jasmine, Cheren, Blue, Adaman...) cut damage."""
import collections, json, os, sys
O = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(O, "touched")
K = os.path.join(O, "..", "kpf_2026-09-26", "reading")
FIELDS = ("moves", "decisions", "openings", "winner_seat", "points", "seed")
bad_total = 0


def load(p):
    return {(g["pairing"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}


def same(a, b, label):
    global bad_total
    f = [x for x in FIELDS if all(x in g for g in a.values()) and all(x in g for g in b.values())]
    missing = set(a) ^ set(b)
    bad = [k for k in a if k in b and any(a[k][x] != b[k][x] for x in f)]
    bad_total += len(bad) + len(missing)
    print(f"  {label}: {len(a) - len(bad) - len(missing & set(a))} of {len(a)} games identical on {f}"
          + (f"; {len(missing)} keys missing" if missing else "") + (f"; DIFFER e.g. {bad[:3]}" if bad else ""))


def reach(w, label, by_key=None):
    rows = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for k, g in w.items():
        name = by_key(g) if by_key else g.get("a", "?")
        r = rows[name]
        r[0] += 1; r[1] += g["reach_barrier"] > 0; r[2] += g["reach_barrier"]; r[3] += g["reach_turn"] > 0; r[4] += g["reach_turn"]
    print(f"  reach ({label}): games where a cut applied on the board / cuts applied")
    for n, (g, gb, nb, gt, nt) in sorted(rows.items()):
        print(f"    {n:40} {g:5} games | Barrier cut in {gb:4} games ({nb:5} hits) | turn-effect cut in {gt:4} games ({nt:5} hits)")
    return rows


print("1. Carrier lists v the 8 panel lists, same seeds (22,801,000,000 + pairing x 10,000 + i):")
old, new, watch = (load(os.path.join(T, f"carriers_kp3_{s}.jsonl")) for s in ("old", "new", "watch"))
same(old, new, "kp3, old official build v new build")
same(new, watch, "kp3, new build v the watch build (watch-only)")
same(load(os.path.join(T, "carriers_k3_old.jsonl")), load(os.path.join(T, "carriers_k3_new.jsonl")), "k3, old v new (250 deals)")
reach(watch, "kp3, by list")
print("2. The Scizor coverage row (recorded on an engine tree identical to 83e17ae) replayed:")
for bot in ("kp3", "k3"):
    same(load(os.path.join(K, f"scizor_{bot}.jsonl")), load(os.path.join(T, f"scizor_{bot}_new.jsonl")), f"{bot}, recorded v new build")
sw = load(os.path.join(T, "scizor_kp3_watch.jsonl"))
same(load(os.path.join(T, "scizor_kp3_new.jsonl")), sw, "kp3, new build v the watch build")
reach(sw, "Scizor row, kp3", by_key=lambda g: f"scizor v {g.get('b', '?')}")
print("3. Dustin's recorded Skarmory (deck 07) commands on both builds (count.py: sha256 of every chosen action per game):")
for lab, what in (("floor", "the floor check's block, seed 7,100"), ("alt", "the largest Jasmine block, seed 21,102,860,000")):
    a = json.load(open(os.path.join(T, f"summary_pin28_{lab}_old.json")))
    b = json.load(open(os.path.join(T, f"summary_pin28_{lab}_new.json")))
    ga, gb = a["game_hash"], b["game_hash"]
    diff = [s for s in ga if gb.get(s) != ga[s]]
    bad_total += len(diff) + len(set(ga) ^ set(gb))
    print(f"  {what}: {len(ga) - len(diff)} of {len(ga)} games identical (move hash, outcome, points)"
          + (f"; DIFFER e.g. {diff[:3]}" if diff else "") + f"; Jasmine plays {len(b.get('jasmine_plays', []))}")
print("RESULT:", "ALL IDENTICAL" if bad_total == 0 else f"{bad_total} DIFFERENCES")
sys.exit(1 if bad_total else 0)
