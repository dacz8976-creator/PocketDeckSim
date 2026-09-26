"""kpr3 beside k3 and kp3 on the 45-cell scoreboard (Sept 26; descriptive, pre-repair).
- New 17 cells: ../new_k3.jsonl, ../new_kp3.jsonl (7fc6ccb) and new_kpr3.jsonl (e09fb46 + the pairs patch, kp3
  identity checked), all on the gauntlet's deals.
- Frozen 28: the table references for k3/kp3 (as read_gauntlet.py) and the cloud's kpr3 table at e09fb46
  (rl/results/kpr_2026-09-25/kpr3_500.jsonl on claude/pensive-ptolemy-spwc0b, read through git show), on the table's deals.
- Limitless cells, metrics (score.py's tau = "real error", average miss, favourite right, correlation): read_gauntlet.py's own.
Usage (WSL): python3 read_kpr3.py > kpr3_reading.txt"""
import itertools, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import read_gauntlet as RG  # noqa: E402

BRANCH_FILE = "origin/claude/pensive-ptolemy-spwc0b:rl/results/kpr_2026-09-25/kpr3_500.jsonl"
PILOTS = ("k3", "kp3", "kpr3")
L = RG.load_cells()
tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
tmp.write(subprocess.run(["git", "show", BRANCH_FILE], cwd=HERE, capture_output=True, text=True, check=True).stdout)
tmp.close()
ref = {pl: RG.games_by_key(RG.REF[pl], pl) for pl in ("k3", "kp3")}
ref["kpr3"] = RG.games_by_key([tmp.name], "kpr3")
new = {pl: RG.games_by_key([os.path.join(os.path.dirname(HERE), f"new_{pl}.jsonl")], pl) for pl in ("k3", "kp3")}
new["kpr3"] = RG.games_by_key([os.path.join(HERE, "new_kpr3.jsonl")], "kpr3")

frozen = {}
for p, (a, b) in enumerate(itertools.combinations(RG.TABLE, 2)):
    for pl in PILOTS:
        sc = []
        for i in range(500):
            r = ref[pl].get((p, i))
            assert r and (r["a"], r["b"]) == (a, b) and r["seed"] == 72_000_000 + 10_000 * p + i, (pl, p, i)
            sc.append(r["first_deck_score"])
        frozen.setdefault((a, b), {})[pl] = RG.cell_stats(sc)
new17 = [(8 + o, "rayquaza", opp) for o, opp in enumerate(RG.PANEL)] + \
        [(16 + o, "altaria_greninja", opp) for o, opp in enumerate(RG.PANEL)] + [(24, "rayquaza", "altaria_greninja")]
sim = {}
for p, key, opp in new17:
    for pl in PILOTS:
        sc = []
        for i in range(500):
            r = new[pl].get((p, i))
            assert r and r["seed"] == 21_108_000_000 + 10_000 * p + i and r["a"] == key, (pl, p, i)
            sc.append(r["first_deck_score"])
        sim.setdefault((key, opp), {})[pl] = RG.cell_stats(sc)

print("kpr3 beside k3 and kp3 on the 45-cell scoreboard (pre-repair; descriptive). Real error = score.py's tau.")
print(f"{'Limitless half':14} {'pilot':5} | {'frozen 28':>17} | {'new 17':>17} | {'all 45':>17} | fav right (45)")
for ds in ("development", "pooled"):
    for pl in PILOTS:
        fz = [{"S": frozen[k][pl]["p"], "nS": 500, "L": L[(ds, *k)].get("p", 0.5), "nL": L[(ds, *k)]["n"]} for k in frozen]
        nw = [{"S": sim[k][pl]["p"], "nS": 500, "L": L[(ds, *k)].get("p", 0.5), "nL": L[(ds, *k)]["n"]} for k in sim]
        m = [RG.metrics(x) for x in (fz, nw, fz + nw)]
        f = lambda d: f"{d['tau']:5.1f} / miss {d['average_miss']:4.1f}"
        print(f"{ds:14} {pl:5} | {f(m[0]):>17} | {f(m[1]):>17} | {f(m[2]):>17} | {m[2]['favorite_right']}/{m[2]['cells']}")
print("\nNew decks, panel average (8 cells; equal weight) and Limitless (development / pooled):")
for key in ("rayquaza", "altaria_greninja"):
    cells = [(key, o) for o in RG.PANEL]
    avg = {pl: sum(sim[c][pl]["pct"] for c in cells) / 8 for pl in PILOTS}
    lim = {ds: sum(L[(ds, *c)]["pct"] for c in cells if L[(ds, *c)]["n"]) / sum(1 for c in cells if L[(ds, *c)]["n"])
           for ds in ("development", "pooled")}
    print(f"  {key:17} k3 {avg['k3']:.1f}  kp3 {avg['kp3']:.1f}  kpr3 {avg['kpr3']:.1f}  | Limitless {lim['development']:.1f} / {lim['pooled']:.1f}")
print("\nNew cells (deck a's score %): k3 / kp3 / kpr3 | Limitless dev (n) / pooled (n)")
for k in sim:
    s = sim[k]
    print(f"  {k[0]:16} v {k[1]:16} {s['k3']['pct']:5.1f} {s['kp3']['pct']:5.1f} {s['kpr3']['pct']:5.1f} | "
          f"{L[('development', *k)].get('pct', float('nan')):5.1f} ({L[('development', *k)]['n']}) / "
          f"{L[('pooled', *k)].get('pct', float('nan')):5.1f} ({L[('pooled', *k)]['n']})")
os.unlink(tmp.name)
