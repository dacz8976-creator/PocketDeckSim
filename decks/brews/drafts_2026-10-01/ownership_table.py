#!/usr/bin/env python3
"""ownership_table.py (Oct 2, 2026): what his own lists say about card counts: for every card of the four drafts (by name), the most copies he ran in any list of his own
(decks/dustin/*.txt and the brews with Ladder Log games), and which list. A list he ran is evidence he owns at least that many copies; a card
with no entry is unverified. Run from the repository root: `python3 decks/brews/drafts_2026-10-01/ownership_table.py`. His lists come from origin/main's blobs; the draft lists are read from this folder."""
import csv, io, os, re, subprocess, sys, collections
M = "origin/main"
sh = lambda *a: subprocess.run(["git"] + list(a), capture_output=True, text=True, encoding="utf-8").stdout
ladder = list(csv.DictReader(io.StringIO(sh("show", f"{M}:rl/results/limitless_skill_model_2026-09-25/ladder_log_games.csv"))))
played = sorted({r["dustin_deck_or_brew"] for r in ladder})
tags = set()
for d in played:
    m = re.match(r"(Deck|Brew)\s+(\d+[a-z]?)", d)
    if m:
        tags.add((m[1].lower(), m[2]))
tags.add(("brew", "08"))   # brew 08 (7-3 in the Ladder Log artifact, after the CSV's dates)
files = {}
for kind, num in sorted(tags):
    pat = f"decks/dustin/{num}-" if kind == "deck" else f"decks/brews/brew-{num}-"
    for f in sh("ls-tree", "-r", "--name-only", M, "decks/dustin/", "decks/brews/").split():
        if f.endswith(".txt") and f.startswith(pat if kind == "deck" else f"decks/brews/brew-{num}"):
            files[f] = (kind, num)
# every deck in decks/dustin is his own list even without ladder games
for f in sh("ls-tree", "-r", "--name-only", M, "decks/dustin/").split():
    if f.endswith(".txt"):
        files.setdefault(f, ("deck", f.split("/")[-1][:2]))
print("lists read:", len(files), "| ladder tags:", sorted(tags), file=sys.stderr)
best = {}   # name -> (count, list)
for f in sorted(files):
    for line in sh("show", f"{M}:{f}").splitlines():
        m = re.match(r"(\d+)\s+(.+?)\s+([A-Za-z0-9\-]+)\s+(\d+)$", line.strip())
        if m:
            n, name = int(m[1]), m[2]
            if name not in best or n > best[name][0]:
                best[name] = (n, f.replace("decks/", ""))
rows = []
HERE = os.path.dirname(os.path.abspath(__file__))
for dr in ("A-shark-tempo", "B-tide-heal", "C-meowstic-hatterene-v2", "D-entei-grimhound"):
    txt = open(os.path.join(HERE, f"draft-{dr}.txt"), encoding="utf-8").read()
    for line in txt.splitlines():
        m = re.match(r"(\d+)\s+(.+?)\s+([A-Za-z0-9\-]+)\s+(\d+)$", line.strip())
        if m:
            rows.append((dr[0], int(m[1]), m[2], f"{m[3]} {m[4]}"))
out = ["| draft | needs | card (id) | most copies in his own lists (list) |", "|---|---|---|---|"]
for d, n, name, cid in rows:
    b = best.get(name)
    ev = f"{b[0]} ({b[1]})" if b else "none in his lists"
    mark = "" if b and b[0] >= n else " **not shown at this count**"
    out.append(f"| {d} | {n} | {name} ({cid}) | {ev}{mark} |")
print("\n".join(out))