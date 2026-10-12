#!/usr/bin/env python3
"""The checks prepare.sh makes (the engine switch carrying kta and km, Sept 30). Each prints what it found and exits 0
when the check passes, 1 when it fails, 2 on a malformed input.
Rules switch 2's copy (rl/results/engine_switch_rules2_2026-10/; ADAPTATION_SPEC.md SC-1, SC-2, Oct 9): the copy of the
Oct 1 switch's switch_check.py with one change, the pairing filters of `same` (--pairings, --exclude-pairings). Its
callers are sitting1.sh (steps 7, 7b, 7c: identity and the complete/rules/pairs-decks checks; 7c's 24 new rows with
--exclude-pairings 7, deck 10 v t-weezing, 1,380 deals) and sitting2.sh (8b, 8: watch v new and Oct 1's reused games;
9: B2e with --exclude-pairings 32-39,80-87, 40,000 deals, and the 16 named pairings' watch v plain with --pairings,
8,000; 10: cli, screen). Without the two options every check reads as on Oct 1.

  same NEW --ref REF [--ref REF ...] --expect N [--max-i K] [--pairings P] [--exclude-pairings P] --label L
      identity. For each REF (its games with i < K when --max-i is given): exactly N games, one per (pairing, i), each
      carrying the core fields (CORE). NEW holds exactly those N deals, once each, and no other. Every NEW game equals its
      REF game on every field the reference records: the union of REF's keys, so a field one game records and the other
      lacks (an optional counter such as "abilities") is a difference too. One line per REF; exit 1 if any REF fails.
      --pairings keeps only those pairings, --exclude-pairings leaves those out (P: a comma list, ranges allowed, e.g.
      32-39,80-87); both filter NEW and every REF before anything is counted, so N (--expect) counts the deals left.
  complete FILE --pairings P --games N --seed-base B --bot-a X --bot-b Y (--pairs PAIRS.tsv | --decks)
      FILE is exactly the deals (pairing in P, i < N), once each, and every game is the one that command plays: seed
      B + 10,000 x pairing + i, first_seat i % 2, bot_a X, bot_b Y, and the decks of the pairs file's row (a = held_key,
      b = opponent, a_file = held_file, b_file = panel_file) or, for --decks, legality_scan's NAMES pair (no files).
  rules PAGE
      a legality_scan page ends with its Findings section and lists no RULE finding.
  cli OUT --code C --num N
      a deckgym simulate output: prints the Sept 28 line ("cli C,C: " + every line holding "Player 0 won", "Player 1 won"
      or "Draws", joined by spaces, trailing space), and exits 1 unless it holds each of the three once, their counts
      add up to N, and nothing panicked.
  screen NEW REF
      run_screen.py's output equals REF line for line, the "engine <path>" of each "== " header aside (the program path
      differs by design; the numbers may not).
  pairs-decks PAIRS.tsv [PAIRS.tsv ...]
      the deck files the pairs files name (held_file, panel_file), one per line, sorted, relative to the repository.
"""
import argparse, json, re, sys

CORE = ("pairing", "i", "a", "b", "seed", "first_seat", "bot_a", "bot_b", "moves", "decisions", "openings",
        "winner_seat", "points")
NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]  # legality_scan's
TABLE28 = [(x, y) for k, x in enumerate(NAMES) for y in NAMES[k + 1:]]   # --decks: pairing p is the p-th (a, b), a < b
MISSING = object()


def short(path):
    return path.split("/rl/results/", 1)[1] if "/rl/results/" in path else path


def pairing_set(spec):
    """'32-39,80,81' -> {32, ..., 39, 80, 81} (None for no filter)."""
    if spec is None:
        return None
    out = set()
    for part in (x.strip() for x in spec.split(",")):
        if not part:
            continue
        m = re.fullmatch(r"(\d+)-(\d+)", part)
        if m and int(m.group(1)) <= int(m.group(2)):
            out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.add(int(part))
        else:
            raise ValueError(f"pairings {spec!r}: {part!r} is not a pairing or a range")
    if not out:
        raise ValueError(f"pairings {spec!r}: none")
    return out


def read_games(path, max_i=None, keep=None, drop=None):
    """{(pairing, i): game} and the deals seen twice (only pairings in keep, none in drop, when given)."""
    out, dup = {}, []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            if max_i is not None and g["i"] >= max_i:
                continue
            if keep is not None and g["pairing"] not in keep:
                continue
            if drop is not None and g["pairing"] in drop:
                continue
            k = (g["pairing"], g["i"])
            if k in out:
                dup.append(k)
            out[k] = g
    return out, dup


