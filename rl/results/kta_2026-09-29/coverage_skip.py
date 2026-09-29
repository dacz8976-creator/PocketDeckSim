#!/usr/bin/env python3
"""The coverage shortcut: which pairings' mixed rows run (kta REGISTRATION.md, top block item 3).

Dustin, Sept 29, verbatim: "For coverage, skip mixed rows only when every corresponding deal has matching complete move
fingerprints, decks, seeds and seats. Matching winners alone is insufficient."

For each pairing, the candidate's both-sides games and kog3's both-sides games are compared deal by deal, on the deal
key (pairing, i). A pairing is SKIPPED only when both files hold every deal i = 0 .. N-1 of it exactly once and every
corresponding pair of games is equal on ALL of:
    moves                 the complete move fingerprint (every chosen move, in order)
    a, b                  both decks (the names the scan writes)
    a_file, b_file        both decks' files (compared whenever either game carries them; the --pairs runs always do)
    seed                  the seed
    first_seat            the seats (which seat the first-named deck sat in)
Any single deal that differs on any one of these runs the pairing's mixed rows in full. winner_seat is never a
criterion: for a pairing that runs, the report prints how many of its differing deals had equal winners, to show that
equal winners did not make it skip.

  coverage_skip.py --group NAME --base FILE --cand FILE --pairings 0,1,.. --deals N --report OUT.txt --json OUT.json
                   [--base-code kog3] [--cand-code kta3] [--context TEXT]

Prints the pairings whose mixed rows run, comma-separated (empty if none), on stdout. The report (committed beside
the runs) names every pairing it skips and why, and every pairing that runs and why. Exit 0 when the comparison was
made; 2 when an input is not a complete both-sides file of those pairings (the runner stops: no pairing is skipped on
an incomplete comparison).
"""
import argparse, hashlib, json, os, sys

RULE = ("\"For coverage, skip mixed rows only when every corresponding deal has matching complete move fingerprints, "
        "decks, seeds and seats. Matching winners alone is insufficient.\" (Dustin, Sept 29; REGISTRATION.md top block, "
        "item 3)")
REQUIRED = ("moves", "a", "b", "seed", "first_seat")
OPTIONAL = ("a_file", "b_file")          # compared whenever either game of the deal carries it
FIELDS = REQUIRED[:3] + OPTIONAL + REQUIRED[3:]


