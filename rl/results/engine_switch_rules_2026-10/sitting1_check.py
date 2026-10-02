#!/usr/bin/env python3
"""The checks sitting1.sh makes beside switch_check.py (the rules switch, PLAN.md steps 7b and 7c). Each prints what it
found and exits 0 when the check passes, 1 when it fails, 2 on a malformed or missing input.

  counters FILE [FILE ...] --label L [--offgate-in P,P,...]
      The watch build's per-game counters (both F5 instrument_scan.py scripts, R = f8cfa9c). Every game must carry
      every counter (else exit 2: not the watch build's output). Every REPAIR counter must read 0 in every game:
        exact ({n, first, ticks}, every firing tick): vs_confusion_first_built, vs_confused_choice_chosen,
                         vs_confused_choice_offered, coin_cut_recorded, coin_full_prevention, coin_queued_offered,
                         coin_queued_offered_any; and vs_confused_choice (+ vs_confused_choice_first), plain
      offgate_helper_by_mechanic ({mechanic: [ticks]}) must be well formed, its union equal to offgate_helper_choice's ticks.
        superset:        vs_confused_attack, coin_defender_attack, coin_queued_attack_damage
      The two OFF-GATE counters may read anything; they are evidence for different rewritten lines, so each gets its own
      verdict, counted over the games of the pairings named by --offgate-in (all games without it):
        offgate_helper_choice (queued_attack_damage_choice's else branch: the queued choices B's rewritten helpers build
          off the gate) must be above 0 in at least one of those games: the proof that they run those lines;
        offgate_discard_then_damage (discard_then_damage_choice's fall-through: Chase Order with the discard, Gyarados's
          Wild Swing; the equivalence readings' rows 13 and 22) must also be above 0 with --require-discard (step 7b:
          the table's vespiquen cells run Chase Order's discard; SECOND_READ_F1_F7_opus.md finding 2); without it
          (step 7c, whose scope has no t-vespiquen pairing) it is reported, and when it reads 0 a line says that
          condition 3 for rows 13 and 22 is not met there and is carried to steps 8 and 8b.
      The counter does not record which side fired it; --offgate-in names pairings where only the side that matters can.
      One line per file, one line per pairing with its off-gate firings, one line per deck (the "a" side) in the
      --offgate-in pairings, the rows 13 and 22 line when it applies, then the verdict line.
  floor NEWDIR REFDIR NAME --label L
      A floor page replayed by floor.py's own call on the new deckgym (floor_with.py) against the recorded page:
      NAME_games.jsonl holds the same games in the same order, each equal on every field of floor.py's per-game summary
      record (the union of both records' keys: seed, seat, result, points, turns and the like; a summary, not the moves
      or decisions), keyed (opponent, seat, seed) once each; NAME_coverage.json is byte-equal; NAME.md is equal line for
      line, the program path in its "- Engine:" line aside (the replay names the new program by design; nothing else may
      differ).
  pairs7c --repo R --out FILE
      Writes step 7c's pairs file: Dustin's decks 02, 06, 08 and 14 (in that order) against the 8 lists in
      decks/screen/opponents/ (sorted), pairings 40-71 of the rules switch's block (seed = 23,100,000,000 + pairing x
      10,000 + i, i < 60). Step 8 uses pairings 0-31 and step 8b 32-35 of the same block, so 40-71 collide with neither.
"""
import argparse, glob, json, os, re, sys

EXACT_DICT = ("vs_confusion_first_built", "coin_cut_recorded", "coin_full_prevention", "coin_queued_offered",
              # added at f8cfa9c (the second read's finding 4): every firing tick is kept; all must read 0 on the table
              "coin_queued_offered_any", "vs_confused_choice_chosen", "vs_confused_choice_offered")
BY_MECHANIC = "offgate_helper_by_mechanic"   # {mechanic: [ticks]}; its union must equal offgate_helper_choice's ticks
SUPERSET_INT = ("vs_confused_attack", "coin_defender_attack", "coin_queued_attack_damage")
HEADS_INT = "vs_confused_choice"
HEADS_FIRST = "vs_confused_choice_first"
OFFGATE_HELPER, OFFGATE_DISCARD = "offgate_helper_choice", "offgate_discard_then_damage"
OFFGATE = (OFFGATE_HELPER, OFFGATE_DISCARD)
REPAIR = EXACT_DICT + (HEADS_INT,) + SUPERSET_INT
CARRIED = ("condition 3 of the refactor rule for rows 13 and 22 (discard_then_damage_choice's fall-through: Chase Order "
           "with the discard, Gyarados's Wild Swing) is not met here; it is carried to steps 8 and 8b (8b's l-sharpedo v "
           "meowth_carefree, the Wild Swing control, and t-vespiquen v meowth_carefree)")