def tsv(path):
    """A --pairs file's rows as dicts (read as legality_scan reads it: BOM dropped, fields trimmed)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip()]
    header = [h.strip() for h in lines[0].split("\t")]
    return [dict(zip(header, (x.strip() for x in ln.split("\t")))) for ln in lines[1:]]


def same(a):
    keep, drop = pairing_set(a.pairings), pairing_set(a.exclude_pairings)
    flt = ((f"; pairings {a.pairings} only" if keep is not None else "")
           + (f"; pairings {a.exclude_pairings} left out" if drop is not None else ""))
    new, new_dup = read_games(a.new, keep=keep, drop=drop)
    ok_all = True
    for ref_path in a.ref:
        ref, ref_dup = read_games(ref_path, a.max_i, keep, drop)
        issues = []
        lacking = [f for f in CORE if not all(f in g for g in ref.values())]
        if lacking:
            issues.append(f"the reference lacks {', '.join(lacking)} in some games: not an identity reference")
        if ref_dup:
            issues.append(f"the reference holds {len(ref_dup)} deals twice (first {ref_dup[0]})")
        if len(ref) != a.expect:
            issues.append(f"the reference holds {len(ref)} deals, expected {a.expect}")
        if new_dup:
            issues.append(f"the new file holds {len(new_dup)} deals twice (first {new_dup[0]})")
        fields = sorted(set().union(*(g.keys() for g in ref.values()))) if ref else []
        missing = sorted(k for k in ref if k not in new)
        extra = sorted(k for k in new if k not in ref)
        bad = []
        for k in sorted(ref):
            if k in new:
                d = [f for f in fields if new[k].get(f, MISSING) != ref[k].get(f, MISSING)]
                if d:
                    bad.append((k, d))
        if missing:
            issues.append(f"{len(missing)} reference deals missing from the new file (first {missing[0]})")
        if extra:
            issues.append(f"{len(extra)} new deals not in the reference (first {extra[0]})")
        if len(new) != a.expect:
            issues.append(f"the new file holds {len(new)} deals, expected {a.expect}")
        if bad:
            issues.append(f"{len(bad)} deals differ; first: "
                          + "; ".join(f"{k} on {', '.join(d)}" for k, d in bad[:3]))
        eq = len(ref) - len(missing) - len(bad)
        new_only = sorted(set().union(*(g.keys() for g in new.values())) - set(fields)) if new else []
        ok = not issues
        ok_all &= ok
        print(f"{a.label}: v {short(ref_path)} {eq} of {len(ref)} equal on every field the reference records "
              f"({len(fields)} fields: {', '.join(fields)}){flt}"
              + (f"; the new file also records {', '.join(new_only)}" if new_only else "")
              + ("" if ok else "; DIFFERS: " + "; ".join(issues)))
    return ok_all


def complete(a):
    want = {(p, i) for p in (int(x) for x in a.pairings.split(",") if x != "") for i in range(a.games)}
    if a.pairs:
        decks = {int(r["pairing"]): {"a": r["held_key"], "b": r["opponent"], "a_file": r["held_file"],
                                     "b_file": r["panel_file"]} for r in tsv(a.pairs)}
    else:
        decks = {p: {"a": x, "b": y, "a_file": None, "b_file": None} for p, (x, y) in enumerate(TABLE28)}
    got, n, bad = set(), 0, []
    with open(a.file, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            n += 1
            got.add((g["pairing"], g["i"]))
            exp = {"seed": a.seed_base + 10_000 * g["pairing"] + g["i"], "first_seat": g["i"] % 2, "bot_a": a.bot_a,
                   "bot_b": a.bot_b, **decks.get(g["pairing"], {"a": None, "b": None})}
            diff = [k for k, v in exp.items() if g.get(k) != v]
            if diff:
                bad.append(((g["pairing"], g["i"]), diff))
    ok = n == len(want) and got == want and not bad
    print(f"{short(a.file)}: {n} games; {'complete' if ok else 'NOT the expected'} set of {len(want)} deals "
          f"(seeds {a.seed_base:,} + pairing x 10,000 + i, first_seat i % 2, {a.bot_a} v {a.bot_b}, decks from "
          f"{short(a.pairs) if a.pairs else 'legality_scan NAMES (--decks)'})"
          + ("" if not bad else f"; {len(bad)} games are not the expected game, the first {bad[0][0]} on {', '.join(bad[0][1])}")
          + ("" if got <= want else f"; {len(got - want)} deals outside the set")
          + ("" if want <= got else f"; {len(want - got)} deals missing"))
    return ok


def rules(a):
    text = open(a.page, encoding="utf-8").read()
    if "\nFindings (occurrences / games affected):" not in text:
        print(f"{short(a.page)}: no Findings section (an incomplete page)")
        return False
    tail = text.split("\nFindings (occurrences / games affected):", 1)[1]
    found = [ln.strip() for ln in tail.splitlines() if ln.strip().startswith("RULE")]
    print(f"{short(a.page)}: " + ("no RULE finding" if not found else f"RULE findings: {'; '.join(found)}"))
    return not found


def cli(a):
    text = open(a.out, encoding="utf-8", errors="replace").read()
    lines = [ln for ln in text.split("\n") if re.search(r"Player 0 won|Player 1 won|Draws", ln)]
    print(f"cli {a.code},{a.code}: " + "".join(ln + " " for ln in lines))
    counts = {}
    for key, pat in (("p0", r"Player 0 won: (\d+)"), ("p1", r"Player 1 won: (\d+)"), ("d", r"Draws: (\d+)")):
        hits = [m for ln in lines for m in re.findall(pat, ln)]
        counts[key] = int(hits[0]) if len(hits) == 1 else None
    problems = []
    if any(v is None for v in counts.values()):
        problems.append("not exactly one each of the Player 0 won / Player 1 won / Draws lines")
    elif sum(counts.values()) != a.num:
        problems.append(f"the counts add up to {sum(counts.values())}, not {a.num}")
    if "panicked" in text or "RUST_BACKTRACE" in text:
        problems.append("the program panicked")
    if problems:
        print(f"cli {a.code}: " + "; ".join(problems), file=sys.stderr)
    return not problems


def screen(a):
    norm = lambda ln: re.sub(r"; engine .*\)$", "; engine <program>)", ln) if ln.startswith("== ") else ln
    new = [norm(ln.rstrip("\n")) for ln in open(a.new, encoding="utf-8")]
    ref = [norm(ln.rstrip("\n")) for ln in open(a.ref, encoding="utf-8")]
    bad = [(k + 1, x, y) for k, (x, y) in enumerate(zip(new, ref)) if x != y]
    eq = sum(x == y for x, y in zip(new, ref))
    heads = sum(ln.startswith("== ") for ln in ref)
    ok = not bad and len(new) == len(ref) and heads > 0
    print(f"run_screen: {short(a.new)} v {short(a.ref)}: {eq} of {len(ref)} lines equal ({heads} decks; "
          f"the header's engine path aside)"
          + ("" if len(new) == len(ref) else f"; {len(new)} lines v {len(ref)}")
          + ("" if not bad else f"; first difference, line {bad[0][0]}: {bad[0][1]!r} v {bad[0][2]!r}"))
    return ok


def pairs_decks(a):
    files = sorted({r[c] for p in a.pairs for r in tsv(p) for c in ("held_file", "panel_file")})
    print("\n".join(files))
    return True


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("same"); s.add_argument("new"); s.add_argument("--ref", action="append", required=True)
    s.add_argument("--expect", type=int, required=True); s.add_argument("--max-i", type=int); s.add_argument("--label", required=True)
    s.add_argument("--pairings"); s.add_argument("--exclude-pairings")   # rules switch 2 (SC-1): filters on NEW and every REF
    c = sub.add_parser("complete"); c.add_argument("file"); c.add_argument("--pairings", required=True)
    c.add_argument("--games", type=int, required=True); c.add_argument("--seed-base", type=int, required=True)
    c.add_argument("--bot-a", required=True); c.add_argument("--bot-b", required=True)
    g = c.add_mutually_exclusive_group(required=True); g.add_argument("--pairs"); g.add_argument("--decks", action="store_true")
    r = sub.add_parser("rules"); r.add_argument("page")
    k = sub.add_parser("cli"); k.add_argument("out"); k.add_argument("--code", required=True); k.add_argument("--num", type=int, required=True)
    q = sub.add_parser("screen"); q.add_argument("new"); q.add_argument("ref")
    p = sub.add_parser("pairs-decks"); p.add_argument("pairs", nargs="+")
    a = ap.parse_args()
    fn = {"same": same, "complete": complete, "rules": rules, "cli": cli, "screen": screen, "pairs-decks": pairs_decks}[a.cmd]
    try:
        ok = fn(a)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"{a.cmd}: malformed or missing input: {e!r}")
        sys.exit(2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
