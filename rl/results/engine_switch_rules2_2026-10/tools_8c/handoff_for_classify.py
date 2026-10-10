#!/usr/bin/env python3
"""Rules switch 2, step 8c: the hand-off adapter (the laptop's spec, Oct 10, item 2).

classify_8c.py reads a hand-off row's `exact_counters` and `offgate_counters` (its lines 173 and 186, and the same names in the cloud's
check hand-off, classify_check_8b/handoff_8b.tsv). sitting2_check.py's `handoff` writes the same two things under the names
`reach2_counters` and `offgate2_counters`, beside `round1_counters` and `superset_counters` and nine more columns. Without a bridge
classify_8c.py stops with a KeyError on the first row. This script is the bridge:

    python3 handoff_for_classify.py --in handoff_8c.tsv --out handoff_for_classify.tsv

Input shapes (the header must be one of them exactly, in any order; there is no other):
  sitting-2   sitting2_check.py's HEADER (23 columns): `reach2_counters` becomes `exact_counters` and `offgate2_counters` becomes
              `offgate_counters`, each in its own place; every other column, `round1_counters` and `superset_counters` included,
              is carried through unchanged, cell for cell.
  classify    the 13 columns of classify_check_8b/handoff_8b.tsv, already what classify_8c.py reads: copied unchanged.
  adapted     the sitting-2 header with the two names changed, i.e. this script's own output: copied unchanged (so running it twice
              is harmless).
Anything else is refused (exit 2, nothing written): an unknown or a missing column, a header mixing the old and new names, a column
twice, a row of another width, a cell that is not the JSON it must be, a pairing or deal that is not a number, a cell that begins with
a double quote (classify_8c.py reads the file with csv, which would strip it). In the sitting-2 and adapted shapes the two counter
cells must be the compact form sitting2_check.py writes: an object whose values are lists of ticks, or objects of such lists (a keyed
counter). The cloud's shape is checked only to be a JSON object (its exact_counters also holds counters of other shapes).
The output is written only after every row is checked; it is never written over an existing file."""
import argparse, json, sys
from pathlib import Path

# sitting2_check.py's HEADER (test_handoff_for_classify.py compares this copy with that file's, when it is beside this folder).
SITTING2 = ("step", "bot", "pairing", "i", "seed", "held_file", "held_blob", "panel_file", "panel_blob", "old_moves", "new_moves",
            "moves_differ", "differing_fields", "old_winner", "new_winner", "old_points", "new_points", "category", "reach2_counters",
            "offgate2_counters", "round1_counters", "superset_counters", "revert_switches")
# classify_check_8b/handoff_8b.tsv's header (the cloud's), the columns classify_8c.py reads.
CLASSIFY = ("step", "bot", "pairing", "i", "seed", "held_file", "held_blob", "panel_file", "panel_blob", "old_moves", "new_moves",
            "exact_counters", "offgate_counters")
RENAME = {"reach2_counters": "exact_counters", "offgate2_counters": "offgate_counters"}
ADAPTED = tuple(RENAME.get(c, c) for c in SITTING2)
CARRIED_JSON = ("round1_counters", "superset_counters")
COUNTER_CELLS = ("exact_counters", "offgate_counters")


class Refuse(Exception):
    """The input is not a hand-off this script knows. Nothing is written."""


def shape_of(header):
    if len(set(header)) != len(header):
        raise Refuse(f"a column twice: {sorted(c for c in set(header) if header.count(c) > 1)}")
    cols = set(header)
    for name, known in (("sitting-2", SITTING2), ("adapted", ADAPTED), ("classify", CLASSIFY)):
        if cols == set(known):
            return name
    known = set(SITTING2) | set(ADAPTED) | set(CLASSIFY)
    why = []
    if cols & set(RENAME) and cols & set(RENAME.values()):
        why.append("it has both the sitting-2 names (reach2_counters, offgate2_counters) and the classifier's (exact_counters, offgate_counters)")
    if cols - known:
        why.append("unknown column " + ", ".join(sorted(cols - known)))
    for name, ref in (("sitting-2", SITTING2), ("classify", CLASSIFY)):
        if not (cols - set(ref)) and set(ref) - cols:
            why.append(f"it is {name}'s without " + ", ".join(sorted(set(ref) - cols)))
    if not why:
        why.append(f"missing {sorted(set(ADAPTED) - cols)} for sitting-2's, {sorted(set(CLASSIFY) - cols)} for the classifier's")
    raise Refuse("the header is none of the three shapes (sitting-2, classify, adapted): " + "; ".join(why))


def tick_list(v):
    return isinstance(v, list) and all(isinstance(t, int) and not isinstance(t, bool) for t in v)


def check_counters(cell, strict, where):
    try:
        v = json.loads(cell)
    except json.JSONDecodeError as e:
        raise Refuse(f"{where}: not JSON ({e}): {cell[:80]!r}")
    if not isinstance(v, dict):
        raise Refuse(f"{where}: not a JSON object: {cell[:80]!r}")
    if strict:
        for name, val in v.items():
            if not (tick_list(val) or (isinstance(val, dict) and all(tick_list(t) for t in val.values()))):
                raise Refuse(f"{where}: {name} is {json.dumps(val)[:60]}, not a list of ticks or an object of such lists")


def convert(src, dst):
    """Read the hand-off at `src`, write the classifier's at `dst`; returns a one-line summary. Raises Refuse."""
    src, dst = Path(src), Path(dst)
    if src.resolve() == dst.resolve():
        raise Refuse("--out is --in")
    if dst.exists():
        raise Refuse(f"{dst} exists: it is not written over")
    try:
        text = src.read_text(encoding="utf-8")
    except OSError as e:
        raise Refuse(f"{src}: {e}")
    lines = [ln for ln in text.split("\n") if ln != ""]
    if not lines:
        raise Refuse(f"{src} is empty")
    header = lines[0].split("\t")
    shape = shape_of(header)
    strict = shape != "classify"
    out_header = [RENAME.get(c, c) for c in header] if shape == "sitting-2" else header
    at = {c: j for j, c in enumerate(header)}
    out = ["\t".join(out_header)]
    for n, ln in enumerate(lines[1:], 2):
        cells = ln.split("\t")
        if len(cells) != len(header):
            raise Refuse(f"line {n}: {len(cells)} cells, the header has {len(header)}")
        if any(c.startswith('"') for c in cells):
            raise Refuse(f"line {n}: a cell begins with a double quote (the classifier's csv reader would strip it)")
        for col in ("pairing", "i"):
            if not cells[at[col]].isdigit():
                raise Refuse(f"line {n}: {col} is {cells[at[col]]!r}, not a number")
        for col in header:
            if col in RENAME or col in COUNTER_CELLS:
                check_counters(cells[at[col]], strict, f"line {n}, {col}")
            elif col in CARRIED_JSON:
                check_counters(cells[at[col]], False, f"line {n}, {col}")
        out.append("\t".join(cells))
    dst.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    done = ("reach2_counters -> exact_counters, offgate2_counters -> offgate_counters; round1_counters, superset_counters and "
            f"{len(header) - 4} other columns carried through" if shape == "sitting-2" else "copied unchanged")
    return f"{shape} shape, {len(lines) - 1} rows -> {dst}: {done}"


def main(argv=None, log=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    a = ap.parse_args(argv)
    try:
        log(convert(a.src, a.dst))
    except Refuse as e:
        log(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
