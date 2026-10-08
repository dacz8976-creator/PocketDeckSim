"""Which deck lists in the repository hold one of the five attacks whose return damage takes Weakness (rules/02 sec. 2):
Mega Sableye ex (Cursed Jewel), Alolan Sandslash (Spike Armor), Togedemaru (Bristling Spikes), Chesnaught (Needle
Lariat), Turtonator (Shell Trap). Committed files only (git ls-files), read-only."""
import os, re, subprocess, collections
ROOT = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
IDS = {("B3b", "041"): "Mega Sableye ex", ("B3b", "081"): "Mega Sableye ex", ("B3b", "088"): "Mega Sableye ex",
       ("A3", "039"): "Alolan Sandslash", ("A3b", "048"): "Togedemaru (Bristling Spikes)", ("P-A", "090"): "Togedemaru (Bristling Spikes)",
       ("B2", "010"): "Chesnaught", ("B1", "047"): "Turtonator (Shell Trap)"}
files = subprocess.run(["git", "-C", ROOT, "ls-files", "*.txt"], capture_output=True, text=True).stdout.split("\n")
hits = collections.defaultdict(list)
decks = 0
for f in files:
    if not f:
        continue
    p = os.path.join(ROOT, f)
    try:
        lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        continue
    cardlines = [l.strip().lstrip("﻿") for l in lines if re.match(r"^\s*\d+\s+\S", l)]
    if not cardlines or not any(l.startswith("Energy:") for l in (x.strip().lstrip("﻿") for x in lines[:3])):
        continue
    decks += 1
    for l in cardlines:
        w = l.split()
        if len(w) >= 3 and (w[-2], w[-1]) in IDS:
            hits[f].append(f"{w[0]}x {IDS[(w[-2], w[-1])]} {w[-2]} {w[-1]}")
print(f"deck files scanned: {decks}; lists with a return-damage attacker: {len(hits)}")
by_dir = collections.defaultdict(list)
for f, h in sorted(hits.items()):
    by_dir[os.path.dirname(f)].append((os.path.basename(f), h))
for d, xs in sorted(by_dir.items()):
    print(f"\n{d}/  ({len(xs)})")
    for n, h in xs:
        print(f"  {n}: {'; '.join(h)}")
