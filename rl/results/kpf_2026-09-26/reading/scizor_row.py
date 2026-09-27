"""The Scizor coverage row (pairings 0-7 of the gauntlet's new_decks.tsv) at 9bffbda, the repaired engine, where the
promotion fix removes Bullet Slugger's false +50: panel score and cells under k3, kp3 and kpf3, beside the Limitless
cells (0 to 13 matches each; coverage only, never an accuracy claim). Usage: python3 scizor_row.py"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "..", "..", "gauntlet_runs_2026-09-26")
sys.path.insert(0, G)
import read_gauntlet as RG  # noqa: E402
L = RG.load_cells()
rows = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(G, "tsv", "new_decks.tsv"), encoding="utf-8"), delimiter="\t")}
key = rows[0]["held_key"]
sim = {}
for bot in ("k3", "kp3", "kpf3"):
    for g in map(json.loads, open(os.path.join(HERE, f"scizor_{bot}.jsonl"), encoding="utf-8")):
        sim.setdefault(rows[g["pairing"]]["opponent"], {}).setdefault(bot, []).append(g["first_deck_score"])
print(f"COVERAGE row: {key} (not an accuracy claim; Limitless cells have 0 to 13 matches)")
print("| opponent | k3 | kp3 | kpf3 | Limitless pooled (n) |\n|---|---:|---:|---:|---:|")
avg = {b: [] for b in ("k3", "kp3", "kpf3")}
for opp, s in sim.items():
    v = {b: 100 * sum(x) / len(x) for b, x in s.items()}
    for b in avg:
        avg[b].append(v[b])
    c = L.get(("pooled", key, opp), {})
    print(f"| {opp} | {v['k3']:.1f} | {v['kp3']:.1f} | {v['kpf3']:.1f} | {c.get('pct', float('nan')):.1f} ({c.get('n', 0)}) |")
print("| panel average | " + " | ".join(f"{sum(a) / len(a):.1f}" for a in avg.values()) + " | 32.2 (pooled, 8 opponents) |")
