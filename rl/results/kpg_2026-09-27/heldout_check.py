"""kpg's held-out check (REGISTRATION.md section 4): each B2e archetype's panel score (equal-weight over its 8 panel
opponents, pairings 0-47) under kp3 and kpg3 at the official engine, against its Limitless pooled equal-weight average
(development beside). A veto fires when an archetype moves more than 2 points further; under rule v2 it counts only
through mixed rows, which would then be run. Dustin's files (48-95) are reported, never counted. Also the Scizor coverage
row. Usage: python3 heldout_check.py > heldout_check.md"""
import csv, json, os
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)
B2E = os.path.join(RES, "b2e_card_check_2026-09-26")
KPF = os.path.join(RES, "kpf_2026-09-26", "reading")
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(B2E, "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")}
lim = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(B2E, "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        lim[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])
names = sorted({k for k, _ in lim["pooled"]})


def panel(path, rows):
    by = defaultdict(list)
    for g in map(json.loads, open(path, encoding="utf-8")):
        r = rows[g["pairing"]]
        by[(r["block"], r["held_key"], r["opponent"])].append(g["first_deck_score"])
    out = defaultdict(dict)
    for (block, k, o), s in by.items():
        out[(block, k)][o] = 100 * sum(s) / len(s)
    return out


a, b = panel(os.path.join(KPF, "b2e_kp3.jsonl"), tsv), panel(os.path.join(HERE, "b2e_kpg3.jsonl"), tsv)
print("# kpg's held-out check (official engine, main-83e17ae)\n")
print("| block | deck | kp3 panel | kpg3 panel | Limitless pooled (dev) | further by | veto (>2) |\n|---|---|---:|---:|---:|---:|---|")
fires = []
for (block, k) in sorted(a):
    x, y = sum(a[(block, k)].values()) / 8, sum(b[(block, k)].values()) / 8
    base = k.replace("dustin_", "")
    arch = next((n for n in names if n == base), None) or next((n for n in names if n.startswith(base)), None)
    cells = [o for o in a[(block, k)] if (arch, o) in lim["pooled"]]
    L = sum(lim["pooled"][(arch, o)] for o in cells) / len(cells)
    Ld = [lim["development"][(arch, o)] for o in cells if (arch, o) in lim["development"]]
    fur = abs(y - L) - abs(x - L)
    counted = block.startswith("A")
    v = ("FIRES (mixed rows needed)" if fur > 2 else "no") if counted else "reported only"
    if counted and fur > 2:
        fires.append(k)
    print(f"| {block} | {k} | {x:.1f} | {y:.1f} | {L:.1f} ({sum(Ld) / len(Ld):.1f}) | {fur:+.1f} | {v} |")
print(f"\nHeld-out veto: {'none fires' if not fires else 'FIRES for ' + ', '.join(fires)}")
G = os.path.join(RES, "gauntlet_runs_2026-09-26")
nd = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(G, "tsv", "new_decks.tsv"), encoding="utf-8"), delimiter="\t")}
sc = {}
for bot, path in (("kp3", os.path.join(KPF, "scizor_kp3.jsonl")), ("kpg3", os.path.join(HERE, "scizor_kpg3.jsonl"))):
    s = [g["first_deck_score"] for g in map(json.loads, open(path, encoding="utf-8"))]
    sc[bot] = 100 * sum(s) / len(s)
print(f"\nScizor coverage row (reported, not gated): panel average kp3 {sc['kp3']:.1f} -> kpg3 {sc['kpg3']:.1f} (real 32.2 pooled, few matches)")
