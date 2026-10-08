"""P2 smoke (Oct 8): where each game P2 changed first differs. trace_P.txt and trace_P2.txt are the TRACE lines (trace_patch.py)
of the same deals on the scan built from the engine before P2 and from P2 (each reproduces its smoke games' moves). For each deal
it prints the first tick whose line differs. If the chosen move differs there, the board before it is the same on both engines
(every earlier line is equal), so no P2 hit back has landed yet: the bots' search saw the +20 ahead ("in look-ahead"). If the
move is the same and a board after it differs, P2's damage landed at that tick, and the exact counter must fire there.
Usage: python3 first_difference.py   (writes first_difference_output.txt here)"""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    out = {}
    for line in (HERE / name).read_text(encoding="utf-8").splitlines():
        if line.startswith("TRACE "):
            out.setdefault(line.split()[1], []).append(line)
    return out


p, p2 = load("trace_P.txt"), load("trace_P2.txt")
out = []
for key in sorted(p):
    a, b = p[key], p2[key]
    k = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), None)
    out.append(f"deal {key}: {len(a)} ticks before P2, {len(b)} on P2; first difference at tick {k}")
    if k is None:
        continue
    ha, hb = a[k].split(" || ")[0], b[k].split(" || ")[0]
    if ha != hb:
        out.append("  a different move from the same board (in look-ahead):")
        out.append(f"    before P2: {ha}")
        out.append(f"    P2:        {hb}")
        before = a[k - 1].split(" || ")
        out.append(f"    the board both chose from: side 0: {before[1]}")
        out.append(f"                               side 1: {before[2]}")
    else:
        out.append(f"  the same move, a different board after it (P2's damage landed): {ha}")
        out.append(f"    before P2: {a[k].split(' || ')[1:]}")
        out.append(f"    P2:        {b[k].split(' || ')[1:]}")
(HERE / "first_difference_output.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