DECKS_7C = ("decks/dustin/02-arceus-crobat.txt", "decks/dustin/06-mega-blaziken-tournament-list.txt",
            "decks/dustin/08-garchomp-toolbox.txt", "decks/dustin/14-comfey-raticate-hypno.txt")
BASE_7C, FIRST_7C, DEALS_7C = 23_100_000_000, 40, 60


def short(path):
    return path.split("/rl/results/", 1)[1] if "/rl/results/" in path else path


def pairings(spec):
    out = set()
    for part in (x for x in spec.split(",") if x.strip()):
        if "-" in part:
            lo, hi = part.split("-", 1)
            out |= set(range(int(lo), int(hi) + 1))
        else:
            out.add(int(part))
    return out


class Malformed(Exception):
    pass


def as_exact(g, name):
    """An exact counter at R = f8cfa9c: {n, first, ticks}, every firing tick kept (n == len(ticks), first == ticks[0] or
    null, ticks strictly ascending ints)."""
    v = g.get(name)
    where = f"game {(g.get('pairing'), g.get('i'))}: {name}"
    if not (isinstance(v, dict) and set(v) == {"n", "first", "ticks"} and isinstance(v["n"], int)
            and (v["first"] is None or isinstance(v["first"], int)) and isinstance(v["ticks"], list)):
        raise Malformed(f"{where} is {v!r}, not {{n, first, ticks}}")
    t = v["ticks"]
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in t) or any(a >= b for a, b in zip(t, t[1:])):
        raise Malformed(f"{where} {v!r}: ticks are not strictly ascending ints")
    if v["n"] != len(t) or v["first"] != (t[0] if t else None):
        raise Malformed(f"{where} {v!r}: n, first and ticks disagree")
    return v["n"], v["first"]


def check_by_mechanic(g):
    """offgate_helper_by_mechanic is {mechanic: [ticks]}, and the union of its lists is offgate_helper_choice's ticks."""
    m = g.get(BY_MECHANIC)
    where = f"game {(g.get('pairing'), g.get('i'))}: {BY_MECHANIC}"
    if not isinstance(m, dict) or not all(isinstance(k, str) and isinstance(x, list) for k, x in m.items()):
        raise Malformed(f"{where} is {m!r}, not {{mechanic: [ticks]}}")
    union = sorted({t for x in m.values() for t in x})
    if union != g["offgate_helper_choice"]["ticks"]:
        raise Malformed(f"{where}: its ticks {union} are not offgate_helper_choice's {g['offgate_helper_choice']['ticks']}")


def as_int(g, name):
    v = g.get(name)
    if not isinstance(v, int) or isinstance(v, bool):
        raise Malformed(f"game {(g.get('pairing'), g.get('i'))}: {name} is {v!r}, not a count")
    return v


