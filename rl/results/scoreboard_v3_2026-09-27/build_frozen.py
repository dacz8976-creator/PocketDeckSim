"""Scoreboard v3: the frozen table on the repaired engine (Dustin, Sept 27: "k3 and kp3 on all 45 cells get re-run on
the repaired build and become the new frozen table"). The games are kpf's reading runs at 9bffbda, whose engine/ is
identical to the official release's source (the merge 83e17ae); pin_identity.txt shows the official build replays them.
- 28 table cells: ../kpf_2026-09-26/reading/table_{k3,kp3}.jsonl (72,000,000 + p x 10,000 + i, i < 500).
- 17 new cells: ../kpf_2026-09-26/reading/new17_{k3,kp3}.jsonl (21,108,000,000 + p x 10,000 + i, pairings 8-24).
- Limitless: scoreboard v2's development cells for the 28, the gauntlet's development cells for the 17; pooled beside.
Writes frozen_cells.csv, frozen_summary.json and prints the tables for README.md. Usage: python3 build_frozen.py"""
import csv, hashlib, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(RES, "gauntlet_runs_2026-09-26"))
import read_gauntlet as RG  # noqa: E402

RUN = os.path.join(RES, "kpf_2026-09-26", "reading")
files = {(s, b): os.path.join(RUN, f"{s}_{b}.jsonl") for s in ("table", "new17") for b in ("k3", "kp3")}
L = RG.load_cells()
new17 = [(8 + o, "rayquaza", opp) for o, opp in enumerate(RG.PANEL)] + \
        [(16 + o, "altaria_greninja", opp) for o, opp in enumerate(RG.PANEL)] + [(24, "rayquaza", "altaria_greninja")]
sim, rows = {}, []
for bot in ("k3", "kp3"):
    t = RG.games_by_key([files[("table", bot)]], bot)
    n = RG.games_by_key([files[("new17", bot)]], bot)
    for p, (a, b) in enumerate(itertools.combinations(RG.TABLE, 2)):
        sc = [t[(p, i)]["first_deck_score"] for i in range(500)]
        assert all(t[(p, i)]["seed"] == 72_000_000 + 10_000 * p + i for i in range(500))
        sim.setdefault((a, b), {})[bot] = RG.cell_stats(sc)
    for p, a, b in new17:
        sc = [n[(p, i)]["first_deck_score"] for i in range(500)]
        assert all(n[(p, i)]["seed"] == 21_108_000_000 + 10_000 * p + i for i in range(500))
        sim.setdefault((a, b), {})[bot] = RG.cell_stats(sc)
summary = {"engine": "main-83e17ae (repaired; engine/ = 9bffbda)", "files": {}, "metrics": {}}
for k, f in files.items():
    summary["files"][os.path.relpath(f, RES)] = hashlib.sha256(open(f, "rb").read()).hexdigest()
for ds in ("development", "pooled"):
    for bot in ("k3", "kp3"):
        c28 = [{"S": sim[k][bot]["p"], "nS": 500, "L": L[(ds, *k)]["p"], "nL": L[(ds, *k)]["n"]} for k in itertools.combinations(RG.TABLE, 2)]
        c17 = [{"S": sim[(a, b)][bot]["p"], "nS": 500, "L": L[(ds, a, b)]["p"], "nL": L[(ds, a, b)]["n"]} for _, a, b in new17]
        c27 = [c for k, c in zip(itertools.combinations(RG.TABLE, 2), c28) if k != RG.QUARANTINE]
        summary["metrics"][f"{ds} {bot}"] = {name: RG.metrics(x) for name, x in
                                            (("frozen 28", c28), ("27 decision set", c27), ("new 17", c17), ("all 45", c28 + c17))}
with open(os.path.join(HERE, "frozen_cells.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["a", "b", "k3", "kp3", "limitless_dev", "n_dev", "limitless_pooled", "n_pooled"])
    for (a, b), s in sim.items():
        w.writerow([a, b, f"{s['k3']['pct']:.1f}", f"{s['kp3']['pct']:.1f}", f"{L[('development', a, b)].get('pct', float('nan')):.1f}",
                    L[("development", a, b)]["n"], f"{L[('pooled', a, b)].get('pct', float('nan')):.1f}", L[("pooled", a, b)]["n"]])
json.dump(summary, open(os.path.join(HERE, "frozen_summary.json"), "w", encoding="utf-8"), indent=1)
print("| Limitless half | Pilot | frozen 28 | 27 decision set | new 17 | all 45 | favourite right (45) |")
print("|---|---|---:|---:|---:|---:|---:|")
for key, m in summary["metrics"].items():
    ds, bot = key.split()
    print(f"| {ds} | {bot} | {m['frozen 28']['tau']:.1f} | {m['27 decision set']['tau']:.1f} | {m['new 17']['tau']:.1f} | "
          f"{m['all 45']['tau']:.1f} | {m['all 45']['favorite_right']}/{m['all 45']['cells']} |")
