"""The development run's kx3 Tool placements without effect, decided again (Oct 6; trainer_habits scripted --redecide):
kx3 as the development run played it (`_tools` off, which must give the logged placement) and with `_tools` (the play-out
rule and the tie-break). Run from the repository root:
  python3 rl/results/playout_tool_rule_2026-10-06/tie_break/redecide.py [redecide.jsonl]"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "redecide.jsonl"
rs = [json.loads(l) for l in open(path, encoding="utf-8")]


def kind(r):
    on = r["on"]["reason"]
    if on.startswith("tie-break: Tool effect"):
        return "the tie-break placed it where it has an effect"
    if "km's move kept" in on and "its play-outs lead the placement with one" in on:
        return "stays: km3's placement leads the one with an effect beyond the noise"
    if on.startswith("play-outs:"):
        return "a play-out lead beyond the noise picked " + ("a placement with an effect" if r["on_lands_right"] else "a placement without one")
    if not r["rule_would_move"]:
        return "no placement has an effect: no tie-break"
    return "other: " + on[:60]


print(f"{path.name}: {len(rs)} placements without effect re-decided; in games replayed exactly: {sum(r['replayed_exactly'] for r in rs)}")
print(f"kx3 as in the development run (_tools off) gives the logged placement: {sum(r['off_equals_logged'] for r in rs)} of {len(rs)}")
for movable in (True, False):
    sub = [r for r in rs if r["rule_would_move"] == movable]
    print(f"\n{'another placement has an effect (the rule would move it)' if movable else 'no placement has an effect'}: {len(sub)}")
    print(f"  with _tools, it now lands where it has an effect: {sum(r['on_lands_right'] for r in sub)}")
    print(f"  with _tools, the placement changes: {sum(r['on']['chosen'] != r['off']['chosen'] for r in sub)}")
    for k, n in Counter(kind(r) for r in sub).most_common():
        print(f"    {n:3d}  {k}")
    by_tool = Counter((r["tool"], r["on_lands_right"]) for r in sub)
    print("  by Tool (lands right / all): " + ", ".join(f"{t} {by_tool[(t, True)]}/{by_tool[(t, True)] + by_tool[(t, False)]}" for t in sorted({r['tool'] for r in sub})))
stay = [r for r in rs if r["rule_would_move"] and not r["on_lands_right"]]
if stay:
    print("\nthe ones that stay without effect:")
    for r in stay:
        print(f"  {r['key']} decision {r['decision']}, turn {r['turn']}: {r['tool']} on spot {r['on']['chosen']} (board {r['board']}); {r['on']['reason'][:200]}")
