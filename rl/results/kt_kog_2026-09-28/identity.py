"""Identity at kt's build on kog (README.md step 2; kt amendment 2, item 7): a run against its reference, game by game,
on moves, choices, openings, winner, points and seed, over the deals both hold (i < deals), and the run's scan page
clean of rule findings. Appends one line to identity/identity_check.txt; exits 1 on any difference.
Usage: python3 identity.py <label> <run.jsonl> <reference.jsonl> <deals>"""
import json, re, sys
from pathlib import Path

label, run, ref, deals = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4])
FIELDS = ("moves", "decisions", "openings", "winner_seat", "points", "seed")


def load(path):
    games = {}
    for line in open(path, encoding="utf-8"):
        g = json.loads(line)
        if g["i"] < deals:
            games[(g["a"], g["b"], g["pairing"], g["i"])] = g
    return games


mine, theirs = load(run), load(ref)
fields = [f for f in FIELDS if all(f in g for g in theirs.values())]
missing = [k for k in theirs if k not in mine]
bad = [k for k in theirs if k in mine and any(mine[k][f] != theirs[k][f] for f in fields)]
page = run.with_suffix(".txt").read_text(encoding="utf-8")
clean = re.search(r"Findings \(occurrences / games affected\):\s*\n\s*none", page) is not None
ok = not missing and not bad and len(mine) == len(theirs) and clean
line = (f"{label}: {len(theirs) - len(missing) - len(bad)} of {len(theirs)} games equal on {', '.join(fields)}"
        f" (run has {len(mine)}; missing {len(missing)}, differing {len(bad)}); {'clean' if clean else 'RULE FINDINGS'}"
        f"; {'PASS' if ok else 'FAIL'}")
out = Path(__file__).resolve().parent / "identity" / "identity_check.txt"
out.parent.mkdir(exist_ok=True)
with open(out, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print(line)
sys.exit(0 if ok else 1)
