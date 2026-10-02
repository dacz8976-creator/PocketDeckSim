#!/usr/bin/env python3
"""Affected-deck inventory for the cloud's coin-prevention round 2 (second read, Oct 2), by card id, against origin/main plus any overrides given as PATH=FILE. Run from the repository root."""
import collections, re, subprocess, sys
M = "origin/main"
sh = lambda *a: subprocess.run(["git"] + list(a), capture_output=True, text=True, encoding="utf-8").stdout
IDS = {
    "Will": ["A4 156", "A4 196"],
    "Victini": ["B3 025", "P-B 049"],
    "block-coin attackers": ["A1a 050", "A2a 028", "A2b 012", "B1 143", "B1a 026", "B2 102", "B3 096", "A4 056", "A4 169"],
    "coin Abilities": ["B2 124", "B2 204", "A4 080", "A2 114", "B3b 050"],
    "own-Bench/own-Pokemon attackers": ["A1 103", "B1 302", "A4 072", "B1 088", "B1 237", "P-B 004", "A3 083", "P-A 066", "A3b 039", "B2 140", "B4 083", "A4 098", "B3a 034", "B4a 014", "B4a 080", "B4a 089", "B2b 046", "B2b 104"],
    "Ditto": ["A1 205", "A1 247", "B1a 055", "B3b 099", "P-B 012"],
    "Vespiquen ex": ["B4 011", "B4 180", "B4 194"],
    "Gyarados (Wild Swing)": ["A4 045", "A4 215"],
    "Ariados": ["B1a 006", "B1a 070"],
    "Gholdengo": ["B4a 051", "B4a 109"],
    "Mesagoza / Arcade": ["B2a 093", "B4a 072"],
    "Guts: Conkeldurr, Ursaluna": ["A3 096", "B3b 058"],
    "Galarian Cursola": ["A4a 035"],
    "site attackers (Ogerpon B2 048, Urshifu B3 051, Blastoise B1a 019, Mega Blastoise ex B1a 020/078/084, Hoopa B4 077, Slowking A4a 018, Mega Kangaskhan ex B2 127/189/202, B4 231)":
        ["B2 048", "B3 051", "B1a 019", "B1a 020", "B1a 078", "B1a 084", "B4 077", "A4a 018", "B2 127", "B2 189", "B2 202", "B4 231"],
}
FOSSIL = re.compile(r"Fossil|Old Amber", re.I)
files = [f for f in sh("ls-tree", "-r", "--name-only", M, "decks/").split("\n") if f.endswith(".txt")]
files += [f for f in sh("ls-tree", "-r", "--name-only", M, "rl/results/engine_switch_rules_2026-10/carriers/").split("\n") if f.endswith(".txt")]
override = {a.split("=", 1)[0]: open(a.split("=", 1)[1], encoding="utf-8").read() for a in sys.argv[1:]}
hold = collections.defaultdict(lambda: collections.defaultdict(set))
for f in files:
    txt = override.get(f) or sh("show", f"{M}:{f}")
    for line in txt.splitlines():
        m = re.match(r"(\d+)\s+(.+?)\s+([A-Za-z0-9\-]+)\s+(\d+)$", line.strip())
        if not m:
            continue
        cid = f"{m[3]} {m[4]}"
        for cat, ids in IDS.items():
            if cid in ids:
                hold[cat][f].add(f"{m[1]} {m[2]} {cid}")
        if FOSSIL.search(m[2]):
            hold["Fossils (by name)"][f].add(f"{m[1]} {m[2]} {cid}")
print(f"{len(files)} deck files read at {M}")
for cat in list(IDS) + ["Fossils (by name)"]:
    print("== " + cat)
    if not hold[cat]:
        print("   none")
    for f, cs in sorted(hold[cat].items()):
        print(f"   {f}: " + "; ".join(sorted(cs)))
