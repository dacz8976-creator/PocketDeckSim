"""P2 (Oct 8): the return-damage counters in real games (run_smoke_p2.sh). games_p_plain.jsonl, games_p2_plain.jsonl and
games_p2_watch.jsonl hold the same deals (pairs.tsv, 50 a pairing, km3 on both sides) played by the scan built on the engine
before P2, on P2, and on P2 with both watch scripts. It prints whether the counters change any move (P2 plain v P2 watch), which
games P2 changes (P v P2, by moves and by result), and, per pairing, where P2's two counters fired (games, ticks), with the
games where the exact counter fired set beside the games P2 changed.
Usage: python3 compare.py   (writes compare_output.txt here)"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
load = lambda v: {(r["pairing"], r["i"]): r for r in map(json.loads, open(HERE / f"games_{v}.jsonl", encoding="utf-8"))}
old, new, watch = load("p_plain"), load("p2_plain"), load("p2_watch")
pairs = {int(l.split("\t")[0]): l.split("\t") for l in (HERE / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:]}

out = []
same = sum(new[k]["moves"] == watch[k]["moves"] for k in new)
out.append(f"P2 plain v P2 watch (the counters change no play): same moves in {same} of {len(new)} games"
           + ("" if set(new) == set(watch) else "; THE GAME SETS DIFFER"))
moved = {k for k in old if old[k]["moves"] != new[k]["moves"]}
result = {k for k in old if (old[k]["winner_seat"], old[k]["points"]) != (new[k]["winner_seat"], new[k]["points"])}
out.append(f"P v P2: {len(moved)} of {len(old)} games play differently, {len(result)} end differently (winner or points)"
           + ("" if set(old) == set(new) else "; THE GAME SETS DIFFER"))
for p, row in sorted(pairs.items()):
    keys = sorted(k for k in watch if k[0] == p)
    exact = {k for k in keys if watch[k]["attack_return_weakness"]["n"]}
    ticks = sum(watch[k]["attack_return_weakness"]["n"] for k in keys)
    out.append(f"\npairing {p}, {row[1]} v {row[3]} ({len(keys)} games):")
    out.append(f"  attack_return_weakness: {len(exact)} games, {ticks} ticks")
    by = {}
    for k in keys:
        for key, t in watch[k]["offgate_return_by_source"].items():
            g, n = by.get(key, (0, 0))
            by[key] = (g + 1, n + len(t))
    for key, (g, n) in sorted(by.items()):
        out.append(f"  offgate_return_by_source[{key}]: {g} games, {n} ticks")
    if not by:
        out.append("  offgate_return_by_source: none")
    p_moved = {k for k in moved if k[0] == p}
    p_result = {k for k in result if k[0] == p}
    out.append(f"  P v P2: {len(p_moved)} games play differently, {len(p_result)} end differently")
    out.append(f"  games P2 changed where the exact counter fired: {len(p_moved & exact)} of {len(p_moved)}; "
               f"exact without a change: {len(exact - p_moved)}")
    if p_moved - exact:
        out.append(f"  CHANGED WITHOUT THE EXACT COUNTER: deals {sorted(k[1] for k in p_moved - exact)}")
(HERE / "compare_output.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
