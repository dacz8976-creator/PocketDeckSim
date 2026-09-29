#!/usr/bin/env python3
"""The checks run_kta.sh makes on its own files (kta REGISTRATION.md sections 3 to 5.1). Each prints what it found and
exits 0 when the check passes, 1 when it fails (2 for a malformed input).

  complete FILE --pairings 0,1,.. --games N --seed-base B --bot-a X --bot-b Y (--pairs PAIRS.tsv | --decks)
                                               FILE holds exactly the deals (pairing, i < N) of those pairings, once each,
                                               and every game is the one that run plays: seed = B + pairing x 10,000 + i,
                                               first_seat = i % 2 (legality_scan's seat rule), bot_a X and bot_b Y, and its
                                               decks those of the pairs file's row (a = held_key, b = opponent, a_file =
                                               held_file, b_file = panel_file) or, for --decks, legality_scan's NAMES pair
                                               (no a_file or b_file). The runner reuses an output only when this holds, and
                                               moves a .part only when it holds.
  same MINE REF --max-i N --expect C --label L identity (section 4, check 2): MINE's games equal REF's games with i < N,
                                               deal for deal, on every field in ID_FIELDS; both hold exactly C such games
  rules PAGE                                   section 4, check 5: the scan page's Findings list no RULE finding
  ab-complete FILE --games N --block B [--opponents K] [--pilot P] [--deck NN] [--opp-dir DIR]
                                               one A/B arm: K opponents x N games (N/2 per seat), each (opp, seat, i) once,
                                               seeds B + 10,000 x deck + 1,000 x opponent index (+500 seat 1) + i; with
                                               --deck, the rows' deck is NN (the file's name); with --opp-dir, the opponents
                                               are the first K lists of DIR/*.txt in sorted order (as kta_ab_play.py picks)
  ab-same MINE REF --label L                   section 4, check 3: every row of MINE equals REF's row for the same
                                               (opp, seat, i), every field
  footprint --base-table F --base-new17 F --cand-table F --cand-new17 F --code C --expect N
                                               section 5.1: the share of the 45 cells' paired games whose moves differ,
                                               the route from the COUNTS (under 15%: 100 d < 15 n), the cells changed
  trace-complete PERGAME MOVES --games N --seed S
                                               a trace arm: trace_pilot.py's per-game rows and kta_trace_moves.py's rows are
                                               the same N games (seeds S .. S+N-1, the same winner per seed)
  census-fp CENSUS TABLE --deals N             section 4, check 6: the counter file's seeds and move fingerprints equal the
                                               fresh table file's, deal for deal, for i < N on the 28 pairings
  inputs --root R --pairs-dir D --build B --decks "07 05 .." --here H --gate G
                                               the input files the games read beside the three pinned programs, one per
                                               line (relative to R when inside it), sorted: every deck file the pairs files
                                               in D name, the pairs files, R's decks/research/*.txt and
                                               decks/screen/opponents/*.txt, B's decks/research/*.txt (--decks runs),
                                               decks/dustin/<NN>-*.txt of each A/B deck, decks/screen/floor.py, trace_pilot.py,
                                               the gate file G and the runner's own scripts in H. run_kta.sh writes their
                                               sha256 at its first start (<out>/ec7e1a8_fresh_inputs.sha256) and checks at
                                               every step that the hashes and this list are unchanged.
"""
import argparse, glob, json, os, sys

ID_FIELDS = ("pairing", "a", "b", "i", "seed", "bot_a", "bot_b", "first_seat", "winner_seat", "points", "turns",
             "first_deck_score", "moves", "decisions", "openings")
NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]  # legality_scan's
TABLE28 = [(x, y) for k, x in enumerate(NAMES) for y in NAMES[k + 1:]]   # --decks: pairing p is the p-th (a, b), a < b


def rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def tsv(path):
    """A --pairs file's rows as dicts (read as legality_scan reads it: BOM dropped, fields trimmed)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip()]
    header = [h.strip() for h in lines[0].split("\t")]
    return [dict(zip(header, (x.strip() for x in ln.split("\t")))) for ln in lines[1:]]


def complete(a):
    want = {(p, i) for p in (int(x) for x in a.pairings.split(",") if x != "") for i in range(a.games)}
    if a.pairs:
        decks = {int(r["pairing"]): {"a": r["held_key"], "b": r["opponent"], "a_file": r["held_file"], "b_file": r["panel_file"]}
                 for r in tsv(a.pairs)}
    else:
        decks = {p: {"a": x, "b": y, "a_file": None, "b_file": None} for p, (x, y) in enumerate(TABLE28)}
    got, n, bad = set(), 0, []
    for g in rows(a.file):
        n += 1
        got.add((g["pairing"], g["i"]))
        exp = {"seed": a.seed_base + 10_000 * g["pairing"] + g["i"], "first_seat": g["i"] % 2, "bot_a": a.bot_a,
               "bot_b": a.bot_b, **decks.get(g["pairing"], {"a": None, "b": None})}
        diff = [f for f, v in exp.items() if g.get(f) != v]
        if diff:
            bad.append(((g["pairing"], g["i"]), diff))
    ok = n == len(want) and got == want and not bad
    print(f"{a.file}: {n} games; {'complete' if ok else 'NOT the expected'} set of {len(want)} deals "
          f"(seeds {a.seed_base:,} + pairing x 10,000 + i, first_seat i % 2, {a.bot_a} v {a.bot_b}, decks from "
          f"{a.pairs or 'legality_scan NAMES (--decks)'})"
          + ("" if not bad else f"; {len(bad)} games are not the expected game, the first {bad[0][0]} on {', '.join(bad[0][1])}"))
    return ok


def same(a):
    ref = {(g["pairing"], g["i"]): g for g in rows(a.ref) if g["i"] < a.max_i}
    mine = {}
    for g in rows(a.mine):
        k = (g["pairing"], g["i"])
        if k in mine:
            print(f"{a.label}: deal {k} twice in {a.mine}")
            return False
        mine[k] = g
    missing = [f for f in ID_FIELDS if not all(f in g for g in ref.values())]
    if missing:
        print(f"{a.label}: the reference lacks {missing}; not an identity")
        return False
    bad = [k for k in ref if k not in mine or any(mine[k].get(f) != ref[k][f] for f in ID_FIELDS)]
    extra = [k for k in mine if k not in ref]
    ok = not bad and not extra and len(ref) == a.expect
    print(f"{a.label}: {len(ref) - len(bad)} of {len(ref)} equal on {', '.join(ID_FIELDS)}"
          f"{'' if not extra else f'; {len(extra)} games not in the reference'}"
          f"{'' if len(ref) == a.expect else f'; expected {a.expect} reference games'}"
          f"{'' if not bad else f'; first differing deal {sorted(bad)[0]}'}")
    return ok


def rules(a):
    text = open(a.page, encoding="utf-8").read()
    if "\nFindings (occurrences / games affected):" not in text:
        print(f"{a.page}: no Findings section (an incomplete page)")
        return False
    tail = text.split("\nFindings (occurrences / games affected):", 1)[1]
    found = [ln.strip() for ln in tail.splitlines() if ln.strip().startswith("RULE")]
    print(f"{a.page}: " + ("no RULE finding" if not found else f"RULE findings: {'; '.join(found)}"))
    return not found


def ab_rows(path):
    out = {}
    for g in rows(path):
        k = (g["opp"], g["seat"], g["i"])
        if k in out:
            raise SystemExit(f"{path}: {k} twice")
        out[k] = g
    return out


def ab_complete(a):
    got = ab_rows(a.file)
    opps = sorted({k[0] for k in got})
    h = a.games // 2
    want = {(o, s, i) for o in opps for s, n in ((0, h), (1, a.games - h)) for i in range(n)}
    deck = {g["deck"] for g in got.values()}
    ok = len(opps) == a.opponents and set(got) == want and len(deck) == 1
    why = ""
    if ok:
        d = deck.pop()
        bad = [k for k, g in got.items()
               if g["seed"] != a.block + 10_000 * d + 1_000 * opps.index(k[0]) + 500 * k[1] + k[2]]
        pil = {g.get("pilot") for g in got.values()}
        ok = not bad and (a.pilot is None or pil == {a.pilot}) and {g.get("opp_pilot") for g in got.values()} == {"kog3"}
        if a.deck is not None and d != int(a.deck):
            ok, why = False, f"; deck {d}, not {a.deck}"
        if a.opp_dir is not None:
            names = [os.path.splitext(os.path.basename(p))[0] for p in sorted(glob.glob(os.path.join(a.opp_dir, "*.txt")))]
            if opps != names[:a.opponents]:
                ok, why = False, why + f"; opponents {opps}, not the first {a.opponents} of {a.opp_dir}"
    print(f"{a.file}: {len(got)} games, {len(opps)} opponents; {'complete' if ok else 'NOT a complete arm'} "
          f"({a.opponents} x {a.games}, seeds from {a.block:,}){why}")
    return ok


def ab_same(a):
    mine, ref = ab_rows(a.mine), ab_rows(a.ref)
    bad = [k for k in mine if k not in ref or mine[k] != ref[k]]
    print(f"{a.label}: {len(mine) - len(bad)} of {len(mine)} equal on every field of the reference's row for the same "
          f"(opp, seat, i)" + ("" if not bad else f"; first differing {sorted(bad)[0]}"))
    return not bad and len(mine) > 0


def footprint(a):
    def load(p):
        return {(g["a"], g["b"], g["i"]): g for g in rows(p)}
    b1, b2, c1, c2 = (load(p) for p in (a.base_table, a.base_new17, a.cand_table, a.cand_new17))
    if set(b1) & set(b2) or set(c1) & set(c2):
        print("STOP: the table and the new cells share a deal key (a, b, i)")
        sys.exit(2)
    base, cand = {**b1, **b2}, {**c1, **c2}
    if base.keys() != cand.keys() or len(base) != a.expect:
        print(f"STOP: {len(base)} and {len(cand)} games, {len(base.keys() ^ cand.keys())} unpaired; expected {a.expect}")
        sys.exit(2)
    unpaired = [k for k in base if any(base[k][f] != cand[k][f] for f in ("seed", "first_seat", "pairing"))]
    if unpaired:
        print(f"STOP: {len(unpaired)} deals with a different seed, seat or pairing, e.g. {unpaired[0]}")
        sys.exit(2)
    diff = [k for k in base if base[k]["moves"] != cand[k]["moves"]]
    d, n = len(diff), len(base)
    route = "reserve route (5.2)" if 100 * d < 15 * n else "ordinary rule (5.3)"
    cells = {}
    for k in base:
        cells.setdefault((k[0], k[1]), [0, 0])[1] += 1
    for k in diff:
        cells[(k[0], k[1])][0] += 1
    changed = sorted(c for c, (x, _) in cells.items() if x)
    print(f"FOOTPRINT {a.code}: {d} of {n} paired games on the 45 cells differ from kog3's = {100 * d / n:.2f}% -> {route}")
    print(f"  (the route is fixed from the counts: under 15% means 100 x {d} < 15 x {n}; the prediction, about 2.5%, "
          f"never picks it)")
    print(f"  cells with a changed game: {len(changed)} of {len(cells)}")
    for c in changed:
        print(f"    {c[0]} v {c[1]}: {cells[c][0]} of {cells[c][1]}")
    print(f"ROUTE {'reserve' if 100 * d < 15 * n else 'ordinary'}")
    return True


def trace_complete(a):
    pg, mv = rows(a.pergame), rows(a.moves)
    want = list(range(a.seed, a.seed + a.games))
    s1, s2 = sorted(g["seed"] for g in pg), sorted(g["seed"] for g in mv)
    w1 = {g["seed"]: g["won"] for g in pg}
    w2 = {g["seed"]: g["won"] for g in mv}
    ok = s1 == want and s2 == want and w1 == w2
    print(f"trace {a.pergame}: {len(pg)} and {len(mv)} games; seeds {a.seed}+{a.games} "
          f"{'complete' if s1 == want and s2 == want else 'NOT complete'}; "
          f"winners {'equal per seed' if w1 == w2 else 'DIFFER'} between trace_pilot.py and kta_trace_moves.py")
    return ok


def census_fp(a):
    table = {(g["pairing"], g["i"]): (g["seed"], g["moves"]) for g in rows(a.table) if g["i"] < a.deals}
    mine = {(g["pairing"], g["i"]): (g["seed"], g["moves"]) for g in rows(a.census)}
    bad = [k for k in table if mine.get(k) != table[k]]
    ok = not bad and len(table) == 28 * a.deals and len(mine) == len(table)
    print(f"{a.census}: {len(table) - len(bad)} of {len(table)} seeds and move fingerprints equal {a.table}'s; "
          f"{len(mine)} games in the counter file")
    return ok


def inputs(a):
    root = os.path.normpath(a.root)
    names = []
    for pf in sorted(glob.glob(os.path.join(a.pairs_dir, "*.tsv"))):
        names.append(pf)
        for r in tsv(pf):
            names += [os.path.join(root, r["held_file"]), os.path.join(root, r["panel_file"])]
    for pat in ("decks/research/*.txt", "decks/screen/opponents/*.txt"):
        names += glob.glob(os.path.join(root, pat))
    names += glob.glob(os.path.join(a.build, "decks", "research", "*.txt"))
    for d in a.decks.split():
        names += glob.glob(os.path.join(root, "decks", "dustin", f"{d}-*.txt"))
    names += [os.path.join(root, "decks", "screen", "floor.py"),
              os.path.join(root, "rl", "results", "gauntlet_runs_2026-09-26", "trace_pilot.py"), a.gate]
    for pat in ("run_kta.sh", "run_kta_ab.sh", "kta_*.py", "make_pairs.py", "coverage_skip.py"):
        names += glob.glob(os.path.join(a.here, pat))
    out = set()
    for p in names:
        p = os.path.normpath(os.path.abspath(p))
        out.add(os.path.relpath(p, root) if p.startswith(root + os.sep) else p)
    print("\n".join(sorted(out)))
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("complete"); p.add_argument("file"); p.add_argument("--pairings", required=True)
    p.add_argument("--games", type=int, required=True); p.add_argument("--seed-base", type=int, required=True)
    p.add_argument("--bot-a", required=True); p.add_argument("--bot-b", required=True)
    m = p.add_mutually_exclusive_group(required=True); m.add_argument("--pairs"); m.add_argument("--decks", action="store_true")
    p = sub.add_parser("same"); p.add_argument("mine"); p.add_argument("ref"); p.add_argument("--max-i", type=int, required=True)
    p.add_argument("--expect", type=int, required=True); p.add_argument("--label", required=True)
    p = sub.add_parser("rules"); p.add_argument("page")
    p = sub.add_parser("ab-complete"); p.add_argument("file"); p.add_argument("--games", type=int, required=True)
    p.add_argument("--block", type=int, required=True); p.add_argument("--opponents", type=int, default=8)
    p.add_argument("--pilot", default=None); p.add_argument("--deck", default=None); p.add_argument("--opp-dir", default=None)
    p = sub.add_parser("ab-same"); p.add_argument("mine"); p.add_argument("ref"); p.add_argument("--label", required=True)
    p = sub.add_parser("footprint")
    for x in ("--base-table", "--base-new17", "--cand-table", "--cand-new17", "--code"):
        p.add_argument(x, required=True)
    p.add_argument("--expect", type=int, required=True)
    p = sub.add_parser("trace-complete"); p.add_argument("pergame"); p.add_argument("moves")
    p.add_argument("--games", type=int, required=True); p.add_argument("--seed", type=int, required=True)
    p = sub.add_parser("census-fp"); p.add_argument("census"); p.add_argument("table"); p.add_argument("--deals", type=int, required=True)
    p = sub.add_parser("inputs")
    for x in ("--root", "--pairs-dir", "--build", "--decks", "--here", "--gate"):
        p.add_argument(x, required=True)
    a = ap.parse_args()
    fn = {"complete": complete, "same": same, "rules": rules, "ab-complete": ab_complete, "ab-same": ab_same,
          "footprint": footprint, "trace-complete": trace_complete, "census-fp": census_fp, "inputs": inputs}[a.cmd]
    sys.exit(0 if fn(a) else 1)


if __name__ == "__main__":
    main()
