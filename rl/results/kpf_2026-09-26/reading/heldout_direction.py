#!/usr/bin/env python3
"""The held-out direction, reported beside every verdict (rl/RUN5.md, "The held-out direction, reported beside every
verdict"; Dustin, Sept 29). It gates nothing.

For B2e's held-out archetypes (pairings 0-47: the six A_archetype decks against the panel of 8) it prints how each one
moved under a candidate: from the base's figure to the candidate's, against its Limitless figure, and the change in miss.
The arithmetic is read_koh.py's 6a and read_kt.py's 5a, unchanged:
  - a deck's figure = the mean over the 8 panel opponents of that pairing's mean first_deck_score x 100 (equal weight);
  - its Limitless figure = the mean over the same opponents of the POOLED Limitless score for (archetype, opponent),
    over the opponents that have a pooled cell with n > 0 (limitless_cells.csv, dataset "pooled");
  - miss = |figure - Limitless|; change in miss = candidate's miss minus base's miss (+ = further, - = closer).

Usage (python3):
  heldout_direction.py BASE_b2e.jsonl CANDIDATE_b2e.jsonl [--b2e-dir DIR] [--dustin]
BASE and CANDIDATE are the two B2e both-sides files (each pilot on both sides, 96 pairings x 500 deals = 48,000 games).
Stops (exit 1, no result printed) unless both files are complete, both-sides, and on the same deals.
--dustin also prints Dustin's files (pairings 48-95) beside, reported only, not in the summary line.
--b2e-dir defaults to ../../b2e_card_check_2026-09-26 (b2e_pairings.tsv and limitless_cells.csv).
As a module: compute(base_path, cand_path, b2e_dir=DEFAULT_B2E) returns (base_pilot, cand_pilot, rows), each row
(block, deck, base_figure, cand_figure, limitless, n_limitless_opponents, change_in_miss), block "A_archetype" or "B_dustin".
Reads two jsonl files and two small tables; runs no game.
"""
import argparse, csv, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_B2E = os.path.abspath(os.path.join(HERE, "..", "..", "b2e_card_check_2026-09-26"))


def die(msg):
    sys.exit("STOP: " + msg)


def load(path):
    """({(pairing, i): (seed, first_deck_score)}, pilot). STOP unless 48,000 distinct games and one pilot on both sides."""
    rows, pilots = {}, set()
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            key = (g["pairing"], g["i"])
            if key in rows:
                die(f"{path}: game {key} appears twice")
            rows[key] = (g["seed"], g["first_deck_score"])
            pilots.add((g["bot_a"], g["bot_b"]))
    if len(rows) != 96 * 500:
        die(f"{path}: {len(rows)} games, expected {96 * 500}: an incomplete or wrong file, nothing read from it")
    if len(pilots) != 1 or len({p for pair in pilots for p in pair}) != 1:
        die(f"{path}: pilots {sorted(pilots)}; a both-sides file has one pilot on both sides (is this a mixed-rows file?)")
    return rows, next(iter(pilots))[0]


def compute(base_path, cand_path, b2e_dir=DEFAULT_B2E):
    tsv = {int(r["pairing"]): r for r in csv.DictReader(
        open(os.path.join(b2e_dir, "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")}
    lim = {}
    for r in csv.DictReader(open(os.path.join(b2e_dir, "limitless_cells.csv"), encoding="utf-8")):
        if r["dataset"] == "pooled" and int(r["n"]):
            lim[(r["archetype"], r["opponent"])] = float(r["score_pct"])
    names = sorted({k for k, _ in lim})

    base, bname = load(base_path)
    cand, cname = load(cand_path)
    if base.keys() != cand.keys():
        die(f"the two files do not hold the same games ({len(base.keys() ^ cand.keys())} in only one)")
    bad = [k for k in base if base[k][0] != cand[k][0]]
    if bad:
        die(f"{len(bad)} games have a different seed in the two files, e.g. {bad[0]}: not the same deals")

    def panel(rows):
        by = defaultdict(list)
        for (p, _i), (_seed, s) in rows.items():
            r = tsv[p]
            by[(r["block"], r["held_key"], r["opponent"])].append(s)
        res = defaultdict(dict)
        for (block, k, o), s in by.items():
            res[(block, k)][o] = 100 * sum(s) / len(s)
        return res

    a, b = panel(base), panel(cand)
    if not all(a[k].keys() == b[k].keys() and len(a[k]) == 8 for k in a):
        die("a held-out deck does not have the panel's 8 opponents in both files")

    rows = []
    for (block, k) in sorted(a):
        x, y = sum(a[(block, k)].values()) / 8, sum(b[(block, k)].values()) / 8
        stem = k.replace("dustin_", "")
        arch = next((n for n in names if n == stem), None) or next((n for n in names if n.startswith(stem)), None)
        if arch is None:
            die(f"no Limitless archetype for held-out deck {k}")
        cells = [o for o in a[(block, k)] if (arch, o) in lim]
        L = sum(lim[(arch, o)] for o in cells) / len(cells)
        rows.append((block, k, x, y, L, len(cells), abs(y - L) - abs(x - L)))
    return bname, cname, rows


def show(bname, cname, rows, title, summary):
    """One block: a line per deck, then the summary line. `rows` are compute()'s rows of one block."""
    if title:
        print(title)
    for _block, k, x, y, L, n, ch in rows:
        note = "" if n == 8 else f" (Limitless figure over {n} of 8 opponents)"
        print(f"   {k:28} {bname} {x:5.1f} -> {cname} {y:5.1f}; Limitless {L:5.1f}; miss {abs(x - L):4.1f} -> {abs(y - L):4.1f}; "
              f"change in miss {ch:+.2f} ({'further' if ch > 0 else 'closer' if ch < 0 else 'unchanged'}){note}")
    closer = sum(1 for r in rows if r[6] < 0)
    further = sum(1 for r in rows if r[6] > 0)
    same = len(rows) - closer - further
    mean = sum(r[6] for r in rows) / len(rows)
    print(f"   {summary}: {closer} closer, {further} further" + (f", {same} unchanged" if same else "")
          + f", mean change in miss {mean:+.2f} (reported, gates nothing)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base")
    ap.add_argument("candidate")
    ap.add_argument("--b2e-dir", default=DEFAULT_B2E)
    ap.add_argument("--dustin", action="store_true", help="also print Dustin's files (pairings 48-95), reported only")
    args = ap.parse_args()
    bname, cname, rows = compute(args.base, args.candidate, args.b2e_dir)
    show(bname, cname, [r for r in rows if r[0].startswith("A")],
         f"Held-out direction, {bname} -> {cname} (B2e pairings 0-47; panel average equal-weight over 8; Limitless pooled; "
         f"change in miss: + = further from Limitless, - = closer):", "held-out direction")
    if args.dustin:
        show(bname, cname, [r for r in rows if r[0].startswith("B")],
             "\nDustin's files (pairings 48-95), reported beside, not in the summary above:", "Dustin's files")


if __name__ == "__main__":
    main()
