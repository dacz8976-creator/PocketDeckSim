#!/usr/bin/env python3
"""Does an engine built from the merged main replay the table's reference games move for move? Groundwork for the
question in RUN5's A2 line (whether a new build becomes the project's verified engine): nothing is switched here.

    python compare.py <new per-game jsonl> <reference jsonl> [<reference jsonl> ...]

Both sides are legality_scan --games-out files (one line per game: pairing, i, a, b, seed, moves (a hash of every
move), winner_seat, points, turns, first_deck_score). A game matches when every one of those fields is equal. Prints
the count, and the first mismatches if any.
"""
import json
import sys

FIELDS = ("a", "b", "seed", "first_seat", "moves", "winner_seat", "points", "turns", "first_deck_score")


def load(paths):
    out = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                out[(r["pairing"], r["i"])] = r
    return out


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    new, ref = load([sys.argv[1]]), load(sys.argv[2:])
    keys = sorted(set(new) | set(ref))
    missing_new = [k for k in keys if k not in new]
    missing_ref = [k for k in keys if k not in ref]
    both = [k for k in keys if k in new and k in ref]
    bad = [k for k in both if any(new[k].get(f) != ref[k].get(f) for f in FIELDS)]
    print(f"new: {sys.argv[1]} ({len(new):,} games); reference: {', '.join(sys.argv[2:])} ({len(ref):,} games)")
    print(f"games in both: {len(both):,}; identical on {', '.join(FIELDS)}: {len(both) - len(bad):,} of {len(both):,}")
    print(f"only in new: {len(missing_ref)}; only in reference: {len(missing_new)}")
    for k in bad[:5]:
        diff = {f: (ref[k].get(f), new[k].get(f)) for f in FIELDS if new[k].get(f) != ref[k].get(f)}
        print(f"  MISMATCH pairing {k[0]} deal {k[1]}: {diff}")
    ok = not bad and not missing_new and not missing_ref and len(both) > 0
    print("RESULT:", "IDENTICAL" if ok else "NOT IDENTICAL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