def fail(msg):
    print(f"coverage_skip: STOP: {msg}", file=sys.stderr)
    sys.exit(2)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(path, pairings, deals, code):
    games, n = {}, 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            n += 1
            key = (g["pairing"], g["i"])
            if key in games:
                fail(f"{path}: deal {key} appears twice")
            if g["pairing"] not in pairings:
                fail(f"{path}: a game of pairing {g['pairing']}, which is not in this group")
            for fld in REQUIRED:
                if fld not in g:
                    fail(f"{path}: deal {key} has no {fld} field")
            if (g.get("bot_a"), g.get("bot_b")) != (code, code):
                fail(f"{path}: deal {key} is {g.get('bot_a')} v {g.get('bot_b')}, not {code} on both sides")
            games[key] = g
    want = {(p, i) for p in pairings for i in range(deals)}
    if set(games) != want:
        miss, extra = len(want - set(games)), len(set(games) - want)
        fail(f"{path}: not a complete both-sides file of these pairings ({miss} deals missing, {extra} extra); "
             f"no pairing is skipped on an incomplete comparison")
    return games, n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", required=True)
    ap.add_argument("--base", required=True, help="kog3's both-sides games")
    ap.add_argument("--cand", required=True, help="the candidate's both-sides games")
    ap.add_argument("--pairings", required=True)
    ap.add_argument("--deals", type=int, required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--base-code", default="kog3")
    ap.add_argument("--cand-code", default="kta3")
    ap.add_argument("--context", default="")
    a = ap.parse_args()
    pairings = [int(x) for x in a.pairings.split(",") if x != ""]
    if not pairings:
        fail("no pairings named")
    base, nb = load(a.base, set(pairings), a.deals, a.base_code)
    cand, nc = load(a.cand, set(pairings), a.deals, a.cand_code)

    lines = [f"COVERAGE SHORTCUT, {a.group}",
             f"Rule: {RULE}",
             "Compared deal by deal, on the deal key (pairing, i): " + ", ".join(FIELDS) +
             " (moves = the complete move fingerprint; a, b, a_file, b_file = both decks; seed; first_seat = the seats).",
             "A pairing is skipped only when every one of its deals is equal on all of them. winner_seat is not a criterion.",
             f"{a.base_code} both sides: {a.base} ({nb} games, sha256 {sha(a.base)})",
             f"{a.cand_code} both sides: {a.cand} ({nc} games, sha256 {sha(a.cand)})",
             f"{len(pairings)} pairings x {a.deals} deals."]
    if a.context:
        lines.append(a.context)
    lines.append("")
    per, run, skipped = {}, [], []
    for p in pairings:
        by_field = {f: 0 for f in FIELDS}
        differing, winners_equal, first = 0, 0, None
        for i in range(a.deals):
            g0, g1 = base[(p, i)], cand[(p, i)]
            bad = [f for f in FIELDS
                   if (f in REQUIRED or f in g0 or f in g1) and g0.get(f, None) != g1.get(f, None)]
            if bad:
                differing += 1
                winners_equal += g0.get("winner_seat") == g1.get("winner_seat")
                for f in bad:
                    by_field[f] += 1
                if first is None:
                    first = {"i": i, "fields": bad}
        g = base[(p, 0)]
        name = f"{g['a']} v {g['b']}"
        compared = ", ".join(f for f in FIELDS if f in REQUIRED or f in g)
        # One line per pairing, "SKIP|RUN <group> <pairing>: <equal> of <deals> deals equal on <fields>...", the format
        # read_kta.py parses (its INPUT CONTRACT, coverage_skip.txt); nothing else in the report starts with SKIP or RUN.
        if differing == 0:
            skipped.append(p)
            why = f"all {a.deals} corresponding deals equal on {compared}"
            lines.append(f"SKIP {a.group} {p}: {a.deals} of {a.deals} deals equal on {compared} ({name}): its mixed rows are skipped")
        else:
            run.append(p)
            fields = ", ".join(f"{f} {n}" for f, n in by_field.items() if n)
            why = (f"{differing} of {a.deals} deals differ ({fields}); first at i = {first['i']} ({', '.join(first['fields'])}); "
                   f"winners equal on {winners_equal} of those {differing} deals, which does not make it skip")
            lines.append(f"RUN {a.group} {p}: {a.deals - differing} of {a.deals} deals equal on {compared} ({name}): its mixed "
                         f"rows run; {why}")
        per[str(p)] = {"cell": name, "skip": differing == 0, "differing_deals": differing, "by_field": by_field,
                       "first_difference": first, "winners_equal_among_differing": winners_equal, "why": why}
    lines += ["", f"Skipped pairings ({len(skipped)}): " + (",".join(map(str, skipped)) or "none"),
              f"Pairings whose mixed rows run ({len(run)}): " + (",".join(map(str, run)) or "none")]
    for path, text in ((a.report, "\n".join(lines) + "\n"),
                       (a.json, json.dumps({"group": a.group, "rule": RULE, "fields": list(FIELDS), "deals": a.deals,
                                            "base": {"code": a.base_code, "file": os.path.basename(a.base), "sha256": sha(a.base)},
                                            "cand": {"code": a.cand_code, "file": os.path.basename(a.cand), "sha256": sha(a.cand)},
                                            "context": a.context, "pairings": per, "skipped": skipped, "run": run},
                                           indent=1) + "\n")):
        with open(path + ".part", "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(path + ".part", path)
    print(",".join(map(str, run)))


if __name__ == "__main__":
    main()