def counters(a):
    want = pairings(a.offgate_in) if a.offgate_in else None
    all_zero, lines, per_pair, per_deck = True, [], {}, {}
    scope_games, scope_fired = 0, {k: 0 for k in OFFGATE}   # games in scope, and in how many of them each counter fired
    total_games = 0
    for path in a.files:
        n, bad, fired = 0, [], {k: [0, 0, None] for k in OFFGATE}   # games, firings, earliest first tick
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                g = json.loads(ln)
                n += 1
                nonzero = []
                for k in EXACT_DICT:
                    if as_exact(g, k)[0]:
                        nonzero.append(k)
                for k in SUPERSET_INT + (HEADS_INT,):
                    if as_int(g, k):
                        nonzero.append(k)
                if HEADS_FIRST not in g:
                    raise Malformed(f"game {(g.get('pairing'), g.get('i'))}: no {HEADS_FIRST}")
                if g[HEADS_FIRST] is not None:
                    nonzero.append(HEADS_FIRST)
                as_exact(g, OFFGATE_HELPER)
                check_by_mechanic(g)
                if nonzero:
                    bad.append(((g["pairing"], g["i"]), nonzero))
                key = (g["pairing"], g.get("a"), g.get("b"))
                row = per_pair.setdefault(key, {k: [0, 0] for k in OFFGATE} | {"games": 0})
                row["games"] += 1
                in_scope = want is None or g["pairing"] in want
                if in_scope:
                    scope_games += 1
                    deck = per_deck.setdefault(g.get("a"), {k: [0, 0] for k in OFFGATE} | {"games": 0, "pairings": set()})
                    deck["games"] += 1
                    deck["pairings"].add(g["pairing"])
                for k in OFFGATE:
                    c, first = as_exact(g, k)
                    if c:
                        fired[k][0] += 1
                        fired[k][1] += c
                        fired[k][2] = first if fired[k][2] is None else min(fired[k][2], first)
                        row[k][0] += 1
                        row[k][1] += c
                        if in_scope:
                            scope_fired[k] += 1
                            deck[k][0] += 1
                            deck[k][1] += c
        total_games += n
        all_zero &= not bad
        off = "; ".join(f"{k} fired in {v[0]} of {n} games ({v[1]} ticks, earliest at tick {v[2]})" if v[0]
                        else f"{k} fired in 0 of {n} games" for k, v in fired.items())
        lines.append(f"{a.label}: {short(path)}: {n} games; the {len(REPAIR)} repair counters ({', '.join(REPAIR)}; "
                     f"and {HEADS_FIRST} null) "
                     + (f"read 0 in all {n} games" if not bad else
                        f"are NOT all 0: {len(bad)} games, first {bad[0][0]} ({', '.join(bad[0][1])})")
                     + f"; off-gate: {off}")
    for (p, x, y), row in sorted(per_pair.items(), key=lambda kv: kv[0][0]):
        lines.append(f"  pairing {p} {x} v {y}: {row['games']} games; "
                     + "; ".join(f"{k} in {row[k][0]} games ({row[k][1]} ticks)" for k in OFFGATE))
    scope = f"pairings {a.offgate_in}" if want is not None else "these games"
    if want is not None:
        for x, d in sorted(per_deck.items(), key=lambda kv: min(kv[1]["pairings"])):
            lines.append(f"  deck {x} in {scope} (its pairings {','.join(str(p) for p in sorted(d['pairings']))}): "
                         f"{d['games']} games; {OFFGATE_HELPER} "
                         + (f"above 0 in {d[OFFGATE_HELPER][0]} games ({d[OFFGATE_HELPER][1]} ticks)"
                            if d[OFFGATE_HELPER][0] else "0 (this deck's own helper attacks never ran there)")
                         + f"; {OFFGATE_DISCARD} in {d[OFFGATE_DISCARD][0]} games")
    helper_ok, disc_ok = scope_fired[OFFGATE_HELPER] > 0, scope_fired[OFFGATE_DISCARD] > 0
    if not disc_ok and not a.require_discard:
        lines.append(f"{a.label}: {OFFGATE_DISCARD} read 0 in {scope} ({scope_games} games): {CARRIED}")
    # --require-discard (step 7b): the table's vespiquen cells run Chase Order's discard (research/vespiquen.txt holds
    # Vespiquen ex and Basic [G] Bench Pokemon), so the fall-through literal runs there and its counter must fire
    # (SECOND_READ_F1_F7_opus.md finding 2).
    ok = all_zero and helper_ok and (disc_ok or not a.require_discard) and total_games > 0
    lines.append(f"{a.label}: {'PASS' if ok else 'does not pass'}: repair counters 0 in every game: "
                 f"{'yes' if all_zero else 'no'}; {OFFGATE_HELPER} above 0 in {scope}: "
                 + (f"yes, in {scope_fired[OFFGATE_HELPER]} of {scope_games} games" if helper_ok
                    else f"no, in none of {scope_games} games (required)")
                 + f"; {OFFGATE_DISCARD} above 0 in {scope}: "
                 + (f"yes, in {scope_fired[OFFGATE_DISCARD]} of {scope_games} games" if disc_ok
                    else ("no, in none of " + str(scope_games) + " games (required)" if a.require_discard
                          else "no (not required here: rows 13 and 22 are carried to steps 8 and 8b)"))
                 + f" ({total_games} games)")
    print("\n".join(lines))
    return ok


