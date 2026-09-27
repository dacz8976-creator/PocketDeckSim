"""kp3 against kpr3 on legality_scan's counters, summed over each bot's 14,000 table games: the discard attacks as Hyper
Ray (used or passed, on turns it could knock out and turns it couldn't) and every activated Ability's offered and used
turns, by cell. Usage: python3 summarize.py [bot ...] (default kp3 kpr3)."""
import json, sys
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent
bots = sys.argv[1:] or ['kp3', 'kpr3']

def load(bot):
    attacks = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))  # title -> cell -> [ko used, ko passed, no-ko used, no-ko passed]
    abilities = defaultdict(lambda: defaultdict(lambda: [0, 0]))      # title -> cell -> [offered, used]
    n = 0
    for line in open(D / f'{bot}_500_counters.jsonl'):
        g = json.loads(line); n += 1
        cell = f"{g['a']} v {g['b']}"
        found = dict(g.get('discard_attacks', {}))
        if 'hyper_ray' in g:
            found['Hyper Ray'] = g['hyper_ray']
        for title, counts in found.items():
            for k in range(4):
                attacks[title][cell][k] += counts[k]
        for title, (offered, used) in g.get('abilities', {}).items():
            abilities[title][cell][0] += offered
            abilities[title][cell][1] += used
    return n, attacks, abilities

def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"

runs = {bot: load(bot) for bot in bots if (D / f'{bot}_500_counters.jsonl').exists()}
titles = sorted({t for _, a, _ in runs.values() for t in a})
print("Discard attacks, not-KO-able turns used (used of offered), and KO-able turns passed:")
for title in titles:
    cells = sorted({c for _, a, _ in runs.values() for c in a[title]})
    print(f"  {title}")
    for cell in cells + ['all cells']:
        row = []
        for bot, (_, a, _) in runs.items():
            v = [sum(a[title][c][k] for c in cells) for k in range(4)] if cell == 'all cells' else a[title][cell]
            row.append(f"{bot} no-KO used {v[2]} of {v[2] + v[3]} ({pct(v[2], v[2] + v[3])}), KO passed {v[1]} of {v[0] + v[1]}")
        print(f"    {cell:22s} " + " | ".join(row))
print("Activated Abilities, used of offered turns:")
for title in sorted({t for _, _, b in runs.values() for t in b}):
    cells = sorted({c for _, _, b in runs.values() for c in b[title]})
    print(f"  {title}")
    for cell in cells + ['all cells']:
        row = []
        for bot, (_, _, b) in runs.items():
            v = [sum(b[title][c][k] for c in cells) for k in range(2)] if cell == 'all cells' else b[title][cell]
            row.append(f"{bot} {v[1]} of {v[0]} ({pct(v[1], v[0])})")
        print(f"    {cell:22s} " + " | ".join(row))
print("Games: " + ", ".join(f"{bot} {n}" for bot, (n, _, _) in runs.items()))
