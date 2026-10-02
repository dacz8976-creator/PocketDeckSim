"""Sonnet's S3 (Sept 30): the first differing decision in the 4 smoke games the repair changed without a redirected
snipe being chosen (i = 16, 23, 29, 32), from the two engines' tick-by-tick traces (coin_trace.rs):
trace_legacy_d21511a.jsonl.gz (without the repair) and trace_fixed_e52a73b.jsonl.gz (with it, at the Chase Order
engine). For each game it prints the first tick where the offered moves, the chosen move or the board differ, and what
both engines offered and chose there.
Usage: python3 first_diff.py"""
import gzip, json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    """Each game's tick rows, in order, and its closing row (the move fingerprint)."""
    games, done = {}, {}
    for r in map(json.loads, gzip.open(HERE / name, "rt")):
        if r.get("done"):
            done[r["i"]] = r
        else:
            games.setdefault(r["i"], []).append(r)
    return games, done


old, old_done = load("trace_legacy_d21511a.jsonl.gz")
new, new_done = load("trace_fixed_e52a73b.jsonl.gz")
short = lambda a: a.replace('Attack { energy_required: [Fire], title: "Tongue Whip", fixed_damage: 0, effect: Some("This attack does 30 damage to 1 of your opponent\'s Benched Pokémon.") }', "Tongue Whip")
for i in sorted(old):
    a, b = old[i], new[i]
    k = next(t for t in range(min(len(a), len(b)))
             if (a[t]["chosen"], a[t]["offered"], a[t]["board"]) != (b[t]["chosen"], b[t]["offered"], b[t]["board"]))
    x, y = a[k], b[k]
    print(f"i = {i}: first difference at tick {k}, turn {x['turn']}, mover seat {x['actor']}, after {a[k-1]['chosen'][:40]}...")
    print(f"  same board before it: {x['board'] == y['board']}; same number of offered moves: {x['n'] == y['n']}")
    print(f"  board: {x['board']}")
    print(f"  without the repair, offered: {[short(o) for o in x['offered']]}")
    print(f"  with the repair,    offered: {[short(o) for o in y['offered']]}")
    print(f"  without the repair, chose:   {short(x['chosen'])}")
    print(f"  with the repair,    chose:   {short(y['chosen'])}")
print("fingerprints:", {i: (old_done[i]["moves"], new_done[i]["moves"]) for i in sorted(old_done)})
