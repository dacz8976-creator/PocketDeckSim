"""Identity at km's build B, km on kta (the km registration, section 4.1, as Amendment 1 (c) item 4 re-bases it; items
1 to 3, 5 and 6): a run against its reference, game by game, on moves, choices, openings, winner, points, seed and seats
(and the deck files where the reference has them), over the deals both hold (i < deals) and, with --pairings, only those
pairings; and the run's scan page clean of rule findings. With --clean-only (item 7, km3's smoke) there is no
reference: the page must be clean and the run complete, and nothing else is looked at. Appends one line to
identity/identity_check.txt; exits 1 on any difference.
Usage: python3 identity.py <label> <run.jsonl> <reference.jsonl | --clean-only> <deals> [--pairings 0,2,...]"""
import json, re, sys
from pathlib import Path

label, run, ref, deals = sys.argv[1], Path(sys.argv[2]), sys.argv[3], int(sys.argv[4])
only = set(int(p) for p in sys.argv[sys.argv.index("--pairings") + 1].split(",")) if "--pairings" in sys.argv else None
FIELDS = ("moves", "decisions", "openings", "winner_seat", "points", "seed", "first_seat", "a_file", "b_file")


def load(path):
    games = {}
    for line in open(path, encoding="utf-8"):
        g = json.loads(line)
        if g["i"] < deals and (only is None or g["pairing"] in only):
            games[(g["a"], g["b"], g["pairing"], g["i"])] = g
    return games


mine = load(run)
page = run.with_suffix(".txt").read_text(encoding="utf-8")
clean = re.search(r"Findings \(occurrences / games affected\):\s*\n\s*none", page) is not None
if ref == "--clean-only":
    cells = {(a, b, p) for a, b, p, _ in mine}
    complete = all(len([k for k in mine if k[:3] == c]) == deals for c in cells) and (only is None or {c[2] for c in cells} == only)
    ok = clean and complete and len(mine) > 0
    line = (f"{label}: {len(mine)} games in {len(cells)} cells, {'complete' if complete else 'INCOMPLETE'}; "
            f"{'clean' if clean else 'RULE FINDINGS'}; {'PASS' if ok else 'FAIL'} (no reference: results not read)")
else:
    theirs = load(Path(ref))
    fields = [f for f in FIELDS if all(f in g for g in theirs.values())]
    missing = [k for k in theirs if k not in mine]
    bad = [k for k in theirs if k in mine and any(mine[k].get(f) != theirs[k][f] for f in fields)]
    ok = not missing and not bad and len(mine) == len(theirs) and len(theirs) > 0 and clean
    line = (f"{label}: {len(theirs) - len(missing) - len(bad)} of {len(theirs)} games equal on {', '.join(fields)}"
            f" (run has {len(mine)}; missing {len(missing)}, differing {len(bad)}); {'clean' if clean else 'RULE FINDINGS'}"
            f"; {'PASS' if ok else 'FAIL'}")
out = Path(__file__).resolve().parent / "identity" / "identity_check.txt"
out.parent.mkdir(exist_ok=True)
with open(out, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print(line)
sys.exit(0 if ok else 1)
