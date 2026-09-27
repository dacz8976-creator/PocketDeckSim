"""kpf's held-out-deck veto check (RUN5 Rules: "a held-out deck more than 2 further" from Limitless), B2e's way:
each archetype's panel score (its equal-weight average over the 8 panel opponents, B2e pairings 0-47) under kp3 and
kpf3 at 9bffbda, against the Limitless pooled equal-weight average (B2e's reference; development beside). Dustin's
matching files (pairings 48-95) are reported beside, never counted. Under rule v2 a veto counts only through mixed
rows; none were run for B2e, so a firing veto reads "awaits mixed rows". Usage: python3 heldout_check.py"""
import csv, json, os
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
B2E = os.path.join(HERE, "..", "..", "b2e_card_check_2026-09-26")
tsv = [r for r in csv.DictReader(open(os.path.join(B2E, "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")]
lim = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(B2E, "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        lim[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])


def panel(bot):
    by = defaultdict(list)
    games = [json.loads(l) for l in open(os.path.join(HERE, f"b2e_{bot}.jsonl"), encoding="utf-8")]
    rows = {int(r["pairing"]): r for r in tsv}
    for g in games:
        r = rows[g["pairing"]]
        by[(r["block"], r["held_key"], r["opponent"])].append(g["first_deck_score"])
    out = defaultdict(dict)
    for (block, key, opp), s in by.items():
        out[(block, key)][opp] = 100 * sum(s) / len(s)
    return out


kp3, kpf3 = panel("kp3"), panel("kpf3")
print("| block | deck | kp3 panel | kpf3 panel | Limitless pooled (dev) | |kp3-L| | |kpf3-L| | further by | veto (>2) |")
print("|---|---|---:|---:|---:|---:|---:|---:|---|")
for (block, key) in sorted(kp3):
    a = sum(kp3[(block, key)].values()) / len(kp3[(block, key)])
    b = sum(kpf3[(block, key)].values()) / len(kpf3[(block, key)])
    names = sorted({k for k, _ in lim["pooled"]})
    arch = next((k for k in names if k == key), None) or next((k for k in names if k.startswith(key)), None)
    if arch:
        cells = [o for o in kp3[(block, key)] if (arch, o) in lim["pooled"]]
        L = sum(lim["pooled"][(arch, o)] for o in cells) / len(cells)
        Ld = [lim["development"][(arch, o)] for o in cells if (arch, o) in lim["development"]]
        further = abs(b - L) - abs(a - L)
        counted = block.startswith("A")
        verdict = ("FIRES (awaits mixed rows)" if further > 2 else "no") if counted else "reported only"
        print(f"| {block} | {key} | {a:.1f} | {b:.1f} | {L:.1f} ({sum(Ld) / len(Ld):.1f}) | {abs(a - L):.1f} | {abs(b - L):.1f} | {further:+.1f} | {verdict} |")
    else:
        print(f"| {block} | {key} | {a:.1f} | {b:.1f} | (no Limitless key) | | | | reported only |")
