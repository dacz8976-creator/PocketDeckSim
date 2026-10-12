"""P2's off-switch, gate 1 (Oct 9): the per-game results of two `deckgym simulate --results-output` runs, compared game for
game (matched by game seed) on every field but game_id (a random label). Prints the count of equal games and a digest of each
run (sha256 of the sorted per-game JSON without game_id, first 16 hex). Usage: compare_simulate.py <name>=<dir> <name>=<dir>"""
import glob, hashlib, json, sys

runs = {}
for arg in sys.argv[1:]:
    name, d = arg.split("=", 1)
    games = {}
    for f in glob.glob(d + "/*.json"):
        g = json.load(open(f, encoding="utf-8"))
        g.pop("game_id", None)
        games[g["randomness"]["game_seed"]] = json.dumps(g, sort_keys=True)
    runs[name] = games
(a, ga), (b, gb) = runs.items()
diff = sorted(s for s in set(ga) | set(gb) if ga.get(s) != gb.get(s))
digest = lambda g: hashlib.sha256("\n".join(g[s] for s in sorted(g)).encode()).hexdigest()[:16]
print(f"games: {a} {len(ga)}, {b} {len(gb)}; equal game for game (matched by game seed): {len(set(ga) & set(gb)) - len([s for s in diff if s in ga and s in gb])}; different: {len(diff)} {diff[:10]}")
print(f"digest {a}: {digest(ga)}")
print(f"digest {b}: {digest(gb)}")