def floor(a):
    name = a.name
    issues = []
    new_g = os.path.join(a.newdir, f"{name}_games.jsonl")
    ref_g = os.path.join(a.refdir, f"{name}_games.jsonl")
    new = [json.loads(ln) for ln in open(new_g, encoding="utf-8") if ln.strip()]
    ref = [json.loads(ln) for ln in open(ref_g, encoding="utf-8") if ln.strip()]
    keyf = lambda g: (g.get("opponent"), g.get("seat"), g.get("seed"))  # noqa: E731
    for label, games in (("recorded", ref), ("replayed", new)):
        keys = [keyf(g) for g in games]
        if len(set(keys)) != len(keys):
            issues.append(f"the {label} page holds a game twice")
    if len(new) != len(ref):
        issues.append(f"{len(new)} replayed games v {len(ref)} recorded")
    fields = sorted(set().union(*(g.keys() for g in ref + new))) if ref or new else []
    bad = [(k, [f for f in fields if new[k].get(f, "<absent>") != ref[k].get(f, "<absent>")])
           for k in range(min(len(new), len(ref)))]
    bad = [(k, d) for k, d in bad if d]
    if bad:
        k, d = bad[0]
        issues.append(f"{len(bad)} games differ; the first, line {k + 1} {keyf(ref[k])}, on {', '.join(d)}")
    eq = min(len(new), len(ref)) - len(bad)
    same_bytes = open(new_g, "rb").read() == open(ref_g, "rb").read()
    cov_new = open(os.path.join(a.newdir, f"{name}_coverage.json"), "rb").read()
    cov_ref = open(os.path.join(a.refdir, f"{name}_coverage.json"), "rb").read()
    if cov_new != cov_ref:
        issues.append("the coverage file differs from the recorded one")
    norm = lambda ln: re.sub(r"^- Engine: \S+ ", "- Engine: <program> ", ln)  # noqa: E731
    md_new = [norm(ln.rstrip("\n")) for ln in open(os.path.join(a.newdir, f"{name}.md"), encoding="utf-8")]
    md_ref = [norm(ln.rstrip("\n")) for ln in open(os.path.join(a.refdir, f"{name}.md"), encoding="utf-8")]
    engine_lines = sum(ln.startswith("- Engine: <program> ") for ln in md_ref)
    if engine_lines != 1:
        issues.append(f"the recorded page has {engine_lines} '- Engine:' lines, not 1")
    md_bad = [(k + 1, x, y) for k, (x, y) in enumerate(zip(md_new, md_ref)) if x != y]
    if md_bad or len(md_new) != len(md_ref):
        issues.append(f"the page differs: {len(md_new)} lines v {len(md_ref)}"
                      + (f", first at line {md_bad[0][0]}: {md_bad[0][1]!r} v {md_bad[0][2]!r}" if md_bad else ""))
    ok = not issues
    print(f"{a.label}: {short(new_g)} v {short(ref_g)}: {eq} of {len(ref)} games equal on every field of the per-game "
          f"summary record ({len(fields)} fields: {', '.join(fields)}; no moves or decisions); the games file {'byte-equal' if same_bytes else 'not byte-equal'}; "
          f"coverage {'byte-equal' if cov_new == cov_ref else 'differs'}; page {len(md_ref)} lines"
          + (", equal but for the program path" if not md_bad and len(md_new) == len(md_ref) else "")
          + ("" if ok else "; DIFFERS: " + "; ".join(issues)))
    return ok


def pairs7c(a):
    opps = sorted(glob.glob(os.path.join(a.repo, "decks", "screen", "opponents", "*.txt")))
    if len(opps) != 8:
        raise Malformed(f"decks/screen/opponents holds {len(opps)} lists, not 8")
    for d in DECKS_7C:
        if not os.path.isfile(os.path.join(a.repo, d)):
            raise Malformed(f"{d} is missing")
    head = ["pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last",
            "sub_block_end"]
    rows, p = ["\t".join(head)], FIRST_7C
    for d in DECKS_7C:
        key = os.path.splitext(os.path.basename(d))[0]
        for o in opps:
            oname = os.path.splitext(os.path.basename(o))[0]
            s = BASE_7C + 10_000 * p
            rows.append("\t".join(str(x) for x in (p, "rules7c", key, d, oname.removeprefix("t-"),
                                                   f"decks/screen/opponents/{oname}.txt", s, s + DEALS_7C - 1,
                                                   s + 9_999)))
            p += 1
    text = "\n".join(rows) + "\n"
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    last = p - 1
    print(f"pairs7c: {short(a.out)}: pairings {FIRST_7C}-{last} ({last - FIRST_7C + 1} rows: "
          f"{', '.join(os.path.splitext(os.path.basename(d))[0][:2] for d in DECKS_7C)} x the 8 panel lists), "
          f"i < {DEALS_7C}, seeds {BASE_7C + 10_000 * FIRST_7C:,} - {BASE_7C + 10_000 * last + DEALS_7C - 1:,} "
          f"(23,100,000,000 + pairing x 10,000 + i; step 8 uses pairings 0-31 and 8b 32-35, seeds up to "
          f"{BASE_7C + 10_000 * 35 + 499:,})")
    return True


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("counters"); c.add_argument("files", nargs="+"); c.add_argument("--label", required=True)
    c.add_argument("--offgate-in")
    c.add_argument("--require-discard", action="store_true",
                   help="offgate_discard_then_damage must also be above 0 in scope (step 7b: the vespiquen cells)")
    f = sub.add_parser("floor"); f.add_argument("newdir"); f.add_argument("refdir"); f.add_argument("name")
    f.add_argument("--label", required=True)
    p = sub.add_parser("pairs7c"); p.add_argument("--repo", required=True); p.add_argument("--out", required=True)
    a = ap.parse_args()
    fn = {"counters": counters, "floor": floor, "pairs7c": pairs7c}[a.cmd]
    try:
        ok = fn(a)
    except (OSError, ValueError, KeyError, TypeError, Malformed) as e:
        print(f"{a.cmd}: malformed or missing input: {e!r}")
        sys.exit(2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
